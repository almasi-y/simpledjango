from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.conf import settings
from .models import UserProfile
from .forms import CustomUserCreationForm, UserProfileForm, AdminUserEditForm
import uuid


def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'accounts/home.html')


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Send verification email (mock)
            send_verification_email(user)
            messages.success(request, 'Registration successful! Please check your email for verification.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


@login_required
def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def dashboard(request):
    """User dashboard view"""
    context = {
        'user': request.user,
        'profile': request.user.userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    """View user profile"""
    context = {
        'user': request.user,
        'profile': request.user.userprofile,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Old password is incorrect.')
        elif new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        else:
            request.user.set_password(new_password1)
            request.user.save()
            messages.success(request, 'Password changed successfully! Please log in again.')
            return redirect('accounts:login')
    
    return render(request, 'accounts/change_password.html')


def verify_email(request, token):
    """Email verification view"""
    try:
        profile = UserProfile.objects.get(verification_token=token)
        if not profile.is_verified:
            profile.is_verified = True
            profile.save()
            messages.success(request, 'Email verified successfully! You can now log in.')
        else:
            messages.info(request, 'Email already verified.')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid verification token.')
    
    return redirect('accounts:login')


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.user_type == 'admin'


@user_passes_test(is_admin)
def admin_panel(request):
    """Admin panel view"""
    users = User.objects.all().select_related('userprofile')
    context = {
        'users': users,
        'total_users': users.count(),
        'verified_users': users.filter(userprofile__is_verified=True).count(),
        'admin_users': users.filter(userprofile__user_type='admin').count(),
    }
    return render(request, 'accounts/admin_panel.html', context)


@user_passes_test(is_admin)
def admin_user_edit(request, user_id):
    """Admin edit user view"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('accounts:admin_panel')
    else:
        form = AdminUserEditForm(instance=user.userprofile)
    
    context = {
        'form': form,
        'user_being_edited': user,
    }
    return render(request, 'accounts/admin_user_edit.html', context)


@user_passes_test(is_admin)
def admin_user_delete(request, user_id):
    """Admin delete user view"""
    user = get_object_or_404(User, id=user_id)
    
    if request.user.id == user.id:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('accounts:admin_panel')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('accounts:admin_panel')
    
    return render(request, 'accounts/admin_user_delete.html', {'user_to_delete': user})


def send_verification_email(user):
    """Send verification email (mock implementation)"""
    token = user.userprofile.verification_token
    
    # Use Django's reverse to generate the URL properly
    verification_path = reverse('accounts:verify_email', kwargs={'token': token})
    verification_url = f"http://localhost:8080{verification_path}"
    
    subject = 'Verify your email address'
    message = f"""Hi {user.first_name or user.username},

Thank you for registering! Please click the link below to verify your email address:
{verification_url}

If you didn't create this account, please ignore this email.

Best regards,
User Management Team"""
    
    # In development, this will print to console
    print("=" * 80)
    print(f"VERIFICATION EMAIL SENT TO: {user.email}")
    print(f"VERIFICATION URL: {verification_url}")
    print(f"TOKEN: {token}")
    print("=" * 80)


def verification_test(request):
    """Test page for verification links (development only)"""
    if not settings.DEBUG:
        return HttpResponseForbidden("This page is only available in DEBUG mode")
    
    users = User.objects.all().select_related('userprofile')
    return render(request, 'accounts/verification_test.html', {'users': users})

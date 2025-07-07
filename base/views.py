from datetime import timezone
import profile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from .forms import ProfileForm

from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from .models import Profile, OtpToken

def home(request):
    profiles = Profile.objects.all()
    
    context = {
        'profiles': profiles
    }
    return render(request, 'home.html', context)

def profile(request, pk):
    profile = get_object_or_404(Profile, id=pk)
    context = {
        'profile':profile
    }
    return render(request, 'profile.html', context)

@login_required
def profile_edit(request, pk):
    """Edit profile details"""
    profile = get_object_or_404(Profile, id=pk)
    if request.user.username != profile.user.username:
        return HttpResponse("You are not allowed to edit this profile.")

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProfileForm(instance=profile)

    context = {'form': form}
    return render(request, 'profile_form.html', context)

@login_required
def profile_delete(request, pk):
    profile = Profile.objects.get(id=pk)  # Fetch the room by primary key
    
    if request.user.username != profile.user.username:
        return HttpResponse("You are not allowed to delete this profile.")

    
    if request.method == 'POST':
        profile.delete()  
        return redirect('home')  
    return render(request, 'base/delete.html', {'obj': profile})


@csrf_protect
def signup(request):
    form = ProfileForm()
    if request.method == 'POST':
       form = ProfileForm(request.POST)
       if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! An OTP was sent to your Email")
            return redirect("verify_email", username=request.POST['username'])
    context = {"form": form}
    return render(request, "signup.html", context)

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = auth.authenticate(username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request,'incorrect credentials')
            return redirect ('signin')
        
    return render(request, 'signin.html')

def verify_email(request, username):
    user = get_user_model().objects.get(username=username)
    user_otp = OtpToken.objects.filter(user=user).last()
    
    
    if request.method == 'POST':
        # valid token
        if user_otp.otp_code == request.POST['otp_code']:
            
            # checking for expired token
            if user_otp.otp_expires_at > timezone.now():
                user.is_active=True
                user.save()
                messages.success(request, "Account activated successfully!! You can Login.")
                return redirect("signin")
            
            # expired token
            else:
                messages.warning(request, "The OTP has expired, get a new OTP!")
                return redirect("verify-email", username=user.username)
        
        
        # invalid otp code
        else:
            messages.warning(request, "Invalid OTP entered, enter a valid OTP!")
            return redirect("verify-email", username=user.username)
        
    context = {}
    return render(request, "verify_token.html", context)




def verification_success(request):
    """Display verification success page"""
    return render(request, 'verification_success.html')

def verification_failed(request):
    return render(request, 'verification_failed.html')

def resend_otp(request):
    if request.method == 'POST':
        user_email = request.POST["otp_email"]
        
        if get_user_model().objects.filter(email=user_email).exists():
            user = get_user_model().objects.get(email=user_email)
            otp = OtpToken.objects.create(user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))
            
            
            # email variables
            subject="Email Verification"
            message = f"""
                                Hi {user.username}, here is your OTP {otp.otp_code} 
                                it expires in 5 minute, use the url below to redirect back to the website
                                http://127.0.0.1:8000/verify-email/{user.username}
                                
                                """
            sender = "clintonmatics@gmail.com"
            receiver = [user.email, ]
        
        
            # send email
            send_mail(
                    subject,
                    message,
                    sender,
                    receiver,
                    fail_silently=False,
                )
            
            messages.success(request, "A new OTP has been sent to your email-address")
            return redirect("verify-email", username=user.username)

        else:
            messages.warning(request, "This email dosen't exist in the database")
            return redirect("resend-otp")
        
           
    context = {}
    return render(request, "resend_otp.html", context)



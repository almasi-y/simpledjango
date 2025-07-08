from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile
from .forms import CustomUserCreationForm, UserProfileForm


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        """Test that UserProfile is created when User is created"""
        self.assertTrue(hasattr(self.user, 'userprofile'))
        self.assertEqual(self.user.userprofile.user_type, 'user')
        self.assertFalse(self.user.userprofile.is_verified)
    
    def test_user_profile_str(self):
        """Test UserProfile string representation"""
        expected = f"{self.user.username} - user"
        self.assertEqual(str(self.user.userprofile), expected)
    
    def test_full_name_property(self):
        """Test full_name property"""
        self.user.first_name = 'John'
        self.user.last_name = 'Doe'
        self.user.save()
        self.assertEqual(self.user.userprofile.full_name, 'John Doe')
        
        # Test with no names
        self.user.first_name = ''
        self.user.last_name = ''
        self.user.save()
        self.assertEqual(self.user.userprofile.full_name, '')


class CustomUserCreationFormTest(TestCase):
    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'user_type': 'user',
            'phone_number': '1234567890',
            'address': '123 Test St'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_password_mismatch(self):
        """Test form with mismatched passwords"""
        form_data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'testpass123',
            'password2': 'differentpass',
            'user_type': 'user'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_form_save(self):
        """Test form save creates user and profile correctly"""
        form_data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'user_type': 'admin',
            'phone_number': '1234567890',
            'address': '123 Test St'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'john@example.com')
        self.assertEqual(user.userprofile.user_type, 'admin')
        self.assertEqual(user.userprofile.phone_number, '1234567890')


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.admin_user.userprofile.user_type = 'admin'
        self.admin_user.userprofile.save()
    
    def test_home_view(self):
        """Test home page loads correctly"""
        response = self.client.get(reverse('accounts:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User Management System')
    
    def test_register_view_get(self):
        """Test register page loads correctly"""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Account')
    
    def test_register_view_post_valid(self):
        """Test user registration with valid data"""
        form_data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'user_type': 'user',
            'phone_number': '1234567890',
            'address': '123 Test St'
        }
        response = self.client.post(reverse('accounts:register'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        
        # Check user was created
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.email, 'john@example.com')
    
    def test_login_view_get(self):
        """Test login page loads correctly"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_login_view_post_valid(self):
        """Test user login with valid credentials"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
    
    def test_login_view_post_invalid(self):
        """Test user login with invalid credentials"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
    
    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_authenticated(self):
        """Test dashboard loads for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
    
    def test_profile_view_requires_login(self):
        """Test profile view requires authentication"""
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_view_authenticated(self):
        """Test profile view loads for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Profile')
    
    def test_admin_panel_requires_admin(self):
        """Test admin panel requires admin user"""
        # Test unauthenticated user
        response = self.client.get(reverse('accounts:admin_panel'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test regular user
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:admin_panel'))
        self.assertEqual(response.status_code, 302)  # Redirect (access denied)
    
    def test_admin_panel_admin_access(self):
        """Test admin panel loads for admin user"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('accounts:admin_panel'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Panel')
    
    def test_email_verification(self):
        """Test email verification with valid token"""
        token = self.user.userprofile.verification_token
        response = self.client.get(reverse('accounts:verify_email', args=[token]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Check user is verified
        self.user.userprofile.refresh_from_db()
        self.assertTrue(self.user.userprofile.is_verified)
    
    def test_email_verification_invalid_token(self):
        """Test email verification with invalid token"""
        import uuid
        invalid_token = uuid.uuid4()
        response = self.client.get(reverse('accounts:verify_email', args=[invalid_token]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Check user is not verified
        self.user.userprofile.refresh_from_db()
        self.assertFalse(self.user.userprofile.is_verified)

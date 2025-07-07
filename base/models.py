from django.db import models
from django.contrib.auth import get_user_model
import secrets
from django.conf import settings

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=100)
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True) 
    is_email_verified = models.BooleanField(default=False)

    

    def __str__(self):
        return self.user.username
    
class OtpToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps")
    otp_code = models.CharField(max_length=6, default=secrets.token_hex(3))
    tp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)
    
    
    def __str__(self):
        return self.user.username
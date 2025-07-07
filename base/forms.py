from django.forms import ModelForm 
from .models import Profile

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'  # Include all fields from the Room model
          # Exclude fields that should not be set by the form
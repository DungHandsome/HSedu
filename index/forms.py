from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User, Student, Teacher, Announcement

class SignUpForm(UserCreationForm):
    # Additional fields not in AbstractUser by default
    full_name = forms.CharField(max_length=255, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    is_teacher = forms.BooleanField(required=False, label="Register as Teacher?")
    
    # Role-specific fields
    major = forms.CharField(max_length=255, required=False, label="Major (Teachers only)")
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "full_name", "phone_number", "is_teacher")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with this username already exists.")
        return username

class AnnouncementForm(forms.ModelForm):    
    class Meta:
        model = Announcement
        fields = ['title', 'content']


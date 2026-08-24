from django import forms
from django.contrib.auth.models import User
from .models import Profile, Review, UserProfile
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            validate_password(password)   # Django's built-in strength checker
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return password

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password2'):
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_pic']

class ReviewForm(forms.ModelForm):

    rating = forms.ChoiceField(
        choices=[
            (5, "⭐⭐⭐⭐⭐ Excellent"),
            (4, "⭐⭐⭐⭐ Very Good"),
            (3, "⭐⭐⭐ Good"),
            (2, "⭐⭐ Fair"),
            (1, "⭐ Poor"),
        ]
    )

    class Meta:
        model = Review
        fields = ['rating', 'review']

        widgets = {
            'review': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write your review here...'
            })
        }

class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['profile_name', 'avatar', 'is_kids']
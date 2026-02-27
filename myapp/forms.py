from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from captcha.fields import CaptchaField

from .models import EngagementRecord


class RegisterForm(UserCreationForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Username'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Email'
        })
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password'
        })
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )

    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove default help text
        for fieldname in self.fields:
            self.fields[fieldname].help_text = None

        # Style captcha input
        self.fields['captcha'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Captcha'
        })


class LoginForm(forms.Form):

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Username'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password'
        })
    )

    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['captcha'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Captcha'
        })
    
        self.fields['captcha'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Captcha'
        })

class EngagementRecordForm(forms.ModelForm):
    class Meta:
        model = EngagementRecord
        fields = ['attention_score', 'emotion']
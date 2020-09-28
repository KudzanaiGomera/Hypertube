from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class AccountForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2'
        ]

class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(help_text=False)
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email'
        ]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic']


class CommentForm(forms.ModelForm): 
    class Meta:
        model = Comment
        fields = ['comment']
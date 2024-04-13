from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList

from .models import Account, UserProfile
 
 
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter your password',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm password',
    }))
     
    class Meta:
        model = Account
        fields = [
            'first_name', 'last_name', 'phone_number', 'email', 'password'
        ]
    
    # Implement CSS class to all fields 
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter your first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter your last name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter your phone number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
    # def clean(self):
    #     cleaned_data = super(RegistrationForm, self).clean()
    #     password = cleaned_data.get('password')
    #     confirm_password = cleaned_data.get('confirm_password')
        
    #     if password != confirm_password:
    #         raise forms.ValidationError(
    #             "password does not match!"
    #         )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        model = self.Meta.model
        user = model.objects.filter(email__iexact=email)
        
        if user.exists():
            raise forms.ValidationError("A user with that email already exists!")
        
        return self.cleaned_data.get('email')


    def clean_password(self):
        password = self.cleaned_data.get('password')
        confrim_password = self.data.get('confirm_password')
        
        if password != confrim_password:
            raise forms.ValidationError("Passwords do not match")

        return self.cleaned_data.get('password')
    
    
class UserForm(forms.ModelForm):
    
    class Meta:
        model = Account
        fields = (
            'first_name', 'last_name', 'phone_number',
        )
        
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        
        
class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        required=False, error_messages={'invalid': ('Image files only')}, widget=forms.FileInput
    ) # get rid of extra information
    class Meta:
        model = UserProfile
        fields = (
            'address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture',
        )
        
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
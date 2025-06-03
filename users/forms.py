

# users/forms.py - Create a proper form class
from django import forms
from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'user_type', 'department', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full rounded-md py-1 px-2 border-gray-500 focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50',
                'placeholder': 'Enter username'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full rounded-md py-1 px-2 border-gray-500 focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full rounded-md py-1 px-2 border-gray-500 focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50',
                'placeholder': 'Enter last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full rounded-md py-1 px-2 border-gray-500 focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50',
                'placeholder': 'Enter email address'
            }),
            'department': forms.Select(attrs={
                'class': 'w-full rounded-md py-1 px-2 border-gray-500 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50',
            }),
            'user_type': forms.Select(attrs={
                'class': 'w-full rounded-md py-1 px-2 border-gray-500 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded py-1 px-2 border-gray-500 text-blue-600 focus:ring-blue-500'
            })
        }

    def __init__(self, *args, **kwargs):
        is_update = kwargs.pop('is_update', False)
        super().__init__(*args, **kwargs)
        
        # Make username readonly for updates
        if is_update:
            self.fields['username'].widget.attrs['readonly'] = True
        
        # Set required fields
        self.fields['username'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['user_type'].required = True

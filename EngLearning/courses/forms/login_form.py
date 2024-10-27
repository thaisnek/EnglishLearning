from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ValidationError

class LoginForm(AuthenticationForm):
    username = forms.EmailField(max_length=255, required=True, label='Email Address')

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("Email or Password invalid")

        self.cleaned_data['username'] = user.username

        return super().clean()

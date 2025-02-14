from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import UserProfile
import re
from django.utils import timezone

class CustomAuthenticationForm(AuthenticationForm):
    """
    Кастомна форма автентифікації з покращеним UI та валідацією.
    """
    username = forms.CharField(
        label=_('Username or Email'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your username or email'),
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your password'),
            'autocomplete': 'current-password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('username') or not cleaned_data.get('password'):
            raise forms.ValidationError(_('Both username and password are required.'))
        return cleaned_data

class CustomUserCreationForm(UserCreationForm):
    """
    Розширена форма створення користувача з додатковою валідацією.
    """
    username = forms.CharField(
        label=_('Username'),
        min_length=3,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'username'
        })
    )
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'autocomplete': 'email'
        })
    )
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_username(self):
        """Перевірка унікальності імені користувача та його формату."""
        username = self.cleaned_data.get('username')
        if not re.match(r'^[\w.@+-]+$', username):
            raise forms.ValidationError(
                _('Username can only contain letters, numbers, and @/./+/-/_ characters.')
            )
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_('This username is already taken.'))
        return username

    def clean_email(self):
        """Перевірка унікальності email."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is already registered.'))
        return email

    def clean_password2(self):
        """Перевірка співпадіння паролів та їх складності."""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Passwords do not match.'))
        
        # Перевірка складності пароля
        if len(password2) < 8:
            raise forms.ValidationError(_('Password must be at least 8 characters long.'))
        if not re.search(r'[A-Z]', password2):
            raise forms.ValidationError(_('Password must contain at least one uppercase letter.'))
        if not re.search(r'[a-z]', password2):
            raise forms.ValidationError(_('Password must contain at least one lowercase letter.'))
        if not re.search(r'\d', password2):
            raise forms.ValidationError(_('Password must contain at least one digit.'))
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password2):
            raise forms.ValidationError(_('Password must contain at least one special character.'))
        
        return password2

class UserProfileForm(forms.ModelForm):
    """
    Форма для профілю користувача з розширеною валідацією.
    """
    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'birth_year', 'gender')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your first name')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your last name')
            }),
            'birth_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your birth year')
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def clean_first_name(self):
        """Перевірка формату імені."""
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            if not re.match(r'^[A-Za-zА-Яа-яІіЇїЄєҐґ\s\'-]+$', first_name):
                raise forms.ValidationError(_('First name can only contain letters, spaces, hyphens and apostrophes.'))
        return first_name

    def clean_last_name(self):
        """Перевірка формату прізвища."""
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            if not re.match(r'^[A-Za-zА-Яа-яІіЇїЄєҐґ\s\'-]+$', last_name):
                raise forms.ValidationError(_('Last name can only contain letters, spaces, hyphens and apostrophes.'))
        return last_name

    def clean_birth_year(self):
        """Перевірка року народження."""
        birth_year = self.cleaned_data.get('birth_year')
        if birth_year:
            current_year = timezone.now().year
            if birth_year < 1900 or birth_year > current_year:
                raise forms.ValidationError(_('Please enter a valid birth year between 1900 and current year.'))
        return birth_year

    def clean_gender(self):
        """Перевірка статі."""
        gender = self.cleaned_data.get('gender')
        if not gender:
            raise forms.ValidationError(_('Please select your gender.'))
        if gender not in dict(UserProfile.GENDER_CHOICES).keys():
            raise forms.ValidationError(_('Invalid gender selection.'))
        return gender 
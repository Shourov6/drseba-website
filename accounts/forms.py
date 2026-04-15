"""
Forms for accounts app
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import User, PatientProfile


def is_gmail_address(value):
    return bool(value) and value.strip().lower().endswith('@gmail.com')


def normalize_bd_phone(country_code, phone_number):
    country_code = (country_code or '+880').strip()
    phone_number = ''.join(ch for ch in (phone_number or '') if ch.isdigit())

    if phone_number.startswith('880') and len(phone_number) == 13:
        phone_number = phone_number[2:]

    if phone_number.startswith('0') and len(phone_number) == 11:
        return f'{country_code}{phone_number[1:]}'

    if phone_number.startswith('1') and len(phone_number) == 10:
        return f'{country_code}{phone_number}'

    return ''


def generate_unique_username(base_value):
    base_value = ''.join(ch for ch in (base_value or '').strip().lower() if ch.isalnum() or ch in '._-')
    if not base_value:
        base_value = 'user'

    username = base_value[:150]
    suffix = 1
    while User.objects.filter(username=username).exists():
        suffix += 1
        username = f'{base_value[:140]}{suffix}'[:150]
    return username


class LoginForm(forms.Form):
    """Login form using phone number or Gmail address"""

    identifier = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mobile number or Gmail address'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class SimpleUserCreationForm(UserCreationForm):
    """Simplified user creation form with minimal validation"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password help text
        self.fields['password1'].help_text = 'Any simple password (4+ characters)'
        self.fields['password2'].help_text = 'Confirm your password'
    
    def clean_password1(self):
        """Allow any password with at least 1 character"""
        password1 = self.cleaned_data.get('password1')
        if password1 and len(password1) < 1:
            raise forms.ValidationError("Password must be at least 1 character.")
        return password1
    
    def clean_password2(self):
        """Check passwords match"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        return password2


class PatientRegistrationForm(SimpleUserCreationForm):
    """Patient registration form - simplified and user friendly"""
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name (optional)'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name (optional)'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Gmail address (must be unique)'
        })
    )
    country_code = forms.ChoiceField(
        choices=[('+880', '+880')],
        initial='+880',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    phone_number = forms.CharField(
        max_length=11,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '01XXXXXXXXX'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password (4+ characters)'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'country_code', 'phone_number', 'password1', 'password2']
    
    def clean_email(self):
        """Check email is unique"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        if email and not is_gmail_address(email):
            raise forms.ValidationError("Please use a Gmail address.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)
    
    def clean_phone_number(self):
        """Validate Bangladeshi mobile number"""
        phone_number = (self.cleaned_data.get('phone_number') or '').strip()
        if not phone_number:
            raise forms.ValidationError("Mobile number is required.")
        if not phone_number.isdigit() or len(phone_number) != 11 or not phone_number.startswith('01'):
            raise forms.ValidationError("Enter a valid Bangladeshi mobile number with 11 digits, starting with 01.")
        full_phone = normalize_bd_phone(self.cleaned_data.get('country_code'), phone_number)
        if not full_phone:
            raise forms.ValidationError("Enter a valid Bangladeshi mobile number.")
        if User.objects.filter(phone=full_phone).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone_number
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = normalize_bd_phone(self.cleaned_data.get('country_code'), self.cleaned_data['phone_number'])
        user.role = 'patient'
        user.username = generate_unique_username(user.phone or user.email.split('@')[0])
        if commit:
            user.save()
            PatientProfile.objects.create(user=user)
        return user


class DoctorRegistrationForm(UserCreationForm):
    """Doctor registration form"""
    
    phone_regex = RegexValidator(
        regex=r'^\+?8801[3-9]\d{8}$|^\d{10,}$',
        message="Enter a valid phone number (e.g., +8801711111111 or 01711111111)"
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Gmail address'
        })
    )
    phone = forms.CharField(
        validators=[phone_regex],
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number (optional)'
        })
    )
    bmdc_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'BMDC Registration Number'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'bmdc_number', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)
        self.fields['username'] = forms.CharField(required=False, widget=forms.HiddenInput(), initial='')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        if email and not is_gmail_address(email):
            raise forms.ValidationError("Please use a Gmail address.")
        return email

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()
        if phone and not phone.isdigit() and not phone.startswith('+880'):
            raise forms.ValidationError("Enter a valid phone number.")
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.role = 'doctor'
        user.is_verified = False  # Doctors need verification
        user.username = generate_unique_username(user.email.split('@')[0])
        if commit:
            user.save()
        return user


class PatientProfileForm(forms.ModelForm):
    """Patient profile update form"""
    
    class Meta:
        model = PatientProfile
        fields = ['date_of_birth', 'gender', 'blood_group', 'address', 'city', 
                  'district', 'emergency_contact', 'medical_history', 'allergies', 'profile_picture']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., A+'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+8801XXXXXXXXX'}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class PasswordChangeForm(forms.Form):
    """Password change form"""
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current Password'
        })
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("New passwords do not match.")
        
        return cleaned_data


class EmployeeCreationForm(forms.ModelForm):
    """Admin form for creating employee accounts"""
    
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Set Password for Employee'
        }),
        help_text='The password the employee will use to log in'
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+8801XXXXXXXXX'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        email = cleaned_data.get('email')
        
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        if email and not is_gmail_address(email):
            raise forms.ValidationError("Please use a Gmail address.")
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
            if len(password) < 4:
                raise forms.ValidationError("Password must be at least 4 characters long.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'employee'
        user.username = generate_unique_username(self.cleaned_data['email'].split('@')[0])
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class DoctorCreationForm(forms.ModelForm):
    """Admin form for creating doctor accounts"""
    
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Set Password for Doctor'
        }),
        help_text='The password the doctor will use to log in'
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+8801XXXXXXXXX'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        email = cleaned_data.get('email')
        
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        if email and not is_gmail_address(email):
            raise forms.ValidationError("Please use a Gmail address.")
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
            if len(password) < 4:
                raise forms.ValidationError("Password must be at least 4 characters long.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'doctor'
        user.username = generate_unique_username(self.cleaned_data['email'].split('@')[0])
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

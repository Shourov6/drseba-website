from django import forms
from django.contrib.auth import get_user_model
from doctors.models import Doctor, Specialty
from .forms import is_gmail_address, generate_unique_username

User = get_user_model()

class DoctorAdminCreationForm(forms.ModelForm):
    # User fields
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    # Doctor fields
    bmdc_number = forms.CharField(max_length=20, required=True)
    specialties = forms.ModelMultipleChoiceField(queryset=Specialty.objects.all(), required=True, widget=forms.CheckboxSelectMultiple)
    qualifications = forms.CharField(widget=forms.Textarea, required=True)
    experience_years = forms.IntegerField(min_value=0, required=True)
    about = forms.CharField(widget=forms.Textarea, required=False)
    profile_picture = forms.ImageField(required=False)
    cover_image = forms.ImageField(required=False)
    consultation_fee_online = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    consultation_fee_in_person = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    is_verified = forms.BooleanField(required=False)
    is_active = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Doctor
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'password', 'confirm_password',
            'bmdc_number', 'specialties', 'qualifications', 'experience_years', 'about',
            'profile_picture', 'cover_image', 'consultation_fee_online', 'consultation_fee_in_person',
            'is_verified', 'is_active'
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        email = cleaned_data.get('email')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        if email and not is_gmail_address(email):
            raise forms.ValidationError('Please use a Gmail address.')
        return cleaned_data

    def save(self, commit=True):
        # Create user
        user = User(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data['phone'],
            role='doctor',
            username=generate_unique_username(self.cleaned_data['email'].split('@')[0]),
            is_active=self.cleaned_data.get('is_active', True),
        )
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        # Create doctor profile
        doctor = Doctor(
            user=user,
            bmdc_number=self.cleaned_data['bmdc_number'],
            qualifications=self.cleaned_data['qualifications'],
            experience_years=self.cleaned_data['experience_years'],
            about=self.cleaned_data['about'],
            consultation_fee_online=self.cleaned_data['consultation_fee_online'],
            consultation_fee_in_person=self.cleaned_data['consultation_fee_in_person'],
            is_verified=self.cleaned_data.get('is_verified', False),
            is_active=self.cleaned_data.get('is_active', True),
        )
        if self.cleaned_data.get('profile_picture'):
            doctor.profile_picture = self.cleaned_data['profile_picture']
        if self.cleaned_data.get('cover_image'):
            doctor.cover_image = self.cleaned_data['cover_image']
        if commit:
            doctor.save()
            doctor.specialties.set(self.cleaned_data['specialties'])
        return doctor

"""
Forms for doctors app
"""
from django import forms
from .models import Review, Doctor, DoctorHospital
from accounts.models import User


class ReviewForm(forms.ModelForm):
    """Review form"""
    
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Rating'
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Share your experience with this doctor...'
        }),
        label='Your Review'
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']


class DoctorProfileForm(forms.ModelForm):
    """Doctor profile update form"""
    
    class Meta:
        model = Doctor
        fields = [
            'qualifications', 'experience_years', 'about',
            'consultation_fee_online', 'consultation_fee_in_person',
            'profile_picture', 'cover_image'
        ]
        widgets = {
            'qualifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'consultation_fee_online': forms.NumberInput(attrs={'class': 'form-control'}),
            'consultation_fee_in_person': forms.NumberInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DoctorHospitalForm(forms.ModelForm):
    """Doctor hospital/chamber form"""
    
    class Meta:
        model = DoctorHospital
        fields = [
            'hospital', 'room_number', 'consultation_days',
            'morning_start', 'morning_end', 'evening_start', 'evening_end',
            'is_primary', 'is_active'
        ]
        widgets = {
            'hospital': forms.Select(attrs={'class': 'form-select'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'consultation_days': forms.CheckboxSelectMultiple(),
            'morning_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'morning_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'evening_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'evening_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DoctorAccountCreationForm(forms.ModelForm):
    """Admin form for creating doctor user accounts"""
    
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
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
            if len(password) < 4:
                raise forms.ValidationError("Password must be at least 4 characters long.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'doctor'
        user.username = self.cleaned_data['email'].split('@')[0]  # Use email prefix as username
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

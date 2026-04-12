"""
Forms for DrSeva Healthcare Admin Dashboard
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Doctor, Hospital, DoctorHospital, Patient, Employee, Appointment, Payment


class LoginForm(AuthenticationForm):
    """Custom login form with role selection"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    ]
    
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class DoctorForm(forms.ModelForm):
    """Form for adding/editing doctors"""
    class Meta:
        model = Doctor
        fields = [
            'name', 'age', 'gender', 'phone', 'email', 'profile_photo',
            'qualification', 'specialty', 'experience', 'medical_license_number', 'about',
            'commission_percentage', 'consultation_language', 'online_appointment',
            'max_patients_per_day', 'emergency_available',
            'certificates', 'id_proof', 'license_document', 'status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doctor Name'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., MBBS, MD (Cardiology)'}),
            'specialty': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Cardiology'}),
            'experience': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years of Experience'}),
            'medical_license_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'License Number'}),
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'About Doctor'}),
            'commission_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'consultation_language': forms.Select(attrs={'class': 'form-control'}),
            'online_appointment': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_patients_per_day': forms.NumberInput(attrs={'class': 'form-control'}),
            'emergency_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class DoctorHospitalForm(forms.ModelForm):
    """Form for doctor hospital schedule"""
    class Meta:
        model = DoctorHospital
        fields = ['hospital', 'days', 'time', 'contact_number', 'chamber_address', 'consultation_fee', 'service_charge']
        widgets = {
            'hospital': forms.Select(attrs={'class': 'form-control'}),
            'days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Sun, Tue, Thu'}),
            'time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 09:00 - 12:00'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'}),
            'chamber_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Chamber Address'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Consultation Fee (৳)'}),
            'service_charge': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Service Charge (৳)'}),
        }


class HospitalForm(forms.ModelForm):
    """Form for adding/editing hospitals"""
    class Meta:
        model = Hospital
        fields = ['name', 'location', 'contact', 'email', 'total_beds', 'icu_beds', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hospital Name'}),
            'location': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Hospital Location/Address'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'total_beds': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total Beds'}),
            'icu_beds': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ICU Beds'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class PatientForm(forms.ModelForm):
    """Form for adding/editing patients"""
    class Meta:
        model = Patient
        fields = ['name', 'age', 'gender', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Patient Name'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }


class EmployeeForm(forms.ModelForm):
    """Form for adding/editing employees"""
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password (leave blank to keep unchanged)'})
    )
    
    class Meta:
        model = Employee
        fields = ['name', 'age', 'gender', 'phone', 'email', 'profile_photo', 'role', 'status', 'hire_date', 'password']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee Name'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def save(self, commit=True):
        employee = super().save(commit=False)
        
        # Create or update associated User
        if not employee.user_id:
            user = User.objects.create_user(
                username=self.cleaned_data['email'].split('@')[0],
                email=self.cleaned_data['email'],
                password=self.cleaned_data.get('password', 'defaultpass123'),
                role='admin' if self.cleaned_data['role'] == 'Admin' else 'employee',
                first_name=self.cleaned_data['name']
            )
            employee.user = user
        elif self.cleaned_data.get('password'):
            employee.user.set_password(self.cleaned_data['password'])
            employee.user.save()
        
        if commit:
            employee.save()
        return employee


class AppointmentForm(forms.ModelForm):
    """Form for adding/editing appointments"""
    class Meta:
        model = Appointment
        fields = [
            'patient', 'doctor', 'date', 'time', 'appointment_type',
            'service_charge', 'notes', 'is_distributed', 'managed_by',
            'manager_status', 'doctor_status'
        ]
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'appointment_type': forms.Select(attrs={'class': 'form-control'}),
            'service_charge': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Service Charge (৳)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional Notes'}),
            'is_distributed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'managed_by': forms.Select(attrs={'class': 'form-control'}),
            'manager_status': forms.Select(attrs={'class': 'form-control'}),
            'doctor_status': forms.Select(attrs={'class': 'form-control'}),
        }


class PaymentForm(forms.ModelForm):
    """Form for adding/editing payments"""
    class Meta:
        model = Payment
        fields = ['patient', 'doctor', 'consultation_fee', 'service_charge', 'payment_method', 'status', 'payment_date']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Consultation Fee (৳)'}),
            'service_charge': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Service Charge (৳)'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

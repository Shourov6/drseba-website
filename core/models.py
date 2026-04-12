"""
Models for DrSeva Healthcare Admin Dashboard
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class User(AbstractUser):
    """Custom User model with role-based access"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_employee_user(self):
        return self.role == 'employee'
    
    def __str__(self):
        return f"{self.username} ({self.role})"


class Hospital(models.Model):
    """Hospital model"""
    hospital_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    location = models.TextField()
    contact = models.CharField(max_length=20)
    email = models.EmailField()
    total_beds = models.PositiveIntegerField(default=0)
    icu_beds = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.hospital_id:
            self.hospital_id = f"HOS-{uuid.uuid4().hex[:4].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class Doctor(models.Model):
    """Doctor model with professional details"""
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    LANGUAGE_CHOICES = [
        ('Bangla', 'Bangla'),
        ('English', 'English'),
        ('Both', 'Both'),
    ]
    
    doctor_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    profile_photo = models.ImageField(upload_to='doctors/', blank=True, null=True)
    
    # Professional details
    qualification = models.CharField(max_length=300)
    specialty = models.CharField(max_length=100)
    experience = models.PositiveIntegerField(default=0)
    medical_license_number = models.CharField(max_length=100)
    about = models.TextField(blank=True, null=True)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    
    # Consultation settings
    consultation_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='Both')
    online_appointment = models.BooleanField(default=True)
    max_patients_per_day = models.PositiveIntegerField(default=20)
    emergency_available = models.BooleanField(default=False)
    
    # Documents
    certificates = models.FileField(upload_to='documents/certificates/', blank=True, null=True)
    id_proof = models.FileField(upload_to='documents/id_proofs/', blank=True, null=True)
    license_document = models.FileField(upload_to='documents/licenses/', blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')
    registration_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.doctor_id:
            self.doctor_id = f"DOC-{uuid.uuid4().hex[:4].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Dr. {self.name}"
    
    class Meta:
        ordering = ['-created_at']


class DoctorHospital(models.Model):
    """Many-to-Many relationship between Doctor and Hospital with additional fields"""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='hospital_schedules')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctor_schedules')
    days = models.CharField(max_length=100)  # e.g., "Sun, Tue, Thu"
    time = models.CharField(max_length=50)  # e.g., "09:00 - 12:00"
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    chamber_address = models.TextField(blank=True, null=True)
    patient_count = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.doctor.name} - {self.hospital.name}"
    
    class Meta:
        unique_together = ['doctor', 'hospital']
        ordering = ['-created_at']


class Patient(models.Model):
    """Patient model"""
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class Employee(models.Model):
    """Employee model for appointment managers"""
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Employee', 'Employee'),
    ]
    
    employee_id = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile', blank=True, null=True)
    name = models.CharField(max_length=200)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    profile_photo = models.ImageField(upload_to='employees/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Employee')
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')
    hire_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = f"EMP-{uuid.uuid4().hex[:4].upper()}"
        super().save(*args, **kwargs)
    
    def get_assigned_appointments_count(self):
        return self.assigned_appointments.count()
    
    def __str__(self):
        return f"{self.name} ({self.employee_id})"
    
    class Meta:
        ordering = ['-created_at']


class Appointment(models.Model):
    """Appointment model with status tracking"""
    STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'),
        ('Pending', 'Pending'),
        ('Cancelled', 'Cancelled'),
    ]
    
    TYPE_CHOICES = [
        ('Consultation', 'Consultation'),
        ('Follow-up', 'Follow-up'),
        ('Checkup', 'Checkup'),
        ('Emergency', 'Emergency'),
    ]
    
    appointment_id = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    
    # Appointment details
    date = models.DateField()
    time = models.TimeField()
    appointment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Consultation')
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    
    # Distribution status
    is_distributed = models.BooleanField(default=False)
    managed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='assigned_appointments', blank=True, null=True)
    
    # Status tracking
    manager_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    doctor_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    final_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_final_status(self):
        """Calculate final status based on manager and doctor status"""
        if self.manager_status == 'Cancelled' or self.doctor_status == 'Cancelled':
            return 'Cancelled'
        elif self.manager_status == 'Pending' or self.doctor_status == 'Pending':
            return 'Pending'
        elif self.manager_status == 'Confirmed' and self.doctor_status == 'Confirmed':
            return 'Confirmed'
        return 'Pending'
    
    def save(self, *args, **kwargs):
        if not self.appointment_id:
            self.appointment_id = f"APT-{uuid.uuid4().hex[:4].upper()}"
        # Auto-calculate final status
        self.final_status = self.calculate_final_status()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.appointment_id} - {self.patient.name} with {self.doctor.name}"
    
    class Meta:
        ordering = ['-date', '-time']


class Payment(models.Model):
    """Payment/Invoice model"""
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Overdue', 'Overdue'),
    ]
    
    METHOD_CHOICES = [
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('Cash', 'Cash'),
        ('Insurance', 'Insurance'),
        ('Bank Transfer', 'Bank Transfer'),
    ]
    
    invoice_id = models.CharField(max_length=20, unique=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='payments', blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='payments')
    
    # Amount details
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment details
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='Cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_date = models.DateField(default=timezone.now)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_total(self):
        """Calculate total amount"""
        return self.consultation_fee + self.service_charge
    
    def save(self, *args, **kwargs):
        if not self.invoice_id:
            self.invoice_id = f"INV-{uuid.uuid4().hex[:4].upper()}"
        self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.invoice_id} - {self.patient.name}"
    
    class Meta:
        ordering = ['-created_at']

"""
Models for doctors app
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from decimal import Decimal
import re


class Specialty(models.Model):
    """Doctor specialty/specialization"""
    
    name = models.CharField(max_length=100, unique=True)
    name_bn = models.CharField(max_length=100, blank=True, help_text="Bangla name")
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or name")
    color = models.CharField(max_length=7, default="#0A74DA", help_text="Hex color code")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Specialty'
        verbose_name_plural = 'Specialties'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Hospital(models.Model):
    """Hospital/Clinic model"""
    
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='hospitals/logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Bed information
    total_beds = models.PositiveIntegerField(default=0)
    icu_beds_available = models.PositiveIntegerField(default=0)
    
    # Location coordinates for map
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Hospital'
        verbose_name_plural = 'Hospitals'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_doctors_count(self):
        """Get number of doctors associated with this hospital"""
        return self.doctors.count()


class Doctor(models.Model):
    """Doctor profile model"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    
    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    
    # Professional Information
    bmdc_number = models.CharField(max_length=20, unique=True, help_text="BMDC Registration Number")
    specialties = models.ManyToManyField(Specialty, related_name='doctors')
    qualifications = models.TextField(help_text="Degrees and qualifications")
    experience_years = models.PositiveIntegerField(default=0)
    about = models.TextField(blank=True, help_text="Doctor's bio/description")
    
    # Profile
    profile_picture = models.ImageField(upload_to='doctors/profiles/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='doctors/covers/', blank=True, null=True)
    
    # Consultation Fees
    consultation_fee_online = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    consultation_fee_in_person = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    verification_date = models.DateTimeField(null=True, blank=True)
    
    # Rating
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Commission rate (percentage)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'
        ordering = ['-rating', '-total_reviews']

    @staticmethod
    def _strip_dr_prefix(value):
        """Remove leading Dr prefixes like Dr, Dr., dr, dr."""
        if not value:
            return ''
        return re.sub(r'^\s*dr\.?\s+', '', str(value), flags=re.IGNORECASE).strip()

    def _clean_name(self):
        first = self._strip_dr_prefix(self.user.first_name)
        last = self._strip_dr_prefix(self.user.last_name)
        full = f"{first} {last}".strip()
        if full:
            return full
        return self._strip_dr_prefix(self.user.get_full_name() or self.user.username)
    
    def __str__(self):
        return f"Dr. {self._clean_name()}"
    
    def get_full_name(self):
        return f"Dr. {self._clean_name()}"
    
    def get_primary_specialty(self):
        return self.specialties.first()

    def get_hospital_consultation_fee(self, hospital=None):
        """Return in-person fee configured on DoctorHospital association."""
        hospital_links = self.hospitals.filter(is_active=True)

        if hospital is not None:
            hospital_id = hospital.id if hasattr(hospital, 'id') else hospital
            specific_link = hospital_links.filter(hospital_id=hospital_id).first()
            if specific_link and (specific_link.consultation_fee or Decimal('0.00')) > Decimal('0.00'):
                return specific_link.consultation_fee

        primary_link = hospital_links.filter(is_primary=True).first()
        if primary_link and (primary_link.consultation_fee or Decimal('0.00')) > Decimal('0.00'):
            return primary_link.consultation_fee

        lowest_link = hospital_links.filter(consultation_fee__gt=0).order_by('consultation_fee').first()
        if lowest_link:
            return lowest_link.consultation_fee

        return Decimal('0.00')

    def get_consultation_fee(self, consultation_type='in_person', hospital=None):
        """Resolve consultation fee consistently across the project."""
        consultation_type = (consultation_type or 'in_person').lower()

        if consultation_type == 'online':
            return self.consultation_fee_online or Decimal('0.00')

        hospital_fee = self.get_hospital_consultation_fee(hospital=hospital)
        if hospital_fee > Decimal('0.00'):
            return hospital_fee

        return self.consultation_fee_in_person or Decimal('0.00')

    @property
    def display_in_person_fee(self):
        """Template-friendly in-person fee."""
        return self.get_consultation_fee('in_person')

    @property
    def display_online_fee(self):
        """Template-friendly online fee."""
        return self.get_consultation_fee('online')
    
    def update_rating(self):
        """Update doctor's average rating"""
        reviews = self.reviews.filter(is_active=True)
        if reviews.exists():
            self.rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.total_reviews = reviews.count()
            self.save()


class DoctorHospital(models.Model):
    """Doctor's association with hospitals (chambers)"""
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='hospitals')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctors')
    room_number = models.CharField(max_length=20, blank=True)
    consultation_days = models.JSONField(default=list, help_text="List of days: ['Mon', 'Tue', etc]")
    
    # Per-hospital fees
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Consultation fee for this hospital")
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Service charge for this hospital")

    # Time slots (2-hour intervals)
    morning_start = models.TimeField(null=True, blank=True)
    morning_end = models.TimeField(null=True, blank=True)
    evening_start = models.TimeField(null=True, blank=True)
    evening_end = models.TimeField(null=True, blank=True)

    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Doctor Hospital'
        verbose_name_plural = 'Doctor Hospitals'
        unique_together = ['doctor', 'hospital']
    
    def __str__(self):
        return f"{self.doctor} - {self.hospital}"


class Review(models.Model):
    """Patient reviews for doctors"""
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews')
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ['doctor', 'patient']
    
    def __str__(self):
        return f"{self.patient.username}'s review for {self.doctor}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.doctor.update_rating()


class DoctorWeeklySchedule(models.Model):
    """Doctor's recurring weekly schedule"""
    
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='weekly_schedules')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctor_weekly_schedules')
    
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Doctor Weekly Schedule'
        verbose_name_plural = 'Doctor Weekly Schedules'
        ordering = ['day_of_week', 'start_time']
        unique_together = ['doctor', 'hospital', 'day_of_week']
    
    def __str__(self):
        return f"{self.doctor} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time} @ {self.hospital}"
    
    def get_day_of_week_display(self):
        return dict(self.DAYS_OF_WEEK).get(self.day_of_week, 'Unknown')


class DoctorAvailability(models.Model):
    """Doctor's availability for appointments"""
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availabilities')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    
    # Time slots (2-hour blocks)
    TIME_SLOTS = [
        ('09:00-11:00', '9:00 AM - 11:00 AM'),
        ('11:00-13:00', '11:00 AM - 1:00 PM'),
        ('14:00-16:00', '2:00 PM - 4:00 PM'),
        ('16:00-18:00', '4:00 PM - 6:00 PM'),
        ('18:00-20:00', '6:00 PM - 8:00 PM'),
    ]
    
    time_slot = models.CharField(max_length=20, choices=TIME_SLOTS)
    is_available = models.BooleanField(default=True)
    is_booked = models.BooleanField(default=False)
    
    # For custom schedule exceptions (optional, for special dates)
    is_exception = models.BooleanField(default=False)  # True if this is a custom date override
    custom_start_time = models.TimeField(null=True, blank=True)  # For custom exception times
    custom_end_time = models.TimeField(null=True, blank=True)  # For custom exception times
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Doctor Availability'
        verbose_name_plural = 'Doctor Availabilities'
        ordering = ['date', 'time_slot']
        unique_together = ['doctor', 'hospital', 'date', 'time_slot']
    
    def __str__(self):
        return f"{self.doctor} - {self.date} {self.time_slot}"

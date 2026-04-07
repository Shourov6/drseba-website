from django.db import models


class Specialty(models.Model):
    """Doctor specialties like Cardiologist, Dentist, etc."""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class or emoji")
    color = models.CharField(max_length=20, default="#0d6efd", help_text="Color code for the specialty card")
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Specialties"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Hospital(models.Model):
    """Partner hospitals"""
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='hospitals/', blank=True, null=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Doctor(models.Model):
    """Doctor profiles"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='doctors')
    image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    experience_years = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    review_count = models.PositiveIntegerField(default=0)
    consultation_fee = models.PositiveIntegerField(default=500)
    is_verified = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    about = models.TextField(blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors')
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_featured', '-rating', 'name']
    
    def __str__(self):
        return f"Dr. {self.name}"


class Testimonial(models.Model):
    """Patient testimonials"""
    name = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.rating} stars"


class Service(models.Model):
    """Services like Doctor Search, Diagnostic, Ambulance, etc."""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    url = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name


class Statistic(models.Model):
    """Website statistics like 15,000+ doctors, etc."""
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=50)
    icon = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.value} {self.label}"

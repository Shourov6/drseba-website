"""
Admin configuration for DrSeva Healthcare Admin Dashboard
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Doctor, Hospital, DoctorHospital, Patient, Employee, Appointment, Payment


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin"""
    list_display = ['username', 'email', 'role', 'phone', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'phone']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'age', 'gender', 'profile_photo')}),
    )


class DoctorHospitalInline(admin.TabularInline):
    """Inline for DoctorHospital relationship"""
    model = DoctorHospital
    extra = 1
    fields = ['hospital', 'days', 'time', 'consultation_fee', 'service_charge', 'patient_count']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """Doctor Admin"""
    list_display = ['doctor_id', 'name', 'specialty', 'experience', 'commission_percentage', 'status', 'registration_date']
    list_filter = ['specialty', 'status', 'registration_date', 'consultation_language']
    search_fields = ['name', 'doctor_id', 'specialty', 'phone', 'email']
    inlines = [DoctorHospitalInline]
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'age', 'gender', 'phone', 'email', 'profile_photo')
        }),
        ('Professional Details', {
            'fields': ('qualification', 'specialty', 'experience', 'medical_license_number', 'about', 'commission_percentage')
        }),
        ('Consultation Settings', {
            'fields': ('consultation_language', 'online_appointment', 'max_patients_per_day', 'emergency_available')
        }),
        ('Documents', {
            'fields': ('certificates', 'id_proof', 'license_document'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'registration_date')
        }),
    )
    
    readonly_fields = ['registration_date', 'doctor_id']


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    """Hospital Admin"""
    list_display = ['hospital_id', 'name', 'location', 'contact', 'total_beds', 'icu_beds', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'hospital_id', 'location', 'contact']
    
    fieldsets = (
        ('Hospital Information', {
            'fields': ('hospital_id', 'name', 'location')
        }),
        ('Contact Details', {
            'fields': ('contact', 'email')
        }),
        ('Capacity', {
            'fields': ('total_beds', 'icu_beds')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )
    
    readonly_fields = ['hospital_id', 'created_at']


@admin.register(DoctorHospital)
class DoctorHospitalAdmin(admin.ModelAdmin):
    """DoctorHospital Admin"""
    list_display = ['doctor', 'hospital', 'days', 'time', 'consultation_fee', 'service_charge', 'patient_count']
    list_filter = ['hospital', 'days']
    search_fields = ['doctor__name', 'hospital__name']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Patient Admin"""
    list_display = ['name', 'age', 'gender', 'phone', 'email', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['name', 'phone', 'email']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Employee Admin"""
    list_display = ['employee_id', 'name', 'role', 'phone', 'email', 'status', 'hire_date', 'get_assigned_appointments_count']
    list_filter = ['role', 'status', 'hire_date']
    search_fields = ['name', 'employee_id', 'phone', 'email']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('employee_id', 'name', 'age', 'gender', 'phone', 'email', 'profile_photo')
        }),
        ('Employment Details', {
            'fields': ('role', 'status', 'hire_date')
        }),
    )
    
    readonly_fields = ['employee_id']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Appointment Admin"""
    list_display = ['appointment_id', 'patient', 'doctor', 'date', 'time', 'appointment_type', 'is_distributed', 'final_status']
    list_filter = ['appointment_type', 'final_status', 'manager_status', 'doctor_status', 'date', 'is_distributed']
    search_fields = ['appointment_id', 'patient__name', 'doctor__name']
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('appointment_id', 'patient', 'doctor', 'date', 'time', 'appointment_type')
        }),
        ('Charges', {
            'fields': ('service_charge', 'notes')
        }),
        ('Distribution', {
            'fields': ('is_distributed', 'managed_by')
        }),
        ('Status', {
            'fields': ('manager_status', 'doctor_status', 'final_status')
        }),
    )
    
    readonly_fields = ['appointment_id', 'final_status']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Payment Admin"""
    list_display = ['invoice_id', 'patient', 'doctor', 'total_amount', 'payment_method', 'status', 'payment_date']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['invoice_id', 'patient__name', 'doctor__name']
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_id', 'appointment')
        }),
        ('Parties', {
            'fields': ('patient', 'doctor')
        }),
        ('Amount Details', {
            'fields': ('consultation_fee', 'service_charge', 'total_amount')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'status', 'payment_date')
        }),
    )
    
    readonly_fields = ['invoice_id', 'total_amount']

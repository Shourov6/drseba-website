"""
Admin configuration for accounts app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PatientProfile, EmployeeProfile, PhoneVerification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_verified', 'is_active']
    list_filter = ['role', 'is_verified', 'is_active', 'language', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone', 'is_verified', 'language', 'dark_mode')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone', 'email')
        }),
    )


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    """Patient Profile Admin"""
    list_display = ['user', 'age', 'gender', 'blood_group', 'city', 'district']
    list_filter = ['gender', 'blood_group', 'city', 'district', 'marital_status', 'smoking_status', 'alcohol_consumption']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'city', 'district']
    filter_horizontal = ['favorite_doctors']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'created_at', 'updated_at')
        }),
        ('Demographics', {
            'fields': ('date_of_birth', 'gender', 'marital_status', 'occupation', 'number_of_children')
        }),
        ('Health Metrics', {
            'fields': ('blood_group', 'height', 'weight')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'district', 'emergency_contact_name', 'emergency_contact_phone', 
                      'emergency_contact', 'secondary_emergency_contact')
        }),
        ('Lifestyle', {
            'fields': ('smoking_status', 'alcohol_consumption')
        }),
        ('Medical History', {
            'fields': ('medical_history', 'chronic_diseases', 'surgical_history', 'family_medical_history', 
                      'allergies', 'current_medications', 'last_checkup_date', 'notes_for_doctor')
        }),
        ('Insurance', {
            'fields': ('insurance_provider', 'insurance_policy_number')
        }),
        ('Preferences', {
            'fields': ('profile_picture', 'favorite_doctors', 'preferred_communication')
        }),
    )


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    """Employee Profile Admin"""
    list_display = ['user', 'employee_id', 'department', 'designation', 'is_active']
    list_filter = ['department', 'is_active', 'joining_date']
    search_fields = ['user__username', 'user__email', 'employee_id']


@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    """Phone Verification Admin"""
    list_display = ['user', 'phone', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__username', 'phone']

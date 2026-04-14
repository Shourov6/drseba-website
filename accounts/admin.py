"""
Admin configuration for accounts app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, PatientProfile, EmployeeProfile, PhoneVerification
from .forms import EmployeeCreationForm
from .forms_doctor_admin import DoctorAdminCreationForm


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
    
    def get_urls(self):
        """Add custom URLs for quick account creation"""
        urls = super().get_urls()
        custom_urls = [
            path('create-employee/', self.admin_site.admin_view(self.create_employee_account), name='create_employee'),
            path('create-doctor/', self.admin_site.admin_view(self.create_doctor_account), name='create_doctor'),
        ]
        return custom_urls + urls
    
    def create_employee_account(self, request):
        """Admin view for creating employee account with password"""
        if request.method == 'POST':
            form = EmployeeCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(
                    request, 
                    f'Employee account created successfully! Email: {user.email}. They can log in with their email and the password you set.'
                )
                return redirect('..')
        else:
            form = EmployeeCreationForm()
        
        return render(request, 'admin/create_simple_account.html', {
            'form': form,
            'title': 'Create New Employee Account',
            'account_type': 'Employee'
        })
    
    from django.db import transaction, IntegrityError

    def create_doctor_account(self, request):
        """Admin view for creating doctor account with all required info (atomic, no partial saves)"""
        if request.method == 'POST':
            form = DoctorAdminCreationForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        doctor = form.save()
                    messages.success(
                        request,
                        f'Doctor account created successfully! Email: {doctor.user.email}. They can log in with their email and the password you set.'
                    )
                    return redirect('..')
                except IntegrityError:
                    form.add_error('email', 'A database error occurred. Please try again.')
            # If not valid or error, fall through to render form with errors
        else:
            form = DoctorAdminCreationForm()
        return render(request, 'admin/create_simple_account.html', {
            'form': form,
            'title': 'Create New Doctor Account',
            'account_type': 'Doctor'
        })


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    """Patient Profile Admin"""
    list_display = ['user', 'date_of_birth', 'gender', 'blood_group', 'city']
    list_filter = ['gender', 'blood_group', 'city', 'district']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    filter_horizontal = ['favorite_doctors']


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    """Employee Profile Admin"""
    list_display = ['user', 'employee_id', 'department', 'designation', 'is_active']
    list_filter = ['department', 'is_active', 'joining_date']
    search_fields = ['user__username', 'user__email', 'employee_id']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',),
        }),
        ('Employee Information', {
            'fields': ('employee_id', 'department', 'designation', 'joining_date', 'profile_picture', 'is_active'),
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form for employee creation"""
        form = super().get_form(request, obj, **kwargs)
        return form


@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    """Phone Verification Admin"""
    list_display = ['user', 'phone', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__username', 'phone']

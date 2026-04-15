"""
Views for accounts app
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import (
    LoginForm,
    PatientRegistrationForm,
    DoctorRegistrationForm,
    PatientProfileForm,
    PasswordChangeForm,
    is_gmail_address,
    normalize_bd_phone,
)
from .models import User, PatientProfile


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = (form.cleaned_data.get('identifier') or '').strip()
            password = form.cleaned_data.get('password')
            user = None

            if '@' in identifier:
                user = User.objects.filter(email__iexact=identifier).first()
            else:
                normalized_phone = normalize_bd_phone('+880', identifier)
                if normalized_phone:
                    user = User.objects.filter(phone=normalized_phone).first()
                if not user:
                    user = User.objects.filter(username__iexact=identifier, role='admin').first()

            if not user:
                messages.error(request, 'No account found for that mobile number or Gmail address.')
            elif user.is_super_admin():
                if user.check_password(password):
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('dashboard:admin_dashboard')
                messages.error(request, 'Invalid admin username/email or password.')
            elif user.is_doctor() or user.is_employee():
                if not is_gmail_address(identifier):
                    messages.error(request, 'Doctors and employees must log in using Gmail only.')
                elif user.check_password(password):
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    if user.is_super_admin():
                        return redirect('dashboard:admin_dashboard')
                    elif user.is_doctor():
                        return redirect('dashboard:doctor_dashboard')
                    elif user.is_employee():
                        return redirect('dashboard:employee_dashboard')
                    return redirect('dashboard:patient_dashboard')
                else:
                    messages.error(request, 'Invalid Gmail address or password.')
            elif user.is_patient():
                if user.check_password(password):
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    if user.is_super_admin():
                        return redirect('dashboard:admin_dashboard')
                    elif user.is_doctor():
                        return redirect('dashboard:doctor_dashboard')
                    elif user.is_employee():
                        return redirect('dashboard:employee_dashboard')
                    return redirect('dashboard:patient_dashboard')
                else:
                    messages.error(request, 'Invalid mobile number/Gmail or password.')
        else:
            messages.error(request, 'Enter a valid mobile number or Gmail address.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def patient_register(request):
    """Patient registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard:patient_dashboard')
    
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to DrSeba.com')
            return redirect('dashboard:patient_dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'accounts/patient_register.html', {'form': form})


def doctor_register(request):
    """Doctor registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard:doctor_dashboard')
    
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Your account is pending verification.')
            return redirect('accounts:login')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = DoctorRegistrationForm()
    
    return render(request, 'accounts/doctor_register.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile_view(request):
    """User profile view"""
    user = request.user
    context = {'user': user}
    
    if user.is_patient():
        try:
            profile = user.patient_profile
        except PatientProfile.DoesNotExist:
            profile = PatientProfile.objects.create(user=user)
        context['profile'] = profile
    
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_update(request):
    """Profile update view"""
    user = request.user
    
    if user.is_patient():
        try:
            profile = user.patient_profile
        except PatientProfile.DoesNotExist:
            profile = PatientProfile.objects.create(user=user)
        
        if request.method == 'POST':
            form = PatientProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('accounts:profile')
            else:
                for error in form.errors.values():
                    messages.error(request, error)
        else:
            form = PatientProfileForm(instance=profile)
        
        return render(request, 'accounts/profile_update.html', {'form': form})
    
    return redirect('accounts:profile')


@login_required
def password_change(request):
    """Password change view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data.get('current_password')
            new_password = form.cleaned_data.get('new_password')
            
            if request.user.check_password(current_password):
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully!')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Current password is incorrect.')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PasswordChangeForm()
    
    return render(request, 'accounts/password_change.html', {'form': form})


def set_language(request, lang):
    """Set language preference"""
    if lang in ['en', 'bn']:
        if request.user.is_authenticated:
            request.user.language = lang
            request.user.save()
        request.session['language'] = lang
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def set_theme(request, mode):
    """Set theme preference"""
    if mode in ['light', 'dark']:
        if request.user.is_authenticated:
            request.user.dark_mode = (mode == 'dark')
            request.user.save()
        request.session['theme'] = mode
    return redirect(request.META.get('HTTP_REFERER', 'home'))

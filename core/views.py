"""
Views for DrSeva Healthcare Admin Dashboard
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import User, Doctor, Hospital, DoctorHospital, Patient, Employee, Appointment, Payment
from .forms import (
    LoginForm, DoctorForm, DoctorHospitalForm, HospitalForm,
    PatientForm, EmployeeForm, AppointmentForm, PaymentForm
)


def login_view(request):
    """Login view with role-based access"""
    if request.user.is_authenticated:
        if request.user.is_admin():
            return redirect('dashboard')
        else:
            return redirect('employee_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if role matches
            if (role == 'admin' and user.is_admin()) or (role == 'employee' and user.is_employee_user()):
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                if user.is_admin():
                    return redirect('dashboard')
                else:
                    return redirect('employee_dashboard')
            else:
                messages.error(request, 'Invalid role selected for this user.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Admin Dashboard view with analytics"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('employee_dashboard')
    
    # Analytics data
    total_doctors = Doctor.objects.filter(status='Active').count()
    total_hospitals = Hospital.objects.filter(status='Active').count()
    total_appointments = Appointment.objects.count()
    total_revenue = Payment.objects.filter(status='Paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    active_employees = Employee.objects.filter(status='Active').count()
    total_patients = Patient.objects.count()
    
    # Recent appointments
    recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-created_at')[:5]
    
    # Monthly revenue data for charts
    current_month = timezone.now().month
    monthly_revenue = []
    for i in range(6):
        month = current_month - i
        year = timezone.now().year
        if month <= 0:
            month += 12
            year -= 1
        revenue = Payment.objects.filter(
            status='Paid',
            payment_date__month=month,
            payment_date__year=year
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        monthly_revenue.append({'month': month, 'revenue': revenue})
    
    # Appointments by specialty
    appointments_by_specialty = Appointment.objects.values('doctor__specialty').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'total_doctors': total_doctors,
        'total_hospitals': total_hospitals,
        'total_appointments': total_appointments,
        'total_revenue': total_revenue,
        'active_employees': active_employees,
        'total_patients': total_patients,
        'recent_appointments': recent_appointments,
        'monthly_revenue': monthly_revenue,
        'appointments_by_specialty': appointments_by_specialty,
    }
    return render(request, 'dashboard.html', context)


@login_required
def employee_dashboard_view(request):
    """Employee Dashboard view"""
    if request.user.is_admin():
        return redirect('dashboard')
    
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('login')
    
    # Employee's assigned appointments
    assigned_appointments = Appointment.objects.filter(
        managed_by=employee
    ).select_related('patient', 'doctor').order_by('-date', '-time')[:10]
    
    # Performance metrics
    total_assignments = employee.get_assigned_appointments_count()
    confirmed_appointments = Appointment.objects.filter(
        managed_by=employee,
        final_status='Confirmed'
    ).count()
    pending_appointments = Appointment.objects.filter(
        managed_by=employee,
        final_status='Pending'
    ).count()
    
    completion_rate = (confirmed_appointments / total_assignments * 100) if total_assignments > 0 else 0
    
    context = {
        'employee': employee,
        'assigned_appointments': assigned_appointments,
        'total_assignments': total_assignments,
        'confirmed_appointments': confirmed_appointments,
        'pending_appointments': pending_appointments,
        'completion_rate': round(completion_rate, 1),
    }
    return render(request, 'employee_dashboard.html', context)


# ==================== DOCTORS VIEWS ====================

@login_required
def doctors_list_view(request):
    """Doctors list view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    doctors = Doctor.objects.all()
    
    if search:
        doctors = doctors.filter(
            Q(name__icontains=search) |
            Q(doctor_id__icontains=search) |
            Q(specialty__icontains=search)
        )
    
    if status_filter:
        doctors = doctors.filter(status=status_filter)
    
    # Get hospital schedules for each doctor
    doctor_data = []
    for doctor in doctors:
        schedules = DoctorHospital.objects.filter(doctor=doctor)
        if schedules.exists():
            for schedule in schedules:
                doctor_data.append({
                    'doctor': doctor,
                    'schedule': schedule,
                })
        else:
            doctor_data.append({
                'doctor': doctor,
                'schedule': None,
            })
    
    context = {
        'doctor_data': doctor_data,
        'search': search,
        'status_filter': status_filter,
    }
    return render(request, 'doctors/list.html', context)


@login_required
def doctor_add_view(request):
    """Add new doctor view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save()
            
            # Handle hospital schedules
            hospital_ids = request.POST.getlist('hospital[]')
            days_list = request.POST.getlist('days[]')
            time_list = request.POST.getlist('time[]')
            contact_list = request.POST.getlist('contact_number[]')
            address_list = request.POST.getlist('chamber_address[]')
            fee_list = request.POST.getlist('consultation_fee[]')
            charge_list = request.POST.getlist('service_charge[]')
            
            for i in range(len(hospital_ids)):
                if hospital_ids[i]:
                    DoctorHospital.objects.create(
                        doctor=doctor,
                        hospital_id=hospital_ids[i],
                        days=days_list[i] if i < len(days_list) else '',
                        time=time_list[i] if i < len(time_list) else '',
                        contact_number=contact_list[i] if i < len(contact_list) else '',
                        chamber_address=address_list[i] if i < len(address_list) else '',
                        consultation_fee=fee_list[i] if i < len(fee_list) else 0,
                        service_charge=charge_list[i] if i < len(charge_list) else 0,
                    )
            
            messages.success(request, 'Doctor added successfully!')
            return redirect('doctors_list')
    else:
        form = DoctorForm()
    
    hospitals = Hospital.objects.filter(status='Active')
    context = {
        'form': form,
        'hospitals': hospitals,
    }
    return render(request, 'doctors/add.html', context)


@login_required
def doctor_edit_view(request, doctor_id):
    """Edit doctor view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
    
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doctor updated successfully!')
            return redirect('doctors_list')
    else:
        form = DoctorForm(instance=doctor)
    
    hospitals = Hospital.objects.filter(status='Active')
    schedules = DoctorHospital.objects.filter(doctor=doctor)
    
    context = {
        'form': form,
        'doctor': doctor,
        'hospitals': hospitals,
        'schedules': schedules,
    }
    return render(request, 'doctors/edit.html', context)


@login_required
def doctor_delete_view(request, doctor_id):
    """Delete doctor view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
    
    if request.method == 'POST':
        doctor.delete()
        messages.success(request, 'Doctor deleted successfully!')
        return redirect('doctors_list')
    
    context = {'doctor': doctor}
    return render(request, 'doctors/delete.html', context)


@login_required
def doctor_detail_view(request, doctor_id):
    """Doctor detail view"""
    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
    schedules = DoctorHospital.objects.filter(doctor=doctor)
    
    context = {
        'doctor': doctor,
        'schedules': schedules,
    }
    return render(request, 'doctors/detail.html', context)


# ==================== HOSPITALS VIEWS ====================

@login_required
def hospitals_list_view(request):
    """Hospitals list view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    hospitals = Hospital.objects.all()
    
    if search:
        hospitals = hospitals.filter(
            Q(name__icontains=search) |
            Q(hospital_id__icontains=search) |
            Q(location__icontains=search)
        )
    
    if status_filter:
        hospitals = hospitals.filter(status=status_filter)
    
    context = {
        'hospitals': hospitals,
        'search': search,
        'status_filter': status_filter,
    }
    return render(request, 'hospitals/list.html', context)


@login_required
def hospital_add_view(request):
    """Add new hospital view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    if request.method == 'POST':
        form = HospitalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hospital added successfully!')
            return redirect('hospitals_list')
    else:
        form = HospitalForm()
    
    context = {'form': form}
    return render(request, 'hospitals/add.html', context)


@login_required
def hospital_edit_view(request, hospital_id):
    """Edit hospital view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    hospital = get_object_or_404(Hospital, hospital_id=hospital_id)
    
    if request.method == 'POST':
        form = HospitalForm(request.POST, instance=hospital)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hospital updated successfully!')
            return redirect('hospitals_list')
    else:
        form = HospitalForm(instance=hospital)
    
    context = {
        'form': form,
        'hospital': hospital,
    }
    return render(request, 'hospitals/edit.html', context)


@login_required
def hospital_delete_view(request, hospital_id):
    """Delete hospital view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    hospital = get_object_or_404(Hospital, hospital_id=hospital_id)
    
    if request.method == 'POST':
        hospital.delete()
        messages.success(request, 'Hospital deleted successfully!')
        return redirect('hospitals_list')
    
    context = {'hospital': hospital}
    return render(request, 'hospitals/delete.html', context)


# ==================== APPOINTMENTS VIEWS ====================

@login_required
def appointments_list_view(request):
    """Appointments list view with tabs"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    tab = request.GET.get('tab', 'distributed')
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if tab == 'distributed':
        appointments = Appointment.objects.filter(is_distributed=True)
    else:
        appointments = Appointment.objects.filter(is_distributed=False)
    
    if search:
        appointments = appointments.filter(
            Q(patient__name__icontains=search) |
            Q(doctor__name__icontains=search)
        )
    
    if status_filter:
        appointments = appointments.filter(final_status=status_filter)
    
    appointments = appointments.select_related('patient', 'doctor', 'managed_by').order_by('-date', '-time')
    employees = Employee.objects.filter(status='Active')
    
    context = {
        'appointments': appointments,
        'employees': employees,
        'tab': tab,
        'search': search,
        'status_filter': status_filter,
    }
    return render(request, 'appointments/list.html', context)


@login_required
def appointment_add_view(request):
    """Add new appointment view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            messages.success(request, 'Appointment added successfully!')
            return redirect('appointments_list')
    else:
        form = AppointmentForm()
    
    context = {'form': form}
    return render(request, 'appointments/add.html', context)


@login_required
def appointment_edit_view(request, appointment_id):
    """Edit appointment view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully!')
            return redirect('appointments_list')
    else:
        form = AppointmentForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'appointments/edit.html', context)


@login_required
def appointment_delete_view(request, appointment_id):
    """Delete appointment view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
    
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Appointment deleted successfully!')
        return redirect('appointments_list')
    
    context = {'appointment': appointment}
    return render(request, 'appointments/delete.html', context)


@login_required
def appointment_assign_view(request, appointment_id):
    """Assign appointment to employee"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        if employee_id:
            employee = get_object_or_404(Employee, id=employee_id)
            appointment.managed_by = employee
            appointment.is_distributed = True
            appointment.manager_status = 'Pending'
            appointment.doctor_status = 'Pending'
            appointment.save()
            messages.success(request, 'Appointment assigned successfully!')
        else:
            messages.error(request, 'Please select an employee.')
    
    return redirect('appointments_list')


# ==================== EMPLOYEES VIEWS ====================

@login_required
def employees_list_view(request):
    """Employees list view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    search = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    
    employees = Employee.objects.all()
    
    if search:
        employees = employees.filter(
            Q(name__icontains=search) |
            Q(employee_id__icontains=search) |
            Q(phone__icontains=search)
        )
    
    if role_filter:
        employees = employees.filter(role=role_filter)
    
    context = {
        'employees': employees,
        'search': search,
        'role_filter': role_filter,
    }
    return render(request, 'employees/list.html', context)


@login_required
def employee_add_view(request):
    """Add new employee view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee added successfully!')
            return redirect('employees_list')
    else:
        form = EmployeeForm()
    
    context = {'form': form}
    return render(request, 'employees/add.html', context)


@login_required
def employee_edit_view(request, employee_id):
    """Edit employee view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    employee = get_object_or_404(Employee, employee_id=employee_id)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully!')
            return redirect('employees_list')
    else:
        form = EmployeeForm(instance=employee)
    
    context = {
        'form': form,
        'employee': employee,
    }
    return render(request, 'employees/edit.html', context)


@login_required
def employee_delete_view(request, employee_id):
    """Delete employee view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    employee = get_object_or_404(Employee, employee_id=employee_id)
    
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully!')
        return redirect('employees_list')
    
    context = {'employee': employee}
    return render(request, 'employees/delete.html', context)


@login_required
def employee_detail_view(request, employee_id):
    """Employee detail view"""
    employee = get_object_or_404(Employee, employee_id=employee_id)
    
    context = {'employee': employee}
    return render(request, 'employees/detail.html', context)


# ==================== PAYMENTS VIEWS ====================

@login_required
def payments_list_view(request):
    """Payments list view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    payments = Payment.objects.all()
    
    if search:
        payments = payments.filter(
            Q(invoice_id__icontains=search) |
            Q(patient__name__icontains=search) |
            Q(doctor__name__icontains=search)
        )
    
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    # Summary cards
    total_revenue = Payment.objects.filter(status='Paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_payments = Payment.objects.filter(status='Pending').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    overdue_payments = Payment.objects.filter(status='Overdue').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    payments = payments.select_related('patient', 'doctor').order_by('-created_at')
    
    context = {
        'payments': payments,
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
        'overdue_payments': overdue_payments,
        'search': search,
        'status_filter': status_filter,
    }
    return render(request, 'payments/list.html', context)


@login_required
def payment_add_view(request):
    """Add new payment view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment added successfully!')
            return redirect('payments_list')
    else:
        form = PaymentForm()
    
    context = {'form': form}
    return render(request, 'payments/add.html', context)


@login_required
def payment_edit_view(request, invoice_id):
    """Edit payment view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    payment = get_object_or_404(Payment, invoice_id=invoice_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment updated successfully!')
            return redirect('payments_list')
    else:
        form = PaymentForm(instance=payment)
    
    context = {
        'form': form,
        'payment': payment,
    }
    return render(request, 'payments/edit.html', context)


@login_required
def payment_delete_view(request, invoice_id):
    """Delete payment view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    payment = get_object_or_404(Payment, invoice_id=invoice_id)
    
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Payment deleted successfully!')
        return redirect('payments_list')
    
    context = {'payment': payment}
    return render(request, 'payments/delete.html', context)


@login_required
def payment_invoice_view(request, invoice_id):
    """View invoice"""
    payment = get_object_or_404(Payment, invoice_id=invoice_id)
    
    context = {'payment': payment}
    return render(request, 'payments/invoice.html', context)


# ==================== REPORTS VIEWS ====================

@login_required
def reports_view(request):
    """Analytics and Reports view"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    # Monthly data for charts
    current_year = timezone.now().year
    
    monthly_appointments = []
    monthly_revenue = []
    
    for month in range(1, 13):
        appointments_count = Appointment.objects.filter(
            date__month=month,
            date__year=current_year
        ).count()
        
        revenue = Payment.objects.filter(
            status='Paid',
            payment_date__month=month,
            payment_date__year=current_year
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        monthly_appointments.append(appointments_count)
        monthly_revenue.append(float(revenue))
    
    # Doctor performance
    doctor_performance = Doctor.objects.annotate(
        patient_count=Count('appointments')
    ).order_by('-patient_count')[:5]
    
    # Hospital performance
    hospital_performance = Hospital.objects.annotate(
        appointment_count=Count('doctor_schedules__appointments')
    ).order_by('-appointment_count')[:5]
    
    # Payment method distribution
    payment_methods = Payment.objects.values('payment_method').annotate(
        count=Count('id')
    )
    
    context = {
        'monthly_appointments': monthly_appointments,
        'monthly_revenue': monthly_revenue,
        'doctor_performance': doctor_performance,
        'hospital_performance': hospital_performance,
        'payment_methods': payment_methods,
    }
    return render(request, 'reports.html', context)


# ==================== PATIENT VIEWS ====================

@login_required
def patient_detail_view(request, patient_id):
    """Patient detail view"""
    patient = get_object_or_404(Patient, id=patient_id)
    appointments = Appointment.objects.filter(patient=patient).select_related('doctor')
    
    context = {
        'patient': patient,
        'appointments': appointments,
    }
    return render(request, 'patients/detail.html', context)

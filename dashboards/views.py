
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

@login_required
def admin_patient_detail(request, user_id):
    """Admin view for patient profile details"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    User = get_user_model()
    user = get_object_or_404(User, id=user_id, role='patient')
    try:
        profile = user.patient_profile
    except Exception:
        profile = None
    context = {
        'patient': user,
        'profile': profile,
    }
    return render(request, 'dashboards/admin_patient_detail.html', context)
"""
Views for dashboards app
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from django.utils.text import slugify
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.urls import reverse
from datetime import date, timedelta, datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import quote
import json
import string
import secrets
import re

from accounts.models import User, PatientProfile, EmployeeProfile
from accounts.forms import is_gmail_address, generate_unique_username
from doctors.models import Doctor, Specialty, Hospital, Review, DoctorHospital, DoctorWeeklySchedule, DoctorAvailability
from appointments.models import Appointment, CartItem, AppointmentHistory
from payments.models import Payment, Invoice, DoctorEarning
from .models import AdminNotification


def dashboard_index(request):
    """Redirect to appropriate dashboard based on user role"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if request.user.is_super_admin():
        return redirect('dashboard:admin_dashboard')
    elif request.user.is_doctor():
        return redirect('dashboard:doctor_dashboard')
    elif request.user.is_employee():
        return redirect('dashboard:employee_dashboard')
    else:
        return redirect('dashboard:patient_dashboard')


# Patient Dashboard
@login_required
def patient_dashboard(request):
    """Patient dashboard"""
    if not request.user.is_patient():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get patient profile
    try:
        profile = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        profile = PatientProfile.objects.create(user=request.user)
    
    # Upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        patient=request.user,
        date__gte=date.today(),
        status__in=['pending', 'confirmed']
    ).order_by('date', 'time_slot')[:5]
    
    # Past appointments: include any appointment that is already in the past,
    # plus lifecycle-closed appointments regardless of date.
    past_appointments = Appointment.objects.filter(
        patient=request.user
    ).filter(
        Q(date__lt=date.today()) |
        Q(status__in=['completed', 'cancelled', 'no_show'])
    ).order_by('-date', '-time_slot')[:5]
    
    # Cart items
    cart_items = CartItem.objects.filter(patient=request.user)
    
    # Favorite doctors
    favorite_doctors = profile.favorite_doctors.all()[:4]
    
    # Recent payments
    recent_payments = Payment.objects.filter(
        appointment__patient=request.user,
        status='completed'
    ).order_by('-created_at')[:5]
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'cart_count': cart_items.count(),
        'favorite_doctors': favorite_doctors,
        'recent_payments': recent_payments,
        'profile': profile,
    }
    
    return render(request, 'dashboards/patient_dashboard.html', context)


# Doctor Dashboard
@login_required
def doctor_dashboard(request):
    """Doctor dashboard"""
    if not request.user.is_doctor():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        doctor = request.user.doctor_profile
    except:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    # Today's appointments
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        date=date.today()
    ).order_by('time_slot')
    
    # Upcoming appointments
    upcoming_count = Appointment.objects.filter(
        doctor=doctor,
        date__gt=date.today(),
        status__in=['pending', 'confirmed']
    ).count()
    
    # Total patients
    total_patients = Appointment.objects.filter(
        doctor=doctor,
        status='completed'
    ).values('patient').distinct().count()
    
    # Rating
    rating = doctor.rating
    total_reviews = doctor.total_reviews
    
    # Monthly earnings
    from django.db.models import Sum
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    monthly_earnings = DoctorEarning.objects.filter(
        doctor=doctor,
        month=current_month,
        year=current_year
    ).aggregate(total=Sum('doctor_amount'))['total'] or 0
    
    # Recent reviews
    recent_reviews = Review.objects.filter(
        doctor=doctor,
        is_active=True
    ).select_related('patient').order_by('-created_at')[:5]
    
    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'upcoming_count': upcoming_count,
        'total_patients': total_patients,
        'rating': rating,
        'total_reviews': total_reviews,
        'monthly_earnings': monthly_earnings,
        'recent_reviews': recent_reviews,
    }
    
    return render(request, 'dashboards/doctor_dashboard.html', context)


@login_required
def doctor_profile(request):
    """Doctor profile view"""
    if not request.user.is_doctor():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        doctor = request.user.doctor_profile
    except:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    context = {
        'doctor': doctor,
    }
    
    return render(request, 'dashboards/doctor_profile.html', context)


@login_required
def doctor_profile_edit(request):
    """Edit doctor profile"""
    if not request.user.is_doctor():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        doctor = request.user.doctor_profile
    except:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    from doctors.forms import DoctorProfileForm
    
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard:doctor_profile')
    else:
        form = DoctorProfileForm(instance=doctor)
    
    context = {
        'form': form,
        'doctor': doctor,
    }
    
    return render(request, 'dashboards/doctor_profile_edit.html', context)


@login_required
def doctor_schedule(request):
    """Doctor schedule management"""
    if not request.user.is_doctor():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        doctor = request.user.doctor_profile
    except:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    hospitals = DoctorHospital.objects.filter(doctor=doctor, is_active=True)
    weeklySchedules = DoctorWeeklySchedule.objects.filter(
        doctor=doctor
    ).select_related('hospital').order_by('day_of_week', 'start_time')
    
    context = {
        'hospitals': hospitals,
        'weeklySchedules': weeklySchedules,
    }
    
    return render(request, 'dashboards/doctor_schedule.html', context)


def _sync_future_availability_for_schedule(schedule):
    """Keep future availability aligned with current weekly schedule status/time window."""
    start_date = date.today()
    end_date = start_date + timedelta(days=30)

    slot_windows = []
    for slot_value, _ in DoctorAvailability.TIME_SLOTS:
        slot_start, slot_end = slot_value.split('-')
        slot_windows.append(
            (
                slot_value,
                datetime.strptime(slot_start, '%H:%M').time(),
                datetime.strptime(slot_end, '%H:%M').time(),
            )
        )

    overlapping_slots = []
    for slot_value, slot_start, slot_end in slot_windows:
        if slot_end <= schedule.start_time or slot_start >= schedule.end_time:
            continue
        overlapping_slots.append(slot_value)

    total_days = (end_date - start_date).days + 1
    for offset in range(total_days):
        current_date = start_date + timedelta(days=offset)
        if current_date.weekday() != schedule.day_of_week:
            continue

        day_queryset = DoctorAvailability.objects.filter(
            doctor=schedule.doctor,
            hospital=schedule.hospital,
            date=current_date,
            is_exception=False,
            is_booked=False,
        )

        if not schedule.is_active:
            day_queryset.update(is_available=False)
            continue

        if overlapping_slots:
            day_queryset.filter(time_slot__in=overlapping_slots).update(is_available=True)
            day_queryset.exclude(time_slot__in=overlapping_slots).update(is_available=False)

            for slot_value in overlapping_slots:
                DoctorAvailability.objects.get_or_create(
                    doctor=schedule.doctor,
                    hospital=schedule.hospital,
                    date=current_date,
                    time_slot=slot_value,
                    defaults={
                        'is_available': True,
                        'is_booked': False,
                        'is_exception': False,
                    },
                )


DAY_LABELS_SHORT = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
DAY_TOKEN_TO_INDEX = {
    'mon': 0,
    'monday': 0,
    'tue': 1,
    'tues': 1,
    'tuesday': 1,
    'wed': 2,
    'wednesday': 2,
    'thu': 3,
    'thur': 3,
    'thurs': 3,
    'thursday': 3,
    'fri': 4,
    'friday': 4,
    'sat': 5,
    'saturday': 5,
    'sun': 6,
    'sunday': 6,
}


def _parse_day_indices(day_tokens):
    """Parse mixed day tokens to stable day indexes (0=Mon ... 6=Sun)."""
    parsed = set()
    for token in day_tokens:
        raw = str(token or '').strip().lower()
        if not raw:
            continue
        if raw.isdigit():
            value = int(raw)
            if 0 <= value <= 6:
                parsed.add(value)
            continue
        mapped = DAY_TOKEN_TO_INDEX.get(raw)
        if mapped is not None:
            parsed.add(mapped)
            continue
        mapped = DAY_TOKEN_TO_INDEX.get(raw[:3])
        if mapped is not None:
            parsed.add(mapped)
    return sorted(parsed)


def _day_labels_from_indices(day_indices):
    return [DAY_LABELS_SHORT[index] for index in sorted(set(day_indices)) if 0 <= index <= 6]


def _derive_schedule_window(morning_start, morning_end, evening_start, evening_end):
    """Pick a single weekly window spanning provided morning/evening ranges."""
    windows = []
    if morning_start and morning_end:
        windows.append((morning_start, morning_end))
    if evening_start and evening_end:
        windows.append((evening_start, evening_end))

    if not windows:
        return None, None

    starts = [window[0] for window in windows]
    ends = [window[1] for window in windows]
    start_time = min(starts)
    end_time = max(ends)

    if start_time >= end_time:
        return None, None
    return start_time, end_time


def _disable_future_availability_for_day(doctor, hospital, day_index):
    """Turn off non-exception future slots for a removed weekly day."""
    start_date = date.today()
    end_date = start_date + timedelta(days=30)
    total_days = (end_date - start_date).days + 1

    for offset in range(total_days):
        current_date = start_date + timedelta(days=offset)
        if current_date.weekday() != day_index:
            continue
        DoctorAvailability.objects.filter(
            doctor=doctor,
            hospital=hospital,
            date=current_date,
            is_exception=False,
            is_booked=False,
        ).update(is_available=False)


def _sync_weekly_schedules_for_hospital(doctor, hospital, day_windows):
    """Apply per-day weekly schedules for one doctor-hospital pair.

    day_windows format: {day_index: (start_time, end_time)}
    """
    normalized_windows = {}
    for day_index, window in (day_windows or {}).items():
        if window is None or len(window) != 2:
            continue
        start_time, end_time = window
        if start_time and end_time and start_time < end_time and 0 <= int(day_index) <= 6:
            normalized_windows[int(day_index)] = (start_time, end_time)

    if not normalized_windows:
        stale_qs = DoctorWeeklySchedule.objects.filter(doctor=doctor, hospital=hospital)
        for stale in stale_qs:
            _disable_future_availability_for_day(doctor, hospital, stale.day_of_week)
        stale_qs.delete()
        return

    requested_days = set(normalized_windows.keys())
    existing = {
        item.day_of_week: item
        for item in DoctorWeeklySchedule.objects.filter(doctor=doctor, hospital=hospital)
    }

    for day_index in requested_days:
        start_time, end_time = normalized_windows[day_index]
        schedule, _ = DoctorWeeklySchedule.objects.update_or_create(
            doctor=doctor,
            hospital=hospital,
            day_of_week=day_index,
            defaults={
                'start_time': start_time,
                'end_time': end_time,
                'is_active': True,
            },
        )
        _sync_future_availability_for_schedule(schedule)

    for day_index, schedule in existing.items():
        if day_index in requested_days:
            continue
        _disable_future_availability_for_day(doctor, hospital, day_index)
        schedule.delete()


@login_required
def doctor_add_schedule(request):
    """Add or update a weekly schedule for doctor"""
    if not request.user.is_doctor():
        messages.error(request, 'Access denied.')
        return redirect('home')

    try:
        doctor = request.user.doctor_profile
    except Exception:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')

    if request.method != 'POST':
        return redirect('dashboard:doctor_schedule')

    hospital_id = request.POST.get('hospital_id')
    day_of_week = request.POST.get('day_of_week')
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time')

    if not all([hospital_id, day_of_week, start_time, end_time]):
        messages.error(request, 'All schedule fields are required.')
        return redirect('dashboard:doctor_schedule')

    try:
        hospital_link = DoctorHospital.objects.get(
            id=hospital_id,
            doctor=doctor,
            is_active=True,
        )
    except DoctorHospital.DoesNotExist:
        messages.error(request, 'Invalid hospital selection.')
        return redirect('dashboard:doctor_schedule')

    try:
        day_of_week = int(day_of_week)
    except (TypeError, ValueError):
        messages.error(request, 'Invalid day selected.')
        return redirect('dashboard:doctor_schedule')

    if day_of_week < 0 or day_of_week > 6:
        messages.error(request, 'Day must be between Monday and Sunday.')
        return redirect('dashboard:doctor_schedule')

    if start_time >= end_time:
        messages.error(request, 'End time must be after start time.')
        return redirect('dashboard:doctor_schedule')

    schedule, created = DoctorWeeklySchedule.objects.update_or_create(
        doctor=doctor,
        hospital=hospital_link.hospital,
        day_of_week=day_of_week,
        defaults={
            'start_time': start_time,
            'end_time': end_time,
            'is_active': True,
        },
    )

    _sync_future_availability_for_schedule(schedule)

    if created:
        messages.success(request, f'Schedule added for {schedule.get_day_of_week_display()}.')
    else:
        messages.success(request, f'Schedule updated for {schedule.get_day_of_week_display()}.')

    return redirect('dashboard:doctor_schedule')


@login_required
def doctor_toggle_schedule_status(request, schedule_id):
    """Toggle active/deactive status for doctor's weekly schedule"""
    if not request.user.is_doctor():
        messages.error(request, 'Access denied.')
        return redirect('home')

    try:
        doctor = request.user.doctor_profile
    except Exception:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')

    if request.method != 'POST':
        return redirect('dashboard:doctor_schedule')

    schedule = get_object_or_404(DoctorWeeklySchedule, id=schedule_id, doctor=doctor)
    schedule.is_active = not schedule.is_active
    schedule.save(update_fields=['is_active', 'updated_at'])

    _sync_future_availability_for_schedule(schedule)

    state_label = 'activated' if schedule.is_active else 'deactivated'
    messages.success(request, f'Schedule {state_label} for {schedule.get_day_of_week_display()}.')
    return redirect('dashboard:doctor_schedule')


@login_required
def doctor_delete_schedule(request):
    """Delete weekly schedule for doctor"""
    if not request.user.is_doctor():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        doctor = request.user.doctor_profile
    except:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            from doctors.models import DoctorWeeklySchedule
            
            schedule_id = request.POST.get('schedule_id')
            
            if not schedule_id:
                messages.error(request, 'Schedule ID is required.')
                return redirect('dashboard:doctor_schedule')
            
            schedule = DoctorWeeklySchedule.objects.get(id=schedule_id, doctor=doctor)
            schedule_name = f"{schedule.get_day_of_week_display()} ({schedule.start_time} - {schedule.end_time})"
            schedule.delete()
            messages.success(request, f'Schedule for {schedule_name} deleted successfully!')
            return redirect('dashboard:doctor_schedule')
            
        except DoctorWeeklySchedule.DoesNotExist:
            messages.error(request, 'Schedule not found.')
            return redirect('dashboard:doctor_schedule')
        except Exception as e:
            messages.error(request, f'Error deleting schedule: {str(e)}')
            return redirect('dashboard:doctor_schedule')
    
    return redirect('dashboard:doctor_schedule')


@login_required
def doctor_notifications(request):
    """Doctor notifications"""
    if not request.user.is_doctor():
        messages.error(request, 'Access denied.')
        return redirect('home')

    try:
        doctor = request.user.doctor_profile
    except Exception:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')

    recent_appointments = Appointment.objects.filter(
        doctor=doctor
    ).select_related('patient').order_by('-updated_at', '-created_at')[:20]

    notifications = []
    for appointment in recent_appointments:
        patient_name = appointment.patient.get_full_name() if appointment.patient else appointment.guest_full_name or 'Guest patient'

        if appointment.status == 'cancelled':
            message_text = f'Appointment cancelled by {patient_name}'
            is_read = True
        elif appointment.status == 'completed':
            message_text = f'Appointment completed with {patient_name}'
            is_read = True
        elif appointment.status == 'confirmed':
            message_text = f'Appointment confirmed for {patient_name}'
            is_read = True
        else:
            message_text = f'New appointment booked by {patient_name}'
            is_read = False

        notifications.append(
            {
                'message': message_text,
                'time': appointment.updated_at.strftime('%d %b %Y, %I:%M %p'),
                'is_read': is_read,
            }
        )
    
    context = {
        'doctor': doctor,
        'notifications': notifications,
    }
    
    return render(request, 'dashboards/doctor_notifications.html', context)


# Admin Dashboard
@login_required
def admin_dashboard(request):
    """Super admin dashboard"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Statistics
    total_doctors = Doctor.objects.count()
    total_patients = User.objects.filter(role='patient').count()
    total_appointments = Appointment.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Pending verifications
    pending_verifications = Doctor.objects.filter(is_verified=False).count()
    
    # Recent appointments
    recent_appointments = Appointment.objects.order_by('-created_at')[:10]

    # Recent registered patients
    recent_patients = User.objects.filter(role='patient').order_by('-date_joined')[:10]

    # Today's appointments
    today_appointments = Appointment.objects.filter(date=date.today()).count()

    # Monthly revenue chart data
    from django.db.models.functions import TruncMonth

    monthly_revenue = Payment.objects.filter(
        status='completed'
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')[:12]

    # Persist and load dashboard notifications.
    generated_notifications = []

    if pending_verifications > 0:
        generated_notifications.append(
            {
                'source_key': 'pending_verifications',
                'title': 'Doctor verification required',
                'message': f'{pending_verifications} doctor account(s) pending verification.',
                'notif_type': 'warning',
                'target_url': reverse('dashboard:admin_doctors'),
            }
        )

    recent_pending_appointments = Appointment.objects.filter(status='pending').order_by('-created_at')[:3]
    for appointment in recent_pending_appointments:
        patient_name = 'Guest Patient'
        if appointment.patient:
            patient_name = appointment.patient.get_full_name() or appointment.patient.username or 'Guest Patient'
        elif appointment.guest_full_name:
            patient_name = appointment.guest_full_name

        doctor_name = 'Unknown Doctor'
        if appointment.doctor:
            doctor_name = appointment.doctor.get_full_name() or appointment.doctor.user.get_full_name() or appointment.doctor.user.username or 'Unknown Doctor'

        generated_notifications.append(
            {
                'source_key': f'pending_appt_{appointment.id}',
                'title': 'Pending appointment',
                'message': f"{patient_name} requested an appointment with {doctor_name}.",
                'notif_type': 'info',
                'target_url': reverse('dashboard:admin_appointments'),
            }
        )

    recent_payments = Payment.objects.order_by('-created_at')[:2]
    for payment in recent_payments:
        generated_notifications.append(
            {
                'source_key': f'payment_{payment.id}',
                'title': 'Payment update',
                'message': f"Invoice {payment.invoice_number} is {payment.status.replace('_', ' ').title()}.",
                'notif_type': 'success' if payment.status == 'completed' else 'warning',
                'target_url': reverse('dashboard:admin_payments'),
            }
        )

    for item in generated_notifications:
        notification, created = AdminNotification.objects.get_or_create(
            admin_user=request.user,
            source_key=item['source_key'],
            defaults={
                'title': item['title'],
                'message': item['message'],
                'notif_type': item['notif_type'],
                'target_url': item['target_url'],
            },
        )
        if not created:
            changed = False
            if notification.title != item['title']:
                notification.title = item['title']
                changed = True
            if notification.message != item['message']:
                notification.message = item['message']
                changed = True
                notification.is_read = False
            if notification.notif_type != item['notif_type']:
                notification.notif_type = item['notif_type']
                changed = True
            if notification.target_url != item['target_url']:
                notification.target_url = item['target_url']
                changed = True
            if changed:
                notification.save()

    admin_notifications = AdminNotification.objects.filter(admin_user=request.user).order_by('-created_at')[:8]
    unread_notifications_count = AdminNotification.objects.filter(admin_user=request.user, is_read=False).count()

    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'total_revenue': total_revenue,
        'pending_verifications': pending_verifications,
        'recent_appointments': recent_appointments,
        'recent_patients': recent_patients,
        'today_appointments': today_appointments,
        'monthly_revenue': monthly_revenue,
        'admin_notifications': admin_notifications,
        'unread_notifications_count': unread_notifications_count,
    }

    return render(request, 'dashboards/admin_dashboard.html', context)


@login_required
def mark_admin_notification_read(request, notification_id):
    """Mark a single admin notification as read and redirect."""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')

    notification = get_object_or_404(AdminNotification, id=notification_id, admin_user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read', 'updated_at'])

    next_url = request.GET.get('next') or notification.target_url or reverse('dashboard:admin_dashboard')
    return redirect(next_url)


@login_required
def mark_all_admin_notifications_read(request):
    """Mark all admin notifications as read."""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')

    if request.method == 'POST':
        AdminNotification.objects.filter(admin_user=request.user, is_read=False).update(is_read=True)

    return redirect('dashboard:admin_dashboard')


@login_required
def admin_users(request):
    """Admin user management"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    users = User.objects.all().order_by('-date_joined')

    search_query = request.GET.get('search', '').strip()
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    context = {
        'users': users,
        'search_query': search_query,
    }
    
    return render(request, 'dashboards/admin_users.html', context)


@login_required
def admin_employees(request):
    """Admin employees management"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    employees = User.objects.filter(role='employee').order_by('-date_joined')
    
    # Handle search filter
    search_query = request.GET.get('search', '').strip()
    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    context = {
        'employees': employees,
        'search_query': search_query,
    }
    
    return render(request, 'dashboards/admin_employees.html', context)


@login_required
def search_employees(request):
    """Autocomplete search for employees"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'results': []})
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'success': True, 'results': []})
    
    employees = User.objects.filter(
        role='employee',
    ).filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query) |
        Q(phone__icontains=query)
    ).values('id', 'first_name', 'last_name', 'email', 'phone', 'date_joined')[:10]
    
    results = []
    for emp in employees:
        full_name = f"{emp['first_name']} {emp['last_name']}"
        results.append({
            'id': emp['id'],
            'name': full_name,
            'email': emp['email'],
            'phone': emp['phone'] or 'N/A',
            'url': reverse('dashboard:admin_employees') + f'?search={quote(full_name)}',
            'display': f"{full_name} ({emp['email']})"
        })
    
    return JsonResponse({'success': True, 'results': results})


@login_required
def search_doctors(request):
    """Autocomplete search for doctors"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'results': []})
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'success': True, 'results': []})
    
    doctors = Doctor.objects.filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query) |
        Q(user__email__icontains=query) |
        Q(bmdc_number__icontains=query)
    ).select_related('user').prefetch_related('specialties')[:10]
    
    results = []
    for doc in doctors:
        full_name = f"Dr. {doc.user.first_name} {doc.user.last_name}"
        specialty = doc.specialties.first()
        specialty_name = specialty.name if specialty else 'N/A'
        results.append({
            'id': doc.id,
            'name': full_name,
            'email': doc.user.email,
            'specialty': specialty_name,
            'url': reverse('dashboard:admin_doctors') + f'?search={quote(query)}&tab=doctors',
            'display': f"{full_name} - {specialty_name}"
        })
    
    return JsonResponse({'success': True, 'results': results})


@login_required
def search_hospitals(request):
    """Autocomplete search for hospitals"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'results': []})
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'success': True, 'results': []})
    
    hospitals = Hospital.objects.filter(
        Q(name__icontains=query) |
        Q(phone__icontains=query) |
        Q(email__icontains=query)
    ).values('id', 'name', 'phone', 'email', 'city')[:10]
    
    results = []
    for hosp in hospitals:
        results.append({
            'id': hosp['id'],
            'name': hosp['name'],
            'phone': hosp['phone'] or 'N/A',
            'city': hosp['city'] or 'N/A',
            'url': reverse('dashboard:admin_doctors') + f'?search={quote(query)}&tab=hospitals',
            'display': f"{hosp['name']} - {hosp['city']}"
        })
    
    return JsonResponse({'success': True, 'results': results})


@login_required
def search_appointments(request):
    """Autocomplete search for appointments"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'results': []})
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'success': True, 'results': []})
    
    appointments = Appointment.objects.filter(
        Q(patient__first_name__icontains=query) |
        Q(patient__last_name__icontains=query) |
        Q(doctor__user__first_name__icontains=query) |
        Q(doctor__user__last_name__icontains=query)
    ).select_related('patient', 'doctor').values('id', 'patient__first_name', 'patient__last_name', 'doctor__user__first_name', 'doctor__user__last_name', 'date', 'status')[:10]
    
    results = []
    for appt in appointments:
        patient_name = f"{appt['patient__first_name']} {appt['patient__last_name']}"
        doctor_name = f"Dr. {appt['doctor__user__first_name']} {appt['doctor__user__last_name']}"
        results.append({
            'id': appt['id'],
            'patient': patient_name,
            'doctor': doctor_name,
            'date': str(appt['date']),
            'status': appt['status'],
            'url': reverse('appointments:detail', args=[appt['id']]),
            'display': f"{patient_name} - {doctor_name} ({appt['date']})"
        })
    
    return JsonResponse({'success': True, 'results': results})


@login_required
def search_payments(request):
    """Autocomplete search for payments"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'results': []})
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'success': True, 'results': []})
    
    payments = Payment.objects.filter(
        Q(appointment__patient__first_name__icontains=query) |
        Q(appointment__patient__last_name__icontains=query) |
        Q(appointment__doctor__user__first_name__icontains=query) |
        Q(appointment__doctor__user__last_name__icontains=query)
    ).select_related('appointment', 'appointment__invoice', 'appointment__patient', 'appointment__doctor__user')[:10]
    
    results = []
    for pay in payments:
        patient_name = pay.appointment.patient.get_full_name() if pay.appointment.patient else pay.appointment.guest_full_name or 'Guest'
        doctor_name = pay.appointment.doctor.get_full_name()
        try:
            invoice = pay.appointment.invoice
        except Exception:
            invoice = None
        results.append({
            'id': pay.id,
            'patient': patient_name,
            'doctor': doctor_name,
            'amount': str(pay.amount),
            'date': str(pay.created_at.date()),
            'url': reverse('payments:view_invoice', args=[invoice.id]) if invoice else reverse('payments:success', args=[pay.id]),
            'display': f"{patient_name} - {doctor_name} (৳{pay.amount})"
        })
    
    return JsonResponse({'success': True, 'results': results})


@login_required
def search_users(request):
    """Autocomplete search for users"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'results': []})
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'success': True, 'results': []})
    
    users = User.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    ).values('id', 'first_name', 'last_name', 'email', 'is_super_admin', 'is_doctor', 'is_employee', 'is_patient')[:10]
    
    results = []
    for user in users:
        role = []
        if user['is_super_admin']:
            role.append('Admin')
        if user['is_doctor']:
            role.append('Doctor')
        if user['is_employee']:
            role.append('Employee')
        if user['is_patient']:
            role.append('Patient')
        
        role_str = ', '.join(role) if role else 'User'
        full_name = f"{user['first_name']} {user['last_name']}"
        
        results.append({
            'id': user['id'],
            'name': full_name,
            'email': user['email'],
            'role': role_str,
            'url': reverse('dashboard:admin_users') + f'?search={quote(full_name)}',
            'display': f"{full_name} ({user['email']}) - {role_str}"
        })
    
    return JsonResponse({'success': True, 'results': results})


@login_required
def admin_doctors(request):
    """Admin doctor management"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    doctors = Doctor.objects.all().order_by('-created_at')
    hospitals = Hospital.objects.all().order_by('-created_at')
    active_tab = request.GET.get('tab', 'doctors')

    search_query = request.GET.get('search', '').strip()
    if search_query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(bmdc_number__icontains=search_query) |
            Q(specialties__name__icontains=search_query) |
            Q(hospitals__hospital__name__icontains=search_query)
        ).distinct()
        hospitals = hospitals.filter(
            Q(name__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        ).distinct()
    
    context = {
        'doctors': doctors,
        'hospitals': hospitals,
        'search_query': search_query,
        'active_tab': active_tab,
    }
    
    return render(request, 'dashboards/admin_doctors.html', context)


@login_required
def admin_doctor_create(request):
    """Admin page for creating a new doctor (full page form)"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')

    hospitals = Hospital.objects.all().order_by('-created_at')

    # Ensure specialty dropdown has options on fresh databases.
    if not Specialty.objects.exists():
        default_specialties = [
            ('Cardiologist', 'Heart and cardiovascular system specialist'),
            ('Pediatrician', 'Children and infant health specialist'),
            ('Ophthalmologist', 'Eye and vision care specialist'),
            ('Orthopedic', 'Bone and joint specialist'),
            ('Neurologist', 'Brain and nervous system specialist'),
            ('Dermatologist', 'Skin and dermatology specialist'),
            ('Medicine Specialist', 'Internal medicine and general health'),
            ('Gynecologist', 'Women health and reproductive specialist'),
        ]
        Specialty.objects.bulk_create([
            Specialty(
                name=name,
                description=description,
                is_active=True,
                order=index,
            )
            for index, (name, description) in enumerate(default_specialties)
        ])

    specialties = Specialty.objects.filter(is_active=True).order_by('name')

    context = {
        'hospitals': hospitals,
        'specialties': specialties,
    }

    return render(request, 'dashboards/admin_doctor_create.html', context)


@login_required
def admin_specialty_create(request):
    """Admin page for managing specialties."""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')

    search_query = request.GET.get('search', '').strip()

    specialties = Specialty.objects.all().order_by('order', 'name')
    if search_query:
        specialties = specialties.filter(
            Q(name__icontains=search_query) |
            Q(name_bn__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        description = (request.POST.get('description') or '').strip()
        icon_path = ''

        if not name:
            messages.error(request, 'Specialty name is required.')
            return redirect('dashboard:admin_specialty_create')

        if Specialty.objects.filter(name__iexact=name).exists():
            messages.error(request, 'A specialty with this name already exists.')
            return redirect('dashboard:admin_specialty_create')

        icon_file = request.FILES.get('icon_image')
        if icon_file:
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg'}
            original_name = icon_file.name or ''
            extension = '.' + original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else ''

            if extension not in allowed_extensions:
                messages.error(request, 'Invalid icon format. Use JPG, PNG, WEBP, GIF, or SVG.')
                return redirect('dashboard:admin_specialty_create')

            safe_name = slugify(name) or 'specialty'
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')
            file_name = f"specialties/icons/{safe_name}-{timestamp}{extension}"
            icon_path = default_storage.save(file_name, icon_file)

        Specialty.objects.create(
            name=name,
            description=description,
            icon=icon_path,
            is_active=True,
        )

        messages.success(request, f'Specialty "{name}" created successfully.')
        return redirect('dashboard:admin_specialty_create')

    return render(request, 'dashboards/admin_specialty_create.html', {
        'specialties': specialties,
        'search_query': search_query,
    })


@login_required
def search_specialties(request):
    """Autocomplete search for specialties."""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'results': []})

    query = request.GET.get('q', '').strip()

    if len(query) < 1:
        return JsonResponse({'success': True, 'results': []})

    specialties = Specialty.objects.filter(
        Q(name__icontains=query) |
        Q(name_bn__icontains=query) |
        Q(description__icontains=query)
    ).order_by('order', 'name')[:10]

    results = []
    for specialty in specialties:
        results.append({
            'id': specialty.id,
            'name': specialty.name,
            'description': specialty.description or 'No description',
            'url': reverse('dashboard:admin_specialty_create') + f'?search={quote(query)}',
            'display': specialty.name,
        })

    return JsonResponse({'success': True, 'results': results})


@login_required
def create_specialty_ajax(request):
    """Create specialty from admin doctor create page modal."""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method.'}, status=405)

    name = (request.POST.get('name') or '').strip()
    description = (request.POST.get('description') or '').strip()
    icon_path = ''

    if not name:
        return JsonResponse({'success': False, 'message': 'Specialty name is required.'}, status=400)

    if Specialty.objects.filter(name__iexact=name).exists():
        return JsonResponse({'success': False, 'message': 'A specialty with this name already exists.'}, status=400)

    icon_file = request.FILES.get('icon_image')
    if icon_file:
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg'}
        original_name = icon_file.name or ''
        extension = '.' + original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else ''

        if extension not in allowed_extensions:
            return JsonResponse(
                {'success': False, 'message': 'Invalid icon format. Use JPG, PNG, WEBP, GIF, or SVG.'},
                status=400,
            )

        safe_name = slugify(name) or 'specialty'
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')
        file_name = f"specialties/icons/{safe_name}-{timestamp}{extension}"
        icon_path = default_storage.save(file_name, icon_file)

    specialty = Specialty.objects.create(
        name=name,
        description=description,
        icon=icon_path,
        is_active=True,
    )

    return JsonResponse(
        {
            'success': True,
            'message': 'Specialty created successfully.',
            'specialty': {
                'id': specialty.id,
                'name': specialty.name,
                'icon': specialty.icon,
            },
        }
    )


@login_required
def update_specialty(request, specialty_id):
    """Update specialty from admin specialty management page."""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('dashboard:admin_specialty_create')

    specialty = get_object_or_404(Specialty, id=specialty_id)

    name = (request.POST.get('name') or '').strip()
    name_bn = (request.POST.get('name_bn') or '').strip()
    description = (request.POST.get('description') or '').strip()
    is_active = request.POST.get('is_active') == 'on'

    if not name:
        messages.error(request, 'Specialty name is required.')
        return redirect('dashboard:admin_specialty_create')

    if Specialty.objects.filter(name__iexact=name).exclude(id=specialty.id).exists():
        messages.error(request, 'A specialty with this name already exists.')
        return redirect('dashboard:admin_specialty_create')

    icon_file = request.FILES.get('icon_image')
    if icon_file:
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg'}
        original_name = icon_file.name or ''
        extension = '.' + original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else ''

        if extension not in allowed_extensions:
            messages.error(request, 'Invalid icon format. Use JPG, PNG, WEBP, GIF, or SVG.')
            return redirect('dashboard:admin_specialty_create')

        safe_name = slugify(name) or 'specialty'
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')
        file_name = f"specialties/icons/{safe_name}-{timestamp}{extension}"
        specialty.icon = default_storage.save(file_name, icon_file)

    specialty.name = name
    specialty.name_bn = name_bn
    specialty.description = description
    specialty.is_active = is_active
    specialty.save()

    messages.success(request, f'Specialty "{specialty.name}" updated successfully.')
    return redirect('dashboard:admin_specialty_create')


@login_required
def delete_specialty(request, specialty_id):
    """Delete specialty from admin specialty management page."""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('dashboard:admin_specialty_create')

    specialty = get_object_or_404(Specialty, id=specialty_id)
    specialty_name = specialty.name

    if specialty.doctors.exists():
        messages.error(request, f'Cannot delete "{specialty_name}" because doctors are assigned to it.')
        return redirect('dashboard:admin_specialty_create')

    specialty.delete()
    messages.success(request, f'Specialty "{specialty_name}" deleted successfully.')
    return redirect('dashboard:admin_specialty_create')


@login_required
def verify_doctor(request, doctor_id):
    """Verify doctor account"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    doctor.is_verified = True
    doctor.verification_date = timezone.now()
    doctor.save()
    
    messages.success(request, f'Doctor {doctor.get_full_name()} has been verified.')
    return redirect('dashboard:admin_doctors')


@login_required
def toggle_doctor_status(request, doctor_id):
    """Toggle doctor active/inactive status"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.is_active = not doctor.is_active
    doctor.save()
    
    status = "activated" if doctor.is_active else "deactivated"
    messages.success(request, f'Doctor {doctor.get_full_name()} has been {status}.')
    return redirect('dashboard:admin_doctors')


@login_required
def delete_doctor(request, doctor_id):
    """Delete doctor account and profile."""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('dashboard:admin_doctors')

    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor_name = doctor.get_full_name()
    user = doctor.user

    # Deleting the user cascades to Doctor profile via OneToOne relation.
    user.delete()
    messages.success(request, f'Doctor {doctor_name} has been deleted.')
    return redirect('dashboard:admin_doctors')


@login_required
def delete_hospital(request, hospital_id):
    """Delete hospital from admin dashboard."""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('dashboard:admin_doctors')

    hospital = get_object_or_404(Hospital, id=hospital_id)
    hospital_name = hospital.name
    hospital.delete()
    messages.success(request, f'Hospital {hospital_name} has been deleted.')
    return redirect('dashboard:admin_doctors')


@login_required
def update_hospital(request, hospital_id):
    """Update hospital information"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    hospital = get_object_or_404(Hospital, id=hospital_id)
    
    if request.method == 'POST':
        hospital.name = request.POST.get('hospital_name', hospital.name)
        hospital.city = request.POST.get('location', hospital.city)
        hospital.phone = request.POST.get('contact_number', hospital.phone)
        hospital.email = request.POST.get('email', hospital.email)
        hospital.total_beds = request.POST.get('total_beds', hospital.total_beds)
        hospital.icu_beds_available = request.POST.get('icu_beds', hospital.icu_beds_available)
        hospital.is_active = request.POST.get('status') == 'active'
        hospital.save()
        
        messages.success(request, f'Hospital {hospital.name} has been updated successfully.')
        return redirect('dashboard:admin_doctors')
    
    return redirect('dashboard:admin_doctors')


@login_required
def admin_doctor_detail(request, doctor_id):
    """Admin doctor detail view with edit capabilities"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    hospital_schedules = list(doctor.hospitals.all().select_related('hospital'))
    weekly_schedules = list(
        DoctorWeeklySchedule.objects.filter(doctor=doctor)
        .select_related('hospital')
        .order_by('hospital_id', 'day_of_week', 'start_time')
    )
    weekly_by_hospital = {}
    for weekly in weekly_schedules:
        weekly_by_hospital.setdefault(weekly.hospital_id, []).append(weekly)

    schedule_weekly_payload = {}
    for schedule in hospital_schedules:
        entries = weekly_by_hospital.get(schedule.hospital_id, [])
        schedule.weekly_entries = entries
        schedule.display_rows = []
        if entries:
            day_indices = sorted({entry.day_of_week for entry in entries})
            schedule.display_days = _day_labels_from_indices(day_indices)
            for entry in entries:
                start_text = entry.start_time.strftime('%I:%M %p') if entry.start_time else ''
                end_text = entry.end_time.strftime('%I:%M %p') if entry.end_time else ''
                time_text = f"{start_text} - {end_text}" if start_text and end_text else 'N/A'
                schedule.display_rows.append({
                    'day': entry.get_day_of_week_display(),
                    'time': time_text,
                    'day_index': entry.day_of_week,
                    'start': start_text,
                    'end': end_text,
                })
            schedule.display_time = 'N/A'
            schedule_weekly_payload[str(schedule.id)] = [
                {
                    'day_index': entry.day_of_week,
                    'start': entry.start_time.strftime('%H:%M') if entry.start_time else '',
                    'end': entry.end_time.strftime('%H:%M') if entry.end_time else '',
                }
                for entry in entries
            ]
        else:
            schedule.display_days = schedule.consultation_days or []
            if schedule.morning_start and schedule.morning_end:
                schedule.display_time = f"{schedule.morning_start.strftime('%H:%M')} - {schedule.morning_end.strftime('%H:%M')}"
            elif schedule.evening_start and schedule.evening_end:
                schedule.display_time = f"{schedule.evening_start.strftime('%H:%M')} - {schedule.evening_end.strftime('%H:%M')}"
            else:
                schedule.display_time = 'N/A'

    assigned_hospital_ids = [schedule.hospital_id for schedule in hospital_schedules]
    available_hospitals = Hospital.objects.filter(is_active=True).exclude(id__in=assigned_hospital_ids).order_by('name')
    qualifications_list = [q.strip() for q in re.split(r'[|,\n]+', doctor.qualifications or '') if q.strip()]
    
    context = {
        'doctor': doctor,
        'hospital_schedules': hospital_schedules,
        'available_hospitals': available_hospitals,
        'specialties': Specialty.objects.filter(is_active=True).order_by('name'),
        'qualifications_list': qualifications_list,
        'schedule_weekly_json': json.dumps(schedule_weekly_payload),
    }
    
    return render(request, 'dashboards/admin_doctor_detail.html', context)


@login_required
def add_hospital_schedule(request, doctor_id):
    """Add a hospital schedule for a doctor."""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method.'})

    doctor = get_object_or_404(Doctor, id=doctor_id)

    try:
        from datetime import datetime

        def parse_flexible_time(value):
            if not value:
                return None
            cleaned = str(value).strip().upper().replace('.', '')
            formats = ['%I:%M %p', '%I %p', '%H:%M']
            for fmt in formats:
                try:
                    return datetime.strptime(cleaned, fmt).time()
                except ValueError:
                    continue
            raise ValueError('Invalid time format. Use HH:MM AM/PM or HH:MM')

        hospital_id = request.POST.get('hospital_id')
        if not hospital_id:
            return JsonResponse({'success': False, 'message': 'Please select a hospital.'})

        hospital = get_object_or_404(Hospital, id=hospital_id, is_active=True)

        if DoctorHospital.objects.filter(doctor=doctor, hospital=hospital).exists():
            return JsonResponse({'success': False, 'message': 'This hospital is already assigned to the doctor.'})

        selected_day_indices = []
        selected_starts = []
        selected_ends = []
        day_windows = {}
        for day_index in range(7):
            if request.POST.get(f'day_{day_index}') != 'on':
                continue
            start_time = parse_flexible_time(request.POST.get(f'start_time_{day_index}'))
            end_time = parse_flexible_time(request.POST.get(f'end_time_{day_index}'))
            if not start_time or not end_time:
                return JsonResponse({'success': False, 'message': 'Please set both Start and End for each selected day.'})
            if start_time >= end_time:
                return JsonResponse({'success': False, 'message': 'End time must be after start time for selected days.'})
            selected_day_indices.append(day_index)
            selected_starts.append(start_time)
            selected_ends.append(end_time)
            day_windows[day_index] = (start_time, end_time)

        if selected_day_indices:
            day_indices = sorted(set(selected_day_indices))
            morning_start = min(selected_starts)
            morning_end = max(selected_ends)
            evening_start = None
            evening_end = None
        else:
            days_str = request.POST.get('consultation_days', '')
            raw_days = [day.strip() for day in days_str.split(',') if day.strip()]
            day_indices = _parse_day_indices(raw_days)
            if not day_indices:
                return JsonResponse({'success': False, 'message': 'Please provide at least one consultation day.'})

            morning_start = parse_flexible_time(request.POST.get('morning_start'))
            morning_end = parse_flexible_time(request.POST.get('morning_end'))
            evening_start = parse_flexible_time(request.POST.get('evening_start'))
            evening_end = parse_flexible_time(request.POST.get('evening_end'))

            if not ((morning_start and morning_end) or (evening_start and evening_end)):
                return JsonResponse(
                    {'success': False, 'message': 'Please provide at least one complete time range (morning or evening).'}
                )

            weekly_start, weekly_end = _derive_schedule_window(morning_start, morning_end, evening_start, evening_end)
            if not weekly_start or not weekly_end:
                return JsonResponse({'success': False, 'message': 'End time must be after start time.'})
            day_windows = {day_index: (weekly_start, weekly_end) for day_index in day_indices}

        consultation_days = _day_labels_from_indices(day_indices)
        schedule = DoctorHospital.objects.create(
            doctor=doctor,
            hospital=hospital,
            consultation_days=consultation_days,
            consultation_fee=request.POST.get('consultation_fee') or 0,
            service_charge=request.POST.get('service_charge') or 0,
            morning_start=morning_start,
            morning_end=morning_end,
            evening_start=evening_start,
            evening_end=evening_end,
            is_primary=(not doctor.hospitals.exists()),
            is_active=True,
        )

        _sync_weekly_schedules_for_hospital(doctor, hospital, day_windows)

        return JsonResponse(
            {
                'success': True,
                'message': f'Schedule added for {schedule.hospital.name}.',
            }
        )
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def update_doctor_details(request, doctor_id):
    """Update doctor basic information"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method.'})
    
    doctor = get_object_or_404(Doctor, id=doctor_id)

    def strip_dr_prefix(value):
        if not value:
            return ''
        return re.sub(r'^\s*dr\.?\s+', '', str(value), flags=re.IGNORECASE).strip()
    
    try:
        # Update doctor information
        user = doctor.user
        user.first_name = strip_dr_prefix(request.POST.get('first_name', user.first_name))
        user.last_name = strip_dr_prefix(request.POST.get('last_name', user.last_name))
        user.phone = request.POST.get('phone', user.phone)

        new_email = request.POST.get('email', user.email).strip()
        if new_email and new_email != user.email and User.objects.filter(email=new_email).exclude(id=user.id).exists():
            return JsonResponse({'success': False, 'message': 'Email already in use by another account.'})

        if new_email:
            user.email = new_email

        new_password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        if new_password or confirm_password:
            if len(new_password) < 4:
                return JsonResponse({'success': False, 'message': 'Password must be at least 4 characters long.'})
            if new_password != confirm_password:
                return JsonResponse({'success': False, 'message': 'Passwords do not match.'})
            user.set_password(new_password)

        user.save()
        
        # Update doctor-specific fields
        doctor.bmdc_number = request.POST.get('bmdc_number', doctor.bmdc_number)
        doctor.experience_years = request.POST.get('experience_years', doctor.experience_years)
        qualifications_raw = request.POST.get('qualifications', doctor.qualifications)
        qualifications_items = [q.strip() for q in re.split(r'[|,\n]+', qualifications_raw or '') if q.strip()]
        doctor.qualifications = ' | '.join(qualifications_items)
        doctor.commission_rate = request.POST.get('commission_rate', doctor.commission_rate)
        doctor.is_verified = request.POST.get('is_verified') == 'on'
        doctor.is_active = request.POST.get('is_active') == 'on'
        doctor.save()

        specialty_id = request.POST.get('specialty')
        if specialty_id:
            try:
                specialty = Specialty.objects.get(id=specialty_id)
                doctor.specialties.set([specialty])
            except Specialty.DoesNotExist:
                pass
        
        return JsonResponse({'success': True, 'message': 'Doctor updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def update_hospital_schedule(request, doctor_id, schedule_id):
    """Update doctor's hospital schedule"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method.'})
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    schedule = get_object_or_404(DoctorHospital, id=schedule_id, doctor=doctor)
    
    try:
        from datetime import datetime

        def parse_flexible_time(value):
            if not value:
                return None
            cleaned = str(value).strip().upper().replace('.', '')
            formats = ['%I:%M %p', '%I %p', '%H:%M']
            for fmt in formats:
                try:
                    return datetime.strptime(cleaned, fmt).time()
                except ValueError:
                    continue
            raise ValueError('Invalid time format. Use HH:MM AM/PM or HH:MM')

        selected_day_indices = []
        selected_starts = []
        selected_ends = []
        day_windows = {}
        for day_index in range(7):
            if request.POST.get(f'day_{day_index}') != 'on':
                continue
            start_time = parse_flexible_time(request.POST.get(f'start_time_{day_index}'))
            end_time = parse_flexible_time(request.POST.get(f'end_time_{day_index}'))
            if not start_time or not end_time:
                return JsonResponse({'success': False, 'message': 'Please set both Start and End for each selected day.'})
            if start_time >= end_time:
                return JsonResponse({'success': False, 'message': 'End time must be after start time for selected days.'})
            selected_day_indices.append(day_index)
            selected_starts.append(start_time)
            selected_ends.append(end_time)
            day_windows[day_index] = (start_time, end_time)

        if selected_day_indices:
            day_indices = sorted(set(selected_day_indices))
            schedule.consultation_days = _day_labels_from_indices(day_indices)
            schedule.morning_start = min(selected_starts)
            schedule.morning_end = max(selected_ends)
            schedule.evening_start = None
            schedule.evening_end = None
        else:
            days_str = request.POST.get('consultation_days', '')
            raw_days = [day.strip() for day in days_str.split(',') if day.strip()]
            day_indices = _parse_day_indices(raw_days)
            if not day_indices:
                return JsonResponse({'success': False, 'message': 'Please provide at least one consultation day.'})

            schedule.consultation_days = _day_labels_from_indices(day_indices)

            if request.POST.get('morning_start'):
                schedule.morning_start = parse_flexible_time(request.POST.get('morning_start'))
            if request.POST.get('morning_end'):
                schedule.morning_end = parse_flexible_time(request.POST.get('morning_end'))
            if request.POST.get('evening_start'):
                schedule.evening_start = parse_flexible_time(request.POST.get('evening_start'))
            if request.POST.get('evening_end'):
                schedule.evening_end = parse_flexible_time(request.POST.get('evening_end'))

            weekly_start, weekly_end = _derive_schedule_window(
                schedule.morning_start,
                schedule.morning_end,
                schedule.evening_start,
                schedule.evening_end,
            )
            if not weekly_start or not weekly_end:
                return JsonResponse({'success': False, 'message': 'End time must be after start time.'})
            day_windows = {day_index: (weekly_start, weekly_end) for day_index in day_indices}

        if request.POST.get('consultation_fee') is not None and str(request.POST.get('consultation_fee')).strip() != '':
            schedule.consultation_fee = request.POST.get('consultation_fee')
        if request.POST.get('service_charge') is not None and str(request.POST.get('service_charge')).strip() != '':
            schedule.service_charge = request.POST.get('service_charge')
        
        schedule.save()

        _sync_weekly_schedules_for_hospital(doctor, schedule.hospital, day_windows)
        
        return JsonResponse({'success': True, 'message': 'Schedule updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def remove_doctor_hospital(request, doctor_id, schedule_id):
    """Remove hospital from doctor's schedule"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method.'})
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    schedule = get_object_or_404(DoctorHospital, id=schedule_id, doctor=doctor)
    
    try:
        hospital_name = schedule.hospital.name
        DoctorWeeklySchedule.objects.filter(doctor=doctor, hospital=schedule.hospital).delete()
        DoctorAvailability.objects.filter(
            doctor=doctor,
            hospital=schedule.hospital,
            date__gte=date.today(),
            is_exception=False,
            is_booked=False,
        ).update(is_available=False)
        schedule.delete()
        return JsonResponse({'success': True, 'message': f'{hospital_name} removed successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def create_doctor(request):
    """Create new doctor"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            def to_int(value, default=0):
                try:
                    value = str(value).strip()
                    return int(value) if value else default
                except (TypeError, ValueError):
                    return default

            def to_float(value, default=0.0):
                try:
                    value = str(value).strip()
                    return float(value) if value else default
                except (TypeError, ValueError):
                    return default

            def strip_dr_prefix(value):
                if not value:
                    return ''
                return re.sub(r'^\s*dr\.?\s+', '', str(value), flags=re.IGNORECASE).strip()

            # Get form data
            email = request.POST.get('email')
            first_name = strip_dr_prefix(request.POST.get('first_name', ''))
            last_name = strip_dr_prefix(request.POST.get('last_name', ''))
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            if not is_gmail_address(email):
                messages.error(request, 'Doctors must use a Gmail address.')
                return redirect('dashboard:admin_doctor_create')

            # Validate email
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.')
                return redirect('dashboard:admin_doctor_create')
            
            # Validate password
            if not password:
                messages.error(request, 'Password is required.')
                return redirect('dashboard:admin_doctor_create')
            
            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return redirect('dashboard:admin_doctor_create')
            
            if len(password) < 4:
                messages.error(request, 'Password must be at least 4 characters long.')
                return redirect('dashboard:admin_doctor_create')

            specialty_id = (request.POST.get('specialty') or '').strip()
            if not specialty_id:
                messages.error(request, 'Specialty is required.')
                return redirect('dashboard:admin_doctor_create')

            try:
                specialty = Specialty.objects.get(id=specialty_id, is_active=True)
            except Specialty.DoesNotExist:
                messages.error(request, 'Selected specialty is invalid.')
                return redirect('dashboard:admin_doctor_create')

            qualification_raw = request.POST.get('qualification', '')
            qualification_items = [q.strip() for q in re.split(r'[|,\n]+', qualification_raw or '') if q.strip()]
            normalized_qualifications = ' | '.join(qualification_items)
            
            with transaction.atomic():
                # Create user with provided password
                user = User.objects.create_user(
                    email=email,
                    username=generate_unique_username(email.split('@')[0]),
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )
                user.role = 'doctor'
                user.save()

                # Create doctor profile
                doctor = Doctor.objects.create(
                    user=user,
                    bmdc_number=request.POST.get('bmdc_number'),
                    experience_years=to_int(request.POST.get('experience_years'), 0),
                    qualifications=normalized_qualifications,
                    consultation_fee_online=0,
                    consultation_fee_in_person=0,
                    commission_rate=to_float(request.POST.get('commission_percentage'), 15.0),
                    is_active=request.POST.get('status') == 'active'
                )
                
                # Set date of birth and gender if provided
                if request.POST.get('date_of_birth'):
                    doctor.date_of_birth = request.POST.get('date_of_birth')
                if request.POST.get('gender'):
                    doctor.gender = request.POST.get('gender')
                doctor.save()

                # Handle optional profile picture upload
                if 'profile_picture' in request.FILES:
                    doctor.profile_picture = request.FILES['profile_picture']
                    doctor.save()

                # Add specialty
                doctor.specialties.add(specialty)

                # Add multiple hospitals with per-hospital fees and schedules
                num_hospitals = max(1, to_int(request.POST.get('num_hospitals'), 1))
                from doctors.models import DoctorWeeklySchedule, DoctorAvailability
                from datetime import datetime

                def parse_flexible_time(value):
                    if not value:
                        return None
                    cleaned = str(value).strip().upper().replace('.', '')
                    formats = ['%I:%M %p', '%I %p', '%H:%M']
                    for fmt in formats:
                        try:
                            return datetime.strptime(cleaned, fmt).time()
                        except ValueError:
                            continue
                    return None

                for i in range(num_hospitals):
                    hospital_id = request.POST.get(f'hospital_{i}')
                    if not hospital_id:
                        continue
                    
                    try:
                        hospital = Hospital.objects.get(id=hospital_id)
                        
                        # Get consultation fee and service charge from form
                        consultation_fee = to_float(request.POST.get(f'consultation_fee_{i}'), 500.0)
                        service_charge = to_float(request.POST.get(f'service_charge_{i}'), 50.0)
                        
                        # Create or get DoctorHospital association
                        doctor_hospital, _ = DoctorHospital.objects.get_or_create(
                            doctor=doctor,
                            hospital=hospital,
                            defaults={
                                'is_primary': (i == 0),
                                'consultation_fee': consultation_fee,
                                'service_charge': service_charge,
                            }
                        )
                        doctor_hospital.consultation_fee = consultation_fee
                        doctor_hospital.service_charge = service_charge

                        selected_day_indices = []
                        selected_starts = []
                        selected_ends = []
                        
                        # Process weekly schedules for this hospital
                        # Days 0-6: Monday-Sunday
                        for day_index in range(7):
                            checkbox_name = f'day_{i}_{day_index}'
                            if request.POST.get(checkbox_name) == 'on':
                                start_time_str = request.POST.get(f'start_time_{i}_{day_index}')
                                end_time_str = request.POST.get(f'end_time_{i}_{day_index}')
                                
                                if start_time_str and end_time_str:
                                    try:
                                        # Parse 12-hour (08:15 PM) and 24-hour (20:15) input formats
                                        start_time = parse_flexible_time(start_time_str)
                                        end_time = parse_flexible_time(end_time_str)
                                        if not start_time or not end_time:
                                            continue
                                        
                                        # Update existing schedule if present, otherwise create it
                                        DoctorWeeklySchedule.objects.update_or_create(
                                            doctor=doctor,
                                            hospital=hospital,
                                            day_of_week=day_index,
                                            defaults={
                                                'start_time': start_time,
                                                'end_time': end_time,
                                                'is_active': True,
                                            }
                                        )
                                        selected_day_indices.append(day_index)
                                        selected_starts.append(start_time)
                                        selected_ends.append(end_time)
                                    except (ValueError, Exception):
                                        pass

                        if selected_day_indices and selected_starts and selected_ends:
                            doctor_hospital.consultation_days = _day_labels_from_indices(selected_day_indices)
                            doctor_hospital.morning_start = min(selected_starts)
                            doctor_hospital.morning_end = max(selected_ends)
                            doctor_hospital.evening_start = None
                            doctor_hospital.evening_end = None
                            doctor_hospital.save(
                                update_fields=[
                                    'consultation_days',
                                    'consultation_fee',
                                    'service_charge',
                                    'morning_start',
                                    'morning_end',
                                    'evening_start',
                                    'evening_end',
                                    'updated_at',
                                ]
                            )
                        
                        # Process custom dates for this hospital
                        # Find all custom date entries with pattern: custom_date_{i}_{dateCount}
                        post_data = request.POST
                        custom_date_pattern = re.compile(rf'^custom_date_{i}_(\d+)$')
                        
                        for key in post_data.keys():
                            match = custom_date_pattern.match(key)
                            if match:
                                date_count = match.group(1)
                                date_str = post_data.get(f'custom_date_{i}_{date_count}')
                                status = post_data.get(f'custom_status_{i}_{date_count}', 'available')
                                custom_start_time_str = post_data.get(f'custom_start_time_{i}_{date_count}')
                                custom_end_time_str = post_data.get(f'custom_end_time_{i}_{date_count}')
                                
                                if date_str:
                                    try:
                                        # Parse date string (YYYY-MM-DD from date input)
                                        available_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                                        
                                        # Parse optional custom times
                                        custom_start_time = None
                                        custom_end_time = None
                                        
                                        if custom_start_time_str:
                                            custom_start_time = parse_flexible_time(custom_start_time_str)
                                        if custom_end_time_str:
                                            custom_end_time = parse_flexible_time(custom_end_time_str)

                                        if custom_start_time and custom_end_time:
                                            time_slot_value = f"{custom_start_time.strftime('%H:%M')}-{custom_end_time.strftime('%H:%M')}"
                                        else:
                                            time_slot_value = '09:00-11:00'
                                        
                                        # Update custom date exception if present, otherwise create it
                                        DoctorAvailability.objects.update_or_create(
                                            doctor=doctor,
                                            date=available_date,
                                            hospital=hospital,
                                            defaults={
                                                'is_exception': True,
                                                'custom_start_time': custom_start_time,
                                                'custom_end_time': custom_end_time,
                                                'is_available': (status == 'available'),
                                                'time_slot': time_slot_value,
                                            }
                                        )
                                    except (ValueError, Exception):
                                        pass
                
                    except Hospital.DoesNotExist:
                        pass
            
            messages.success(
                request, 
                f'Doctor {user.get_full_name()} created successfully! '
                f'Added to {num_hospitals} hospital(s) with schedules.'
            )
            return redirect('dashboard:admin_doctors')
            
        except Exception as e:
            messages.error(request, f'Error creating doctor: {str(e)}')
            return redirect('dashboard:admin_doctor_create')
    
    return redirect('dashboard:admin_doctors')


@login_required
def create_hospital(request):
    """Create new hospital"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            location = request.POST.get('location', '').strip()
            district = request.POST.get('district', '').strip() or location

            hospital = Hospital.objects.create(
                name=request.POST.get('hospital_name'),
                address=request.POST.get('address', ''),
                city=location,
                district=district,
                phone=request.POST.get('contact_number', ''),
                email=request.POST.get('email', ''),
                website=request.POST.get('website', ''),
                total_beds=int(request.POST.get('total_beds', 0)),
                icu_beds_available=int(request.POST.get('icu_beds', 0)),
                is_active=request.POST.get('status') == 'active'
            )
            
            messages.success(request, f'Hospital {hospital.name} created successfully.')
            return redirect('dashboard:admin_doctors')
            
        except Exception as e:
            messages.error(request, f'Error creating hospital: {str(e)}')
            return redirect('dashboard:admin_doctors')
    
    return redirect('dashboard:admin_doctors')


@login_required
def create_employee(request):
    """Create new employee"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone = request.POST.get('phone')
            department = request.POST.get('department')
            designation = request.POST.get('designation')
            joining_date = request.POST.get('joining_date')
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')
            is_active = request.POST.get('is_active') == 'on'

            if not is_gmail_address(email):
                messages.error(request, 'Employees must use a Gmail address.')
                return redirect('dashboard:admin_employees')
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'An account with this email already exists.')
                return redirect('dashboard:admin_employees')
            
            # Validate password if provided
            if password and confirm_password:
                if password != confirm_password:
                    messages.error(request, 'Passwords do not match.')
                    return redirect('dashboard:admin_employees')
                if len(password) < 4:
                    messages.error(request, 'Password must be at least 4 characters long.')
                    return redirect('dashboard:admin_employees')
                use_password = password
            else:
                # Generate temporary password if not provided
                use_password = 'Emp' + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10)) + '!@#'
            
            # Create User account
            user = User.objects.create_user(
                username=generate_unique_username(email.split('@')[0]),
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role='employee',
                password=use_password
            )
            
            # Create EmployeeProfile
            employee_id = f'EMP-{user.id:04d}'
            EmployeeProfile.objects.create(
                user=user,
                employee_id=employee_id,
                department=department,
                designation=designation,
                joining_date=joining_date,
                is_active=is_active
            )
            
            if password:
                messages.success(request, f'Employee {user.get_full_name()} created successfully! Email: {user.email}. Password: (as set by admin)')
            else:
                messages.success(request, f'Employee {user.get_full_name()} created successfully. Temporary password: {use_password}')
            return redirect('dashboard:admin_employees')
            
        except Exception as e:
            messages.error(request, f'Error creating employee: {str(e)}')
            return redirect('dashboard:admin_employees')
    
    return redirect('dashboard:admin_employees')


@login_required
def update_employee(request, employee_id):
    """Update employee"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=employee_id)
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.phone = request.POST.get('phone', user.phone)
            user.save()
            
            return JsonResponse({'success': True, 'message': 'Employee updated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def delete_employee(request, employee_id):
    """Delete employee"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=employee_id)
            user.delete()
            return JsonResponse({'success': True, 'message': 'Employee deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def update_user(request, user_id):
    """Update user"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.phone = request.POST.get('phone', user.phone)
            user.role = request.POST.get('role', user.role)
            user.save()
            
            return JsonResponse({'success': True, 'message': 'User updated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def delete_user(request, user_id):
    """Delete user"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({'success': True, 'message': 'User deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def delete_appointment(request, appointment_id):
    """Delete appointment"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method == 'POST':
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.delete()
            return JsonResponse({'success': True, 'message': 'Appointment deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def update_appointment(request, appointment_id):
    """Update appointment details"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method.'})
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Update appointment information
        if request.POST.get('date'):
            appointment.date = request.POST.get('date')
        if request.POST.get('time_slot'):
            appointment.time_slot = request.POST.get('time_slot')
        if request.POST.get('service_charge'):
            appointment.service_fee = request.POST.get('service_charge')
        if request.POST.get('notes'):
            appointment.patient_notes = request.POST.get('notes')
        if request.POST.get('status'):
            appointment.status = request.POST.get('status')
        
        appointment.save()
        return JsonResponse({'success': True, 'message': 'Appointment updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def flag_payment(request, invoice_id):
    """Flag payment"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method == 'POST':
        try:
            reason = request.POST.get('reason')
            notes = request.POST.get('notes', '')
            
            # In a real application, this would update a Payment/Invoice model
            # For now, we'll just return success
            return JsonResponse({'success': True, 'message': f'Payment flagged as {reason}'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def generate_bill(request):
    """Generate bill for doctor"""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'})
    
    if request.method == 'POST':
        try:
            doctor_id = request.POST.get('doctor')
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
            
            # In a real application, this would generate a PDF
            messages.success(request, f'Bill generated for date range {from_date} to {to_date}')
            return JsonResponse({'success': True, 'message': 'Bill generated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def export_report(request):
    """Export payment report"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        # In a real application, this would generate a CSV or Excel file
        # For now, we'll just return a message
        messages.success(request, 'Report exported successfully')
        return redirect('dashboard:admin_payments')
    except Exception as e:
        messages.error(request, f'Error exporting report: {str(e)}')
        return redirect('dashboard:admin_payments')


@login_required
def download_invoice(request, invoice_id):
    """Download invoice"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        # In a real application, this would generate and return a PDF file
        messages.success(request, f'Invoice {invoice_id} downloaded')
        return redirect('dashboard:admin_payments')
    except Exception as e:
        messages.error(request, f'Error downloading invoice: {str(e)}')
        return redirect('dashboard:admin_payments')



@login_required
def admin_appointments(request):
    """Admin appointment management"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get all appointments
    all_appointments = Appointment.objects.all().select_related('doctor', 'doctor__user', 'hospital', 'patient', 'assigned_to').order_by('-created_at')
    employees = User.objects.filter(
        role='employee',
        is_active=True,
    ).select_related('employee_profile').order_by('first_name', 'last_name', 'username')

    search_query = request.GET.get('search', '').strip()
    if search_query:
        all_appointments = all_appointments.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(guest_full_name__icontains=search_query) |
            Q(doctor__user__first_name__icontains=search_query) |
            Q(doctor__user__last_name__icontains=search_query) |
            Q(hospital__name__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(time_slot__icontains=search_query)
        ).distinct()
    
    # Separate distributed and non-distributed
    distributed_appointments = all_appointments.filter(assigned_to__isnull=False)
    non_distributed_appointments = all_appointments.filter(assigned_to__isnull=True)
    
    # Serialize appointments to JSON-friendly format
    def serialize_appointments(appointments):
        data = []
        for appt in appointments:
            data.append({
                'id': appt.id,
                'patient': {
                    'first_name': appt.patient.first_name if appt.patient else '',
                    'last_name': appt.patient.last_name if appt.patient else '',
                    'email': appt.patient.email if appt.patient else appt.guest_email,
                    'phone': appt.patient.phone if appt.patient else appt.guest_phone,
                } if appt.patient else None,
                'guest_full_name': appt.guest_full_name,
                'guest_email': appt.guest_email,
                'guest_phone': appt.guest_phone,
                'guest_age': appt.guest_age,
                'guest_gender': appt.guest_gender,
                'doctor': {
                    'id': appt.doctor.id,
                    'user': {
                        'first_name': appt.doctor.user.first_name,
                        'last_name': appt.doctor.user.last_name,
                        'phone': appt.doctor.user.phone,
                    },
                    'specialties': [{'name': s.name} for s in appt.doctor.specialties.all()],
                    'qualifications': appt.doctor.qualifications,
                },
                'hospital': {
                    'id': appt.hospital.id,
                    'name': appt.hospital.name,
                },
                'assigned_to': {
                    'id': appt.assigned_to_id,
                    'name': appt.assigned_to.get_full_name() or appt.assigned_to.username,
                    'designation': getattr(getattr(appt.assigned_to, 'employee_profile', None), 'designation', ''),
                } if appt.assigned_to else None,
                'date': appt.date.isoformat(),
                'time_slot': appt.time_slot,
                'consultation_type': appt.consultation_type,
                'status': appt.status,
                'total_amount': str(appt.total_amount),
                'service_fee': str(appt.service_fee),
                'patient_notes': appt.patient_notes,
            })
        return data
    
    # Convert to JSON
    import json
    distributed_json = json.dumps(serialize_appointments(distributed_appointments))
    non_distributed_json = json.dumps(serialize_appointments(non_distributed_appointments))
    employees_json = json.dumps([
        {
            'id': employee.id,
            'name': employee.get_full_name() or employee.username,
            'designation': getattr(employee.employee_profile, 'designation', ''),
        }
        for employee in employees
    ])
    
    context = {
        'all_appointments': all_appointments,
        'distributed_appointments': distributed_appointments,
        'non_distributed_appointments': non_distributed_appointments,
        'distributed_appointments_json': distributed_json,
        'non_distributed_appointments_json': non_distributed_json,
        'employees_json': employees_json,
        'recent_appointments': all_appointments[:10],  # For initial display
        'search_query': search_query,
    }
    
    return render(request, 'dashboards/admin_appointments.html', context)


@login_required
def assign_appointment_employee(request, appointment_id):
    """Assign an appointment to an employee."""
    if not request.user.is_super_admin():
        return JsonResponse({'success': False, 'message': 'Access denied.'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    appointment = get_object_or_404(Appointment, id=appointment_id)
    employee_id = request.POST.get('employee_id')

    if not employee_id:
        return JsonResponse({'success': False, 'message': 'Please select an employee.'}, status=400)

    employee = get_object_or_404(User, id=employee_id, role='employee', is_active=True)
    appointment.assigned_to = employee
    appointment.save(update_fields=['assigned_to', 'updated_at'])

    return JsonResponse({
        'success': True,
        'message': 'Employee assigned successfully.',
        'employee_name': employee.get_full_name() or employee.username,
    })


@login_required
def admin_payments(request):
    """Admin payment management"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')

    search_query = request.GET.get('search', '').strip()

    appointments = Appointment.objects.select_related(
        'patient',
        'doctor',
        'doctor__user',
        'payment',
        'invoice',
    ).order_by('-created_at')

    if search_query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(guest_full_name__icontains=search_query) |
            Q(doctor__user__first_name__icontains=search_query) |
            Q(doctor__user__last_name__icontains=search_query) |
            Q(doctor__user__email__icontains=search_query) |
            Q(hospital__name__icontains=search_query) |
            Q(payment__method__icontains=search_query) |
            Q(payment__status__icontains=search_query) |
            Q(invoice__invoice_number__icontains=search_query)
        ).distinct()

    payment_rows = []
    method_icon_map = {
        'bkash': 'bi-wallet2',
        'nagad': 'bi-phone',
        'card': 'bi-credit-card',
        'cash': 'bi-cash-coin',
    }

    for appt in appointments:
        payment = getattr(appt, 'payment', None)
        invoice = getattr(appt, 'invoice', None)

        patient_name = (
            appt.patient.get_full_name().strip()
            if appt.patient and appt.patient.get_full_name().strip()
            else (appt.patient.username if appt.patient else (appt.guest_full_name or 'Guest Patient'))
        )
        doctor_name = f"Dr. {appt.doctor.user.get_full_name() or appt.doctor.user.username}"
        amount = payment.amount if payment else appt.consultation_fee
        service_charge = appt.service_fee
        total_amount = appt.total_amount

        method_key = (payment.method if payment else (appt.payment_method or '')).lower()
        method_display = (
            payment.get_method_display()
            if payment
            else (appt.get_payment_method_display() if appt.payment_method else 'Not Set')
        )

        payment_status = payment.status if payment else ('completed' if appt.is_paid else 'pending')
        invoice_id = invoice.invoice_number if invoice else f"APPT-{appt.id:04d}"

        payment_rows.append({
            'invoice_id': invoice_id,
            'patient_name': patient_name,
            'doctor_name': doctor_name,
            'amount': amount,
            'service_charge': service_charge,
            'total_amount': total_amount,
            'date': appt.created_at.date(),
            'method_display': method_display,
            'method_icon': method_icon_map.get(method_key, 'bi-receipt'),
            'payment_status': payment_status,
        })

    total_revenue = sum(
        row['total_amount']
        for row in payment_rows
        if row['payment_status'] == 'completed'
    )
    pending_amount = sum(
        row['total_amount']
        for row in payment_rows
        if row['payment_status'] in ['pending', 'processing']
    )
    overdue_amount = sum(
        row['total_amount']
        for row in payment_rows
        if row['payment_status'] in ['pending', 'processing'] and row['date'] < date.today()
    )

    context = {
        'payment_rows': payment_rows,
        'recent_transactions': payment_rows[:5],
        'total_revenue': total_revenue,
        'pending_amount': pending_amount,
        'overdue_amount': overdue_amount,
        'search_query': search_query,
    }
    
    return render(request, 'dashboards/admin_payments.html', context)


@login_required
def admin_statistics(request):
    """Admin statistics page"""
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    from django.db.models.functions import TruncDate

    appointments = Appointment.objects.select_related('doctor', 'doctor__user', 'hospital')
    payments = Payment.objects.select_related('appointment')

    total_appointments = appointments.count()
    active_statuses = appointments.filter(status__in=['pending', 'confirmed']).count()
    total_revenue = payments.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0

    this_month_start = date.today().replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    this_month_count = appointments.filter(created_at__date__gte=this_month_start).count()
    last_month_count = appointments.filter(
        created_at__date__gte=last_month_start,
        created_at__date__lte=last_month_end,
    ).count()
    if last_month_count > 0:
        growth_rate = round(((this_month_count - last_month_count) / last_month_count) * 100, 1)
    else:
        growth_rate = 100.0 if this_month_count > 0 else 0.0

    pending_amount = appointments.filter(status__in=['pending', 'confirmed']).aggregate(total=Sum('total_amount'))['total'] or 0
    overdue_amount = appointments.filter(
        date__lt=date.today(),
        status__in=['pending', 'confirmed'],
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    appointments_by_specialty = list(
        appointments.values('doctor__specialties__name')
        .annotate(count=Count('id'))
        .filter(doctor__specialties__name__isnull=False)
        .order_by('-count')[:10]
    )

    daily_appointments = list(
        appointments.filter(created_at__gte=date.today() - timedelta(days=30))
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    max_daily_count = max([item['count'] for item in daily_appointments], default=1)
    for item in daily_appointments:
        item['height'] = max(12, int((item['count'] / max_daily_count) * 100))

    payment_method_distribution = list(
        appointments.exclude(payment_method='')
        .values('payment_method')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    payment_method_labels = {
        'bkash': 'bKash',
        'nagad': 'Nagad',
        'card': 'Card',
        'cash': 'Cash',
    }
    for item in payment_method_distribution:
        item['label'] = payment_method_labels.get(item['payment_method'], item['payment_method'].title())

    hospital_performance = list(
        appointments.values('hospital__name')
        .annotate(count=Count('id'))
        .filter(hospital__name__isnull=False)
        .order_by('-count')[:6]
    )
    max_hospital_count = max([item['count'] for item in hospital_performance], default=1)
    for item in hospital_performance:
        item['height'] = max(20, int((item['count'] / max_hospital_count) * 140))

    doctor_performance = list(
        appointments.values('doctor__user__first_name', 'doctor__user__last_name')
        .annotate(
            appointment_count=Count('id'),
            patient_count=Count('patient', distinct=True),
            avg_rating=Avg('doctor__rating'),
        )
        .order_by('-appointment_count')[:5]
    )
    for idx, item in enumerate(doctor_performance, start=1):
        first = item.get('doctor__user__first_name') or ''
        last = item.get('doctor__user__last_name') or ''
        full_name = f"Dr. {first} {last}".strip()
        item['rank'] = idx
        item['name'] = full_name if full_name != 'Dr.' else 'Dr. Unknown'
        item['rating'] = round(item.get('avg_rating') or 0, 1)

    recent_feedback = Review.objects.filter(is_active=True).select_related(
        'doctor__user',
        'patient',
    ).order_by('-created_at')[:5]

    context = {
        'growth_rate': growth_rate,
        'active_statuses': active_statuses,
        'total_appointments': total_appointments,
        'total_revenue': total_revenue,
        'pending_amount': pending_amount,
        'overdue_amount': overdue_amount,
        'appointments_by_specialty': appointments_by_specialty,
        'daily_appointments': daily_appointments,
        'payment_method_distribution': payment_method_distribution,
        'hospital_performance': hospital_performance,
        'doctor_performance': doctor_performance,
        'recent_feedback': recent_feedback,
    }
    
    return render(request, 'dashboards/admin_statistics.html', context)


# Employee Dashboard
@login_required
def employee_dashboard(request):
    """Employee dashboard"""
    if not request.user.is_employee():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get all appointments (employee manages all appointments)
    all_appointments = Appointment.objects.all().order_by('-created_at')
    
    # Pending appointments
    pending_appointments = Appointment.objects.filter(
        status='pending'
    ).order_by('date', 'time_slot')[:5]
    
    # Today's confirmed appointments
    today_confirmed = Appointment.objects.filter(
        date=date.today(),
        status='confirmed'
    ).count()
    
    # Total pending
    pending_count = Appointment.objects.filter(status='pending').count()
    
    # Statistics for employee
    total_managed = Appointment.objects.exclude(status='pending').count()
    completed_count = Appointment.objects.filter(status='completed').count()
    cancelled_count = Appointment.objects.filter(status='cancelled').count()
    
    # Completion rate calculation
    if total_managed > 0:
        completion_rate = round((completed_count / total_managed) * 100)
    else:
        completion_rate = 0
    
    # Total revenue from managed appointments
    total_revenue = sum(
        appt.total_amount for appt in Appointment.objects.exclude(status='pending')
    )
    
    context = {
        'pending_appointments': pending_appointments,
        'all_appointments': all_appointments,
        'today_confirmed': today_confirmed,
        'pending_count': pending_count,
        'total_managed': total_managed,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'completion_rate': completion_rate,
        'total_revenue': total_revenue,
    }
    
    return render(request, 'dashboards/employee_dashboard.html', context)


@login_required
def employee_appointments(request):
    """Employee appointment view with search and filter"""
    if not request.user.is_employee():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get base queryset
    appointments = Appointment.objects.all().order_by('-created_at')
    
    # Get search query
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    
    # Apply search filter
    if search_query:
        from django.db.models import Q
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(doctor__user__first_name__icontains=search_query) |
            Q(doctor__user__last_name__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter and status_filter != 'all':
        appointments = appointments.filter(status=status_filter)
    
    context = {
        'appointments': appointments,
        'search_query': search_query,
        'status_filter': status_filter,
        'statuses': ['pending', 'confirmed', 'completed', 'cancelled'],
    }
    
    return render(request, 'dashboards/employee_appointments.html', context)


@login_required
def employee_confirm_appointment(request, appointment_id):
    """Employee confirms appointment"""
    if not request.user.is_employee():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    appointment.status = 'confirmed'
    appointment.confirmed_at = timezone.now()
    appointment.save()
    
    # Log history
    from appointments.models import AppointmentHistory
    AppointmentHistory.objects.create(
        appointment=appointment,
        status_from='pending',
        status_to='confirmed',
        changed_by=request.user,
        notes='Confirmed by employee'
    )
    
    messages.success(request, 'Appointment confirmed!')
    return redirect('dashboard:employee_dashboard')


@login_required
def employee_manage_appointment(request, appointment_id):
    """Update managing cost and optionally confirm appointment from employee panel."""
    if not request.user.is_employee():
        messages.error(request, 'Access denied.')
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('dashboard:employee_appointments')

    appointment = get_object_or_404(Appointment, id=appointment_id)
    old_status = appointment.status

    managing_cost_raw = (request.POST.get('managing_cost') or '').strip()
    if managing_cost_raw:
        try:
            managing_cost = Decimal(managing_cost_raw)
            if managing_cost < 0:
                raise InvalidOperation()
            appointment.service_fee = managing_cost
        except (InvalidOperation, ValueError):
            messages.error(request, 'Managing cost must be a valid non-negative number.')
            return redirect('dashboard:employee_appointments')

    appointment.total_amount = (appointment.consultation_fee or Decimal('0.00')) + (appointment.service_fee or Decimal('0.00'))
    appointment.assigned_to = request.user

    action = request.POST.get('action')
    if action == 'confirm' and appointment.status == 'pending':
        appointment.status = 'confirmed'
        appointment.confirmed_at = timezone.now()

    appointment.save()

    if old_status != appointment.status:
        AppointmentHistory.objects.create(
            appointment=appointment,
            status_from=old_status,
            status_to=appointment.status,
            changed_by=request.user,
            notes=f'Updated from employee panel. Managing cost set to {appointment.service_fee}',
        )

    messages.success(request, 'Appointment updated successfully.')
    return redirect('dashboard:employee_appointments')

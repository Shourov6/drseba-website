"""
Views for appointments app
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from datetime import date, datetime, timedelta
from urllib.parse import quote
from decimal import Decimal
import json
from .models import Appointment, CartItem, AppointmentHistory
from doctors.models import Doctor, DoctorAvailability, DoctorWeeklySchedule, DoctorHospital, Hospital
from payments.models import Invoice, DoctorEarning


def _parse_slot_window(slot_value):
    """Parse a time-slot key like '09:00-11:00' into start/end time objects."""
    start_str, end_str = slot_value.split('-')
    return (
        datetime.strptime(start_str, '%H:%M').time(),
        datetime.strptime(end_str, '%H:%M').time(),
    )


def _format_time_slot_12h(slot_value):
    """Convert HH:MM-HH:MM to h:MM AM/PM - h:MM AM/PM for display."""
    try:
        start_str, end_str = slot_value.split('-')
        start_time = datetime.strptime(start_str, '%H:%M')
        end_time = datetime.strptime(end_str, '%H:%M')
        return f"{start_time.strftime('%I:%M %p').lstrip('0')} - {end_time.strftime('%I:%M %p').lstrip('0')}"
    except Exception:
        return slot_value


def _availability_time_slot_value(availability):
    """Return the real time-slot string for an availability, including custom exceptions."""
    if getattr(availability, 'is_exception', False) and availability.custom_start_time and availability.custom_end_time:
        return f"{availability.custom_start_time.strftime('%H:%M')}-{availability.custom_end_time.strftime('%H:%M')}"
    return availability.time_slot


def _sync_future_availabilities_from_weekly(doctor, start_date, end_date):
    """Generate future availability rows from recurring weekly schedules."""
    weekly_schedules = list(
        DoctorWeeklySchedule.objects.filter(
            doctor=doctor,
            is_active=True,
        ).select_related('hospital')
    )
    if not weekly_schedules:
        return

    slot_windows = []
    seen_slots = set()

    def add_slot_window(slot_start, slot_end):
        if not slot_start or not slot_end or slot_end <= slot_start:
            return
        slot_value = f"{slot_start.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}"
        if slot_value in seen_slots:
            return
        seen_slots.add(slot_value)
        slot_windows.append((slot_value, slot_start, slot_end))

    # Default 2-hour slots.
    for slot_value, _ in DoctorAvailability.TIME_SLOTS:
        slot_start, slot_end = _parse_slot_window(slot_value)
        add_slot_window(slot_start, slot_end)

    exceptions = DoctorAvailability.objects.filter(
        doctor=doctor,
        date__gte=start_date,
        date__lte=end_date,
        is_exception=True,
    )
    exception_map = {(ex.hospital_id, ex.date): ex for ex in exceptions}

    # Also support admin dashboard schedules stored in DoctorHospital.
    doctor_hospital_schedules = list(
        DoctorHospital.objects.filter(
            doctor=doctor,
            is_active=True,
        ).select_related('hospital')
    )

    # Include exact windows from schedules so custom times (e.g. 20:00-22:00)
    # are available even when they are outside default TIME_SLOTS.
    for schedule in weekly_schedules:
        add_slot_window(schedule.start_time, schedule.end_time)

    for schedule in doctor_hospital_schedules:
        add_slot_window(schedule.morning_start, schedule.morning_end)
        add_slot_window(schedule.evening_start, schedule.evening_end)

    def normalize_weekday(day_value):
        key = str(day_value or '').strip().lower().replace('.', '')
        day_map = {
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
        return day_map.get(key)

    total_days = (end_date - start_date).days + 1
    for offset in range(total_days):
        current_date = start_date + timedelta(days=offset)
        weekday = current_date.weekday()

        for schedule in weekly_schedules:
            if schedule.day_of_week != weekday:
                continue

            exception = exception_map.get((schedule.hospital_id, current_date))
            if exception:
                if not exception.is_available:
                    DoctorAvailability.objects.filter(
                        doctor=doctor,
                        hospital_id=schedule.hospital_id,
                        date=current_date,
                        is_exception=False,
                        is_booked=False,
                    ).update(is_available=False)
                continue

            for slot_value, slot_start, slot_end in slot_windows:
                # Keep slots that overlap the doctor's configured window.
                if slot_end <= schedule.start_time or slot_start >= schedule.end_time:
                    continue

                availability, created = DoctorAvailability.objects.get_or_create(
                    doctor=doctor,
                    hospital_id=schedule.hospital_id,
                    date=current_date,
                    time_slot=slot_value,
                    defaults={
                        'is_available': True,
                        'is_booked': False,
                        'is_exception': False,
                    },
                )

                # Re-activate normal generated slots if they were previously disabled.
                if not created and not availability.is_exception and not availability.is_booked and not availability.is_available:
                    availability.is_available = True
                    availability.save(update_fields=['is_available', 'updated_at'])

        # Generate from DoctorHospital consultation_days + morning/evening windows.
        for schedule in doctor_hospital_schedules:
            days = schedule.consultation_days or []
            weekdays_for_schedule = {
                normalize_weekday(day_label)
                for day_label in days
                if normalize_weekday(day_label) is not None
            }

            if weekday not in weekdays_for_schedule:
                continue

            exception = exception_map.get((schedule.hospital_id, current_date))
            if exception:
                if not exception.is_available:
                    DoctorAvailability.objects.filter(
                        doctor=doctor,
                        hospital_id=schedule.hospital_id,
                        date=current_date,
                        is_exception=False,
                        is_booked=False,
                    ).update(is_available=False)
                continue

            time_windows = []
            if schedule.morning_start and schedule.morning_end:
                time_windows.append((schedule.morning_start, schedule.morning_end))
            if schedule.evening_start and schedule.evening_end:
                time_windows.append((schedule.evening_start, schedule.evening_end))

            for win_start, win_end in time_windows:
                for slot_value, slot_start, slot_end in slot_windows:
                    if slot_end <= win_start or slot_start >= win_end:
                        continue

                    availability, created = DoctorAvailability.objects.get_or_create(
                        doctor=doctor,
                        hospital_id=schedule.hospital_id,
                        date=current_date,
                        time_slot=slot_value,
                        defaults={
                            'is_available': True,
                            'is_booked': False,
                            'is_exception': False,
                        },
                    )

                    if not created and not availability.is_exception and not availability.is_booked and not availability.is_available:
                        availability.is_available = True
                        availability.save(update_fields=['is_available', 'updated_at'])


def _sync_doctor_earning(appointment):
    """Create or refresh the doctor's earning entry for an appointment."""
    consultation_amount = appointment.consultation_fee or Decimal('0.00')
    if consultation_amount <= Decimal('0.00'):
        consultation_amount = appointment.doctor.get_consultation_fee(
            appointment.consultation_type,
            hospital=appointment.hospital,
        ) or Decimal('0.00')

    earning_defaults = {
        'total_amount': consultation_amount,
        'commission_rate': appointment.doctor.commission_rate,
        'month': timezone.now().month,
        'year': timezone.now().year,
    }

    doctor_earning, created = DoctorEarning.objects.get_or_create(
        doctor=appointment.doctor,
        appointment=appointment,
        defaults=earning_defaults,
    )

    if not created:
        fields_to_update = []
        for field_name, field_value in earning_defaults.items():
            if getattr(doctor_earning, field_name) != field_value:
                setattr(doctor_earning, field_name, field_value)
                fields_to_update.append(field_name)

        if fields_to_update:
            doctor_earning.calculate_earnings()
            fields_to_update.extend(['platform_commission', 'doctor_amount'])
            doctor_earning.save(update_fields=list(dict.fromkeys(fields_to_update)))
        return doctor_earning

    doctor_earning.calculate_earnings()
    doctor_earning.save()
    return doctor_earning


def book_appointment(request, doctor_id):
    """Multi-step appointment booking - NO LOGIN REQUIRED"""
    doctor = get_object_or_404(Doctor, pk=doctor_id, is_verified=True, is_active=True)
    step = request.GET.get('step', '1')
    booking = request.session.get('booking', {})

    # Prevent stale booking session data from another doctor.
    if booking.get('doctor_id') and str(booking.get('doctor_id')) != str(doctor_id):
        booking = {}
        request.session['booking'] = booking
    
    # Get next 21 days of availability
    start_date = date.today()
    end_date = start_date + timedelta(days=21)

    # Weekly schedules are stored separately; materialize upcoming dates for booking.
    _sync_future_availabilities_from_weekly(doctor, start_date, end_date)
    
    availabilities = DoctorAvailability.objects.filter(
        doctor=doctor,
        date__gte=start_date,
        date__lte=end_date,
        is_available=True,
        is_booked=False
    ).select_related('hospital').order_by('date', 'time_slot')
    
    hospitals = Hospital.objects.filter(
        doctors__doctor=doctor,
        doctors__is_active=True,
        is_active=True,
    ).distinct().order_by('name')

    hospital_slot_counts = {
        hospital.id: availabilities.filter(hospital_id=hospital.id).count()
        for hospital in hospitals
    }

    selected_hospital_id = booking.get('hospital_id')
    if selected_hospital_id and not hospitals.filter(id=selected_hospital_id).exists():
        selected_hospital_id = None

    if not selected_hospital_id and hospitals.exists():
        selected_hospital_id = str(hospitals.first().id)

    initial_hospital_availabilities = availabilities.none()
    if selected_hospital_id:
        initial_hospital_availabilities = availabilities.filter(hospital_id=selected_hospital_id)
    
    # Serialize availabilities for JavaScript
    availabilities_json = json.dumps([
        {
            'id': av.id,
            'date': av.date.isoformat(),
            'time_slot': _availability_time_slot_value(av),
            'hospital_id': av.hospital.id,
            'hospital_name': av.hospital.name,
        }
        for av in availabilities
    ])
    
    context = {
        'doctor': doctor,
        'step': step,
        'availabilities': availabilities,
        'initial_hospital_availabilities': initial_hospital_availabilities,
        'availabilities_json': availabilities_json,
        'hospitals': hospitals,
        'selected_hospital_id': selected_hospital_id,
        'hospital_slot_counts': hospital_slot_counts,
        'booking': booking,
        'service_charge': 50,
    }

    def _finalize_booking(create_guest_record=False):
        """Create appointment record from session booking and lock slot atomically."""
        current_booking = request.session.get('booking', {})
        availability_id = current_booking.get('availability_id')
        if not availability_id:
            raise ValueError('Please select an appointment slot first.')

        with transaction.atomic():
            try:
                availability = DoctorAvailability.objects.select_for_update().get(
                    id=availability_id,
                    doctor=doctor,
                    is_available=True,
                    is_booked=False,
                )
            except DoctorAvailability.DoesNotExist as exc:
                raise ValueError('Selected slot is no longer available. Please choose another slot.') from exc

            appointment_payload = {
                'doctor': doctor,
                'hospital': availability.hospital,
                'date': availability.date,
                'time_slot': _availability_time_slot_value(availability),
                'consultation_type': current_booking.get('consultation_type') or 'in_person',
                'payment_method': (current_booking.get('payment_method') or '').lower(),
                'status': 'pending',
                'symptoms': current_booking.get('symptoms', ''),
            }

            consultation_fee = doctor.get_consultation_fee(
                appointment_payload['consultation_type'],
                hospital=availability.hospital,
            ) or Decimal('0.00')

            service_fee = Decimal('50.00')
            appointment_payload['consultation_fee'] = consultation_fee
            appointment_payload['service_fee'] = service_fee
            appointment_payload['total_amount'] = consultation_fee + service_fee

            can_link_patient = request.user.is_authenticated and request.user.is_patient() and not create_guest_record
            if can_link_patient:
                appointment_payload['patient'] = request.user
            else:
                appointment_payload.update({
                    'patient': None,
                    'guest_full_name': current_booking.get('full_name', ''),
                    'guest_email': current_booking.get('email', ''),
                    'guest_phone': current_booking.get('phone', ''),
                    'guest_age': current_booking.get('age') or None,
                    'guest_gender': current_booking.get('gender', ''),
                })

            appointment = Appointment.objects.create(**appointment_payload)

            availability.is_booked = True
            availability.save(update_fields=['is_booked'])

        request.session['guest_appointment'] = {
            'doctor_name': doctor.user.get_full_name(),
            'full_name': current_booking.get('full_name'),
            'email': current_booking.get('email'),
            'phone': current_booking.get('phone'),
            'age': current_booking.get('age'),
            'gender': current_booking.get('gender'),
            'appointment_id': appointment.id,
            'availability': str(availability),
            'payment_method': current_booking.get('payment_method'),
        }
        request.session.pop('booking', None)
        return appointment

    selected_availability = None
    selected_hospital = None
    if booking.get('availability_id'):
        selected_availability = DoctorAvailability.objects.filter(
            id=booking.get('availability_id'),
            doctor=doctor
        ).select_related('hospital').first()
        if selected_availability:
            selected_hospital = selected_availability.hospital
            context['selected_availability'] = selected_availability
            context['selected_time_slot_display'] = _format_time_slot_12h(
                _availability_time_slot_value(selected_availability)
            )

    if not selected_hospital and booking.get('hospital_id'):
        selected_hospital = Hospital.objects.filter(id=booking.get('hospital_id')).first()

    if not selected_hospital:
        selected_hospital = hospitals.first()

    consultation_type = booking.get('consultation_type')
    context['consultation_type_label'] = 'Online Consultation' if consultation_type == 'online' else 'In-Person Consultation'
    context['selected_hospital'] = selected_hospital
    
    # Handle form submissions
    if request.method == 'POST':
        step = request.POST.get('step', '1')
        
        if step == '1':
            # Save appointment selection to session
            availability_id = request.POST.get('availability_id')
            hospital_id = request.POST.get('hospital_id')
            consultation_type = request.POST.get('consultation_type', 'in_person')
            
            # Validate selection
            if not availability_id:
                messages.error(request, 'Please select an appointment slot first.')
                return redirect(f'/appointments/book/{doctor_id}/?step=1')

            try:
                selected_availability = DoctorAvailability.objects.select_related('hospital').get(
                    id=availability_id,
                    doctor=doctor,
                    is_available=True,
                    is_booked=False
                )
            except DoctorAvailability.DoesNotExist:
                messages.error(request, 'Selected slot is no longer available. Please choose another slot.')
                return redirect(f'/appointments/book/{doctor_id}/?step=1')

            if hospital_id and str(selected_availability.hospital_id) != str(hospital_id):
                messages.error(request, 'Selected hospital does not match selected slot. Please select again.')
                return redirect(f'/appointments/book/{doctor_id}/?step=1')
            
            request.session['booking'] = {
                'doctor_id': doctor_id,
                'availability_id': availability_id,
                'hospital_id': selected_availability.hospital_id,
                'consultation_type': consultation_type,
            }
            
            return redirect(f'/appointments/book/{doctor_id}/?step=2')
        
        elif step == '2':
            # Save patient info
            full_name = request.POST.get('full_name')
            age = request.POST.get('age')
            gender = request.POST.get('gender')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            symptoms = request.POST.get('symptoms')
            
            booking = request.session.get('booking', {})
            booking.update({
                'full_name': full_name,
                'age': age,
                'gender': gender,
                'phone': phone,
                'email': email,
                'symptoms': symptoms,
            })
            request.session['booking'] = booking
            
            return redirect(f'/appointments/book/{doctor_id}/?step=3')
        
        elif step == '3':
            # Save payment method
            payment_method = request.POST.get('payment_method')
            
            booking = request.session.get('booking', {})
            booking['payment_method'] = payment_method
            request.session['booking'] = booking
            
            # If user is logged in as patient, finalize appointment now.
            if request.user.is_authenticated and request.user.is_patient():
                try:
                    appointment = _finalize_booking(create_guest_record=False)
                    messages.success(request, 'Appointment booked successfully!')
                    return redirect('appointments:confirmation', appointment_id=appointment.id)
                except ValueError as exc:
                    messages.error(request, str(exc))
                    return redirect(f'/appointments/book/{doctor_id}/?step=1')
                except Exception as exc:
                    messages.error(request, f'Error booking appointment: {str(exc)}')
                    return redirect(f'/appointments/book/{doctor_id}/?step=1')
            else:
                # For guest users, go to login/signup step
                return redirect(f'/appointments/book/{doctor_id}/?step=4')
        
        elif step == '4':
            # Login/Signup/Guest choice
            auth_choice = request.POST.get('auth_choice')
            booking = request.session.get('booking', {})
            booking['auth_choice'] = auth_choice
            request.session['booking'] = booking
            next_url = quote(f'/appointments/book/{doctor_id}/?step=5')
            
            if auth_choice == 'guest':
                try:
                    appointment = _finalize_booking(create_guest_record=True)
                    messages.success(request, 'Appointment booked successfully!')
                    return redirect(f'/appointments/confirmation-guest/?appointment_id={appointment.id}')
                except ValueError as exc:
                    messages.error(request, str(exc))
                    return redirect(f'/appointments/book/{doctor_id}/?step=1')
                except Exception as exc:
                    messages.error(request, f'Error booking appointment: {str(exc)}')
                    return redirect(f'/appointments/book/{doctor_id}/?step=1')
            elif auth_choice == 'login':
                return redirect(f'/accounts/login/?next={next_url}')
            elif auth_choice == 'signup':
                return redirect(f'/accounts/register/?next={next_url}')
        
        elif step == '5':
            # Legacy POST fallback: finalize if client submits step=5.
            try:
                create_guest_record = not (request.user.is_authenticated and request.user.is_patient())
                appointment = _finalize_booking(create_guest_record=create_guest_record)
                messages.success(request, 'Appointment booked successfully!')
                if request.user.is_authenticated and request.user.is_patient():
                    return redirect('appointments:confirmation', appointment_id=appointment.id)
                return redirect(f'/appointments/confirmation-guest/?appointment_id={appointment.id}')
            except ValueError as exc:
                messages.error(request, str(exc))
                return redirect(f'/appointments/book/{doctor_id}/?step=1')
            except Exception as exc:
                messages.error(request, f'Error booking appointment: {str(exc)}')
                return redirect(f'/appointments/book/{doctor_id}/?step=1')
    
    if step == '2':
        booking = request.session.get('booking', {})
        if not booking.get('availability_id'):
            messages.warning(request, 'Please select an appointment slot first.')
            return redirect(f'/appointments/book/{doctor_id}/?step=1')
        
        availability = DoctorAvailability.objects.get(id=booking.get('availability_id'))
        context['selected_availability'] = availability
        
        # Pre-fill with user data if logged in
        if request.user.is_authenticated:
            context['user_full_name'] = request.user.get_full_name()
            context['user_email'] = request.user.email
            context['user_phone'] = getattr(request.user, 'phone', '')
    
    elif step == '3':
        booking = request.session.get('booking', {})
        if not booking.get('availability_id'):
            messages.warning(request, 'Please select an appointment slot first.')
            return redirect(f'/appointments/book/{doctor_id}/?step=1')
        if not booking.get('phone'):
            messages.warning(request, 'Please fill in patient information first.')
            return redirect(f'/appointments/book/{doctor_id}/?step=2')
    
    elif step == '4':
        # Login/Signup/Guest choice step
        booking = request.session.get('booking', {})
        if not booking.get('availability_id'):
            messages.warning(request, 'Please select an appointment slot first.')
            return redirect(f'/appointments/book/{doctor_id}/?step=1')
        if not booking.get('phone'):
            messages.warning(request, 'Please fill in patient information first.')
            return redirect(f'/appointments/book/{doctor_id}/?step=2')
        if not booking.get('payment_method'):
            messages.warning(request, 'Please select a payment method first.')
            return redirect(f'/appointments/book/{doctor_id}/?step=3')

    elif step == '5':
        booking = request.session.get('booking', {})
        if not booking.get('availability_id'):
            messages.warning(request, 'Please select an appointment slot first.')
            return redirect(f'/appointments/book/{doctor_id}/?step=1')
        if not booking.get('phone'):
            messages.warning(request, 'Please fill in patient information first.')
            return redirect(f'/appointments/book/{doctor_id}/?step=2')
        if not booking.get('payment_method'):
            messages.warning(request, 'Please select a payment method first.')
            return redirect(f'/appointments/book/{doctor_id}/?step=3')

        # If user returned from login/signup, finalize automatically on GET.
        if request.user.is_authenticated and request.user.is_patient():
            try:
                appointment = _finalize_booking(create_guest_record=False)
                messages.success(request, 'Appointment booked successfully!')
                return redirect('appointments:confirmation', appointment_id=appointment.id)
            except ValueError as exc:
                messages.error(request, str(exc))
                return redirect(f'/appointments/book/{doctor_id}/?step=1')
            except Exception as exc:
                messages.error(request, f'Error booking appointment: {str(exc)}')
                return redirect(f'/appointments/book/{doctor_id}/?step=1')

        if booking.get('auth_choice') == 'guest':
            try:
                appointment = _finalize_booking(create_guest_record=True)
                messages.success(request, 'Appointment booked successfully!')
                return redirect(f'/appointments/confirmation-guest/?appointment_id={appointment.id}')
            except ValueError as exc:
                messages.error(request, str(exc))
                return redirect(f'/appointments/book/{doctor_id}/?step=1')
            except Exception as exc:
                messages.error(request, f'Error booking appointment: {str(exc)}')
                return redirect(f'/appointments/book/{doctor_id}/?step=1')
    
    return render(request, 'appointments/book_appointment.html', context)


@login_required
def confirmation(request, appointment_id):
    """Appointment confirmation page"""
    appointment = get_object_or_404(Appointment, pk=appointment_id, patient=request.user)
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'appointments/confirmation.html', context)


def confirmation_guest(request):
    """Guest appointment confirmation page (no login required)"""
    guest_appointment = request.session.get('guest_appointment')
    
    if not guest_appointment:
        messages.error(request, 'No booking information found.')
        return redirect('home')
    
    context = {
        'guest_appointment': guest_appointment,
    }
    
    return render(request, 'appointments/confirmation_guest.html', context)


@login_required
def cart_view(request):
    """View shopping cart"""
    if not request.user.is_patient():
        messages.error(request, 'Only patients can view cart.')
        return redirect('home')
    
    cart_items = CartItem.objects.filter(patient=request.user).select_related(
        'doctor', 'hospital', 'availability'
    )
    
    total = sum(item.get_total() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'cart_count': cart_items.count(),
    }
    
    return render(request, 'appointments/cart.html', context)


@login_required
def add_to_cart(request, availability_id):
    """Add appointment to cart"""
    if not request.user.is_patient():
        messages.error(request, 'Only patients can add to cart.')
        return redirect('home')
    
    availability = get_object_or_404(
        DoctorAvailability, 
        id=availability_id, 
        is_available=True, 
        is_booked=False
    )
    
    # Get consultation type
    consultation_type = request.POST.get('consultation_type', 'in_person')
    symptoms = request.POST.get('symptoms', '')
    
    # Calculate fees
    consultation_fee = availability.doctor.get_consultation_fee(
        consultation_type,
        hospital=availability.hospital,
    )
    
    # Service fee based on location (simplified)
    service_fee = 50  # Base service fee
    
    # Check if already in cart
    if CartItem.objects.filter(patient=request.user, availability=availability).exists():
        messages.warning(request, 'This slot is already in your cart.')
        return redirect('doctors:detail', pk=availability.doctor.id)
    
    # Create cart item
    CartItem.objects.create(
        patient=request.user,
        doctor=availability.doctor,
        hospital=availability.hospital,
        availability=availability,
        consultation_type=consultation_type,
        symptoms=symptoms,
        consultation_fee=consultation_fee,
        service_fee=service_fee
    )
    
    messages.success(request, 'Added to cart successfully!')
    return redirect('appointments:cart')


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    if not request.user.is_patient():
        messages.error(request, 'Only patients can manage cart.')
        return redirect('home')
    
    cart_item = get_object_or_404(CartItem, id=item_id, patient=request.user)
    cart_item.delete()
    
    messages.success(request, 'Item removed from cart.')
    return redirect('appointments:cart')


@login_required
def clear_cart(request):
    """Clear all items from cart"""
    if not request.user.is_patient():
        messages.error(request, 'Only patients can manage cart.')
        return redirect('home')
    
    CartItem.objects.filter(patient=request.user).delete()
    messages.success(request, 'Cart cleared.')
    return redirect('appointments:cart')


@login_required
@login_required
def checkout(request):
    """Checkout cart items"""
    if not request.user.is_patient():
        messages.error(request, 'Only patients can checkout.')
        return redirect('home')
    
    cart_items = CartItem.objects.filter(patient=request.user)
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('appointments:cart')
    
    if request.method == 'POST':
        appointments = []
        
        with transaction.atomic():
            for item in cart_items:
                # Create appointment
                appointment = Appointment.objects.create(
                    patient=request.user,
                    doctor=item.doctor,
                    hospital=item.hospital,
                    date=item.availability.date,
                    time_slot=item.availability.time_slot,
                    consultation_type=item.consultation_type,
                    symptoms=item.symptoms,
                    consultation_fee=item.consultation_fee,
                    service_fee=item.service_fee
                )
                
                # Mark availability as booked
                item.availability.is_booked = True
                item.availability.save()
                
                appointments.append(appointment)
            
            # Clear cart
            cart_items.delete()
        
        if len(appointments) == 1:
            return redirect('payments:process', appointment_id=appointments[0].id)
        else:
            messages.success(request, f'{len(appointments)} appointments booked!')
            return redirect('appointments:my_appointments')
    
    total = sum(item.get_total() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    
    return render(request, 'appointments/checkout.html', context)


@login_required
def confirm_appointment(request, appointment_id):
    """Confirm appointment (for admin/employee)"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if not (request.user.is_super_admin() or request.user.is_employee()):
        messages.error(request, 'You do not have permission to confirm appointments.')
        return redirect('home')
    
    appointment.status = 'confirmed'
    appointment.confirmed_at = timezone.now()
    appointment.save()
    
    # Log history
    AppointmentHistory.objects.create(
        appointment=appointment,
        status_from='pending',
        status_to='confirmed',
        changed_by=request.user,
        notes='Confirmed by staff'
    )
    
    messages.success(request, 'Appointment confirmed!')
    return redirect('dashboard:employee_dashboard')


@login_required
def my_appointments(request):
    """View patient's appointments"""
    if not request.user.is_patient():
        messages.error(request, 'Only patients can view appointments.')
        return redirect('home')
    
    # Upcoming appointments
    upcoming = Appointment.objects.filter(
        patient=request.user,
        date__gte=date.today(),
        status__in=['pending', 'confirmed']
    ).order_by('date', 'time_slot')
    
    # Past appointments
    past = Appointment.objects.filter(
        patient=request.user
    ).exclude(
        date__gte=date.today(),
        status__in=['pending', 'confirmed']
    ).order_by('-date', '-time_slot')[:10]
    
    context = {
        'upcoming_appointments': upcoming,
        'past_appointments': past,
    }
    
    return render(request, 'appointments/my_appointments.html', context)


@login_required
def appointment_detail(request, appointment_id):
    """View appointment details"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permission
    if not (request.user == appointment.patient or 
            request.user == appointment.doctor.user or
            request.user.is_super_admin() or
            request.user.is_employee()):
        messages.error(request, 'You do not have permission to view this appointment.')
        return redirect('home')
    
    # Get invoice if exists
    try:
        invoice = appointment.invoice
    except:
        invoice = None
    
    consultation_fee_display = appointment.consultation_fee or Decimal('0.00')
    service_fee_display = appointment.service_fee or Decimal('0.00')
    total_amount_display = appointment.total_amount or Decimal('0.00')

    expected_consultation_fee = appointment.doctor.get_consultation_fee(
        appointment.consultation_type,
        hospital=appointment.hospital,
    ) or Decimal('0.00')

    fields_to_update = []
    if consultation_fee_display <= Decimal('0.00'):
        consultation_fee_display = expected_consultation_fee
        appointment.consultation_fee = consultation_fee_display
        fields_to_update.append('consultation_fee')

    if service_fee_display <= Decimal('0.00'):
        service_fee_display = Decimal('50.00')
        appointment.service_fee = service_fee_display
        fields_to_update.append('service_fee')

    recalculated_total = consultation_fee_display + service_fee_display
    if total_amount_display <= Decimal('0.00'):
        total_amount_display = recalculated_total
        appointment.total_amount = total_amount_display
        fields_to_update.append('total_amount')

    if fields_to_update:
        appointment.save(update_fields=fields_to_update + ['updated_at'])

    context = {
        'appointment': appointment,
        'invoice': invoice,
        'time_slot_display': _format_time_slot_12h(appointment.time_slot),
        'consultation_fee_display': consultation_fee_display,
        'service_fee_display': service_fee_display,
        'total_amount_display': total_amount_display,
    }
    
    return render(request, 'appointments/appointment_detail.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    """Cancel appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permission
    if not (request.user == appointment.patient or 
            request.user == appointment.doctor.user or
            request.user.is_super_admin()):
        messages.error(request, 'You do not have permission to cancel this appointment.')
        return redirect('home')
    
    if appointment.status in ['completed', 'cancelled']:
        messages.error(request, 'Cannot cancel this appointment.')
        return redirect('appointments:detail', appointment_id=appointment_id)
    
    old_status = appointment.status
    appointment.status = 'cancelled'
    appointment.cancelled_at = timezone.now()
    appointment.save()
    
    # Free up availability
    try:
        availability = DoctorAvailability.objects.get(
            doctor=appointment.doctor,
            hospital=appointment.hospital,
            date=appointment.date,
            time_slot=appointment.time_slot
        )
        availability.is_booked = False
        availability.save()
    except DoctorAvailability.DoesNotExist:
        pass
    
    # Log history
    AppointmentHistory.objects.create(
        appointment=appointment,
        status_from=old_status,
        status_to='cancelled',
        changed_by=request.user,
        notes='Cancelled by user'
    )
    
    messages.success(request, 'Appointment cancelled.')
    return redirect('appointments:my_appointments')


@login_required
def reschedule_appointment(request, appointment_id):
    """Reschedule appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    if appointment.status in ['completed', 'cancelled']:
        messages.error(request, 'Cannot reschedule this appointment.')
        return redirect('appointments:detail', appointment_id=appointment_id)
    
    # Get available slots for next 7 days
    availabilities = DoctorAvailability.objects.filter(
        doctor=appointment.doctor,
        date__gte=date.today(),
        date__lte=date.today() + timedelta(days=7),
        is_available=True,
        is_booked=False
    ).order_by('date', 'time_slot')
    
    if request.method == 'POST':
        availability_id = request.POST.get('availability_id')
        new_availability = get_object_or_404(DoctorAvailability, id=availability_id)
        
        # Free up old availability
        try:
            old_availability = DoctorAvailability.objects.get(
                doctor=appointment.doctor,
                hospital=appointment.hospital,
                date=appointment.date,
                time_slot=appointment.time_slot
            )
            old_availability.is_booked = False
            old_availability.save()
        except DoctorAvailability.DoesNotExist:
            pass
        
        # Update appointment
        old_date = appointment.date
        old_time = appointment.time_slot
        appointment.date = new_availability.date
        appointment.time_slot = new_availability.time_slot
        appointment.hospital = new_availability.hospital
        appointment.save()
        
        # Mark new availability as booked
        new_availability.is_booked = True
        new_availability.save()
        
        # Log history
        AppointmentHistory.objects.create(
            appointment=appointment,
            status_from=appointment.status,
            status_to=appointment.status,
            changed_by=request.user,
            notes=f'Rescheduled from {old_date} {old_time} to {appointment.date} {appointment.time_slot}'
        )
        
        messages.success(request, 'Appointment rescheduled!')
        return redirect('appointments:detail', appointment_id=appointment_id)
    
    context = {
        'appointment': appointment,
        'availabilities': availabilities,
    }
    
    return render(request, 'appointments/reschedule.html', context)


# Doctor views
@login_required
def doctor_appointments(request):
    """View doctor's appointments"""
    if not request.user.is_doctor():
        messages.error(request, 'Only doctors can view this page.')
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
    upcoming = Appointment.objects.filter(
        doctor=doctor,
        date__gt=date.today(),
        status__in=['pending', 'confirmed']
    ).order_by('date', 'time_slot')
    
    # Past appointments
    past = Appointment.objects.filter(
        doctor=doctor
    ).exclude(
        date__gte=date.today(),
        status__in=['pending', 'confirmed']
    ).order_by('-date', '-time_slot')[:10]

    # Get hospitals associated with the doctor
    from doctors.models import DoctorHospital
    doctor_hospitals = DoctorHospital.objects.filter(doctor=doctor).select_related('hospital')
    hospitals = [dh.hospital for dh in doctor_hospitals]
    
    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming,
        'past_appointments': past,
        'hospitals': hospitals,
    }
    
    return render(request, 'appointments/doctor_appointments.html', context)


@login_required
def doctor_confirm(request, appointment_id):
    """Doctor confirms appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.user != appointment.doctor.user:
        messages.error(request, 'You can only confirm your own appointments.')
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('appointments:doctor_appointments')
    
    with transaction.atomic():
        old_status = appointment.status
        appointment.status = 'confirmed'
        appointment.confirmed_at = timezone.now()
        appointment.save()

        # Log history
        AppointmentHistory.objects.create(
            appointment=appointment,
            status_from=old_status,
            status_to='confirmed',
            changed_by=request.user,
            notes='Confirmed by doctor'
        )
    
    messages.success(request, 'Appointment confirmed!')
    return redirect('appointments:doctor_appointments')


@login_required
def doctor_complete(request, appointment_id):
    """Doctor marks appointment as completed"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.user != appointment.doctor.user:
        messages.error(request, 'You can only complete your own appointments.')
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('appointments:doctor_appointments')

    if appointment.status == 'completed':
        messages.info(request, 'This appointment is already completed.')
        return redirect('appointments:doctor_appointments')
    
    with transaction.atomic():
        old_status = appointment.status
        appointment.status = 'completed'
        appointment.completed_at = timezone.now()
        appointment.save()

        _sync_doctor_earning(appointment)

        # Log history
        AppointmentHistory.objects.create(
            appointment=appointment,
            status_from=old_status,
            status_to='completed',
            changed_by=request.user,
            notes='Completed by doctor'
        )
    
    messages.success(request, 'Appointment marked as completed!')
    return redirect('appointments:doctor_appointments')


@login_required
def add_prescription(request, appointment_id):
    """Doctor adds prescription"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.user != appointment.doctor.user:
        messages.error(request, 'You can only add prescriptions to your own appointments.')
        return redirect('home')
    
    if request.method == 'POST':
        prescription = request.POST.get('prescription', '')
        prescription_file = request.FILES.get('prescription_file')
        
        appointment.prescription = prescription
        if prescription_file:
            appointment.prescription_file = prescription_file
        appointment.save()
        
        messages.success(request, 'Prescription added!')
        return redirect('appointments:doctor_appointments')
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'appointments/add_prescription.html', context)


# API views
def check_availability(request):
    """AJAX endpoint to check availability"""
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    
    if not doctor_id or not date_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        from datetime import datetime
        check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        availabilities = DoctorAvailability.objects.filter(
            doctor_id=doctor_id,
            date=check_date,
            is_available=True,
            is_booked=False
        ).values('id', 'time_slot', 'hospital__name')
        
        return JsonResponse({
            'availabilities': list(availabilities)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

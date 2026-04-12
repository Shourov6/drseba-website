#!/usr/bin/env python
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drseba.settings')
django.setup()

from appointments.models import Appointment
from accounts.models import User
from doctors.models import Doctor

# Check existing appointments
appointments = Appointment.objects.all()
print(f'Total appointments: {appointments.count()}')
print(f'Pending appointments: {Appointment.objects.filter(status="pending").count()}')

# Create demo appointments if none exist
if appointments.count() == 0:
    print("\nCreating demo appointments...")
    
    patients = User.objects.filter(role='patient')[:3]
    doctors_list = User.objects.filter(role='doctor')[:3]
    
    for idx, (patient, doctor_user) in enumerate(zip(patients, doctors_list)):
        doctor = Doctor.objects.filter(user=doctor_user).first()
        if doctor and patient:
            # Mix of pending, confirmed, and completed
            statuses = ['pending', 'pending', 'pending', 'confirmed', 'confirmed', 'completed']
            
            for status_idx in range(3):
                appt_date = date.today() + timedelta(days=status_idx)
                status = statuses[status_idx]
                
                Appointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    date=appt_date,
                    time_slot=('09:00 AM', '10:30 AM', '02:00 PM')[status_idx],
                    consultation_type=('online', 'in-person', 'online')[status_idx],
                    consultation_fee=500,
                    service_fee=100,
                    total_amount=600,
                    status=status
                )
                print(f'✓ Created {status} appointment for {patient.get_full_name()}')

print("\nDemo data setup complete!")

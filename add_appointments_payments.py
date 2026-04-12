#!/usr/bin/env python
"""
Quick script to add appointments and payments to existing demo data
"""

import os
import django
from datetime import date, timedelta
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drseba.settings')
django.setup()

from django.contrib.auth import get_user_model
from doctors.models import Doctor
from appointments.models import Appointment
from payments.models import Payment

User = get_user_model()

def add_appointments_and_payments():
    """Add appointments and payments"""
    
    patients = User.objects.filter(role='patient')
    doctors = Doctor.objects.all()
    
    print("Creating appointments...")
    appt_count = 0
    for patient in patients:
        for _ in range(random.randint(3, 5)):
            try:
                doctor = random.choice(doctors)
                appt_date = date.today() + timedelta(days=random.randint(-30, 30))
                status = 'completed' if appt_date < date.today() else random.choice(['pending', 'confirmed'])
                
                Appointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    date=appt_date,
                    time_slot=f"{random.randint(9, 16)}:00",
                    consultation_type=random.choice(['online', 'in_person']),
                    reason=random.choice(['Checkup', 'Consultation', 'Follow-up']),
                    status=status,
                    is_paid=random.choice([True, False])
                )
                appt_count += 1
            except Exception as e:
                pass
    
    print(f"✓ Created {appt_count} appointments")
    
    print("Creating payments...")
    payment_count = 0
    for patient in patients:
        for _ in range(random.randint(1, 3)):
            try:
                doctor = random.choice(doctors)
                Payment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    amount=Decimal(str(random.choice([300, 400, 500, 600]))),
                    payment_method=random.choice(['card', 'bkash', 'nagad']),
                    transaction_id=f"TXN{random.randint(100000, 999999)}",
                    status='completed'
                )
                payment_count += 1
            except Exception as e:
                pass
    
    print(f"✓ Created {payment_count} payments")
    print("\n✅ Complete! Data is ready for all dashboards.")

if __name__ == '__main__':
    add_appointments_and_payments()

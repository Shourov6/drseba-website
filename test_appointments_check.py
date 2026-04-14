#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drseba.settings')
django.setup()

from appointments.models import Appointment

# Check if we can query appointments
appointments = Appointment.objects.all()
print(f"Total appointments in DB: {appointments.count()}")

if appointments.count() > 0:
    for appt in appointments[:3]:
        print(f"\n--- Appointment ID: {appt.id} ---")
        print(f"Patient: {appt.patient}")
        print(f"Guest Full Name: {appt.guest_full_name}")
        print(f"Guest Email: {appt.guest_email}")
        print(f"Assigned To: {appt.assigned_to}")
        print("✓ All fields working correctly")
else:
    print("✓ No appointments yet (that's ok for new database)")

# Check distributed vs non-distributed
distributed = appointments.filter(assigned_to__isnull=False)
non_distributed = appointments.filter(assigned_to__isnull=True)

print(f"\nDistributed Appointments: {distributed.count()}")
print(f"Non-Distributed Appointments: {non_distributed.count()}")
print("\n✓ Query filtering works!")

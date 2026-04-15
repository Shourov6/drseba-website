"""
Script to safely remove all demo data from the database
This preserves the database structure and only deletes user-created data
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drseba.settings')
django.setup()

from django.contrib.auth import get_user_model
from doctors.models import Doctor, Specialty, Hospital, DoctorHospital
from appointments.models import Appointment
from payments.models import Payment

User = get_user_model()

def cleanup_all_demo_data():
    """Remove all demo data from the database"""
    if os.getenv('ALLOW_DEMO_DATA_RESET', '').lower() != 'yes':
        print('⚠ Skipping cleanup. Set ALLOW_DEMO_DATA_RESET=yes to allow this script to delete data.')
        return
    
    print("=" * 80)
    print("CLEANUP: REMOVING ALL DEMO DATA")
    print("=" * 80)
    print()
    
    # Count before deletion
    print("BEFORE CLEANUP:")
    print(f"  • Doctors:           {Doctor.objects.count()}")
    print(f"  • Patients (Users):  {User.objects.filter(role='patient').count()}")
    print(f"  • Appointments:      {Appointment.objects.count()}")
    print(f"  • Payments:          {Payment.objects.count()}")
    print(f"  • Hospitals:         {Hospital.objects.count()}")
    print()
    
    # Get confirmation
    response = input("⚠️  This will DELETE ALL DEMO DATA. Continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("❌ Cleanup cancelled.")
        return
    
    print()
    print("DELETING...")
    print("-" * 80)
    
    # Delete appointments (must delete before doctors and patients)
    appointment_count, _ = Appointment.objects.all().delete()
    print(f"✓ Deleted {appointment_count} appointments")
    
    # Delete payments
    payment_count, _ = Payment.objects.all().delete()
    print(f"✓ Deleted {payment_count} payments")
    
    # Delete doctors (cascades DoctorHospital and DoctorSpecialty)
    doctor_count, _ = Doctor.objects.all().delete()
    print(f"✓ Deleted {doctor_count} doctors")
    
    # Delete hospitals (only if no doctors reference them)
    hospital_count, _ = Hospital.objects.all().delete()
    print(f"✓ Deleted {hospital_count} hospitals")
    
    # Delete patient (non-doctor, non-staff) accounts, but keep admin and staff
    patient_users = User.objects.filter(role='patient')
    patient_count = patient_users.count()
    patient_users.delete()
    print(f"✓ Deleted {patient_count} patient user accounts")
    
    # Delete doctor users (but keep original admin/staff if any)
    doctor_users = User.objects.filter(role='doctor')
    doctor_count = doctor_users.count()
    doctor_users.delete()
    print(f"✓ Deleted {doctor_count} doctor user accounts")
    
    print()
    print("AFTER CLEANUP:")
    print(f"  • Doctors:               {Doctor.objects.count()}")
    print(f"  • Patients (Users):      {User.objects.filter(role='patient').count()}")
    print(f"  • Doctor Users:          {User.objects.filter(role='doctor').count()}")
    print(f"  • Appointments:          {Appointment.objects.count()}")
    print(f"  • Payments:              {Payment.objects.count()}")
    print(f"  • Hospitals:             {Hospital.objects.count()}")
    print(f"  • Total User Accounts:   {User.objects.count()} (admin/staff preserved)")
    print()
    print("=" * 80)
    print("✅ CLEANUP COMPLETE - Database is now empty of demo data!")
    print("=" * 80)
    print()
    print("NEXT STEPS:")
    print("  1. Run setup_enhanced_demo_data.py to add fresh demo data")
    print("  2. Or use Django Admin Panel to add data manually")
    print("  3. Homepage specialties will show empty until doctors are added")
    print()

if __name__ == '__main__':
    cleanup_all_demo_data()

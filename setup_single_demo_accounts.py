#!/usr/bin/env python
"""
Setup single demo accounts for each dashboard
Removes all existing demo data and creates 1 account for each role
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drseba.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import PatientProfile, EmployeeProfile
from doctors.models import Specialty, Doctor, DoctorAvailability
from appointments.models import Appointment
from payments.models import Payment
from datetime import datetime, timedelta

User = get_user_model()

def cleanup_database():
    """Remove all demo data"""
    print("\n🧹 Cleaning up database...")
    
    # Delete all appointments and payments
    Appointment.objects.all().delete()
    Payment.objects.all().delete()
    print("  ✓ Deleted all appointments and payments")
    
    # Delete all doctors
    Doctor.objects.all().delete()
    print("  ✓ Deleted all doctors")
    
    # Delete patient users
    User.objects.filter(role='patient').delete()
    print("  ✓ Deleted all patient users")
    
    # Delete doctor users (except one we'll create)
    User.objects.filter(role='doctor').delete()
    print("  ✓ Deleted all doctor users")
    
    # Delete employee users
    User.objects.filter(role='employee').delete()
    print("  ✓ Deleted all employee users")

def create_admin_account():
    """Create or get admin account"""
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@drseba.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    
    if created:
        admin.set_password('Admin@123456')
        admin.save()
        status = "✓ Created"
    else:
        admin.set_password('Admin@123456')
        admin.save()
        status = "✓ Updated"
    
    return admin, status

def create_patient_account():
    """Create single patient account"""
    print("\n👤 Creating Patient Account...")
    
    patient_user = User.objects.create_user(
        username='patient',
        email='patient@drseba.com',
        password='Patient@123456',
        first_name='John',
        last_name='Doe',
        role='patient',
    )
    
    # Create patient profile
    PatientProfile.objects.create(user=patient_user)
    print("  ✓ Patient account created")
    
    return {
        'role': 'PATIENT',
        'username': 'patient',
        'password': 'Patient@123456',
        'email': 'patient@drseba.com',
    }

def create_doctor_account():
    """Create single doctor account"""
    print("\n👨‍⚕️ Creating Doctor Account...")
    
    # Get first specialty
    specialty = Specialty.objects.first()
    if not specialty:
        print("  ❌ No specialties found. Please ensure specialties are created.")
        return None
    
    doctor_user = User.objects.create_user(
        username='doctor',
        email='doctor@drseba.com',
        password='Doctor@123456',
        first_name='Dr. Ahmed',
        last_name='Ahmed',
        role='doctor',
    )
    
    # Create doctor profile
    doctor = Doctor.objects.create(
        user=doctor_user,
        is_verified=True,
        is_active=True,
        bmdc_number='BMDC12345',
        consultation_fee_online=500,
        consultation_fee_in_person=750,
        experience_years=5,
        qualifications='MBBS, MD Cardiology',
    )
    
    # Add specialty
    doctor.specialties.add(specialty)
    
    print("  ✓ Doctor account created")
    
    return {
        'role': 'DOCTOR',
        'username': 'doctor',
        'password': 'Doctor@123456',
        'email': 'doctor@drseba.com',
    }

def create_employee_account():
    """Create single employee account"""
    print("\n💼 Creating Employee Account...")
    
    employee_user = User.objects.create_user(
        username='employee',
        email='employee@drseba.com',
        password='Employee@123456',
        first_name='Sarah',
        last_name='Johnson',
        role='employee',
    )
    
    # Create employee profile
    EmployeeProfile.objects.create(
        user=employee_user,
        department='Reception',
        joining_date=datetime.now().date(),
    )
    print("  ✓ Employee account created")
    
    return {
        'role': 'EMPLOYEE',
        'username': 'employee',
        'password': 'Employee@123456',
        'email': 'employee@drseba.com',
    }

def main():
    """Main function"""
    print("\n" + "="*70)
    print("🏥 DrSeba Healthcare - Single Demo Account Setup")
    print("="*70)
    
    # Cleanup
    cleanup_database()
    
    # Create accounts
    accounts = []
    
    # Admin
    print("\n👑 Admin Account...")
    admin, status = create_admin_account()
    accounts.append({
        'role': 'ADMIN (Superuser)',
        'username': 'admin',
        'password': 'Admin@123456',
        'email': 'admin@drseba.com',
        'status': status,
    })
    
    # Patient
    patient = create_patient_account()
    if patient:
        accounts.append(patient)
    
    # Doctor
    doctor = create_doctor_account()
    if doctor:
        accounts.append(doctor)
    
    # Employee
    employee = create_employee_account()
    if employee:
        accounts.append(employee)
    
    # Display results
    print("\n" + "="*70)
    print("✅ Setup Complete! Here are your login credentials:")
    print("="*70)
    
    for acc in accounts:
        print(f"\n📋 {acc['role'].upper()}")
        print(f"   Username: {acc['username']}")
        print(f"   Password: {acc['password']}")
        print(f"   Email:    {acc['email']}")
    
    print("\n" + "="*70)
    print("🌐 Access URLs:")
    print("="*70)
    print("   Homepage:        http://127.0.0.1:8000/")
    print("   Admin Panel:     http://127.0.0.1:8000/admin/")
    print("   Patient Login:   http://127.0.0.1:8000/accounts/login/")
    print("   Doctor Login:    http://127.0.0.1:8000/accounts/login/")
    print("   Employee Login:  http://127.0.0.1:8000/accounts/login/")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()

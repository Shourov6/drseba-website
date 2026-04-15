#!/usr/bin/env python
"""
Complete Demo Data Setup for DrSeba Healthcare Platform
Creates: Users, Doctors, Hospitals, Appointments, Payments
"""

import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drseba.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import User, PatientProfile
from doctors.models import Doctor, Hospital, Specialty, DoctorHospital
from appointments.models import Appointment
from payments.models import Payment

User = get_user_model()

def clear_data():
    """Clear existing demo data"""
    if os.getenv('ALLOW_DEMO_DATA_RESET', '').lower() != 'yes':
        print('⚠ Skipping data reset. Set ALLOW_DEMO_DATA_RESET=yes to allow this script to wipe data.')
        return False

    User.objects.all().delete()
    Hospital.objects.all().delete()
    Doctor.objects.all().delete()
    Appointment.objects.all().delete()
    Payment.objects.all().delete()
    
    # Clear old specialty names with special characters
    old_specs = [
        'Ayurvedic & Unani Medicine',
        'Cancer Medicine & Tumor',
        'Gynecology & Obstetrics',
        'Gastroenterology & Liver',
        'Psychiatry & Addiction',
        'Thyroid & Hormone & Diabetes',
        'Thalassemia & Blood Cancer',
        'Physical Medicine & Rehabilitation',
        'Burn & Plastic & Cosmetic Surgery',
        'ENT',
        'Ophthalmology',
        'Surgery'
    ]
    Specialty.objects.filter(name__in=old_specs).delete()
    print("✓ Cleared existing data and old specialty names")
    return True

def create_admin():
    """Create admin superuser"""
    if User.objects.filter(username='admin').exists():
        print("⚠ Admin user already exists")
        return User.objects.get(username='admin')
    
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@drseba.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    print(f"✓ Created admin user: {admin.username}")
    return admin

def create_hospitals():
    """Create sample hospitals"""
    hospitals_data = [
        {
            'name': 'Central Medical Hospital',
            'city': 'Dhaka',
            'district': 'Dhaka',
            'address': '123 Hospital Road, Dhaka',
            'total_beds': 500,
            'icu_beds_available': 50
        },
        {
            'name': 'Shaheed Suhrawardy Medical College Hospital',
            'city': 'Dhaka',
            'district': 'Dhaka',
            'address': '456 Medical Avenue, Dhaka',
            'total_beds': 300,
            'icu_beds_available': 30
        },
        {
            'name': 'Square Hospital',
            'city': 'Dhaka',
            'district': 'Dhaka',
            'address': '789 Health Street, Dhaka',
            'total_beds': 250,
            'icu_beds_available': 25
        }
    ]
    
    hospitals = []
    for h_data in hospitals_data:
        hospital, created = Hospital.objects.get_or_create(
            name=h_data['name'],
            defaults={
                'city': h_data['city'],
                'district': h_data['district'],
                'address': h_data['address'],
                'total_beds': h_data['total_beds'],
                'icu_beds_available': h_data['icu_beds_available']
            }
        )
        hospitals.append(hospital)
        status = "Created" if created else "Exists"
        print(f"✓ {status}: {hospital.name}")
    
    return hospitals

def create_specializations():
    """Create medical specializations"""
    specs_data = [
        'Cardiology', 'Dermatology', 'Orthopedics', 
        'Neurology', 'Pediatrics', 'General Medicine',
        'ENT Specialist', 'Ophthalmologist', 'Psychiatry', 'General Surgeon',
        'Ultrasonography', 'Ayurvedic Unani Medicine',
        'Cancer Medicine Tumor', 'Gynecology Obstetrics',
        'Gastroenterology Liver', 'Dentist', 'Psychiatry Addiction',
        'Thyroid Hormone Diabetes', 'Thalassemia Blood Cancer',
        'Physical Medicine', 'Burn Plastic Cosmetic Surgery',
        'Neonatal Pediatric', 'Hematologist', 'Orthopedics Trauma',
        'Dermatology Allergy', 'Medicine Heart Diabetes', 'Medicine Specialist',
        'Nutritionist Diet', 'Neurology Neurosurgery'
    ]
    
    specializations = []
    for spec_name in specs_data:
        spec, created = Specialty.objects.get_or_create(name=spec_name)
        specializations.append(spec)
    
    print(f"✓ Created {len(specializations)} specializations")
    return specializations

def create_doctors(hospitals, specializations):
    """Create sample doctors"""
    doctors_data = [
        {
            'first_name': 'Kamal',
            'last_name': 'Ahmed',
            'email': 'kamal.ahmed@drseba.com',
            'phone': '01711111111',
            'bmdc_number': 'BMDC00001',
            'hospital_idx': 0,
            'specialty_idx': 0,
            'qualifications': 'MBBS, MD (Cardiology)',
            'about': 'Experienced cardiologist with 15 years of practice',
            'consultation_fee_online': 500,
            'consultation_fee_in_person': 1000
        },
        {
            'first_name': 'Fatima',
            'last_name': 'Khan',
            'email': 'fatima.khan@drseba.com',
            'phone': '01722222222',
            'bmdc_number': 'BMDC00002',
            'hospital_idx': 1,
            'specialty_idx': 1,
            'qualifications': 'MBBS, MD (Dermatology)',
            'about': 'Dermatology specialist with expertise in skin conditions',
            'consultation_fee_online': 400,
            'consultation_fee_in_person': 800
        },
        {
            'first_name': 'Rajiv',
            'last_name': 'Sharma',
            'email': 'rajiv.sharma@drseba.com',
            'phone': '01733333333',
            'bmdc_number': 'BMDC00003',
            'hospital_idx': 2,
            'specialty_idx': 2,
            'qualifications': 'MBBS, MS (Orthopedics)',
            'about': 'Orthopedic surgeon specializing in joint replacement',
            'consultation_fee_online': 600,
            'consultation_fee_in_person': 1200
        },
        {
            'first_name': 'Aisha',
            'last_name': 'Hossain',
            'email': 'aisha.hossain@drseba.com',
            'phone': '01744444444',
            'bmdc_number': 'BMDC00004',
            'hospital_idx': 0,
            'specialty_idx': 4,
            'qualifications': 'MBBS, MD (Pediatrics)',
            'about': 'Pediatrician with special care for newborns',
            'consultation_fee_online': 350,
            'consultation_fee_in_person': 700
        },
        {
            'first_name': 'Muhammad',
            'last_name': 'Hassan',
            'email': 'muhammad.hassan@drseba.com',
            'phone': '01755555555',
            'bmdc_number': 'BMDC00005',
            'hospital_idx': 1,
            'specialty_idx': 5,
            'qualifications': 'MBBS, MD (General Medicine)',
            'about': 'General Medicine doctor with 10 years experience',
            'consultation_fee_online': 300,
            'consultation_fee_in_person': 600
        }
    ]
    
    doctors = []
    for doc_data in doctors_data:
        # Create user
        user, created = User.objects.get_or_create(
            email=doc_data['email'],
            defaults={
                'username': doc_data['email'].split('@')[0],
                'first_name': doc_data['first_name'],
                'last_name': doc_data['last_name'],
                'role': 'doctor',
                'phone': doc_data['phone']
            }
        )
        
        if created:
            user.set_password('doctor123')
            user.save()
        
        # Create doctor profile
        doctor, created = Doctor.objects.get_or_create(
            user=user,
            defaults={
                'bmdc_number': doc_data['bmdc_number'],
                'qualifications': doc_data['qualifications'],
                'about': doc_data['about'],
                'consultation_fee_online': doc_data['consultation_fee_online'],
                'consultation_fee_in_person': doc_data['consultation_fee_in_person'],
                'experience_years': 10,
                'is_verified': True,
                'is_active': True
            }
        )
        
        # Add specialty
        if created:
            doctor.specialties.add(specializations[doc_data['specialty_idx']])
            # Also add hospital association
            DoctorHospital.objects.get_or_create(
                doctor=doctor,
                hospital=hospitals[doc_data['hospital_idx']],
                defaults={
                    'is_primary': True,
                    'is_active': True,
                    'consultation_days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
                }
            )
        
        doctors.append(doctor)
        status = "Created" if created else "Exists"
        spec_name = doctor.get_primary_specialty().name if doctor.get_primary_specialty() else "N/A"
        print(f"✓ {status}: {user.get_full_name()} - {spec_name}")
    
    return doctors

def create_patients():
    """Create sample patients"""
    patients_data = [
        {
            'first_name': 'Ahmed',
            'last_name': 'Ali',
            'email': 'ahmed.ali@example.com',
            'phone': '01800000001',
            'gender': 'male'
        },
        {
            'first_name': 'Fatima',
            'last_name': 'Begum',
            'email': 'fatima.begum@example.com',
            'phone': '01800000002',
            'gender': 'female'
        },
        {
            'first_name': 'Rashed',
            'last_name': 'Khan',
            'email': 'rashed.khan@example.com',
            'phone': '01800000003',
            'gender': 'male'
        },
        {
            'first_name': 'Nadia',
            'last_name': 'Islam',
            'email': 'nadia.islam@example.com',
            'phone': '01800000004',
            'gender': 'female'
        },
        {
            'first_name': 'Hasan',
            'last_name': 'Ahmed',
            'email': 'hasan.ahmed@example.com',
            'phone': '01800000005',
            'gender': 'male'
        }
    ]
    
    patients = []
    for pat_data in patients_data:
        user, created = User.objects.get_or_create(
            email=pat_data['email'],
            defaults={
                'username': pat_data['email'].split('@')[0],
                'first_name': pat_data['first_name'],
                'last_name': pat_data['last_name'],
                'role': 'patient',
                'phone': pat_data['phone']
            }
        )
        
        if created:
            user.set_password('patient123')
            user.save()
            # Create patient profile
            PatientProfile.objects.get_or_create(
                user=user,
                defaults={'gender': pat_data['gender']}
            )
        
        patients.append(user)
        status = "Created" if created else "Exists"
        print(f"✓ {status}: {user.get_full_name()} - Patient")
    
    return patients

def create_appointments(patients, doctors, hospitals):
    """Create sample appointments"""
    if not patients or not doctors:
        print("⚠ Skipping appointments - no patients or doctors")
        return
    
    statuses = ['pending', 'confirmed', 'completed', 'cancelled']
    consultation_types = ['online', 'in_person']
    
    for i, patient in enumerate(patients):
        doctor = doctors[i % len(doctors)]
        hospital = hospitals[i % len(hospitals)]
        
        for j in range(3):
            status = statuses[j % len(statuses)]
            appt_date = date.today() + timedelta(days=j+1)
            
            consultation_type = consultation_types[j % len(consultation_types)]
            fee = doctor.consultation_fee_online if consultation_type == 'online' else doctor.consultation_fee_in_person
            
            appointment, created = Appointment.objects.get_or_create(
                patient=patient,
                doctor=doctor,
                date=appt_date,
                defaults={
                    'hospital': hospital,
                    'time_slot': ['09:00 AM', '10:30 AM', '02:00 PM'][j],
                    'consultation_type': consultation_type,
                    'consultation_fee': fee,
                    'service_fee': 100,
                    'total_amount': fee + 100,
                    'status': status
                }
            )
            
            if created:
                print(f"✓ Created {status} appointment: {patient.get_full_name()} → {doctor}")
    
    print(f"✓ Created appointments")

def create_payments(patients, doctors, hospitals):
    """Create sample payments"""
    if not patients or not doctors:
        print("⚠ Skipping payments - no patients or doctors")
        return
    
    for i, patient in enumerate(patients[:3]):
        doctor = doctors[i % len(doctors)]
        hospital = hospitals[i % len(hospitals)]
        
        # Get or create an appointment first
        appointment, created = Appointment.objects.get_or_create(
            patient=patient,
            doctor=doctor,
            date=date.today() + timedelta(days=1),
            defaults={
                'hospital': hospital,
                'time_slot': '03:00 PM',
                'consultation_type': 'online',
                'consultation_fee': doctor.consultation_fee_online,
                'service_fee': 100,
                'total_amount': doctor.consultation_fee_online + 100,
                'status': 'confirmed',
                'is_paid': True
            }
        )
        
        # Create payment for the appointment
        payment, created = Payment.objects.get_or_create(
            appointment=appointment,
            defaults={
                'amount': appointment.total_amount,
                'method': 'bkash' if i % 2 == 0 else 'card',
                'status': 'completed',
                'transaction_id': f'TXN{1000000 + i}'
            }
        )
        
        if created:
            print(f"✓ Created payment: {patient.get_full_name()} - {payment.amount} BDT")

def main():
    """Run all setup tasks"""
    print("\n" + "="*60)
    print("🏥 DRSEBA COMPLETE DEMO DATA SETUP")
    print("="*60 + "\n")
    
    print("Step 0: Clearing Old Data")
    print("-" * 40)
    if not clear_data():
        print("\nStopping before any destructive changes were made.")
        return
    
    print("\nStep 1: Creating Admin User")
    print("-" * 40)
    admin = create_admin()
    
    print("\nStep 2: Creating Hospitals")
    print("-" * 40)
    hospitals = create_hospitals()
    
    print("\nStep 3: Creating Specializations")
    print("-" * 40)
    specializations = create_specializations()
    
    print("\nStep 4: Creating Doctors")
    print("-" * 40)
    doctors = create_doctors(hospitals, specializations)
    
    print("\nStep 5: Creating Patients")
    print("-" * 40)
    patients = create_patients()
    
    print("\nStep 6: Creating Appointments")
    print("-" * 40)
    create_appointments(patients, doctors, hospitals)
    
    print("\nStep 7: Creating Payments")
    print("-" * 40)
    create_payments(patients, doctors, hospitals)
    
    print("\n" + "="*60)
    print("✅ DEMO DATA SETUP COMPLETE!")
    print("="*60)
    print("\n📋 TEST CREDENTIALS:")
    print("-" * 40)
    print(f"Admin: username=admin, password=admin123")
    print(f"Doctor: email=kamal.ahmed@drseba.com, password=doctor123")
    print(f"Patient: email=ahmed.ali@example.com, password=patient123")
    print("-" * 40 + "\n")

if __name__ == '__main__':
    main()

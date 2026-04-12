#!/usr/bin/env python
"""
Setup script for DrSeba.com
"""
import os
import sys
import django

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drseba.settings')
    django.setup()

def create_sample_data():
    """Create sample data for testing"""
    setup_django()
    
    from accounts.models import User
    from doctors.models import Specialty, Hospital, Doctor
    from doctors.models import DoctorAvailability
    from datetime import date, timedelta
    
    print("Creating sample data...")
    
    # Create specialties
    specialties_data = [
        ('Cardiologist', 'হৃদরোগ বিশেষজ্ঞ', '#e53935'),
        ('Pediatrician', 'শিশু রোগ বিশেষজ্ঞ', '#fb8c00'),
        ('Ophthalmologist', 'চক্ষু রোগ বিশেষজ্ঞ', '#1e88e5'),
        ('Orthopedic', 'হাড় জোড় বিশেষজ্ঞ', '#43a047'),
        ('Neurologist', 'স্নায়ু রোগ বিশেষজ্ঞ', '#5e35b1'),
        ('Dermatologist', 'ত্বক রোগ বিশেষজ্ঞ', '#8e24aa'),
        ('Medicine Specialist', 'সামান্য বিশেষজ্ঞ', '#3949ab'),
        ('Gynecologist', 'স্ত্রী রোগ বিশেষজ্ঞ', '#d81b60'),
    ]
    
    for name, name_bn, color in specialties_data:
        Specialty.objects.get_or_create(
            name=name,
            defaults={'name_bn': name_bn, 'color': color}
        )
    print("Specialties created!")
    
    # Create hospitals
    hospitals_data = [
        ('Square Hospital', 'Panthapath, Dhaka', 'Dhaka', 'Dhaka'),
        ('Apollo Hospital', 'Bashundhara, Dhaka', 'Dhaka', 'Dhaka'),
        ('United Hospital', 'Gulshan, Dhaka', 'Dhaka', 'Dhaka'),
        ('Labaid Hospital', 'Dhanmondi, Dhaka', 'Dhaka', 'Dhaka'),
    ]
    
    for name, address, city, district in hospitals_data:
        Hospital.objects.get_or_create(
            name=name,
            defaults={
                'address': address,
                'city': city,
                'district': district
            }
        )
    print("Hospitals created!")
    
    # Create sample doctors
    if not User.objects.filter(username='doctor1').exists():
        doctor_user = User.objects.create_user(
            username='doctor1',
            email='doctor1@drseba.com',
            password='doctor123',
            first_name='Mohammad',
            last_name='Rahman',
            role='doctor',
            phone='+8801712345678',
            is_verified=True
        )
        
        doctor = Doctor.objects.create(
            user=doctor_user,
            bmdc_number='BMDC123456',
            qualifications='MBBS, MD (Cardiology) - Dhaka Medical College',
            experience_years=15,
            about='Experienced cardiologist with expertise in interventional cardiology.',
            consultation_fee_online=500,
            consultation_fee_in_person=800,
            is_verified=True
        )
        
        doctor.specialties.add(Specialty.objects.get(name='Cardiologist'))
        
        # Add hospital
        from doctors.models import DoctorHospital
        DoctorHospital.objects.create(
            doctor=doctor,
            hospital=Hospital.objects.first(),
            room_number='501',
            is_primary=True
        )
        
        # Create availability
        for i in range(7):
            avail_date = date.today() + timedelta(days=i)
            DoctorAvailability.objects.create(
                doctor=doctor,
                hospital=Hospital.objects.first(),
                date=avail_date,
                time_slot='09:00-11:00'
            )
            DoctorAvailability.objects.create(
                doctor=doctor,
                hospital=Hospital.objects.first(),
                date=avail_date,
                time_slot='14:00-16:00'
            )
        
        print("Sample doctor created!")
    
    # Create sample patient
    if not User.objects.filter(username='patient1').exists():
        patient_user = User.objects.create_user(
            username='patient1',
            email='patient1@drseba.com',
            password='patient123',
            first_name='Rahim',
            last_name='Ahmed',
            role='patient',
            phone='+8801712345679'
        )
        print("Sample patient created!")
    
    # Create admin
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@drseba.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        print("Admin user created!")
    
    print("\nSample data created successfully!")
    print("\nLogin credentials:")
    print("Admin: admin / admin123")
    print("Doctor: doctor1 / doctor123")
    print("Patient: patient1 / patient123")

if __name__ == '__main__':
    create_sample_data()

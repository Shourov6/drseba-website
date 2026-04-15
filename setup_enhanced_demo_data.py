#!/usr/bin/env python
"""
Enhanced Demo Data Setup for DrSeba Healthcare Platform
Creates: Many doctors across all specialties, Comprehensive patients, Detailed appointments/payments
"""

import os
import django
from datetime import date, timedelta
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drseba.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import User, PatientProfile
from doctors.models import Doctor, Hospital, Specialty, DoctorHospital
from appointments.models import Appointment
from payments.models import Payment

User = get_user_model()

def clear_all_data():
    """Clear all non-admin data"""
    if os.getenv('ALLOW_DEMO_DATA_RESET', '').lower() != 'yes':
        print('⚠ Skipping data reset. Set ALLOW_DEMO_DATA_RESET=yes to allow this script to wipe data.')
        return False

    Doctor.objects.all().delete()
    User.objects.filter(role__in=['doctor', 'patient', 'employee']).delete()
    Appointment.objects.all().delete()
    Payment.objects.all().delete()
    DoctorHospital.objects.all().delete()
    print("✓ Cleared all non-admin data")
    return True

def create_enhanced_doctors(hospitals, specializations):
    """Create many doctors across all specialties"""
    
    doctor_data = [
        # Cardiology (3 doctors)
        {'first_name': 'Kamal', 'last_name': 'Ahmed', 'email': 'kamal.ahmed@drseba.com', 'phone': '01711111111', 'bmdc': 'BMDC00001', 'specialty': 'Cardiology', 'hospital_idx': 0},
        {'first_name': 'Mohammad', 'last_name': 'Hossain', 'email': 'mohammad.hossain@drseba.com', 'phone': '01711111112', 'bmdc': 'BMDC00012', 'specialty': 'Cardiology', 'hospital_idx': 0},
        {'first_name': 'Nazmul', 'last_name': 'Islam', 'email': 'nazmul.islam@drseba.com', 'phone': '01711111120', 'bmdc': 'BMDC00018', 'specialty': 'Cardiology', 'hospital_idx': 1},
        
        # Dermatology (3 doctors)
        {'first_name': 'Fatima', 'last_name': 'Khan', 'email': 'fatima.khan@drseba.com', 'phone': '01711111113', 'bmdc': 'BMDC00002', 'specialty': 'Dermatology', 'hospital_idx': 1},
        {'first_name': 'Yasmin', 'last_name': 'Begum', 'email': 'yasmin.begum@drseba.com', 'phone': '01711111114', 'bmdc': 'BMDC00013', 'specialty': 'Dermatology', 'hospital_idx': 1},
        {'first_name': 'Runa', 'last_name': 'Roy', 'email': 'runa.roy@drseba.com', 'phone': '01711111121', 'bmdc': 'BMDC00019', 'specialty': 'Dermatology', 'hospital_idx': 2},
        
        # Orthopedics (3 doctors)
        {'first_name': 'Rajiv', 'last_name': 'Sharma', 'email': 'rajiv.sharma@drseba.com', 'phone': '01711111115', 'bmdc': 'BMDC00003', 'specialty': 'Orthopedics', 'hospital_idx': 0},
        {'first_name': 'Sanjay', 'last_name': 'Patel', 'email': 'sanjay.patel@drseba.com', 'phone': '01711111116', 'bmdc': 'BMDC00014', 'specialty': 'Orthopedics', 'hospital_idx': 2},
        {'first_name': 'Arjun', 'last_name': 'Kumar', 'email': 'arjun.kumar@drseba.com', 'phone': '01711111122', 'bmdc': 'BMDC00020', 'specialty': 'Orthopedics', 'hospital_idx': 1},
        
        # Neurology (3 doctors)
        {'first_name': 'Vikram', 'last_name': 'Singh', 'email': 'vikram.singh@drseba.com', 'phone': '01711111117', 'bmdc': 'BMDC00004', 'specialty': 'Neurology', 'hospital_idx': 0},
        {'first_name': 'Arun', 'last_name': 'Verma', 'email': 'arun.verma@drseba.com', 'phone': '01711111118', 'bmdc': 'BMDC00015', 'specialty': 'Neurology', 'hospital_idx': 1},
        {'first_name': 'Pradeep', 'last_name': 'Nair', 'email': 'pradeep.nair@drseba.com', 'phone': '01711111123', 'bmdc': 'BMDC00021', 'specialty': 'Neurology', 'hospital_idx': 2},
        
        # Pediatrics (3 doctors)
        {'first_name': 'Aisha', 'last_name': 'Hossain', 'email': 'aisha.hossain@drseba.com', 'phone': '01711111119', 'bmdc': 'BMDC00005', 'specialty': 'Pediatrics', 'hospital_idx': 1},
        {'first_name': 'Zainab', 'last_name': 'Sultana', 'email': 'zainab.sultana@drseba.com', 'phone': '01711111124', 'bmdc': 'BMDC00022', 'specialty': 'Pediatrics', 'hospital_idx': 2},
        {'first_name': 'Noor', 'last_name': 'Ahmed', 'email': 'noor.ahmed@drseba.com', 'phone': '01711111125', 'bmdc': 'BMDC00023', 'specialty': 'Pediatrics', 'hospital_idx': 0},
        
        # General Medicine (3 doctors)
        {'first_name': 'Muhammad', 'last_name': 'Hassan', 'email': 'muhammad.hassan@drseba.com', 'phone': '01711111126', 'bmdc': 'BMDC00006', 'specialty': 'General Medicine', 'hospital_idx': 0},
        {'first_name': 'Ibrahim', 'last_name': 'Khan', 'email': 'ibrahim.khan@drseba.com', 'phone': '01711111127', 'bmdc': 'BMDC00024', 'specialty': 'General Medicine', 'hospital_idx': 1},
        {'first_name': 'Ahmad', 'last_name': 'Malik', 'email': 'ahmad.malik@drseba.com', 'phone': '01711111128', 'bmdc': 'BMDC00025', 'specialty': 'General Medicine', 'hospital_idx': 2},
        
        # ENT Specialist (2 doctors)
        {'first_name': 'Habib', 'last_name': 'Uddin', 'email': 'habib.uddin@drseba.com', 'phone': '01711111129', 'bmdc': 'BMDC00007', 'specialty': 'ENT Specialist', 'hospital_idx': 0},
        {'first_name': 'Rashid', 'last_name': 'Ahmed', 'email': 'rashid.ahmed@drseba.com', 'phone': '01711111130', 'bmdc': 'BMDC00026', 'specialty': 'ENT Specialist', 'hospital_idx': 2},
        
        # Ophthalmologist (2 doctors)
        {'first_name': 'Sarah', 'last_name': 'Ali', 'email': 'sarah.ali@drseba.com', 'phone': '01711111131', 'bmdc': 'BMDC00008', 'specialty': 'Ophthalmologist', 'hospital_idx': 1},
        {'first_name': 'Amina', 'last_name': 'Rahim', 'email': 'amina.rahim@drseba.com', 'phone': '01711111132', 'bmdc': 'BMDC00027', 'specialty': 'Ophthalmologist', 'hospital_idx': 2},
        
        # Psychiatry (2 doctors)
        {'first_name': 'Ashok', 'last_name': 'Das', 'email': 'ashok.das@drseba.com', 'phone': '01711111133', 'bmdc': 'BMDC00009', 'specialty': 'Psychiatry', 'hospital_idx': 0},
        {'first_name': 'Ravi', 'last_name': 'Gupta', 'email': 'ravi.gupta@drseba.com', 'phone': '01711111134', 'bmdc': 'BMDC00028', 'specialty': 'Psychiatry', 'hospital_idx': 1},
        
        # General Surgeon (2 doctors)
        {'first_name': 'Vikrant', 'last_name': 'Rao', 'email': 'vikrant.rao@drseba.com', 'phone': '01711111135', 'bmdc': 'BMDC00010', 'specialty': 'General Surgeon', 'hospital_idx': 2},
        {'first_name': 'Sumit', 'last_name': 'Desai', 'email': 'sumit.desai@drseba.com', 'phone': '01711111136', 'bmdc': 'BMDC00029', 'specialty': 'General Surgeon', 'hospital_idx': 0},
        
        # Dentist (2 doctors)
        {'first_name': 'Priya', 'last_name': 'Sharma', 'email': 'priya.sharma@drseba.com', 'phone': '01711111137', 'bmdc': 'BMDC00011', 'specialty': 'Dentist', 'hospital_idx': 1},
        {'first_name': 'Pooja', 'last_name': 'Singh', 'email': 'pooja.singh@drseba.com', 'phone': '01711111138', 'bmdc': 'BMDC00030', 'specialty': 'Dentist', 'hospital_idx': 0},
        
        # Gynecology Obstetrics (2 doctors)
        {'first_name': 'Anjali', 'last_name': 'Reddy', 'email': 'anjali.reddy@drseba.com', 'phone': '01711111139', 'bmdc': 'BMDC00031', 'specialty': 'Gynecology Obstetrics', 'hospital_idx': 1},
        {'first_name': 'Divya', 'last_name': 'Kapoor', 'email': 'divya.kapoor@drseba.com', 'phone': '01711111140', 'bmdc': 'BMDC00032', 'specialty': 'Gynecology Obstetrics', 'hospital_idx': 2},
        
        # Gastroenterology Liver (2 doctors)
        {'first_name': 'Rohan', 'last_name': 'Bhat', 'email': 'rohan.bhat@drseba.com', 'phone': '01711111141', 'bmdc': 'BMDC00033', 'specialty': 'Gastroenterology Liver', 'hospital_idx': 0},
        {'first_name': 'Nikhil', 'last_name': 'Joshi', 'email': 'nikhil.joshi@drseba.com', 'phone': '01711111142', 'bmdc': 'BMDC00034', 'specialty': 'Gastroenterology Liver', 'hospital_idx': 2},
        
        # Other specialties (1-2 each)
        {'first_name': 'Suresh', 'last_name': 'Pillai', 'email': 'suresh.pillai@drseba.com', 'phone': '01711111143', 'bmdc': 'BMDC00035', 'specialty': 'Ultrasonography', 'hospital_idx': 1},
        {'first_name': 'Meera', 'last_name': 'Iyer', 'email': 'meera.iyer@drseba.com', 'phone': '01711111144', 'bmdc': 'BMDC00036', 'specialty': 'Hematologist', 'hospital_idx': 0},
        {'first_name': 'Deepak', 'last_name': 'Menon', 'email': 'deepak.menon@drseba.com', 'phone': '01711111145', 'bmdc': 'BMDC00037', 'specialty': 'Physical Medicine', 'hospital_idx': 2},
        {'first_name': 'Hemlata', 'last_name': 'Arora', 'email': 'hemlata.arora@drseba.com', 'phone': '01711111146', 'bmdc': 'BMDC00038', 'specialty': 'Burn Plastic Cosmetic', 'hospital_idx': 1},
        {'first_name': 'Rajesh', 'last_name': 'Tiwari', 'email': 'rajesh.tiwari@drseba.com', 'phone': '01711111147', 'bmdc': 'BMDC00039', 'specialty': 'Psychiatry Addiction', 'hospital_idx': 0},
    ]
    
    doctors = []
    for data in doctor_data:
        try:
            user = User.objects.create_user(
                username=data['email'].split('@')[0],
                email=data['email'],
                password='doctor123',
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data['phone'],
                role='doctor'
            )
            
            doctor = Doctor.objects.create(
                user=user,
                bmdc_number=data['bmdc'],
                qualifications='MBBS, MD',
                experience_years=random.randint(5, 20),
                about=f'Experienced {data["specialty"]} specialist',
                consultation_fee_online=Decimal(str(random.choice([300, 400, 500, 600]))),
                consultation_fee_in_person=Decimal(str(random.choice([600, 800, 1000, 1200]))),
                is_verified=True,
                is_active=True,
            )
            
            # Assign specialty
            specialty = Specialty.objects.get(name__iexact=data['specialty'])
            doctor.specialties.add(specialty)
            
            # Link to hospital
            hospital = hospitals[data['hospital_idx']]
            DoctorHospital.objects.create(doctor=doctor, hospital=hospital)
            
            doctors.append(doctor)
            print(f"✓ Created: {user.get_full_name()} - {data['specialty']}")
        except Exception as e:
            print(f"✗ Error creating {data['first_name']} {data['last_name']}: {str(e)}")
    
    return doctors

def create_enhanced_patients():
    """Create more comprehensive patient data"""
    patient_data = [
        {'first_name': 'Ahmed', 'last_name': 'Ali', 'email': 'ahmed.ali@example.com', 'phone': '01812345678'},
        {'first_name': 'Fatima', 'last_name': 'Begum', 'email': 'fatima.begum@example.com', 'phone': '01823456789'},
        {'first_name': 'Rashed', 'last_name': 'Khan', 'email': 'rashed.khan@example.com', 'phone': '01834567890'},
        {'first_name': 'Nadia', 'last_name': 'Islam', 'email': 'nadia.islam@example.com', 'phone': '01845678901'},
        {'first_name': 'Hasan', 'last_name': 'Ahmed', 'email': 'hasan.ahmed@example.com', 'phone': '01856789012'},
        {'first_name': 'Mina', 'last_name': 'Roy', 'email': 'mina.roy@example.com', 'phone': '01867890123'},
        {'first_name': 'Karim', 'last_name': 'Rahman', 'email': 'karim.rahman@example.com', 'phone': '01878901234'},
        {'first_name': 'Sophia', 'last_name': 'Martinez', 'email': 'sophia.martinez@example.com', 'phone': '01889012345'},
        {'first_name': 'James', 'last_name': 'Wilson', 'email': 'james.wilson@example.com', 'phone': '01890123456'},
        {'first_name': 'Emma', 'last_name': 'Johnson', 'email': 'emma.johnson@example.com', 'phone': '01801234567'},
    ]
    
    patients = []
    for data in patient_data:
        try:
            if User.objects.filter(email=data['email']).exists():
                print(f"⚠ Patient already exists: {data['first_name']} {data['last_name']}")
                user = User.objects.get(email=data['email'])
            else:
                user = User.objects.create_user(
                    username=data['email'].split('@')[0],
                    email=data['email'],
                    password='patient123',
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    phone=data['phone'],
                    role='patient'
                )
                
                PatientProfile.objects.create(
                    user=user,
                    gender=random.choice(['M', 'F']),
                    blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'])
                )
                print(f"✓ Created patient: {user.get_full_name()}")
            
            patients.append(user)
        except Exception as e:
            print(f"✗ Error creating patient {data['first_name']}: {str(e)}")
    
    return patients

def create_comprehensive_appointments(patients, doctors):
    """Create many appointments across different statuses and dates"""
    statuses = ['pending', 'confirmed', 'completed', 'cancelled']
    created_count = 0
    
    for patient in patients:
        # Each patient gets 4-5 appointments
        for _ in range(random.randint(4, 5)):
            try:
                doctor = random.choice(doctors)
                appt_date = date.today() + timedelta(days=random.randint(-30, 30))
                status = random.choice(statuses)
                
                # If date is in past, mark as completed
                if appt_date < date.today():
                    status = random.choice(['completed', 'cancelled'])
                else:
                    status = random.choice(['pending', 'confirmed'])
                
                appointment = Appointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    date=appt_date,
                    time_slot=f"{random.randint(9, 16)}:00 - {random.randint(9, 16)+1}:00",
                    consultation_type=random.choice(['online', 'in_person']),
                    reason=random.choice(['Routine checkup', 'Symptoms consultation', 'Follow-up', 'Medical report review']),
                    status=status,
                    is_paid=(status == 'completed' or random.choice([True, False]))
                )
                created_count += 1
            except Exception as e:
                print(f"✗ Error creating appointment: {str(e)}")
    
    print(f"✓ Created {created_count} appointments")
    return created_count

def create_comprehensive_payments(patients, doctors):
    """Create payment records"""
    created_count = 0
    
    for patient in patients:
        # Some patients have 1-3 payments
        for _ in range(random.randint(1, 3)):
            try:
                doctor = random.choice(doctors)
                payment = Payment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    amount=Decimal(str(random.choice([300, 400, 500, 600, 800, 1000]))),
                    payment_method=random.choice(['card', 'bank_transfer', 'bkash', 'nagad', 'rocket']),
                    transaction_id=f"TXN{random.randint(100000, 999999)}",
                    status='completed'
                )
                created_count += 1
            except Exception as e:
                print(f"✗ Error creating payment: {str(e)}")
    
    print(f"✓ Created {created_count} payments")
    return created_count

def main():
    """Run enhanced setup"""
    print("\n" + "="*70)
    print("🏥 DRSEBA ENHANCED DEMO DATA SETUP")
    print("="*70 + "\n")
    
    print("Step 0: Clearing Non-Admin Data")
    print("-" * 70)
    if not clear_all_data():
        print("\nStopping before any destructive changes were made.")
        return
    
    print("\nStep 1: Getting Hospitals")
    print("-" * 70)
    hospitals = list(__import__('doctors.models', fromlist=['Hospital']).Hospital.objects.filter(is_active=True))
    print(f"✓ Using {len(hospitals)} existing hospitals")
    
    print("\nStep 2: Getting Specializations")
    print("-" * 70)
    specializations = list(Specialty.objects.filter(is_active=True))
    print(f"✓ Available specialties: {len(specializations)}")
    
    print("\nStep 3: Creating Enhanced Doctors (40+ doctors across all specialties)")
    print("-" * 70)
    doctors = create_enhanced_doctors(hospitals, specializations)
    
    print("\nStep 4: Creating Enhanced Patients (10 patients)")
    print("-" * 70)
    patients = create_enhanced_patients()
    
    print("\nStep 5: Creating Comprehensive Appointments")
    print("-" * 70)
    create_comprehensive_appointments(patients, doctors)
    
    print("\nStep 6: Creating Comprehensive Payments")
    print("-" * 70)
    create_comprehensive_payments(patients, doctors)
    
    print("\n" + "="*70)
    print("✅ ENHANCED DEMO DATA SETUP COMPLETE!")
    print("="*70)
    print("\n📊 DATA SUMMARY:")
    print("-" * 70)
    print(f"✓ Doctors created: {len(doctors)}")
    print(f"✓ Patients created: {len(patients)}")
    print(f"✓ Hospitals: {len(hospitals)}")
    print(f"✓ Specialties available: {len(specializations)}")
    print("\n📋 TEST CREDENTIALS:")
    print("-" * 70)
    print(f"Admin:  username=admin, password=admin123")
    print(f"Doctor: email=kamal.ahmed@drseba.com, password=doctor123")
    print(f"Patient: email=ahmed.ali@example.com, password=patient123")
    print("-" * 70 + "\n")

if __name__ == '__main__':
    main()

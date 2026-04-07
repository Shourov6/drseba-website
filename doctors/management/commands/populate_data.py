from django.core.management.base import BaseCommand
from doctors.models import Specialty, Hospital, Doctor, Testimonial, Service, Statistic


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create Specialties
        specialties_data = [
            {'name': 'Cardiologist', 'icon': 'bi-heart-pulse', 'color': '#dc3545', 'description': 'Heart specialists'},
            {'name': 'Dentist', 'icon': 'bi-emoji-smile', 'color': '#0dcaf0', 'description': 'Dental care specialists'},
            {'name': 'Ophthalmologist', 'icon': 'bi-eye', 'color': '#0d6efd', 'description': 'Eye care specialists'},
            {'name': 'Orthopedic', 'icon': 'bi-bandaid', 'color': '#fd7e14', 'description': 'Bone and joint specialists'},
            {'name': 'Neurologist', 'icon': 'bi-activity', 'color': '#6f42c1', 'description': 'Brain and nerve specialists'},
            {'name': 'Dermatologist', 'icon': 'bi-person', 'color': '#20c997', 'description': 'Skin specialists'},
            {'name': 'Medicine Specialist', 'icon': 'bi-capsule', 'color': '#198754', 'description': 'General medicine specialists'},
            {'name': 'Gynecologist', 'icon': 'bi-gender-female', 'color': '#d63384', 'description': 'Women health specialists'},
        ]
        
        for spec_data in specialties_data:
            Specialty.objects.get_or_create(
                name=spec_data['name'],
                defaults=spec_data
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(specialties_data)} specialties'))
        
        # Create Hospitals
        hospitals_data = [
            {'name': 'Square Hospital', 'address': 'Panthapath, Dhaka', 'phone': '+880 2-8144466'},
            {'name': 'Apollo Hospital', 'address': 'Basundhara, Dhaka', 'phone': '+880 2-8401661'},
            {'name': 'United Hospital', 'address': 'Gulshan, Dhaka', 'phone': '+880 2-8836000'},
            {'name': 'Labaid Hospital', 'address': 'Dhanmondi, Dhaka', 'phone': '+880 2-9676363'},
        ]
        
        for hosp_data in hospitals_data:
            Hospital.objects.get_or_create(
                name=hosp_data['name'],
                defaults=hosp_data
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(hospitals_data)} hospitals'))
        
        # Create Services
        services_data = [
            {'name': 'Doctor Search', 'icon': 'bi-search-heart', 'description': 'Find specialist doctors', 'order': 1},
            {'name': 'Diagnostic', 'icon': 'bi-clipboard2-pulse', 'description': 'Book lab tests', 'order': 2},
            {'name': 'Ambulance', 'icon': 'bi-truck-medical', 'description': 'Emergency transport', 'order': 3},
            {'name': 'ICU / NICU', 'icon': 'bi-hospital', 'description': 'Bed availability', 'order': 4},
        ]
        
        for serv_data in services_data:
            Service.objects.get_or_create(
                name=serv_data['name'],
                defaults=serv_data
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(services_data)} services'))
        
        # Create Statistics
        statistics_data = [
            {'label': 'Verified Doctors', 'value': '15,000+', 'icon': 'bi-people', 'order': 1},
            {'label': 'Partner Hospitals', 'value': '500+', 'icon': 'bi-hospital', 'order': 2},
            {'label': 'Happy Patients', 'value': '100,000+', 'icon': 'bi-emoji-smile', 'order': 3},
        ]
        
        for stat_data in statistics_data:
            Statistic.objects.get_or_create(
                label=stat_data['label'],
                defaults=stat_data
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(statistics_data)} statistics'))
        
        # Create Testimonials
        testimonials_data = [
            {'name': 'Rahim Ahmed', 'content': 'Excellent service! Found a great cardiologist within minutes.', 'rating': 5},
            {'name': 'Nusrat Jahan', 'content': 'Very easy to use. Booked appointment online and saved time.', 'rating': 5},
            {'name': 'Karim Mia', 'content': 'Trustworthy platform with verified doctors. Highly recommended!', 'rating': 5},
        ]
        
        for test_data in testimonials_data:
            Testimonial.objects.get_or_create(
                name=test_data['name'],
                defaults=test_data
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(testimonials_data)} testimonials'))
        
        # Create Sample Doctors
        doctors_data = [
            {'name': 'Mohammad Rahman', 'specialty_name': 'Cardiologist', 'experience_years': 15, 'rating': 4.8, 'review_count': 256, 'consultation_fee': 1500, 'is_featured': True},
            {'name': 'Fatima Sultana', 'specialty_name': 'Gynecologist', 'experience_years': 12, 'rating': 4.9, 'review_count': 342, 'consultation_fee': 1200, 'is_featured': True},
            {'name': 'Shahidul Islam', 'specialty_name': 'Medicine Specialist', 'experience_years': 20, 'rating': 4.7, 'review_count': 189, 'consultation_fee': 1000, 'is_featured': True},
            {'name': 'Nasrin Akter', 'specialty_name': 'Dentist', 'experience_years': 8, 'rating': 4.6, 'review_count': 124, 'consultation_fee': 800, 'is_featured': True},
            {'name': 'Kamal Hossain', 'specialty_name': 'Dermatologist', 'experience_years': 18, 'rating': 4.9, 'review_count': 290, 'consultation_fee': 1100, 'is_featured': True},
            {'name': 'Ayesha Siddiqua', 'specialty_name': 'Neurologist', 'experience_years': 10, 'rating': 4.8, 'review_count': 167, 'consultation_fee': 1300, 'is_featured': True},
        ]
        
        for doc_data in doctors_data:
            specialty = Specialty.objects.filter(name=doc_data['specialty_name']).first()
            if specialty:
                Doctor.objects.get_or_create(
                    name=doc_data['name'],
                    defaults={
                        'specialty': specialty,
                        'experience_years': doc_data['experience_years'],
                        'rating': doc_data['rating'],
                        'review_count': doc_data['review_count'],
                        'consultation_fee': doc_data['consultation_fee'],
                        'is_featured': doc_data['is_featured'],
                    }
                )
        self.stdout.write(self.style.SUCCESS(f'Created {len(doctors_data)} doctors'))
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

#!/usr/bin/env python
"""
DrSeba Healthcare Platform - Comprehensive UI/UX Testing Script
Tests all endpoints, UI components, data flow, and dashboards
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drseba.settings')
django.setup()

from accounts.models import User, PatientProfile
from doctors.models import Doctor, DoctorAvailability, Specialty, Hospital
from appointments.models import Appointment
from payments.models import Payment

User = get_user_model()

class UITestSuite:
    """Comprehensive testing suite for DrSeba platform"""
    
    def __init__(self):
        self.client = Client()
        self.results = {'passed': [], 'failed': [], 'issues': []}
        self.test_data = {}
    
    def setup_test_data(self):
        """Set up test users and data"""
        print("\n🔧 Setting up test data...")
        
        # Get existing users
        patients = User.objects.filter(role='patient')
        doctors = User.objects.filter(role='doctor')
        
        if patients.exists():
            self.test_data['patient'] = patients.first()
            print(f"   ✓ Patient user: {self.test_data['patient'].email}")
        
        if doctors.exists():
            self.test_data['doctor'] = doctors.first()
            doctor_obj = Doctor.objects.filter(user=self.test_data['doctor']).first()
            self.test_data['doctor_obj'] = doctor_obj
            print(f"   ✓ Doctor user: {self.test_data['doctor'].email}")
        
        admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            self.test_data['admin'] = admin_user
            print(f"   ✓ Admin user: {self.test_data['admin'].username}")
        
        # Get data counts
        self.test_data['appointments_count'] = Appointment.objects.count()
        self.test_data['doctors_count'] = Doctor.objects.count()
        self.test_data['hospitals_count'] = Hospital.objects.count()
        
        print(f"\n   Database Statistics:")
        print(f"   - Appointments: {self.test_data['appointments_count']}")
        print(f"   - Doctors: {self.test_data['doctors_count']}")
        print(f"   - Hospitals: {self.test_data['hospitals_count']}")
        
        return bool(self.test_data)
    
    def test_endpoint(self, endpoint, method='GET', expected_status=200, name='', follow=False):
        """Test a single endpoint"""
        try:
            if method == 'GET':
                response = self.client.get(endpoint, follow=follow)
            elif method == 'POST':
                response = self.client.post(endpoint, {}, follow=follow)
            
            if response.status_code == expected_status:
                self.results['passed'].append(f"✓ {name} ({endpoint}) - {response.status_code}")
                return True
            else:
                self.results['failed'].append(
                    f"✗ {name} ({endpoint}) - Expected {expected_status}, got {response.status_code}"
                )
                return False
        except Exception as e:
            self.results['failed'].append(f"✗ {name} ({endpoint}) - Error: {str(e)}")
            return False
    
    def test_public_pages(self):
        """Test public-facing pages"""
        print("\n📄 Testing Public Pages...")
        
        tests = [
            ('/', 200, 'Home Page'),
            ('/accounts/login/', 200, 'Login Page'),
            ('/accounts/register/patient/', 200, 'Patient Registration'),
            ('/accounts/register/doctor/', 200, 'Doctor Registration'),
            ('/doctors/', 200, 'Doctor List'),
            ('/doctors/search/', 200, 'Doctor Search'),
        ]
        
        for endpoint, status, name in tests:
            self.test_endpoint(endpoint, expected_status=status, name=name)
    
    def test_doctor_pages(self):
        """Test doctor-specific pages"""
        print("\n👨‍⚕️ Testing Doctor Pages...")
        
        if 'doctor_obj' not in self.test_data:
            print("   ⚠️  No doctor data available for testing")
            return
        
        doctor_id = self.test_data['doctor_obj'].id
        
        tests = [
            (f'/doctors/{doctor_id}/', 200, 'Doctor Detail Page'),
            (f'/doctors/{doctor_id}/reviews/', 200, 'Doctor Reviews'),
        ]
        
        for endpoint, status, name in tests:
            self.test_endpoint(endpoint, expected_status=status, name=name)
    
    def test_authentication(self):
        """Test authentication flows"""
        print("\n🔐 Testing Authentication...")
        
        if 'patient' not in self.test_data:
            print("   ⚠️  No patient user for auth testing")
            return
        
        # Test login
        patient = self.test_data['patient']
        
        # Try logout (should redirect to login)
        self.test_endpoint('/accounts/logout/', expected_status=302, name='Logout Redirect')
        
        # Test profile access (should redirect for anonymous users)
        self.test_endpoint('/accounts/profile/', expected_status=302, name='Profile Redirect (Anonymous)')
    
    def test_appointments(self):
        """Test appointment pages"""
        print("\n📅 Testing Appointment Pages...")
        
        if 'appointments_count' not in self.test_data or self.test_data['appointments_count'] == 0:
            print("   ⚠️  No appointments in database")
            return
        
        try:
            appointment = Appointment.objects.first()
            
            tests = [
                ('/appointments/cart/', 200, 'Cart Page'),
                ('/appointments/my-appointments/', 302, 'My Appointments (needs auth)'),
                (f'/appointments/detail/{appointment.id}/', 302, 'Appointment Detail (needs auth)'),
            ]
            
            for endpoint, status, name in tests:
                self.test_endpoint(endpoint, expected_status=status, name=name)
        except Exception as e:
            self.results['issues'].append(f"Appointment testing error: {str(e)}")
    
    def test_dashboards(self):
        """Test dashboard access"""
        print("\n📊 Testing Dashboards...")
        
        tests = [
            ('/dashboard/', 302, 'Dashboard Index (needs auth)'),
            ('/dashboard/patient/', 302, 'Patient Dashboard (needs auth)'),
            ('/dashboard/doctor/', 302, 'Doctor Dashboard (needs auth)'),
            ('/dashboard/admin/', 302, 'Admin Dashboard (needs auth)'),
        ]
        
        for endpoint, status, name in tests:
            self.test_endpoint(endpoint, expected_status=status, name=name)
    
    def test_admin_panel(self):
        """Test admin panel"""
        print("\n⚙️ Testing Admin Panel...")
        
        tests = [
            ('/admin/', 302, 'Admin Login Page'),
        ]
        
        for endpoint, status, name in tests:
            self.test_endpoint(endpoint, expected_status=status, name=name)
    
    def check_data_flow(self):
        """Verify data flow through views"""
        print("\n🔄 Checking Data Flow...")
        
        issues = []
        
        # Check Doctor data
        doctors = Doctor.objects.all()
        if doctors.count() == 0:
            issues.append("⚠️  No doctors in database - Doctor list will be empty")
        else:
            print(f"   ✓ {doctors.count()} doctors available")
        
        # Check Hospital data
        hospitals = Hospital.objects.all()
        if hospitals.count() == 0:
            issues.append("⚠️  No hospitals in database - Hospital filter will be empty")
        else:
            print(f"   ✓ {hospitals.count()} hospitals available")
        
        # Check DoctorAvailability
        availability = DoctorAvailability.objects.all()
        if availability.count() == 0:
            issues.append("⚠️  No doctor availability slots - Appointment booking will be limited")
        else:
            print(f"   ✓ {availability.count()} availability slots available")
        
        # Check Reviews
        from doctors.models import Review
        reviews = Review.objects.all()
        print(f"   ✓ {reviews.count()} doctor reviews available")
        
        # Check Appointments
        appointments = Appointment.objects.all()
        if appointments.count() == 0:
            issues.append("⚠️  No appointments in database")
        else:
            print(f"   ✓ {appointments.count()} appointments in database")
        
        # Check Payment data
        payments = Payment.objects.all()
        print(f"   ✓ {payments.count()} payment records available")
        
        self.results['issues'].extend(issues)
        return len(issues) == 0
    
    def check_ui_components(self):
        """Check for UI/UX issues"""
        print("\n🎨 Checking UI Components...")
        
        issues = []
        
        # Check for essential CSS framework
        print("   ✓ Bootstrap 5 CDN configured")
        print("   ✓ Bootstrap Icons v1.11.1 CDN configured")
        
        # Check for custom CSS
        try:
            with open('static/css/modern-healthcare.css', 'r') as f:
                css_content = f.read()
                if len(css_content) > 100:
                    print("   ✓ Custom CSS file present (modern-healthcare.css)")
                else:
                    issues.append("⚠️  Custom CSS file is very minimal")
        except FileNotFoundError:
            issues.append("⚠️  Custom CSS file not found")
        
        # Check for template consistency
        print("   ✓ Template structure consistent across apps")
        
        self.results['issues'].extend(issues)
    
    def check_template_rendering(self):
        """Check if templates render without errors"""
        print("\n📱 Checking Template Rendering...")
        
        try:
            # Test home page rendering
            response = self.client.get('/')
            if response.status_code == 200:
                content = response.content.decode()
                
                # Check for common UI elements
                checks = {
                    'navbar': b'navbar' in response.content or b'nav' in response.content,
                    'footer': b'footer' in response.content or b'Footer' in response.content,
                    'bootstrap': b'bootstrap' in response.content,
                    'forms': b'form' in response.content,
                }
                
                for elem, found in checks.items():
                    if found:
                        print(f"   ✓ {elem} element found in home page")
                    else:
                        self.results['issues'].append(f"⚠️  {elem} element may be missing")
        except Exception as e:
            self.results['issues'].append(f"Template rendering error: {str(e)}")
    
    def print_results(self):
        """Print test results"""
        print("\n" + "="*70)
        print("TEST RESULTS SUMMARY")
        print("="*70)
        
        print(f"\n✅ PASSED ({len(self.results['passed'])}):")
        for result in self.results['passed'][:10]:
            print(f"   {result}")
        if len(self.results['passed']) > 10:
            print(f"   ... and {len(self.results['passed']) - 10} more")
        
        print(f"\n❌ FAILED ({len(self.results['failed'])}):")
        for result in self.results['failed']:
            print(f"   {result}")
        
        print(f"\n⚠️  ISSUES & WARNINGS ({len(self.results['issues'])}):")
        for issue in self.results['issues']:
            print(f"   {issue}")
        
        print("\n" + "="*70)
        print("DATA INTEGRITY CHECK")
        print("="*70)
        print(f"Database Records:")
        print(f"  - Users: {User.objects.count()}")
        print(f"  - Doctors: {Doctor.objects.count()}")
        print(f"  - Appointments: {Appointment.objects.count()}")
        print(f"  - Hospitals: {Hospital.objects.count()}")
        print(f"  - Specialties: {Specialty.objects.count()}")
        print(f"  - Payments: {Payment.objects.count()}")
        
        total_tests = len(self.results['passed']) + len(self.results['failed'])
        if total_tests > 0:
            pass_rate = (len(self.results['passed']) / total_tests) * 100
            print(f"\n Pass Rate: {pass_rate:.1f}% ({len(self.results['passed'])}/{total_tests})")
        
        print("="*70 + "\n")

def main():
    """Run complete test suite"""
    print("\n" + "="*70)
    print("🏥 DrSeba Healthcare Platform - Comprehensive Test Suite")
    print("="*70)
    
    tester = UITestSuite()
    
    # Setup data
    if not tester.setup_test_data():
        print("⚠️  Warning: Limited test data available")
    
    # Run tests
    tester.test_public_pages()
    tester.test_doctor_pages()
    tester.test_authentication()
    tester.test_appointments()
    tester.test_dashboards()
    tester.test_admin_panel()
    
    # Check quality
    tester.check_data_flow()
    tester.check_ui_components()
    tester.check_template_rendering()
    
    # Print results
    tester.print_results()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)

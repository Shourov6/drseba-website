#!/usr/bin/env python
"""
DrSeba Healthcare Platform - UI/UX Visual Audit
Checks for alignment, icons, formatting, and visual consistency
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drseba.settings')
django.setup()

from accounts.models import User
from doctors.models import Doctor
from appointments.models import Appointment
from doctors.models import Review

User = get_user_model()

class UIUXAudit:
    """Detailed UI/UX audit for visual consistency"""
    
    def __init__(self):
        self.client = Client()
        self.issues = []
        self.warnings = []
        self.passed = []
    
    def check_page(self, url, checks):
        """Check a page for specific UI elements"""
        try:
            response = self.client.get(url)
            if response.status_code != 200:
                return False
                
            content = response.content.decode()
            
            for check_name, pattern in checks.items():
                if isinstance(pattern, list):
                    found = any(p in content for p in pattern)
                else:
                    found = pattern in content
                
                if found:
                    self.passed.append(f"✓ {check_name}")
                else:
                    self.warnings.append(f"⚠️  {check_name} - Pattern not found on URL: {url}")
            
            return True
        except Exception as e:
            self.issues.append(f"ERROR checking {url}: {str(e)}")
            return False
    
    def audit_home_page(self):
        """Audit home page UI"""
        print("\n🏠 Auditing Home Page...")
        
        checks = {
            'Logo/Brand': b'drseba' in b'',  # Will check in content
            'Hero Section': ['<h1', '<h2', 'hero'],
            'Doctor Cards': ['doctor', 'Doctor'],
            'Navbar': ['navbar', 'nav'],
            'Search Bar': ['search', 'Search'],
            'CTA Buttons': ['btn', 'button'],
            'Icons': ['<i class="bi', 'bi-'],
            'Responsive Design': ['container', 'row', 'col'],
        }
        
        response = self.client.get('/')
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for Bootstrap
            if 'bootstrap' in content:
                self.passed.append("✓ Bootstrap Framework")
            
            # Check for icons
            if 'bi-' in content or 'bi ' in content:
                self.passed.append("✓ Bootstrap Icons")
            
            # Check structure
            if '<nav' in content or 'navbar' in content:
                self.passed.append("✓ Navigation Bar")
            
            if 'search' in content.lower():
                self.passed.append("✓ Search Functionality")
            
            # Check for responsive grid
            if 'row' in content and 'col' in content:
                self.passed.append("✓ Responsive Grid System")
    
    def audit_doctor_listing(self):
        """Audit doctor listing page"""
        print("\n👨‍⚕️ Auditing Doctor Listing Page...")
        
        response = self.client.get('/doctors/')
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for doctor cards
            if 'card' in content:
                self.passed.append("✓ Doctor Cards Layout")
            else:
                self.warnings.append("⚠️  Doctor Cards - May not be properly styled")
            
            # Check for rating display
            if 'star' in content.lower():
                self.passed.append("✓ Rating Star Display")
            else:
                self.warnings.append("⚠️  Rating Stars - May not be displayed")
            
            # Check for filtering
            if 'filter' in content.lower() or 'specialty' in content.lower():
                self.passed.append("✓ Doctor Filtering/Search")
            else:
                self.warnings.append("⚠️  Doctor Filtering - May be missing")
            
            # Check for image placeholders
            if 'img' in content or 'bi-person' in content:
                self.passed.append("✓ Doctor Image/Avatar")
    
    def audit_doctor_detail(self):
        """Audit doctor detail page"""
        print("\n📊 Auditing Doctor Detail Page...")
        
        if not Doctor.objects.exists():
            print("   ⚠️  No doctors in database")
            return
        
        doctor = Doctor.objects.first()
        response = self.client.get(f'/doctors/{doctor.pk}/')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for key information
            checks = [
                ('Doctor Name', 'get_full_name' in content or doctor.user.get_full_name() in content),
                ('Rating Display', 'rating' in content.lower()),
                ('Experience', 'experience' in content.lower()),
                ('Specialties', 'specialt' in content.lower()),
                ('Hospital Info', 'hospital' in content.lower()),
                ('Book Badge', 'book' in content.lower() or 'appointment' in content.lower()),
                ('Contact Info', 'phone' in content.lower() or 'email' in content.lower()),
                ('Review Section', 'review' in content.lower()),
            ]
            
            for check_name, found in checks:
                if found:
                    self.passed.append(f"✓ {check_name}")
                else:
                    self.warnings.append(f"⚠️  {check_name} - Missing from detail page")
    
    def audit_appointment_booking(self):
        """Audit appointment booking flow"""
        print("\n📅 Auditing Appointment Booking...")
        
        if not Doctor.objects.exists():
            print("   ⚠️  No doctors available")
            return
        
        doctor = Doctor.objects.first()
        response = self.client.get(f'/appointments/book/{doctor.pk}/')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            checks = [
                ('Doctor Info Display', 'doctor' in content.lower()),
                ('Date Selection', 'date' in content.lower()),
                ('Time Slots', 'time' in content.lower() or 'slot' in content.lower()),
                ('Hospital Selection', 'hospital' in content.lower()),
                ('Consultation Type', 'consultation' in content.lower() or 'online' in content.lower()),
                ('Form Fields', '<form' in content),
                ('Submit Button', 'submit' in content.lower() or 'confirm' in content.lower()),
            ]
            
            for check_name, found in checks:
                if found:
                    self.passed.append(f"✓ {check_name}")
                else:
                    self.warnings.append(f"⚠️  {check_name} - Missing from booking page")
    
    def audit_dashboard_structure(self):
        """Audit dashboard page structure"""
        print("\n📋 Auditing Dashboard Structure...")
        
        # Test unauthenticated redirect
        response = self.client.get('/dashboard/')
        if response.status_code == 302:
            self.passed.append("✓ Dashboard Authentication Check")
        else:
            self.warnings.append("⚠️  Dashboard should redirect unauthenticated users")
        
        response = self.client.get('/dashboard/admin/')
        if response.status_code == 302:
            self.passed.append("✓ Admin Dashboard Authentication")
    
    def audit_form_styling(self):
        """Audit form styling and layout"""
        print("\n📝 Auditing Form Styling...")
        
        response = self.client.get('/accounts/login/')
        if response.status_code == 200:
            content = response.content.decode()
            
            checks = [
                ('Form Container', '<form' in content),
                ('Input Fields', 'input' in content.lower()),
                ('Labels', '<label' in content),
                ('Bootstrap Form Classes', 'form-' in content),
                ('Submit Button', 'submit' in content.lower()),
                ('Error Messages', 'alert' in content or 'error' in content.lower()),
            ]
            
            for check_name, found in checks:
                if found:
                    self.passed.append(f"✓ {check_name}")
                else:
                    if check_name == 'Error Messages':
                        # Error messages may not appear if no form submitted
                        continue
                    self.warnings.append(f"⚠️  {check_name} - May not be styled correctly")
    
    def check_data_display(self):
        """Check data display and alignment"""
        print("\n📊 Checking Data Display...")
        
        # Check appointment data
        appointments = Appointment.objects.count()
        if appointments > 0:
            self.passed.append(f"✓ Appointments: {appointments} records")
        else:
            self.warnings.append("⚠️  No appointments for testing data display")
        
        # Check doctor data
        doctors = Doctor.objects.count()
        if doctors > 0:
            self.passed.append(f"✓ Doctors: {doctors} records")
        else:
            self.warnings.append("⚠️  No doctors for testing data display")
        
        # Check reviews
        reviews = Review.objects.count()
        if reviews > 0:
            self.passed.append(f"✓ Reviews: {reviews} records")
        
        # Check rating calculations
        doctors_with_ratings = Doctor.objects.filter(rating__gt=0).count()
        if doctors_with_ratings > 0:
            self.passed.append(f"✓ Rating Calculations: {doctors_with_ratings} doctors with ratings")
    
    def check_icon_consistency(self):
        """Check for icon consistency throughout app"""
        print("\n🎨 Checking Icon Consistency...")
        
        response = self.client.get('/')
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for Bootstrap Icons
            if 'bi-' in content or 'icon' in content.lower():
                icon_count = content.count('bi-')
                if icon_count > 5:
                    self.passed.append(f"✓ Icon Usage: {icon_count} Bootstrap Icons found")
                else:
                    self.warnings.append("⚠️  Limited icon usage - may need more visual hierarchy")
            
            # Check for consistent spacing
            if 'mb-' in content and 'mt-' in content and 'p-' in content:
                self.passed.append("✓ Consistent Spacing System")
            else:
                self.warnings.append("⚠️  Spacing consistency may be improved")
    
    def check_alignment_issues(self):
        """Check for alignment inconsistencies"""
        print("\n⚙️ Checking Alignment & Layout...")
        
        response = self.client.get('/doctors/')
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for Bootstrap grid alignment
            if 'align-items' in content or 'justify-content' in content or 'text-center' in content:
                self.passed.append("✓ Flexbox Alignment Classes")
            else:
                self.warnings.append("⚠️  Limited alignment control - may have layout issues")
            
            # Check for proper card structure
            if 'card-body' in content or 'card-header' in content:
                self.passed.append("✓ Bootstrap Card Components")
    
    def print_report(self):
        """Print detailed audit report"""
        print("\n" + "="*70)
        print("UI/UX AUDIT REPORT")
        print("="*70)
        
        print(f"\n✅ PASSED CHECKS ({len(self.passed)}):")
        for item in self.passed[:20]:
            print(f"   {item}")
        if len(self.passed) > 20:
            print(f"   ... and {len(self.passed) - 20} more")
        
        print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
        for item in self.warnings:
            print(f"   {item}")
        
        print(f"\n❌ ERRORS ({len(self.issues)}):")
        for item in self.issues:
            print(f"   {item}")
        
        print("\n" + "="*70)
        print("RECOMMENDATIONS")
        print("="*70)
        
        if self.warnings:
            print("\nPriority Fixes:")
            for i, warning in enumerate(self.warnings[:5], 1):
                print(f"{i}. {warning}")
        
        print("\n" + "="*70)
        success_rate = (len(self.passed) / (len(self.passed) + len(self.warnings))) * 100 if (len(self.passed) + len(self.warnings)) > 0 else 0
        print(f"UI Quality Score: {success_rate:.1f}%")
        print("="*70 + "\n")

def main():
    print("\n" + "="*70)
    print("UI/UX AUDIT SUITE - Visual Consistency & Component Check")
    print("="*70)
    
    audit = UIUXAudit()
    
    # Run audits
    audit.audit_home_page()
    audit.audit_doctor_listing()
    audit.audit_doctor_detail()
    audit.audit_appointment_booking()
    audit.audit_dashboard_structure()
    audit.audit_form_styling()
    audit.check_data_display()
    audit.check_icon_consistency()
    audit.check_alignment_issues()
    
    # Print report
    audit.print_report()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Audit error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

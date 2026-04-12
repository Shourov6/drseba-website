#!/usr/bin/env python
"""Get and display ngrok public URL"""

from pyngrok import ngrok
import time

print("\n" + "="*70)
print("🚀 Creating ngrok tunnel for Django (port 8000)...")
print("="*70 + "\n")

try:
    # Connect ngrok
    public_url = ngrok.connect(8000, "http")
    
    print(f"✅ SUCCESS! Your public URL is ready:\n")
    print(f"🌐 {public_url}")
    print(f"\n{'='*70}")
    print("📋 SHARE THIS LINK WITH OTHERS:")
    print(f"{'='*70}")
    print(f"\n  Homepage:  {public_url}/")
    print(f"  Admin:     {public_url}/admin/")
    print(f"  Dashboard: {public_url}/dashboard/")
    print(f"  Login:     {public_url}/accounts/login/")
    
    print(f"\n{'='*70}")
    print("🔐 TEST LOGIN CREDENTIALS:")
    print(f"{'='*70}\n")
    print("  Admin Account:")
    print("    Username: admin")
    print("    Password: Admin@123456\n")
    print("  Patient Account:")
    print("    Username: patient")
    print("    Password: Patient@123456\n")
    print("  Doctor Account:")
    print("    Username: doctor")
    print("    Password: Doctor@123456\n")
    print("  Employee Account:")
    print("    Username: employee")
    print("    Password: Employee@123456\n")
    
    print(f"{'='*70}")
    print("⏱️  PUBLIC LINK IS ACTIVE!")
    print("   Keep this window open to maintain the connection")
    print("   The link will expire when you close this window")
    print("   Press Ctrl+C to stop\n")
    print(f"{'='*70}\n")
    
    # Keep tunnel active
    while True:
        time.sleep(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure Django is running on port 8000!")

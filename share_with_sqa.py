#!/usr/bin/env python3
"""
DrSeba - Share Project with SQA Team
Simple script to expose local server and generate public URL
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def install_ngrok():
    """Install ngrok via pip"""
    print("\n📦 Installing pyngrok (Python Ngrok wrapper)...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok"])
        print("✅ pyngrok installed successfully!\n")
        return True
    except Exception as e:
        print(f"❌ Failed to install: {e}")
        return False

def share_with_ngrok():
    """Create public URL using Ngrok"""
    try:
        from pyngrok import ngrok
        
        print("\n" + "="*60)
        print("🌐 DrSeba Platform - Share with SQA Team")
        print("="*60)
        
        # Connect to local server
        public_url = ngrok.connect(8000, "http")
        
        print(f"\n✅ Public URL Created Successfully!")
        print(f"\n🔗 SHARE THIS LINK WITH SQA TEAM:\n")
        print(f"   {public_url}")
        print(f"\n📋 Admin Panel:\n")
        print(f"   {public_url}/admin/")
        print(f"\n👤 Test Credentials:")
        print(f"   Admin User: admin")
        print(f"   Patient: patient1@test.com")
        print(f"   Doctor: doctor1@test.com")
        
        print(f"\n⏱️  This URL will stay active as long as this script runs")
        print(f"💾 Keep this terminal OPEN for SQA team to access")
        print(f"\n⚠️  Press Ctrl+C to stop sharing\n")
        
        # Keep running
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n👋 Closing public URL...")
            ngrok.disconnect(public_url)
            print("✅ URL closed")
    
    except ImportError:
        print("❌ pyngrok not found. Installing...")
        if install_ngrok():
            share_with_ngrok()

def share_via_localhost():
    """Alternative: Show local network IP"""
    import socket
    
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    
    print("\n" + "="*60)
    print("🌐 Local Network Sharing (Same Office/Network Only)")
    print("="*60)
    print(f"\n📍 Your IP Address: {ip}")
    print(f"\n🔗 SHARE THIS LINK (if SQA is on same network):\n")
    print(f"   http://{ip}:8000")
    print(f"\n📋 Admin Panel:\n")
    print(f"   http://{ip}:8000/admin/")
    

def main():
    print("\n" + "="*60)
    print("DrSeba Healthcare Platform - SQA Testing Setup")
    print("="*60)
    
    print("\n📌 Choose Share Method:")
    print("1️⃣  Public URL via Ngrok (Recommended - SQA from anywhere)")
    print("2️⃣  Local Network IP (SQA on same network only)")
    print("3️⃣  Show Testing Guide")
    print("4️⃣  Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        print("\n⏳ Checking Ngrok...")
        try:
            from pyngrok import ngrok
            share_with_ngrok()
        except ImportError:
            if install_ngrok():
                share_with_ngrok()
    
    elif choice == "2":
        share_via_localhost()
        input("\nPress Enter to exit...")
    
    elif choice == "3":
        print("\n📖 Opening Testing Guide...")
        guide_path = Path("SQA_TESTING_GUIDE.md")
        if guide_path.exists():
            try:
                os.startfile(guide_path)
            except:
                print(f"View: {guide_path.absolute()}")
        else:
            print("SQA_TESTING_GUIDE.md not found")
    
    elif choice == "4":
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    else:
        print("❌ Invalid choice")
        main()

if __name__ == "__main__":
    # Make sure Django server is running
    print("\n⚠️  IMPORTANT: Make sure Django server is running!")
    print("   In another terminal, run: python manage.py runserver 0.0.0.0:8000\n")
    
    input("Press Enter to continue...")
    
    main()

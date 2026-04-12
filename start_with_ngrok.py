#!/usr/bin/env python
"""
Start Django development server with ngrok tunnel
This creates a public URL to share your local application
"""

import os
import sys
import django
import subprocess
from pyngrok import ngrok

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drseba.settings')
django.setup()

def start_ngrok_tunnel():
    """Start ngrok tunnel on port 8000"""
    print("\n" + "="*70)
    print("🚀 Starting ngrok tunnel...")
    print("="*70 + "\n")
    
    try:
        # Start ngrok tunnel
        public_url = ngrok.connect(8000, "http")
        print(f"✅ ngrok tunnel created!")
        print(f"\n📱 PUBLIC URL: {public_url}")
        print(f"\n🔗 Share this URL with others:")
        print(f"   {public_url}/")
        print(f"\n📋 LOGIN CREDENTIALS:")
        print(f"   Admin:    admin / Admin@123456")
        print(f"   Patient:  patient / Patient@123456")
        print(f"   Doctor:   doctor / Doctor@123456")
        print(f"   Employee: employee / Employee@123456")
        print(f"\n⏱️  This URL will be active while the script runs")
        print(f"   Press Ctrl+C to stop\n")
        print("="*70 + "\n")
        
        # Keep the tunnel active
        ngrok_process = ngrok.get_ngrok_process()
        ngrok_process.proc.wait()
        
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        sys.exit(1)

def main():
    """Start Django and ngrok"""
    print("\n" + "="*70)
    print("🏥 DrSeba Healthcare Platform - Public Share Mode")
    print("="*70)
    
    # Start ngrok in background
    print("\n1. Starting ngrok tunnel...")
    start_ngrok_tunnel()

if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""Diagnostic script to check DrSeba configuration"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drseba.settings')
django.setup()

from django.conf import settings
from django.db import connection
from django.contrib.auth import get_user_model

print("\n" + "="*70)
print("🔍 DrSeba Diagnostic Report")
print("="*70 + "\n")

# 1. Check Database
print("📊 DATABASE CONFIGURATION:")
print(f"   Engine: {settings.DATABASES['default']['ENGINE']}")
print(f"   Database: {settings.DATABASES['default']['NAME']}")
print(f"   Host: {settings.DATABASES['default']['HOST']}")
print(f"   User: {settings.DATABASES['default']['USER']}")

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("   ✅ Connection: OK\n")
except Exception as e:
    print(f"   ❌ Connection: FAILED - {e}\n")
    sys.exit(1)

# 2. Check Users
print("👥 DATABASE USERS:")
User = get_user_model()
users = User.objects.all().values('username', 'email', 'role')
if users.exists():
    for user in users:
        print(f"   ✓ {user['username']} ({user['role']})")
    print()
else:
    print("   ⚠️  No users found\n")

# 3. Check Django Settings
print("⚙️  DJANGO SETTINGS:")
print(f"   DEBUG: {settings.DEBUG}")
print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"   DATABASE: {settings.DATABASES['default']['NAME']}\n")

# 4. Quick Health Check
print("✅ SYSTEM STATUS: ALL OK\n")
print("="*70 + "\n")

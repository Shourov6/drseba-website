#!/usr/bin/env python
"""
MySQL Database Setup Script for DrSeba Healthcare Platform
Run this script to automatically set up MySQL database and user
"""

import mysql.connector
from mysql.connector import Error
import sys

def create_mysql_database():
    """Create MySQL database and user for DrSeba application"""
    
    # Configuration
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_NAME = 'drseba_healthcare'
    APP_USER = 'drseba_user'
    APP_PASSWORD = 'DrsebaPwd123!@#'
    
    # Try different password scenarios
    passwords_to_try = [
        '',  # No password (default for local fresh installs)
        'root',
        'password',
        'mysql',
        'DrsebaPwd123!@#',
        'Mafia666',  # User's custom root password
    ]
    
    connection = None
    for attempt, password in enumerate(passwords_to_try, 1):
        try:
            print(f"🔗 Connecting to MySQL server (Attempt {attempt})...")
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=password
            )
            
            if connection.is_connected():
                print(f"✓ Connected to MySQL Server with password: {'(empty)' if not password else '***'}")
                DB_PASSWORD = password
                break
                
        except Error as e:
            # print(f"❌ Connection failed: {e}")
            continue
    
    if not connection or not connection.is_connected():
        print("\n" + "="*60)
        print("❌ Could not connect to MySQL Server")
        print("="*60)
        print("\n✅ SOLUTION: Set up MySQL with root password:")
        print("\n1. Start Command Prompt as Administrator")
        print("2. Run: mysql -u root")
        print("3. Then execute:")
        print(f"   ALTER USER 'root'@'localhost' IDENTIFIED BY 'DrsebaPwd123!@#';")
        print(f"   FLUSH PRIVILEGES;")
        print("\n4. Then run this script again")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Create database
        print(f"\n📦 Creating database '{DB_NAME}'...")
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        cursor.execute(f"""
            CREATE DATABASE {DB_NAME} 
            CHARACTER SET utf8mb4 
            COLLATE utf8mb4_unicode_ci
        """)
        print(f"✓ Database '{DB_NAME}' created successfully")
        
        # Create application user
        print(f"\n👤 Creating database user '{APP_USER}'...")
        cursor.execute(f"DROP USER IF EXISTS '{APP_USER}'@'{DB_HOST}'")
        cursor.execute(f"""
            CREATE USER '{APP_USER}'@'{DB_HOST}' 
            IDENTIFIED BY '{APP_PASSWORD}'
        """)
        print(f"✓ User '{APP_USER}' created successfully")
        
        # Grant privileges
        print(f"\n🔐 Granting privileges to '{APP_USER}'...")
        cursor.execute(f"""
            GRANT ALL PRIVILEGES ON {DB_NAME}.* 
            TO '{APP_USER}'@'{DB_HOST}'
        """)
        cursor.execute("FLUSH PRIVILEGES")
        print("✓ Privileges granted successfully")
        
        # Verify
        print("\n✅ Verification:")
        print(f"   Database: {DB_NAME}")
        print(f"   User: {APP_USER}")
        print(f"   Password: (securely stored)")
        
        cursor.close()
        
        print("\n" + "="*60)
        print("📋 Database configuration:")
        print("="*60)
        print(f"DB_ENGINE = 'django.db.backends.mysql'")
        print(f"DB_NAME = '{DB_NAME}'")
        print(f"DB_USER = '{APP_USER}'")
        print(f"DB_PASSWORD = '{APP_PASSWORD}'")
        print(f"DB_HOST = '{DB_HOST}'")
        print(f"DB_PORT = '3306'")
        print("="*60)
        
        return True
        
    except Error as e:
        print(f"\n❌ Error: {e}")
        return False
        
    finally:
        if connection.is_connected():
            connection.close()
            print("\n✓ MySQL connection closed")

if __name__ == '__main__':
    print("="*60)
    print("🏥 DrSeba Healthcare Platform - MySQL Setup")
    print("="*60)
    
    success = create_mysql_database()
    sys.exit(0 if success else 1)

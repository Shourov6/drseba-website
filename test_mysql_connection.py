#!/usr/bin/env python
"""Test MySQL connection with various methods"""

import mysql.connector
from mysql.connector import Error
import subprocess
import sys

def try_direct_connection():
    """Try connecting with empty password"""
    passwords = ['', 'root', 'password', 'mysql']
    
    for pwd in passwords:
        try:
            print(f"Trying connection with password: {'(empty)' if not pwd else pwd}")
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pwd
            )
            if conn.is_connected():
                print(f"✓ SUCCESS! Connected with password: {'(empty)' if not pwd else pwd}")
                return conn, pwd
        except Error as e:
            print(f"  ✗ Failed: {e}")
    
    return None, None

def reset_password():
    """Reset MySQL root password"""
    print("\n" + "="*60)
    print("RESETTING MYSQL ROOT PASSWORD")
    print("="*60)
    
    # Stop MySQL
    print("\n1. Stopping MySQL service...")
    result = subprocess.run(['net', 'stop', 'MySQL80'], capture_output=True, text=True)
    print(result.stdout if result.returncode == 0 else "⚠ Could not stop service (may require admin)")
    
    # Start with skip-grant-tables
    print("\n2. Starting MySQL without password check...")
    try:
        mysqld_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe"
        # This will run in background
        subprocess.Popen([mysqld_path, '--skip-grant-tables'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        print("  MySQL started without password check")
        
        import time
        time.sleep(3)  # Wait for MySQL to start
        
        # Connect and reset password
        print("\n3. Resetting root password...")
        conn = mysql.connector.connect(
            host='localhost',
            user='root'
        )
        cursor = conn.cursor()
        cursor.execute("FLUSH PRIVILEGES")
        cursor.execute("ALTER USER 'root'@'localhost' IDENTIFIED BY ''")
        cursor.execute("FLUSH PRIVILEGES")
        cursor.close()
        conn.close()
        print("  ✓ Password reset to empty")
        
        # Stop and restart normally
        print("\n4. Restarting MySQL normally...")
        subprocess.run(['net', 'stop', 'MySQL80'], capture_output=True)
        subprocess.run(['net', 'start', 'MySQL80'], capture_output=True)
        print("  ✓ MySQL restarted")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("MYSQL CONNECTION TEST")
    print("="*60 + "\n")
    
    conn, pwd = try_direct_connection()
    
    if conn:
        print(f"\nUsing password: {'(empty)' if not pwd else pwd}")
        sys.exit(0)
    else:
        print("\n✗ Could not connect with any standard password")
        print("MySQL may not be running. Please start it manually.")
        sys.exit(1)

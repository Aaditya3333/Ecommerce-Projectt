#!/usr/bin/env python
"""
Test script to verify PostgreSQL connection
"""
import os
import sys
import django

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

try:
    django.setup()
    
    from django.db import connection
    
    print("Testing PostgreSQL connection...")
    
    # Test database connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        print(f"Connected to database: {db_name[0]}")
        
        cursor.execute("SELECT current_user;")
        user = cursor.fetchone()
        print(f"Connected as user: {user[0]}")
    
    print("\nConnection test successful! PostgreSQL is working correctly.")
    
except Exception as e:
    print(f"Connection test failed: {e}")
    print("\nPlease check:")
    print("1. PostgreSQL is installed and running")
    print("2. Database 'aaditya_store_db' exists")
    print("3. Password in settings.py is correct")
    print("4. psycopg2-binary is installed")
    sys.exit(1)

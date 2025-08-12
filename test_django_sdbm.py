#!/usr/bin/env python3
# test_django_sdbm.py - Test koneksi SDBM melalui Django
import os
import sys
import django
from datetime import datetime

# Setup Django environment
sys.path.append('.')  # Current directory
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_seiwa.settings')

try:
    django.setup()
    print("✅ Django setup berhasil")
except Exception as e:
    print(f"❌ Django setup gagal: {e}")
    sys.exit(1)

from django.db import connections
from django.contrib.auth import authenticate
from django.test import RequestFactory

def test_django_sdbm_connection():
    """Test koneksi SDBM melalui Django connections"""
    print("=" * 60)
    print("🔧 Django SDBM Connection Test")
    print("=" * 60)
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Test Django database connection
        print("🔍 Testing Django database connection...")
        connection = connections['SDBM']
        cursor = connection.cursor()
        
        # Test basic connection
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()
        print(f"✅ Django connection berhasil!")
        print(f"📊 SQL Server: {version[0][:50]}...")
        
        # Test current user
        cursor.execute("SELECT CURRENT_USER")
        current_user = cursor.fetchone()
        print(f"👤 Current User: {current_user[0]}")
        
        # Test database
        cursor.execute("SELECT DB_NAME()")
        db_name = cursor.fetchone()
        print(f"🏷️  Database: {db_name[0]}")
        
        # Test employees table
        cursor.execute("SELECT COUNT(*) FROM hrbp.employees WHERE is_active = 1")
        count = cursor.fetchone()
        print(f"👥 Active employees: {count[0]}")
        
        # Test sample employee query (seperti di authentication backend)
        print("\n🔍 Testing employee authentication query...")
        cursor.execute("""
            SELECT TOP 3
                e.fullname, 
                e.nickname, 
                e.employee_number, 
                e.level_user, 
                e.job_status, 
                CASE WHEN e.pwd IS NOT NULL THEN 'YES' ELSE 'NO' END as has_password,
                d.name as department_name
            FROM hrbp.employees e
            LEFT JOIN hrbp.position p ON e.id = p.employeeId
            LEFT JOIN hr.department d ON p.departmentId = d.id
            WHERE e.is_active = 1 AND e.pwd IS NOT NULL
            ORDER BY e.employee_number
        """)
        
        employees = cursor.fetchall()
        if employees:
            print("✅ Sample employees with authentication data:")
            for emp in employees:
                print(f"   - {emp[2]}: {emp[0]} ({emp[3]}) - Dept: {emp[6]} - Has Pwd: {emp[5]}")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Django connection gagal: {e}")
        return False

def test_sdbm_authentication_backend():
    """Test SDBM authentication backend"""
    print("\n" + "=" * 60)
    print("🔐 Testing SDBM Authentication Backend")
    print("=" * 60)
    
    try:
        # Import authentication backend
        from authentication import SDBMAuthenticationBackend
        backend = SDBMAuthenticationBackend()
        print("✅ SDBM Authentication Backend loaded")
        
        # Create mock request
        factory = RequestFactory()
        request = factory.post('/login/')
        request.session = {}
        
        # Test dengan employee yang ditemukan dari query sebelumnya
        print("\n🔍 Testing authentication dengan sample employee...")
        
        # Get a test employee
        connection = connections['SDBM']
        cursor = connection.cursor()
        cursor.execute("""
            SELECT TOP 1 employee_number 
            FROM hrbp.employees 
            WHERE is_active = 1 AND pwd IS NOT NULL
            ORDER BY employee_number
        """)
        test_employee = cursor.fetchone()
        cursor.close()
        
        if test_employee:
            test_emp_num = test_employee[0]
            print(f"📋 Testing dengan employee number: {test_emp_num}")
            
            # Test authentication (tanpa password yang benar, hanya test struktur)
            print("⚠️  Note: Testing structure, bukan password yang benar")
            user = backend.authenticate(request, username=test_emp_num, password="test_password")
            
            if user is None:
                print("✅ Authentication backend berjalan (password salah seperti yang diharapkan)")
                print("✅ Struktur authentication backend sudah benar")
            else:
                print(f"✅ Authentication berhasil untuk user: {user.username}")
        else:
            print("❌ Tidak ada employee dengan password untuk testing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing authentication backend: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_authentication_with_real_employee():
    """Test authentication dengan employee number yang user berikan"""
    print("\n" + "=" * 60)
    print("🎯 Test Authentication dengan Employee Real")
    print("=" * 60)
    
    # Tampilkan beberapa employee untuk referensi
    try:
        connection = connections['SDBM']
        cursor = connection.cursor()
        cursor.execute("""
            SELECT TOP 5 employee_number, fullname, level_user 
            FROM hrbp.employees 
            WHERE is_active = 1 AND pwd IS NOT NULL
            ORDER BY employee_number
        """)
        employees = cursor.fetchall()
        cursor.close()
        
        print("📋 Available employees untuk testing:")
        for emp in employees:
            print(f"   - {emp[0]}: {emp[1]} ({emp[2]})")
        
        print("\n💡 Untuk test authentication penuh:")
        print("1. Pilih salah satu employee number dari list di atas")
        print("2. Gunakan Django admin atau form login dengan:")
        print("   - Employee Number: [dari list di atas]") 
        print("   - Password: [password SDBM yang sesuai]")
        print("3. Atau jalankan: python manage.py test_sdbm --test-auth EMPLOYEE_NUMBER")
        
    except Exception as e:
        print(f"❌ Error getting employee list: {e}")

def main():
    """Main test function"""
    success_count = 0
    
    # Test 1: Django connection
    if test_django_sdbm_connection():
        success_count += 1
    
    # Test 2: Authentication backend
    if test_sdbm_authentication_backend():
        success_count += 1
    
    # Test 3: Show available employees
    test_authentication_with_real_employee()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 DJANGO TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Tests passed: {success_count}/2")
    
    if success_count == 2:
        print("\n🎉 Django SDBM integration siap digunakan!")
        print("💡 Next steps:")
        print("1. Update settings.py dengan konfigurasi yang bekerja")
        print("2. Test login melalui web interface")
        print("3. Monitor logs untuk debugging jika ada issue")
    else:
        print("\n⚠️  Beberapa test gagal, perlu troubleshooting")

if __name__ == "__main__":
    main()
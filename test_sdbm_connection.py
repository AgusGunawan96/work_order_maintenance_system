#!/usr/bin/env python3
# test_sdbm_connection.py - Script untuk test koneksi manual ke database SDBM
import pyodbc
import sys
import os
from datetime import datetime

def print_header():
    """Print header script"""
    print("=" * 70)
    print("🔧 SDBM Database Connection Test - PT Seiwa Indonesia")
    print("=" * 70)
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def test_sdbm_connection_option1():
    """Test koneksi menggunakan kredensial sa (Recommended)"""
    print("🔍 [OPSI 1] Testing dengan kredensial 'sa'...")
    
    # Konfigurasi koneksi - OPSI 1 (Recommended)
    server = '172.16.202.223\\SPM'
    database = 'SDBM'
    username = 'sa'
    password = 'loginS@EDP'
    driver = 'ODBC Driver 17 for SQL Server'
    
    return test_connection(server, database, username, password, driver, "Opsi 1 (sa)")

def test_sdbm_connection_option2():
    """Test koneksi menggunakan kredensial seiwa_app (Original)"""
    print("🔍 [OPSI 2] Testing dengan kredensial 'seiwa_app'...")
    
    # Konfigurasi koneksi - OPSI 2 (Original)
    server = '172.16.202.223\\SPM'
    database = 'SDBM'
    username = 'seiwa_app'
    password = 'Password123!'
    driver = 'ODBC Driver 17 for SQL Server'
    
    return test_connection(server, database, username, password, driver, "Opsi 2 (seiwa_app)")

def test_sdbm_connection_option3():
    """Test koneksi tanpa named instance"""
    print("🔍 [OPSI 3] Testing tanpa named instance...")
    
    # Konfigurasi koneksi - OPSI 3 (No Named Instance)
    server = '172.16.202.223'
    database = 'SDBM'
    username = 'sa'
    password = 'loginS@EDP'
    driver = 'ODBC Driver 17 for SQL Server'
    port = '1433'
    
    return test_connection_with_port(server, database, username, password, driver, port, "Opsi 3 (No Named Instance)")

def test_connection(server, database, username, password, driver, option_name):
    """Test koneksi dengan parameter yang diberikan"""
    
    # Connection string
    conn_str = f"""
    DRIVER={{{driver}}};
    SERVER={server};
    DATABASE={database};
    UID={username};
    PWD={password};
    TrustServerCertificate=yes;
    Encrypt=no;
    Connection Timeout=30;
    Command Timeout=30;
    """
    
    try:
        print(f"📡 Mencoba koneksi ke database SDBM ({option_name})...")
        print(f"   Server: {server}")
        print(f"   Database: {database}")
        print(f"   Username: {username}")
        print(f"   Driver: {driver}")
        print()
        
        # Establish connection
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Test 1: Basic connection
        print("✅ Koneksi berhasil!")
        
        # Test 2: Get SQL Server version
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()
        print(f"📊 SQL Server Version: {version[0][:80]}...")
        
        # Test 3: Get current database
        cursor.execute("SELECT DB_NAME()")
        db_name = cursor.fetchone()
        print(f"🏷️  Current Database: {db_name[0]}")
        
        # Test 4: Get current user
        cursor.execute("SELECT CURRENT_USER")
        current_user = cursor.fetchone()
        print(f"👤 Current User: {current_user[0]}")
        
        # Test 5: Check schemas
        print("\n📋 Checking schemas...")
        cursor.execute("""
            SELECT SCHEMA_NAME 
            FROM INFORMATION_SCHEMA.SCHEMATA 
            WHERE SCHEMA_NAME IN ('hrbp', 'hr')
            ORDER BY SCHEMA_NAME
        """)
        schemas = cursor.fetchall()
        
        if schemas:
            print("✅ Required schemas found:")
            for schema in schemas:
                print(f"   - {schema[0]}")
        else:
            print("⚠️  Required schemas (hrbp, hr) not found")
        
        # Test 6: Check employees table
        print("\n👥 Checking employees table...")
        try:
            cursor.execute("SELECT COUNT(*) FROM hrbp.employees WHERE is_active = 1")
            count = cursor.fetchone()
            print(f"✅ Active employees found: {count[0]}")
            
            # Get sample data
            cursor.execute("""
                SELECT TOP 3 employee_number, fullname, level_user 
                FROM hrbp.employees 
                WHERE is_active = 1 
                ORDER BY employee_number
            """)
            samples = cursor.fetchall()
            
            if samples:
                print("📋 Sample employees:")
                for emp in samples:
                    print(f"   - {emp[0]}: {emp[1]} ({emp[2]})")
            
        except Exception as e:
            print(f"❌ Error accessing employees table: {e}")
        
        # Test 7: Check related tables
        print("\n🔗 Checking related tables...")
        related_tables = [
            ('hrbp', 'position'),
            ('hr', 'department'),
            ('hr', 'section'),
            ('hr', 'subsection'),
            ('hr', 'title')
        ]
        
        for schema, table in related_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
                count = cursor.fetchone()
                print(f"   ✅ {schema}.{table}: {count[0]} records")
            except Exception as e:
                print(f"   ❌ {schema}.{table}: Error - {e}")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 {option_name} - CONNECTION TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ {option_name} - Connection failed: {e}")
        print()
        
        # Troubleshooting tips
        if "Login failed" in str(e):
            print("💡 Troubleshooting tips for login failure:")
            print("   1. Check if username/password is correct")
            print("   2. Verify user exists in SQL Server")
            print("   3. Check user permissions on SDBM database")
            
        elif "server was not found" in str(e).lower():
            print("💡 Troubleshooting tips for server not found:")
            print("   1. Check if SQL Server service is running")
            print("   2. Verify server name and instance")
            print("   3. Check network connectivity")
            print("   4. Verify firewall settings")
            
        elif "timeout" in str(e).lower():
            print("💡 Troubleshooting tips for timeout:")
            print("   1. Check network latency")
            print("   2. Increase connection timeout")
            print("   3. Verify server is not overloaded")
        
        return False

def test_connection_with_port(server, database, username, password, driver, port, option_name):
    """Test koneksi dengan port eksplisit"""
    
    # Connection string dengan port
    conn_str = f"""
    DRIVER={{{driver}}};
    SERVER={server},{port};
    DATABASE={database};
    UID={username};
    PWD={password};
    TrustServerCertificate=yes;
    Encrypt=no;
    Connection Timeout=30;
    Command Timeout=30;
    """
    
    try:
        print(f"📡 Mencoba koneksi ke database SDBM ({option_name})...")
        print(f"   Server: {server}:{port}")
        print(f"   Database: {database}")
        print(f"   Username: {username}")
        print()
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()
        print(f"✅ {option_name} - Connection successful!")
        print(f"📊 SQL Server Version: {version[0][:80]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ {option_name} - Connection failed: {e}")
        return False

def check_odbc_drivers():
    """Check available ODBC drivers"""
    print("🔧 Checking available ODBC drivers...")
    try:
        drivers = pyodbc.drivers()
        sql_drivers = [d for d in drivers if 'SQL Server' in d]
        
        if sql_drivers:
            print("✅ SQL Server ODBC drivers found:")
            for driver in sql_drivers:
                print(f"   - {driver}")
        else:
            print("❌ No SQL Server ODBC drivers found!")
            print("💡 Please install 'ODBC Driver 17 for SQL Server'")
        
        return len(sql_drivers) > 0
        
    except Exception as e:
        print(f"❌ Error checking drivers: {e}")
        return False

def test_basic_connectivity():
    """Test basic network connectivity"""
    print("🌐 Testing basic network connectivity...")
    
    import socket
    
    hosts_to_test = [
        ('172.16.202.223', 1433),
        ('172.16.202.237', 1433),
    ]
    
    for host, port in hosts_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {host}:{port} - Reachable")
            else:
                print(f"❌ {host}:{port} - Not reachable")
                
        except Exception as e:
            print(f"❌ {host}:{port} - Error: {e}")

def main():
    """Main function"""
    print_header()
    
    # Check prerequisites
    print("🔍 Checking prerequisites...")
    
    # Check pyodbc
    try:
        import pyodbc
        print("✅ pyodbc module available")
    except ImportError:
        print("❌ pyodbc module not found!")
        print("💡 Install with: pip install pyodbc")
        return
    
    # Check ODBC drivers
    if not check_odbc_drivers():
        print("⚠️  Warning: No SQL Server ODBC drivers found")
    
    print()
    
    # Test network connectivity
    test_basic_connectivity()
    print()
    
    # Test database connections
    success_count = 0
    
    # Option 1: sa credentials (recommended)
    if test_sdbm_connection_option1():
        success_count += 1
    print("-" * 50)
    
    # Option 2: seiwa_app credentials
    if test_sdbm_connection_option2():
        success_count += 1
    print("-" * 50)
    
    # Option 3: no named instance
    if test_sdbm_connection_option3():
        success_count += 1
    print("-" * 50)
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 30)
    print(f"Total tests: 3")
    print(f"Successful: {success_count}")
    print(f"Failed: {3 - success_count}")
    
    if success_count > 0:
        print("\n🎉 At least one connection method works!")
        print("💡 Use the working configuration in your Django settings.py")
    else:
        print("\n❌ All connection attempts failed!")
        print("💡 Please check:")
        print("   1. SQL Server service status")
        print("   2. Network connectivity")
        print("   3. User credentials")
        print("   4. Database permissions")

if __name__ == "__main__":
    main()
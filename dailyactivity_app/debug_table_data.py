# debug_table_data.py
# Script untuk debug isi tabel di DB_Maintenance
# Jalanin dengan: python manage.py shell < debug_table_data.py

from django.db import connections
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_table_data():
    """
    Debug isi tabel di DB_Maintenance untuk cari tau kenapa data kosong
    """
    print("🔍 Debugging table data in DB_Maintenance...")
    
    try:
        connection = connections['DB_Maintenance']
        
        # ===== DEBUG TABEL_LINE =====
        print("\n📋 DEBUGGING TABEL_LINE:")
        print("=" * 50)
        
        with connection.cursor() as cursor:
            # Check total records
            cursor.execute("SELECT COUNT(*) FROM tabel_line")
            total_lines = cursor.fetchone()[0]
            print(f"Total records in tabel_line: {total_lines}")
            
            # Check unique status values
            cursor.execute("SELECT status, COUNT(*) FROM tabel_line GROUP BY status")
            status_counts = cursor.fetchall()
            print(f"Status distribution:")
            for status, count in status_counts:
                print(f"   Status '{status}': {count} records")
            
            # Show sample data
            cursor.execute("SELECT TOP 5 id_line, line, status, keterangan FROM tabel_line")
            sample_lines = cursor.fetchall()
            print(f"\nSample data (first 5 records):")
            for record in sample_lines:
                print(f"   ID: {record[0]}, Line: '{record[1]}', Status: '{record[2]}', Keterangan: '{record[3]}'")
            
            # Check dengan berbagai filter status
            for test_status in ['1', '0', 'A', 'Y', 'N', 'ACTIVE', 'AKTIF']:
                cursor.execute("SELECT COUNT(*) FROM tabel_line WHERE status = ?", [test_status])
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"   🎯 FOUND: Status '{test_status}' has {count} records!")
        
        # ===== DEBUG TABEL_PEKERJAAN =====
        print("\n📋 DEBUGGING TABEL_PEKERJAAN:")
        print("=" * 50)
        
        with connection.cursor() as cursor:
            # Check total records
            cursor.execute("SELECT COUNT(*) FROM tabel_pekerjaan")
            total_pekerjaan = cursor.fetchone()[0]
            print(f"Total records in tabel_pekerjaan: {total_pekerjaan}")
            
            # Check unique status values
            cursor.execute("SELECT status, COUNT(*) FROM tabel_pekerjaan GROUP BY status")
            status_counts = cursor.fetchall()
            print(f"Status distribution:")
            for status, count in status_counts:
                print(f"   Status '{status}': {count} records")
            
            # Show sample data
            cursor.execute("SELECT TOP 5 id_pekerjaan, pekerjaan, status, keterangan FROM tabel_pekerjaan")
            sample_pekerjaan = cursor.fetchall()
            print(f"\nSample data (first 5 records):")
            for record in sample_pekerjaan:
                print(f"   ID: {record[0]}, Pekerjaan: '{record[1]}', Status: '{record[2]}', Keterangan: '{record[3]}'")
            
            # Check dengan berbagai filter status
            for test_status in ['1', '0', 'A', 'Y', 'N', 'ACTIVE', 'AKTIF']:
                cursor.execute("SELECT COUNT(*) FROM tabel_pekerjaan WHERE status = ?", [test_status])
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"   🎯 FOUND: Status '{test_status}' has {count} records!")
        
        # ===== DEBUG TABEL_MESIN =====
        print("\n📋 DEBUGGING TABEL_MESIN:")
        print("=" * 50)
        
        with connection.cursor() as cursor:
            # Check total records
            cursor.execute("SELECT COUNT(*) FROM tabel_mesin")
            total_mesin = cursor.fetchone()[0]
            print(f"Total records in tabel_mesin: {total_mesin}")
            
            # Check unique status values
            cursor.execute("SELECT status, COUNT(*) FROM tabel_mesin GROUP BY status")
            status_counts = cursor.fetchall()
            print(f"Status distribution:")
            for status, count in status_counts:
                print(f"   Status '{status}': {count} records")
            
            # Show sample data with line relationship
            cursor.execute("""
                SELECT TOP 5 id_mesin, mesin, id_line, nomer, status 
                FROM tabel_mesin 
                ORDER BY id_mesin
            """)
            sample_mesin = cursor.fetchall()
            print(f"\nSample data (first 5 records):")
            for record in sample_mesin:
                print(f"   ID: {record[0]}, Mesin: '{record[1]}', Line ID: '{record[2]}', Nomer: '{record[3]}', Status: '{record[4]}'")
        
        # ===== TESTING DIFFERENT STATUS VALUES =====
        print("\n🧪 TESTING QUERIES WITH DIFFERENT STATUS VALUES:")
        print("=" * 50)
        
        # Try different status values for lines
        with connection.cursor() as cursor:
            for test_status in ['1', '0', 'A', 'Y', 'ACTIVE']:
                try:
                    cursor.execute("""
                        SELECT id_line, line 
                        FROM tabel_line 
                        WHERE status = ? 
                        ORDER BY line
                    """, [test_status])
                    results = cursor.fetchall()
                    if results:
                        print(f"✅ tabel_line with status='{test_status}': {len(results)} records")
                        print(f"   Sample: {results[0] if results else 'None'}")
                    else:
                        print(f"❌ tabel_line with status='{test_status}': 0 records")
                except Exception as e:
                    print(f"❌ Error testing status '{test_status}': {str(e)}")
        
        # ===== GENERATE WORKING QUERY =====
        print("\n🚀 GENERATING WORKING QUERIES:")
        print("=" * 50)
        
        with connection.cursor() as cursor:
            # Find working status value for lines
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM tabel_line
                GROUP BY status
                ORDER BY count DESC
            """)
            line_statuses = cursor.fetchall()
            
            if line_statuses:
                best_status = line_statuses[0][0]
                print(f"💡 SUGGESTED: Use status='{best_status}' for tabel_line ({line_statuses[0][1]} records)")
                
                # Test query with best status
                cursor.execute(f"""
                    SELECT TOP 3 id_line, line, keterangan 
                    FROM tabel_line 
                    WHERE status = ?
                    ORDER BY line
                """, [best_status])
                sample = cursor.fetchall()
                print(f"   Working query result: {sample}")
            
            # Find working status value for pekerjaan
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM tabel_pekerjaan
                GROUP BY status
                ORDER BY count DESC
            """)
            pekerjaan_statuses = cursor.fetchall()
            
            if pekerjaan_statuses:
                best_status = pekerjaan_statuses[0][0]
                print(f"💡 SUGGESTED: Use status='{best_status}' for tabel_pekerjaan ({pekerjaan_statuses[0][1]} records)")
                
                # Test query with best status
                cursor.execute(f"""
                    SELECT TOP 3 id_pekerjaan, pekerjaan, keterangan 
                    FROM tabel_pekerjaan 
                    WHERE status = ?
                    ORDER BY pekerjaan
                """, [best_status])
                sample = cursor.fetchall()
                print(f"   Working query result: {sample}")
        
        print(f"\n🎉 Debug completed! Check the suggestions above.")
        return True
        
    except Exception as e:
        print(f"❌ Database debug failed: {str(e)}")
        return False

# Jalankan debug
if __name__ == "__main__":
    debug_table_data()
else:
    # Jika dijalankan dari shell
    debug_table_data()
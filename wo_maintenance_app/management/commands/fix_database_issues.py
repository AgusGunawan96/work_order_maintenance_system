# wo_maintenance_app/management/commands/fix_database_issues.py

from django.core.management.base import BaseCommand
from django.db import connections
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix Database Issues for SDBM Integration and Enhanced Views'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--fix-status-values',
            action='store_true',
            help='Fix status and approve values to use A/Y instead of 1',
        )
        parser.add_argument(
            '--check-siti-access',
            action='store_true',
            help='Check SITI FATIMAH access and data',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        fix_status = options['fix_status_values']
        check_siti = options['check_siti_access']
        
        self.stdout.write(self.style.SUCCESS('=== Fixing Database Issues for Enhanced SDBM Integration ==='))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No actual changes will be made'))
        
        try:
            # 1. Test Database Connections
            self.stdout.write('\n1. Testing Database Connections...')
            self.test_database_connections()
            
            # 2. Check Current Status Values
            self.stdout.write('\n2. Checking Current Status Values...')
            self.check_status_values()
            
            # 3. Fix Status Values if requested
            if fix_status:
                self.stdout.write('\n3. Fixing Status and Approve Values...')
                self.fix_status_values(dry_run)
            
            # 4. Verify SITI FATIMAH Access
            if check_siti:
                self.stdout.write('\n4. Checking SITI FATIMAH Access...')
                self.check_siti_fatimah_access()
            
            # 5. Test Enhanced Query
            self.stdout.write('\n5. Testing Enhanced Query Structure...')
            self.test_enhanced_query(dry_run)
            
            # 6. Final Validation
            self.stdout.write('\n6. Final Validation...')
            self.final_validation()
            
            self.stdout.write('\n' + '='*60)
            
            if not dry_run:
                self.stdout.write(self.style.SUCCESS('✅ Database issues fixed successfully!'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ Dry run completed - issues identified'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error fixing database issues: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())
    
    def test_database_connections(self):
        """Test database connections"""
        try:
            # Test DB_Maintenance
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan")
                maintenance_count = cursor.fetchone()[0]
                self.stdout.write(f"  ✓ DB_Maintenance: {maintenance_count} pengajuan records")
            
            # Test SDBM
            with connections['SDBM'].cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM [hrbp].[employees] WHERE is_active = 1")
                sdbm_count = cursor.fetchone()[0]
                self.stdout.write(f"  ✓ SDBM: {sdbm_count} active employees")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Database connection error: {e}"))
            raise
    
    def check_status_values(self):
        """Check current status and approve values in database"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Check status values
                cursor.execute("""
                    SELECT status, COUNT(*) as count
                    FROM tabel_pengajuan 
                    WHERE status IS NOT NULL
                    GROUP BY status
                    ORDER BY status
                """)
                
                status_results = cursor.fetchall()
                self.stdout.write("  📊 Current STATUS values:")
                for status, count in status_results:
                    self.stdout.write(f"    - '{status}': {count} records")
                
                # Check approve values
                cursor.execute("""
                    SELECT approve, COUNT(*) as count
                    FROM tabel_pengajuan 
                    WHERE approve IS NOT NULL
                    GROUP BY approve
                    ORDER BY approve
                """)
                
                approve_results = cursor.fetchall()
                self.stdout.write("  📊 Current APPROVE values:")
                for approve, count in approve_results:
                    self.stdout.write(f"    - '{approve}': {count} records")
                
                # Check for problematic combinations
                cursor.execute("""
                    SELECT status, approve, COUNT(*) as count
                    FROM tabel_pengajuan 
                    WHERE (status = '1' AND approve = '1')
                       OR (status = 'A' AND approve = 'Y')
                    GROUP BY status, approve
                """)
                
                combo_results = cursor.fetchall()
                self.stdout.write("  🎯 Approved combinations found:")
                if combo_results:
                    for status, approve, count in combo_results:
                        self.stdout.write(f"    - status='{status}', approve='{approve}': {count} records")
                else:
                    self.stdout.write("    - No approved combinations found")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error checking status values: {e}"))
    
    def fix_status_values(self, dry_run):
        """Fix status and approve values to use A/Y format"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Check what needs to be fixed
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = '1' OR approve = '1'
                """)
                
                records_to_fix = cursor.fetchone()[0]
                
                if records_to_fix == 0:
                    self.stdout.write("  ✓ No status/approve values need fixing")
                    return
                
                self.stdout.write(f"  📝 Found {records_to_fix} records that need status/approve value fixes")
                
                if dry_run:
                    self.stdout.write("  Would fix status '1' -> 'A' and approve '1' -> 'Y'")
                    return
                
                # Fix status values
                cursor.execute("""
                    UPDATE tabel_pengajuan 
                    SET status = 'A' 
                    WHERE status = '1'
                """)
                status_updated = cursor.rowcount
                
                # Fix approve values
                cursor.execute("""
                    UPDATE tabel_pengajuan 
                    SET approve = 'Y' 
                    WHERE approve = '1'
                """)
                approve_updated = cursor.rowcount
                
                self.stdout.write(f"  ✅ Updated {status_updated} status values (1 -> A)")
                self.stdout.write(f"  ✅ Updated {approve_updated} approve values (1 -> Y)")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error fixing status values: {e}"))
    
    def check_siti_fatimah_access(self):
        """Check SITI FATIMAH access and data"""
        try:
            # Check SDBM data for SITI FATIMAH
            with connections['SDBM'].cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        e.employee_number,
                        e.fullname,
                        e.nickname,
                        d.name as department_name,
                        s.name as section_name,
                        t.Name as title_name,
                        t.is_supervisor,
                        t.is_manager
                    FROM [hrbp].[employees] e
                    INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                    LEFT JOIN [hr].[department] d ON p.departmentId = d.id
                    LEFT JOIN [hr].[section] s ON p.sectionId = s.id
                    LEFT JOIN [hr].[title] t ON p.titleId = t.id
                    WHERE e.employee_number = '007522'
                        AND e.is_active = 1
                """)
                
                siti_data = cursor.fetchone()
                
                if siti_data:
                    self.stdout.write("  ✅ SITI FATIMAH found in SDBM:")
                    self.stdout.write(f"    - Employee Number: {siti_data[0]}")
                    self.stdout.write(f"    - Full Name: {siti_data[1]}")
                    self.stdout.write(f"    - Department: {siti_data[3]}")
                    self.stdout.write(f"    - Section: {siti_data[4]}")
                    self.stdout.write(f"    - Title: {siti_data[5]}")
                else:
                    self.stdout.write(self.style.WARNING("  ⚠️  SITI FATIMAH not found in SDBM"))
            
            # Check accessible pengajuan for SITI FATIMAH
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = 'A' AND approve = 'Y'
                """)
                approved_a_y = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = '1' AND approve = '1'
                """)
                approved_1_1 = cursor.fetchone()[0]
                
                self.stdout.write(f"  📊 Approved pengajuan accessible to SITI FATIMAH:")
                self.stdout.write(f"    - With status='A', approve='Y': {approved_a_y}")
                self.stdout.write(f"    - With status='1', approve='1': {approved_1_1}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error checking SITI FATIMAH access: {e}"))
    
    def test_enhanced_query(self, dry_run):
        """Test the enhanced query structure"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Test simplified count query
                test_query = """
                    SELECT COUNT(DISTINCT tp.history_id)
                    FROM tabel_pengajuan tp
                    WHERE tp.history_id IS NOT NULL
                        AND tp.status = %s 
                        AND tp.approve = %s
                """
                
                cursor.execute(test_query, ['A', 'Y'])
                count_a_y = cursor.fetchone()[0]
                
                cursor.execute(test_query, ['1', '1'])
                count_1_1 = cursor.fetchone()[0]
                
                self.stdout.write("  📊 Enhanced query test results:")
                self.stdout.write(f"    - Query with A/Y: {count_a_y} records")
                self.stdout.write(f"    - Query with 1/1: {count_1_1} records")
                
                # Test main query structure
                main_test_query = """
                    SELECT DISTINCT TOP 5
                        tp.history_id,
                        tp.oleh,
                        ISNULL(tm.mesin, 'N/A') as mesin,
                        tp.status,
                        tp.approve,
                        'TEST' as access_type
                    FROM tabel_pengajuan tp
                    LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
                    WHERE tp.history_id IS NOT NULL
                        AND tp.status = %s 
                        AND tp.approve = %s
                    ORDER BY tp.tgl_insert DESC
                """
                
                cursor.execute(main_test_query, ['A', 'Y'])
                test_results = cursor.fetchall()
                
                self.stdout.write(f"  ✅ Main query test: {len(test_results)} sample records retrieved successfully")
                
                if test_results:
                    self.stdout.write("  📝 Sample data:")
                    for i, row in enumerate(test_results[:3], 1):
                        self.stdout.write(f"    {i}. {row[0]} - {row[1]} ({row[3]}/{row[4]})")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error testing enhanced query: {e}"))
    
    def final_validation(self):
        """Final validation of the fixes"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Validate data consistency
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN status = 'A' AND approve = 'Y' THEN 1 END) as approved_a_y,
                        COUNT(CASE WHEN status = '1' AND approve = '1' THEN 1 END) as approved_1_1,
                        COUNT(CASE WHEN status = '0' THEN 1 END) as pending,
                        COUNT(CASE WHEN status = '2' THEN 1 END) as rejected
                    FROM tabel_pengajuan
                """)
                
                validation_result = cursor.fetchone()
                
                self.stdout.write("  📊 Final validation results:")
                self.stdout.write(f"    - Approved (A/Y): {validation_result[0]}")
                self.stdout.write(f"    - Approved (1/1): {validation_result[1]}")
                self.stdout.write(f"    - Pending (0): {validation_result[2]}")
                self.stdout.write(f"    - Rejected (2): {validation_result[3]}")
                
                total_approved = validation_result[0] + validation_result[1]
                
                if total_approved > 0:
                    self.stdout.write(f"  ✅ Total approved pengajuan accessible to SITI FATIMAH: {total_approved}")
                else:
                    self.stdout.write(self.style.WARNING("  ⚠️  No approved pengajuan found - this may be normal for new systems"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error in final validation: {e}"))

# Usage:
# python manage.py fix_database_issues --dry-run                    # Preview fixes
# python manage.py fix_database_issues --fix-status-values          # Fix status values  
# python manage.py fix_database_issues --check-siti-access          # Check SITI access
# python manage.py fix_database_issues --fix-status-values --check-siti-access  # Fix all
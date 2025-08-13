# wo_maintenance_app/management/commands/debug_review_button.py

from django.core.management.base import BaseCommand
from django.db import connections
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Debug dan Fix Review Button untuk SITI FATIMAH'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix issues found during debugging',
        )
        parser.add_argument(
            '--test-user',
            type=str,
            default='007522',
            help='Test specific user (default: 007522 - SITI FATIMAH)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output with detailed information',
        )
    
    def handle(self, *args, **options):
        fix_issues = options['fix']
        test_user = options['test_user']
        verbose = options['verbose']
        
        self.stdout.write(self.style.SUCCESS('=== Debug Review Button untuk SITI FATIMAH ==='))
        
        try:
            # 1. Check User Authentication
            self.stdout.write('\n1. Checking User Authentication...')
            self.check_user_authentication(test_user, verbose)
            
            # 2. Check Database Schema
            self.stdout.write('\n2. Checking Database Schema...')
            schema_issues = self.check_database_schema(verbose)
            
            # 3. Check Pengajuan Data
            self.stdout.write('\n3. Checking Pengajuan Data...')
            data_issues = self.check_pengajuan_data(verbose)
            
            # 4. Simulate Views Logic
            self.stdout.write('\n4. Simulating Views Logic...')
            view_issues = self.simulate_views_logic(test_user, verbose)
            
            # 5. Check Template Conditions
            self.stdout.write('\n5. Checking Template Conditions...')
            template_issues = self.check_template_conditions(verbose)
            
            # 6. Fix Issues if requested
            if fix_issues:
                self.stdout.write('\n6. Fixing Issues...')
                self.fix_found_issues(schema_issues, data_issues, view_issues)
            
            # 7. Final Test
            self.stdout.write('\n7. Final Test...')
            self.final_test(test_user)
            
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('✅ Debug completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error during debug: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())
    
    def check_user_authentication(self, test_user, verbose):
        """Check user authentication and SITI FATIMAH detection"""
        try:
            # Check Django user
            try:
                user = User.objects.get(username=test_user)
                self.stdout.write(f'  ✓ Django user {test_user} exists: {user.get_full_name() or user.username}')
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Django user {test_user} not found'))
            
            # Check SDBM employee data
            try:
                from wo_maintenance_app.utils import get_employee_hierarchy_data
                
                # Create mock request object
                class MockUser:
                    def __init__(self, username):
                        self.username = username
                        self.is_authenticated = True
                
                mock_user = MockUser(test_user)
                employee_data = get_employee_hierarchy_data(mock_user)
                
                if employee_data:
                    self.stdout.write(f'  ✓ SDBM employee data found:')
                    self.stdout.write(f'    Name: {employee_data.get("fullname")}')
                    self.stdout.write(f'    Employee Number: {employee_data.get("employee_number")}')
                    self.stdout.write(f'    Department: {employee_data.get("department_name")}')
                    self.stdout.write(f'    Title: {employee_data.get("title_name")}')
                    
                    # Check SITI FATIMAH detection
                    from wo_maintenance_app.utils import REVIEWER_EMPLOYEE_NUMBER
                    is_siti = employee_data.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER
                    self.stdout.write(f'    Is SITI FATIMAH: {is_siti}')
                    
                    if verbose:
                        self.stdout.write(f'    Full employee data: {employee_data}')
                else:
                    self.stdout.write(self.style.WARNING(f'  ⚠️  No SDBM employee data found for {test_user}'))
                    
            except Exception as sdbm_error:
                self.stdout.write(self.style.ERROR(f'  ❌ SDBM connection error: {sdbm_error}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ User authentication check error: {e}'))
    
    def check_database_schema(self, verbose):
        """Check database schema for review system"""
        issues = []
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Check review columns
                required_columns = ['review_status', 'reviewed_by', 'review_date', 'review_notes', 'final_section_id']
                
                for column in required_columns:
                    cursor.execute("""
                        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = %s
                    """, [column])
                    
                    if cursor.fetchone()[0] > 0:
                        self.stdout.write(f'  ✓ Column {column} exists')
                    else:
                        self.stdout.write(self.style.WARNING(f'  ❌ Column {column} missing'))
                        issues.append(f'missing_column_{column}')
                
                # Check data types
                cursor.execute("""
                    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'tabel_pengajuan' 
                        AND COLUMN_NAME IN ('status', 'approve', 'review_status')
                """)
                
                columns_info = cursor.fetchall()
                if verbose:
                    self.stdout.write('  Column details:')
                    for col_info in columns_info:
                        self.stdout.write(f'    {col_info[0]}: {col_info[1]}({col_info[2]}) NULL={col_info[3]}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Schema check error: {e}'))
            issues.append(f'schema_error_{str(e)}')
        
        return issues
    
    def check_pengajuan_data(self, verbose):
        """Check pengajuan data quality"""
        issues = []
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Check constants
                from wo_maintenance_app.utils import STATUS_APPROVED, APPROVE_YES, REVIEWER_EMPLOYEE_NUMBER
                
                self.stdout.write(f'  Constants:')
                self.stdout.write(f'    STATUS_APPROVED = "{STATUS_APPROVED}"')
                self.stdout.write(f'    APPROVE_YES = "{APPROVE_YES}"')
                self.stdout.write(f'    REVIEWER_EMPLOYEE_NUMBER = "{REVIEWER_EMPLOYEE_NUMBER}"')
                
                # Check pengajuan counts
                cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan")
                total_pengajuan = cursor.fetchone()[0]
                self.stdout.write(f'  📊 Total pengajuan: {total_pengajuan}')
                
                # Check status distribution
                cursor.execute("""
                    SELECT status, COUNT(*) 
                    FROM tabel_pengajuan 
                    WHERE status IS NOT NULL
                    GROUP BY status
                    ORDER BY COUNT(*) DESC
                """)
                status_dist = cursor.fetchall()
                self.stdout.write(f'  📊 Status distribution:')
                for status, count in status_dist:
                    self.stdout.write(f'    {status}: {count}')
                
                # Check approve distribution
                cursor.execute("""
                    SELECT approve, COUNT(*) 
                    FROM tabel_pengajuan 
                    WHERE approve IS NOT NULL
                    GROUP BY approve
                    ORDER BY COUNT(*) DESC
                """)
                approve_dist = cursor.fetchall()
                self.stdout.write(f'  📊 Approve distribution:')
                for approve, count in approve_dist:
                    self.stdout.write(f'    {approve}: {count}')
                
                # Check fully approved
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = %s AND approve = %s
                """, [STATUS_APPROVED, APPROVE_YES])
                fully_approved = cursor.fetchone()[0]
                self.stdout.write(f'  ✅ Fully approved (status=A, approve=Y): {fully_approved}')
                
                if fully_approved == 0:
                    issues.append('no_fully_approved_pengajuan')
                    self.stdout.write(self.style.WARNING('  ⚠️  No fully approved pengajuan found!'))
                
                # Check review status
                cursor.execute("""
                    SELECT review_status, COUNT(*) 
                    FROM tabel_pengajuan 
                    WHERE status = %s AND approve = %s
                    GROUP BY review_status
                """, [STATUS_APPROVED, APPROVE_YES])
                review_dist = cursor.fetchall()
                self.stdout.write(f'  📊 Review status for approved pengajuan:')
                for review_status, count in review_dist:
                    status_desc = {
                        None: 'NULL (needs initialization)',
                        '0': 'Pending Review',
                        '1': 'Reviewed (Processed)',
                        '2': 'Reviewed (Rejected)'
                    }.get(review_status, f'Unknown ({review_status})')
                    self.stdout.write(f'    {review_status}: {count} ({status_desc})')
                
                # Sample approved pengajuan
                if verbose and fully_approved > 0:
                    cursor.execute("""
                        SELECT TOP 5 history_id, oleh, status, approve, review_status, tgl_insert
                        FROM tabel_pengajuan 
                        WHERE status = %s AND approve = %s
                        ORDER BY tgl_insert DESC
                    """, [STATUS_APPROVED, APPROVE_YES])
                    
                    sample_data = cursor.fetchall()
                    self.stdout.write(f'  📋 Sample approved pengajuan:')
                    for row in sample_data:
                        self.stdout.write(f'    {row[0]} | {row[1]} | {row[2]}/{row[3]} | review:{row[4]} | {row[5]}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Data check error: {e}'))
            issues.append(f'data_error_{str(e)}')
        
        return issues
    
    def simulate_views_logic(self, test_user, verbose):
        """Simulate views logic untuk SITI FATIMAH"""
        issues = []
        
        try:
            # Simulate enhanced_daftar_laporan logic
            from wo_maintenance_app.utils import get_employee_hierarchy_data, REVIEWER_EMPLOYEE_NUMBER
            
            # Create mock user
            class MockUser:
                def __init__(self, username):
                    self.username = username
                    self.is_authenticated = True
            
            mock_user = MockUser(test_user)
            user_hierarchy = get_employee_hierarchy_data(mock_user)
            
            if not user_hierarchy:
                issues.append('no_user_hierarchy')
                self.stdout.write(self.style.WARNING(f'  ⚠️  No user hierarchy found for {test_user}'))
                return issues
            
            # Check SITI FATIMAH detection
            is_siti_fatimah = (
                user_hierarchy.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER or 
                mock_user.username == REVIEWER_EMPLOYEE_NUMBER or
                mock_user.username == '007522'
            )
            
            self.stdout.write(f'  🔍 SITI FATIMAH detection: {is_siti_fatimah}')
            
            if not is_siti_fatimah:
                issues.append('siti_detection_failed')
                self.stdout.write(self.style.WARNING('  ❌ SITI FATIMAH detection failed!'))
                self.stdout.write(f'    Employee number: {user_hierarchy.get("employee_number")}')
                self.stdout.write(f'    Expected: {REVIEWER_EMPLOYEE_NUMBER}')
                self.stdout.write(f'    Username: {mock_user.username}')
            
            # Simulate query logic
            if is_siti_fatimah:
                with connections['DB_Maintenance'].cursor() as cursor:
                    from wo_maintenance_app.utils import STATUS_APPROVED, APPROVE_YES
                    
                    # Test query untuk mode normal
                    cursor.execute("""
                        SELECT COUNT(*) FROM tabel_pengajuan 
                        WHERE status = %s AND approve = %s
                    """, [STATUS_APPROVED, APPROVE_YES])
                    approved_count = cursor.fetchone()[0]
                    
                    # Test query untuk pending review
                    cursor.execute("""
                        SELECT COUNT(*) FROM tabel_pengajuan 
                        WHERE status = %s AND approve = %s 
                            AND (review_status IS NULL OR review_status = '0')
                    """, [STATUS_APPROVED, APPROVE_YES])
                    pending_review_count = cursor.fetchone()[0]
                    
                    self.stdout.write(f'  📊 Query results for SITI FATIMAH:')
                    self.stdout.write(f'    Total approved: {approved_count}')
                    self.stdout.write(f'    Pending review: {pending_review_count}')
                    
                    if pending_review_count == 0 and approved_count > 0:
                        issues.append('no_pending_review_but_approved_exists')
                        self.stdout.write(self.style.WARNING('  ⚠️  No pending review but approved pengajuan exists'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Views simulation error: {e}'))
            issues.append(f'views_error_{str(e)}')
        
        return issues
    
    def check_template_conditions(self, verbose):
        """Check template conditions for review button"""
        issues = []
        
        try:
            # Simulate template logic
            self.stdout.write('  🎯 Template conditions for review button:')
            self.stdout.write('    Condition 1: is_siti_fatimah = True')
            self.stdout.write('    Condition 2: pengajuan.6 (status) = "A"')
            self.stdout.write('    Condition 3: pengajuan.11 (approve) = "Y"')
            self.stdout.write('    Condition 4: pengajuan.15 (review_status) = "0" or None')
            
            # Check sample pengajuan
            with connections['DB_Maintenance'].cursor() as cursor:
                from wo_maintenance_app.utils import STATUS_APPROVED, APPROVE_YES
                
                cursor.execute("""
                    SELECT TOP 3 
                        history_id,                    -- 0
                        oleh,                          -- 1
                        'N/A',                         -- 2 (mesin)
                        'N/A',                         -- 3 (section)
                        'N/A',                         -- 4 (pekerjaan)
                        deskripsi_perbaikan,           -- 5
                        status,                        -- 6
                        tgl_insert,                    -- 7
                        user_insert,                   -- 8
                        number_wo,                     -- 9
                        'N/A',                         -- 10 (line)
                        approve,                       -- 11
                        tgl_his,                       -- 12
                        jam_his,                       -- 13
                        status_pekerjaan,              -- 14
                        ISNULL(review_status, '0'),    -- 15
                        reviewed_by,                   -- 16
                        review_date,                   -- 17
                        'N/A',                         -- 18 (final_section)
                        'SITI_TEST'                    -- 19 (access_type)
                    FROM tabel_pengajuan 
                    WHERE status = %s AND approve = %s
                    ORDER BY tgl_insert DESC
                """, [STATUS_APPROVED, APPROVE_YES])
                
                sample_pengajuan = cursor.fetchall()
                
                if sample_pengajuan:
                    self.stdout.write('  📋 Sample pengajuan for template test:')
                    for pengajuan in sample_pengajuan:
                        history_id = pengajuan[0]
                        status = pengajuan[6]
                        approve = pengajuan[11]
                        review_status = pengajuan[15]
                        
                        # Template condition check
                        should_show_review = (
                            status == 'A' and 
                            approve == 'Y' and 
                            (review_status == '0' or review_status is None)
                        )
                        
                        self.stdout.write(f'    {history_id}: status={status}, approve={approve}, review_status={review_status} → Review button: {should_show_review}')
                        
                        if not should_show_review and status == 'A' and approve == 'Y':
                            issues.append(f'template_condition_failed_{history_id}')
                else:
                    issues.append('no_sample_pengajuan')
                    self.stdout.write(self.style.WARNING('  ⚠️  No sample pengajuan found for template test'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Template check error: {e}'))
            issues.append(f'template_error_{str(e)}')
        
        return issues
    
    def fix_found_issues(self, schema_issues, data_issues, view_issues):
        """Fix issues found during debugging"""
        try:
            # Fix schema issues
            if any('missing_column' in issue for issue in schema_issues):
                self.stdout.write('  🔧 Fixing missing columns...')
                self.fix_missing_columns()
            
            # Fix data issues
            if 'no_fully_approved_pengajuan' in data_issues:
                self.stdout.write('  🔧 No fix available for no approved pengajuan (create pengajuan manually)')
            
            if any('no_pending_review' in issue for issue in data_issues):
                self.stdout.write('  🔧 Initializing review data...')
                self.initialize_review_data()
            
            # Fix view issues
            if 'siti_detection_failed' in view_issues:
                self.stdout.write('  🔧 SITI FATIMAH detection issue needs manual verification')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Fix error: {e}'))
    
    def fix_missing_columns(self):
        """Fix missing review columns"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                columns_to_add = [
                    ('review_status', 'varchar(1)', 'NULL', 'DEFAULT \'0\''),
                    ('reviewed_by', 'varchar(50)', 'NULL', ''),
                    ('review_date', 'datetime', 'NULL', ''),
                    ('review_notes', 'varchar(max)', 'NULL', ''),
                    ('final_section_id', 'float', 'NULL', '')
                ]
                
                for column_name, data_type, nullable, default in columns_to_add:
                    try:
                        cursor.execute(f"""
                            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                          WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = '{column_name}')
                            BEGIN
                                ALTER TABLE tabel_pengajuan ADD {column_name} {data_type} {nullable} {default}
                            END
                        """)
                        self.stdout.write(f'    ✓ Column {column_name} added/verified')
                    except Exception as col_error:
                        self.stdout.write(self.style.WARNING(f'    ⚠️  Column {column_name} error: {col_error}'))
                        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'    ❌ Column fix error: {e}'))
    
    def initialize_review_data(self):
        """Initialize review data for approved pengajuan"""
        try:
            from wo_maintenance_app.utils import initialize_review_data
            
            success = initialize_review_data()
            if success:
                self.stdout.write('    ✓ Review data initialized successfully')
            else:
                self.stdout.write(self.style.WARNING('    ⚠️  Review data initialization failed'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'    ❌ Review initialization error: {e}'))
    
    def final_test(self, test_user):
        """Final test to verify review button should appear"""
        try:
            self.stdout.write('  🎯 Final Test - Review Button Visibility:')
            
            # Check all conditions
            from wo_maintenance_app.utils import get_employee_hierarchy_data, REVIEWER_EMPLOYEE_NUMBER, STATUS_APPROVED, APPROVE_YES
            
            class MockUser:
                def __init__(self, username):
                    self.username = username
                    self.is_authenticated = True
            
            mock_user = MockUser(test_user)
            user_hierarchy = get_employee_hierarchy_data(mock_user)
            
            # Test 1: User detection
            is_siti_fatimah = (
                user_hierarchy and user_hierarchy.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER
            ) or mock_user.username == REVIEWER_EMPLOYEE_NUMBER
            
            self.stdout.write(f'    ✓ SITI FATIMAH detection: {is_siti_fatimah}')
            
            # Test 2: Pengajuan availability
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = %s AND approve = %s 
                        AND (review_status IS NULL OR review_status = '0')
                """, [STATUS_APPROVED, APPROVE_YES])
                
                available_for_review = cursor.fetchone()[0]
                self.stdout.write(f'    ✓ Pengajuan available for review: {available_for_review}')
                
                # Test 3: Template conditions
                if available_for_review > 0:
                    cursor.execute("""
                        SELECT TOP 1 history_id, status, approve, review_status
                        FROM tabel_pengajuan 
                        WHERE status = %s AND approve = %s 
                            AND (review_status IS NULL OR review_status = '0')
                    """, [STATUS_APPROVED, APPROVE_YES])
                    
                    sample = cursor.fetchone()
                    if sample:
                        template_condition = (
                            is_siti_fatimah and 
                            sample[1] == 'A' and 
                            sample[2] == 'Y' and 
                            (sample[3] == '0' or sample[3] is None)
                        )
                        
                        self.stdout.write(f'    ✓ Template conditions met: {template_condition}')
                        self.stdout.write(f'      Sample: {sample[0]} (status={sample[1]}, approve={sample[2]}, review_status={sample[3]})')
                        
                        if template_condition:
                            self.stdout.write(self.style.SUCCESS('    🎯 SUCCESS: Review button should appear!'))
                        else:
                            self.stdout.write(self.style.ERROR('    ❌ FAIL: Review button will not appear'))
                    else:
                        self.stdout.write(self.style.WARNING('    ⚠️  No sample pengajuan available'))
                else:
                    self.stdout.write(self.style.WARNING('    ⚠️  No pengajuan available for review'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'    ❌ Final test error: {e}'))


# Usage:
# python manage.py debug_review_button --verbose
# python manage.py debug_review_button --fix
# python manage.py debug_review_button --test-user 007522 --verbose
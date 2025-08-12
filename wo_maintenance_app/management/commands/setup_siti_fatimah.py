# wo_maintenance_app/management/commands/setup_siti_fatimah.py
# Create directory: wo_maintenance_app/management/commands/

from django.core.management.base import BaseCommand
from django.db import connections
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Setup dan verifikasi user SITI FATIMAH untuk Review System'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Hanya check data tanpa membuat perubahan',
        )
        parser.add_argument(
            '--create-missing',
            action='store_true',
            help='Buat data yang missing di SDBM atau Django',
        )
    
    def handle(self, *args, **options):
        check_only = options['check_only']
        create_missing = options['create_missing']
        
        self.stdout.write(self.style.SUCCESS('=== SETUP SITI FATIMAH untuk Review System ==='))
        
        # 1. CEK DATA DI SDBM
        self.stdout.write('\n1. Checking SITI FATIMAH di database SDBM...')
        sdbm_data = self.check_sdbm_data()
        
        if sdbm_data:
            self.stdout.write(self.style.SUCCESS(f"  ✅ Found in SDBM: {sdbm_data['fullname']} - {sdbm_data['employee_number']}"))
            self.stdout.write(f"     Department: {sdbm_data['department_name']}")
            self.stdout.write(f"     Section: {sdbm_data['section_name']}")
            self.stdout.write(f"     Title: {sdbm_data['title_name']}")
            self.stdout.write(f"     Job Status: {sdbm_data['job_status']}")
        else:
            self.stdout.write(self.style.ERROR("  ❌ SITI FATIMAH not found in SDBM"))
            if create_missing:
                self.stdout.write("  Creating SITI FATIMAH in SDBM...")
                self.create_siti_fatimah_sdbm()
            else:
                self.stdout.write("  Use --create-missing to create missing data")
                return
        
        # 2. CEK USER DJANGO
        self.stdout.write('\n2. Checking Django User...')
        django_user = self.check_django_user()
        
        if django_user:
            self.stdout.write(self.style.SUCCESS(f"  ✅ Django User exists: {django_user.first_name} {django_user.last_name}"))
            self.stdout.write(f"     Username: {django_user.username}")
            self.stdout.write(f"     Active: {django_user.is_active}")
            self.stdout.write(f"     Staff: {django_user.is_staff}")
        else:
            self.stdout.write(self.style.ERROR("  ❌ Django User not found"))
            if create_missing:
                self.stdout.write("  Creating Django User...")
                self.create_django_user()
            else:
                self.stdout.write("  Use --create-missing to create missing user")
        
        # 3. CEK REVIEW SYSTEM
        self.stdout.write('\n3. Checking Review System setup...')
        review_setup = self.check_review_system()
        
        # 4. CEK PENGAJUAN READY FOR REVIEW
        self.stdout.write('\n4. Checking pengajuan ready for review...')
        self.check_pending_review()
        
        # 5. TEST AUTHENTICATION
        self.stdout.write('\n5. Testing SDBM Authentication...')
        if sdbm_data:
            self.test_authentication(sdbm_data)
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Setup completed! Next steps:'))
        self.stdout.write('1. Login dengan username: 007522')
        self.stdout.write('2. Navigate ke: /wo-maintenance/review/')
        self.stdout.write('3. Check pengajuan yang ready for review')
    
    def check_sdbm_data(self):
        """Check data SITI FATIMAH di SDBM"""
        try:
            with connections['SDBM'].cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        e.fullname, 
                        e.nickname, 
                        e.employee_number, 
                        e.level_user, 
                        e.job_status, 
                        e.pwd, 
                        e.created_date,
                        d.name as department_name,
                        s.name as section_name,
                        ss.name as subsection_name,
                        t.Name as title_name
                    FROM hrbp.employees e
                    LEFT JOIN hrbp.position p ON e.id = p.employeeId
                    LEFT JOIN hr.department d ON p.departmentId = d.id
                    LEFT JOIN hr.section s ON p.sectionId = s.id
                    LEFT JOIN hr.subsection ss ON p.subsectionId = ss.id
                    LEFT JOIN hr.title t ON p.titleId = t.id
                    WHERE e.is_active = 1 and e.employee_number = '007522'
                    ORDER BY e.employee_number desc
                """)
                
                row = cursor.fetchone()
                if row:
                    return {
                        'fullname': row[0],
                        'nickname': row[1], 
                        'employee_number': row[2],
                        'level_user': row[3],
                        'job_status': row[4],
                        'pwd': row[5],
                        'created_date': row[6],
                        'department_name': row[7],
                        'section_name': row[8],
                        'subsection_name': row[9],
                        'title_name': row[10]
                    }
                return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error checking SDBM: {e}"))
            return None
    
    def create_siti_fatimah_sdbm(self):
        """Create SITI FATIMAH di SDBM jika tidak ada"""
        try:
            with connections['SDBM'].cursor() as cursor:
                # Check if employee exists first
                cursor.execute("""
                    SELECT COUNT(*) FROM hrbp.employees 
                    WHERE employee_number = '007522'
                """)
                
                if cursor.fetchone()[0] > 0:
                    self.stdout.write("  Employee 007522 already exists in SDBM")
                    return
                
                # Insert employee (simplified - adjust based on your SDBM structure)
                self.stdout.write("  ⚠️  SITI FATIMAH not found in SDBM.")
                self.stdout.write("  Please contact HR/Admin to add employee 007522 to SDBM database")
                self.stdout.write("  Required data:")
                self.stdout.write("    - Employee Number: 007522")
                self.stdout.write("    - Full Name: SITI FATIMAH")
                self.stdout.write("    - Department: QC/QA (adjust as needed)")
                self.stdout.write("    - Title: REVIEWER/SUPERVISOR")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating SDBM data: {e}"))
    
    def check_django_user(self):
        """Check Django user"""
        try:
            return User.objects.get(username='007522')
        except User.DoesNotExist:
            return None
    
    def create_django_user(self):
        """Create Django user untuk SITI FATIMAH"""
        try:
            user = User.objects.create_user(
                username='007522',
                first_name='SITI',
                last_name='FATIMAH',
                password='007522',  # Default password
                is_active=True,
                is_staff=True
            )
            self.stdout.write(self.style.SUCCESS(f"  ✅ Created Django user: {user.username}"))
            self.stdout.write(self.style.WARNING("  ⚠️  Default password: 007522 (change this!)"))
            return user
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating Django user: {e}"))
            return None
    
    def check_review_system(self):
        """Check review system setup"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Check review columns
                cursor.execute("""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'tabel_pengajuan' 
                        AND COLUMN_NAME IN ('review_status', 'reviewed_by', 'review_date', 'final_section_id')
                """)
                
                review_columns = cursor.fetchone()[0]
                
                if review_columns >= 4:
                    self.stdout.write(self.style.SUCCESS("  ✅ Review system columns exist"))
                else:
                    self.stdout.write(self.style.ERROR(f"  ❌ Missing review columns ({review_columns}/4)"))
                    self.stdout.write("  Run: python manage.py setup_review_system")
                
                return review_columns >= 4
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error checking review system: {e}"))
            return False
    
    def check_pending_review(self):
        """Check pengajuan yang ready for review"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Count approved pengajuan yang belum review
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = '1' AND approve = '1' 
                        AND (review_status IS NULL OR review_status = '0')
                """)
                
                pending_count = cursor.fetchone()[0]
                
                if pending_count > 0:
                    self.stdout.write(self.style.SUCCESS(f"  ✅ Found {pending_count} pengajuan ready for review"))
                    
                    # Show sample
                    cursor.execute("""
                        SELECT TOP 5 history_id, oleh, tgl_insert 
                        FROM tabel_pengajuan 
                        WHERE status = '1' AND approve = '1' 
                            AND (review_status IS NULL OR review_status = '0')
                        ORDER BY tgl_insert ASC
                    """)
                    
                    samples = cursor.fetchall()
                    self.stdout.write("  Sample pengajuan ready for review:")
                    for sample in samples:
                        self.stdout.write(f"    - {sample[0]} by {sample[1]} on {sample[2]}")
                else:
                    self.stdout.write(self.style.WARNING("  ⚠️  No pengajuan ready for review"))
                    
                    # Check if any approved pengajuan exist
                    cursor.execute("""
                        SELECT COUNT(*) FROM tabel_pengajuan 
                        WHERE status = '1' AND approve = '1'
                    """)
                    
                    approved_count = cursor.fetchone()[0]
                    if approved_count > 0:
                        self.stdout.write(f"  Found {approved_count} approved pengajuan total")
                        self.stdout.write("  Initialize for review with:")
                        self.stdout.write("  UPDATE tabel_pengajuan SET review_status = '0' WHERE status = '1' AND approve = '1'")
                    else:
                        self.stdout.write("  No approved pengajuan found. Create and approve some pengajuan first.")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error checking pending review: {e}"))
    
    def test_authentication(self, sdbm_data):
        """Test SDBM authentication"""
        try:
            from django.contrib.auth import authenticate
            
            # Test dengan data yang ada
            if sdbm_data.get('pwd'):
                # Assume password is stored in SDBM (adjust based on your setup)
                self.stdout.write("  Testing authentication with SDBM password...")
                user = authenticate(username='007522', password=sdbm_data['pwd'])
                
                if user:
                    self.stdout.write(self.style.SUCCESS("  ✅ SDBM Authentication working"))
                else:
                    self.stdout.write(self.style.ERROR("  ❌ SDBM Authentication failed"))
            else:
                self.stdout.write("  ⚠️  No password in SDBM data - test with default password")
                
                # Test dengan default password
                user = authenticate(username='007522', password='007522')
                if user:
                    self.stdout.write(self.style.SUCCESS("  ✅ Default password authentication working"))
                else:
                    self.stdout.write(self.style.ERROR("  ❌ Default password authentication failed"))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error testing authentication: {e}"))


# USAGE:
# python manage.py setup_siti_fatimah --check-only      # Check current status
# python manage.py setup_siti_fatimah --create-missing  # Create missing data
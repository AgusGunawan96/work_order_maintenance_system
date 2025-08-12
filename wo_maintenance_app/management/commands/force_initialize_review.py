# wo_maintenance_app/management/commands/force_initialize_review.py

from django.core.management.base import BaseCommand
from django.db import connections
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Force initialize Review System untuk SITI FATIMAH - Emergency Fix'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix-all',
            action='store_true',
            help='Fix semua masalah yang ditemukan',
        )
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Hanya check tanpa melakukan perubahan',
        )
    
    def handle(self, *args, **options):
        fix_all = options['fix_all']
        check_only = options['check_only']
        
        self.stdout.write(self.style.SUCCESS('=== FORCE INITIALIZE REVIEW SYSTEM ==='))
        
        # 1. Check database structure
        self.stdout.write('\n1. Checking database structure...')
        review_columns_exist = self.check_review_columns()
        
        if not review_columns_exist:
            if fix_all:
                self.stdout.write('Adding missing review columns...')
                self.add_review_columns()
            else:
                self.stdout.write(self.style.ERROR('❌ Missing review columns. Use --fix-all to create them.'))
                return
        
        # 2. Check SITI FATIMAH user
        self.stdout.write('\n2. Checking SITI FATIMAH user...')
        user_exists = self.check_siti_fatimah_user()
        
        if not user_exists:
            if fix_all:
                self.stdout.write('Creating SITI FATIMAH user...')
                self.create_siti_fatimah_user()
            else:
                self.stdout.write(self.style.ERROR('❌ SITI FATIMAH user not found. Use --fix-all to create.'))
                return
        
        # 3. Initialize review data
        self.stdout.write('\n3. Initializing review data...')
        if fix_all or not check_only:
            initialized_count = self.initialize_review_data()
            self.stdout.write(self.style.SUCCESS(f'✅ Initialized {initialized_count} pengajuan for review'))
        
        # 4. Check URLs and views
        self.stdout.write('\n4. Checking URLs and views...')
        self.check_urls()
        
        # 5. Final verification
        self.stdout.write('\n5. Final verification...')
        self.final_verification()
        
        self.stdout.write('\n' + '='*60)
        if fix_all:
            self.stdout.write(self.style.SUCCESS('✅ EMERGENCY FIX COMPLETED!'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ CHECK COMPLETED!'))
        
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Login dengan username: 007522, password: 007522')
        self.stdout.write('2. Navigate ke: /wo-maintenance/review/')
        self.stdout.write('3. Verify pengajuan tampil untuk review')
    
    def check_review_columns(self):
        """Check apakah review columns sudah ada"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'tabel_pengajuan' 
                        AND COLUMN_NAME IN ('review_status', 'reviewed_by', 'review_date', 'review_notes', 'final_section_id')
                """)
                
                count = cursor.fetchone()[0]
                if count >= 5:
                    self.stdout.write(self.style.SUCCESS('  ✅ All review columns exist'))
                    return True
                else:
                    self.stdout.write(self.style.ERROR(f'  ❌ Missing review columns ({count}/5)'))
                    return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error checking columns: {e}'))
            return False
    
    def add_review_columns(self):
        """Add missing review columns"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                columns_to_add = [
                    "ALTER TABLE tabel_pengajuan ADD review_status varchar(1) DEFAULT '0'",
                    "ALTER TABLE tabel_pengajuan ADD reviewed_by varchar(50) NULL",
                    "ALTER TABLE tabel_pengajuan ADD review_date datetime NULL",
                    "ALTER TABLE tabel_pengajuan ADD review_notes varchar(max) NULL",
                    "ALTER TABLE tabel_pengajuan ADD final_section_id float NULL"
                ]
                
                for sql in columns_to_add:
                    try:
                        cursor.execute(sql)
                        self.stdout.write(f'  ✅ Added column: {sql.split()[3]}')
                    except Exception as e:
                        if 'already exists' in str(e) or 'duplicate' in str(e).lower():
                            self.stdout.write(f'  ⚠️  Column already exists: {sql.split()[3]}')
                        else:
                            self.stdout.write(f'  ❌ Error adding column: {e}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error adding columns: {e}'))
    
    def check_siti_fatimah_user(self):
        """Check apakah user SITI FATIMAH sudah ada"""
        try:
            user = User.objects.get(username='007522')
            self.stdout.write(self.style.SUCCESS(f'  ✅ User found: {user.first_name} {user.last_name}'))
            self.stdout.write(f'     Active: {user.is_active}, Staff: {user.is_staff}')
            return True
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('  ❌ User SITI FATIMAH (007522) not found'))
            return False
    
    def create_siti_fatimah_user(self):
        """Create user SITI FATIMAH"""
        try:
            user = User.objects.create_user(
                username='007522',
                first_name='SITI',
                last_name='FATIMAH',
                password='007522',
                is_active=True,
                is_staff=True
            )
            self.stdout.write(self.style.SUCCESS(f'  ✅ Created user: {user.username}'))
            self.stdout.write(self.style.WARNING('  ⚠️  Default password: 007522'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error creating user: {e}'))
    
    def initialize_review_data(self):
        """Initialize pengajuan untuk review"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Set semua approved pengajuan untuk review
                cursor.execute("""
                    UPDATE tabel_pengajuan 
                    SET review_status = '0'
                    WHERE status = '1' AND approve = '1' 
                        AND (review_status IS NULL OR review_status = '' OR review_status = '0')
                """)
                
                count = cursor.rowcount
                return count
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error initializing review data: {e}'))
            return 0
    
    def check_urls(self):
        """Check apakah URLs sudah dikonfigurasi"""
        try:
            from django.urls import reverse
            
            urls_to_check = [
                'wo_maintenance_app:review_dashboard',
                'wo_maintenance_app:review_pengajuan_list',
            ]
            
            for url_name in urls_to_check:
                try:
                    url = reverse(url_name)
                    self.stdout.write(self.style.SUCCESS(f'  ✅ URL exists: {url_name} -> {url}'))
                except Exception:
                    self.stdout.write(self.style.ERROR(f'  ❌ URL missing: {url_name}'))
                    self.stdout.write('     Add to urls.py:')
                    if 'dashboard' in url_name:
                        self.stdout.write("     path('review/', views.review_dashboard, name='review_dashboard'),")
                    elif 'list' in url_name:
                        self.stdout.write("     path('review/pengajuan/', views.review_pengajuan_list, name='review_pengajuan_list'),")
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error checking URLs: {e}'))
    
    def final_verification(self):
        """Final verification - count ready pengajuan"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Count approved pengajuan
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = '1' AND approve = '1'
                """)
                total_approved = cursor.fetchone()[0]
                
                # Count ready for review
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = '1' AND approve = '1' 
                        AND review_status = '0'
                """)
                ready_for_review = cursor.fetchone()[0]
                
                self.stdout.write(f'  📊 Total approved pengajuan: {total_approved}')
                self.stdout.write(f'  📋 Ready for review: {ready_for_review}')
                
                if ready_for_review > 0:
                    # Show sample
                    cursor.execute("""
                        SELECT TOP 3 history_id, oleh, tgl_insert 
                        FROM tabel_pengajuan 
                        WHERE status = '1' AND approve = '1' AND review_status = '0'
                        ORDER BY tgl_insert ASC
                    """)
                    
                    samples = cursor.fetchall()
                    self.stdout.write('  📝 Sample pengajuan ready for review:')
                    for sample in samples:
                        self.stdout.write(f'     - {sample[0]} by {sample[1]} on {sample[2]}')
                
                # Test SDBM connection
                try:
                    with connections['SDBM'].cursor() as sdbm_cursor:
                        sdbm_cursor.execute("""
                            SELECT fullname FROM hrbp.employees 
                            WHERE employee_number = '007522' AND is_active = 1
                        """)
                        sdbm_result = sdbm_cursor.fetchone()
                        
                        if sdbm_result:
                            self.stdout.write(self.style.SUCCESS(f'  ✅ SDBM connection OK: Found {sdbm_result[0]}'))
                        else:
                            self.stdout.write(self.style.ERROR('  ❌ SITI FATIMAH not found in SDBM'))
                            self.stdout.write('     Contact HR to add employee 007522 to SDBM')
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ❌ SDBM connection error: {e}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error in final verification: {e}'))


# USAGE:
# python manage.py force_initialize_review --check-only     # Check current status
# python manage.py force_initialize_review --fix-all       # Fix all issues
# python manage.py force_initialize_review                 # Initialize review data only
# wo_maintenance_app/management/commands/setup_user_007522.py
# Create directory: wo_maintenance_app/management/commands/

from django.core.management.base import BaseCommand
from django.db import connections
from django.contrib.auth.models import User
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Setup user 007522 (SITI FATIMAH) untuk akses approved pengajuan'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-user',
            action='store_true',
            help='Create Django user jika belum ada',
        )
        parser.add_argument(
            '--test-data',
            action='store_true',
            help='Create sample approved data untuk testing',
        )
    
    def handle(self, *args, **options):
        create_user = options['create_user']
        test_data = options['test_data']
        
        self.stdout.write(self.style.SUCCESS('=== SETUP USER 007522 (SITI FATIMAH) ==='))
        
        # 1. CHECK EXISTING USER
        self.stdout.write('\n1. Checking Django user 007522...')
        user_exists = self.check_user()
        
        if not user_exists and create_user:
            self.stdout.write('Creating user 007522...')
            self.create_user()
        elif not user_exists:
            self.stdout.write(self.style.WARNING('User 007522 not found. Use --create-user to create.'))
        
        # 2. CHECK PENGAJUAN DATA
        self.stdout.write('\n2. Checking pengajuan data...')
        stats = self.check_pengajuan_data()
        
        # 3. CREATE TEST DATA
        if test_data:
            self.stdout.write('\n3. Creating test approved data...')
            self.create_test_data()
        
        # 4. SHOW RESULTS
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✅ Setup completed!'))
        self.stdout.write('')
        self.stdout.write('🔗 Access URLs:')
        self.stdout.write('  Normal Mode: /wo-maintenance/daftar/?mode=normal')
        self.stdout.write('  Approved Mode: /wo-maintenance/daftar/?mode=approved')
        self.stdout.write('')
        self.stdout.write('👤 Login credentials:')
        self.stdout.write('  Username: 007522')
        self.stdout.write('  Password: 007522 (default - please change)')
        
        if stats:
            self.stdout.write('')
            self.stdout.write('📊 Current Stats:')
            self.stdout.write(f'  Total Approved: {stats.get("total_approved", 0)}')
            self.stdout.write(f'  Pending Review: {stats.get("pending_review", 0)}')
    
    def check_user(self):
        """Check if user 007522 exists"""
        try:
            user = User.objects.get(username='007522')
            self.stdout.write(self.style.SUCCESS(f'  ✅ User exists: {user.first_name} {user.last_name}'))
            self.stdout.write(f'     Active: {user.is_active}, Staff: {user.is_staff}')
            return True
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('  ⚠️  User 007522 not found'))
            return False
    
    def create_user(self):
        """Create user 007522"""
        try:
            user = User.objects.create_user(
                username='007522',
                first_name='SITI',
                last_name='FATIMAH',
                password='007522',
                is_active=True,
                is_staff=True
            )
            self.stdout.write(self.style.SUCCESS('  ✅ User 007522 created successfully'))
            self.stdout.write('  ⚠️  Default password: 007522')
            return user
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error creating user: {e}'))
            return None
    
    def check_pengajuan_data(self):
        """Check pengajuan statistics"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Total pengajuan
                cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE history_id IS NOT NULL")
                total_pengajuan = cursor.fetchone()[0] or 0
                
                # Total approved
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = '1' AND approve = '1'
                """)
                total_approved = cursor.fetchone()[0] or 0
                
                # Pending review
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = '1' AND approve = '1' 
                        AND (review_status IS NULL OR review_status = '0')
                """)
                pending_review = cursor.fetchone()[0] or 0
                
                stats = {
                    'total_pengajuan': total_pengajuan,
                    'total_approved': total_approved,
                    'pending_review': pending_review
                }
                
                self.stdout.write(self.style.SUCCESS(f'  ✅ Database connection OK'))
                self.stdout.write(f'     Total Pengajuan: {total_pengajuan}')
                self.stdout.write(f'     Total Approved: {total_approved}')
                self.stdout.write(f'     Pending Review: {pending_review}')
                
                return stats
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Database error: {e}'))
            return None
    
    def create_test_data(self):
        """Create sample approved data"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Set beberapa pengajuan sebagai approved untuk testing
                cursor.execute("""
                    UPDATE TOP (5) tabel_pengajuan 
                    SET status = '1', approve = '1'
                    WHERE history_id IS NOT NULL 
                        AND (status != '1' OR approve != '1')
                """)
                
                updated_count = cursor.rowcount
                
                if updated_count > 0:
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Created {updated_count} approved pengajuan for testing'))
                else:
                    self.stdout.write('  ℹ️  No pengajuan updated (possibly already approved)')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error creating test data: {e}'))


# USAGE:
# python manage.py setup_user_007522                    # Check status
# python manage.py setup_user_007522 --create-user      # Create user if not exists  
# python manage.py setup_user_007522 --create-user --test-data  # Full setup with test data
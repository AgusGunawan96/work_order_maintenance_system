# wo_maintenance_app/management/commands/setup_enhanced_review.py

from django.core.management.base import BaseCommand
from django.db import connections
from django.contrib.auth.models import User
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Setup Enhanced Review System dengan Process/Reject dan Section Selection'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--full-setup',
            action='store_true',
            help='Full setup: tables, user, data initialization',
        )
        parser.add_argument(
            '--update-tables',
            action='store_true',
            help='Update tables dengan enhanced review columns',
        )
        parser.add_argument(
            '--test-sections',
            action='store_true',
            help='Test dan display section mapping',
        )
        parser.add_argument(
            '--migrate-data',
            action='store_true',
            help='Migrate existing review data ke enhanced format',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== ENHANCED REVIEW SYSTEM SETUP ==='))
        
        if options['full_setup']:
            self.stdout.write('\n🚀 Full Setup Mode')
            self.update_tables()
            self.setup_user_007522()
            self.test_section_mapping()
            self.migrate_existing_data()
            
        elif options['update_tables']:
            self.stdout.write('\n📊 Updating Tables')
            self.update_tables()
            
        elif options['test_sections']:
            self.stdout.write('\n🔍 Testing Section Mapping')
            self.test_section_mapping()
            
        elif options['migrate_data']:
            self.stdout.write('\n🔄 Migrating Data')
            self.migrate_existing_data()
        else:
            self.show_help()
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ Enhanced Review System Ready!'))
        self.show_usage_info()
    
    def update_tables(self):
        """Update database tables untuk enhanced review"""
        self.stdout.write('\n1. Updating database tables...')
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Add enhanced columns to review log
                self.stdout.write('  Adding target_section column...')
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                  WHERE TABLE_NAME = 'tabel_review_log' AND COLUMN_NAME = 'target_section')
                    BEGIN
                        ALTER TABLE tabel_review_log ADD target_section varchar(20) NULL
                    END
                """)
                
                # Update existing review status values untuk clarity
                self.stdout.write('  Updating review status descriptions...')
                cursor.execute("""
                    -- Status '1' = Processed (bukan Approved)
                    -- Status '2' = Rejected
                    -- No direct update needed, just documentation
                """)
                
                self.stdout.write(self.style.SUCCESS('  ✅ Tables updated successfully'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error updating tables: {e}'))
    
    def setup_user_007522(self):
        """Setup user 007522 SITI FATIMAH"""
        self.stdout.write('\n2. Setting up user 007522 (SITI FATIMAH)...')
        
        try:
            user, created = User.objects.get_or_create(
                username='007522',
                defaults={
                    'first_name': 'SITI',
                    'last_name': 'FATIMAH',
                    'is_active': True,
                    'is_staff': True
                }
            )
            
            if created:
                user.set_password('007522')
                user.save()
                self.stdout.write(self.style.SUCCESS('  ✅ User 007522 created'))
            else:
                user.is_active = True
                user.is_staff = True
                user.save()
                self.stdout.write(self.style.SUCCESS('  ✅ User 007522 updated'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error with user: {e}'))
    
    def test_section_mapping(self):
        """Test section mapping untuk IT, Elektrik, Utility, Mekanik"""
        self.stdout.write('\n3. Testing section mapping...')
        
        try:
            mapping_results = {}
            
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT id_section, seksi 
                    FROM tabel_msection 
                    WHERE (status = 'A' OR status IS NULL) AND seksi IS NOT NULL
                    ORDER BY seksi
                """)
                
                sections = cursor.fetchall()
                self.stdout.write(f'  Found {len(sections)} total sections')
                
                # Test mapping
                for section_id, section_name in sections:
                    section_name_upper = str(section_name).strip().upper()
                    
                    if any(keyword in section_name_upper for keyword in ['IT', 'INFORMATION', 'SYSTEM', 'TEKNOLOGI']):
                        mapping_results['💻 IT'] = mapping_results.get('💻 IT', []) + [(section_id, section_name)]
                    elif any(keyword in section_name_upper for keyword in ['ELEKTRIK', 'ELECTRIC', 'LISTRIK']):
                        mapping_results['⚡ Elektrik'] = mapping_results.get('⚡ Elektrik', []) + [(section_id, section_name)]
                    elif any(keyword in section_name_upper for keyword in ['UTILITY', 'UTILITIES', 'UMUM']):
                        mapping_results['🏭 Utility'] = mapping_results.get('🏭 Utility', []) + [(section_id, section_name)]
                    elif any(keyword in section_name_upper for keyword in ['MEKANIK', 'MECHANIC', 'MECHANICAL']):
                        mapping_results['🔧 Mekanik'] = mapping_results.get('🔧 Mekanik', []) + [(section_id, section_name)]
                
                # Display results
                for category, sections in mapping_results.items():
                    self.stdout.write(f'  {category}: {len(sections)} sections')
                    for section_id, section_name in sections[:2]:  # Show first 2
                        self.stdout.write(f'    - {section_id}: {section_name}')
                    if len(sections) > 2:
                        self.stdout.write(f'    ... and {len(sections)-2} more')
                
                self.stdout.write(self.style.SUCCESS('  ✅ Section mapping tested'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error testing mapping: {e}'))
    
    def migrate_existing_data(self):
        """Migrate existing review data ke enhanced format"""
        self.stdout.write('\n4. Migrating existing review data...')
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Update existing approved reviews to "processed"
                cursor.execute("""
                    UPDATE tabel_pengajuan 
                    SET review_status = '1'
                    WHERE review_status = '1' AND reviewed_by = '007522'
                """)
                
                # Count migrations
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN review_status = '1' THEN 1 END) as processed,
                        COUNT(CASE WHEN review_status = '2' THEN 1 END) as rejected,
                        COUNT(CASE WHEN review_status = '0' OR review_status IS NULL THEN 1 END) as pending
                    FROM tabel_pengajuan 
                    WHERE status = '1' AND approve = '1'
                """)
                
                stats = cursor.fetchone()
                processed, rejected, pending = stats
                
                self.stdout.write(f'  📊 Migration Summary:')
                self.stdout.write(f'    Processed: {processed}')
                self.stdout.write(f'    Rejected: {rejected}')
                self.stdout.write(f'    Pending: {pending}')
                
                self.stdout.write(self.style.SUCCESS('  ✅ Data migration completed'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error migrating data: {e}'))
    
    def show_help(self):
        """Show help information"""
        self.stdout.write('\n📖 Available Options:')
        self.stdout.write('  --full-setup     : Complete setup (recommended)')
        self.stdout.write('  --update-tables  : Update database tables only')
        self.stdout.write('  --test-sections  : Test section mapping')
        self.stdout.write('  --migrate-data   : Migrate existing data')
        self.stdout.write('\n💡 Example: python manage.py setup_enhanced_review --full-setup')
    
    def show_usage_info(self):
        """Show usage information"""
        self.stdout.write('\n🎯 Enhanced Review Features:')
        self.stdout.write('  ✅ Process Pengajuan (dengan optional section selection)')
        self.stdout.write('  ❌ Reject Pengajuan')
        self.stdout.write('  💻 IT Section')
        self.stdout.write('  ⚡ Elektrik Section')
        self.stdout.write('  🏭 Utility Section')
        self.stdout.write('  🔧 Mekanik Section')
        
        self.stdout.write('\n🔗 Access URLs:')
        self.stdout.write('  Review Dashboard: /wo-maintenance/review/dashboard/')
        self.stdout.write('  Review List: /wo-maintenance/review/pengajuan/')
        self.stdout.write('  Enhanced Daftar: /wo-maintenance/daftar/?mode=approved')
        
        self.stdout.write('\n👤 Login Info:')
        self.stdout.write('  Username: 007522')
        self.stdout.write('  Password: 007522 (change after first login)')
        
        self.stdout.write('\n📋 Review Process:')
        self.stdout.write('  1. SITI FATIMAH login sebagai 007522')
        self.stdout.write('  2. Akses review list untuk lihat pending review')
        self.stdout.write('  3. Pilih "Process Pengajuan" atau "Reject"')
        self.stdout.write('  4. Optional: Pilih section tujuan (IT/Elektrik/Utility/Mekanik)')
        self.stdout.write('  5. Submit review dengan catatan')


# USAGE EXAMPLES:
# python manage.py setup_enhanced_review --full-setup
# python manage.py setup_enhanced_review --update-tables
# python manage.py setup_enhanced_review --test-sections
# python manage.py setup_enhanced_review --migrate-data
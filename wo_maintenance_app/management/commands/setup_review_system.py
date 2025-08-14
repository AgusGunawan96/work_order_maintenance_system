# wo_maintenance_app/management/commands/setup_review_system.py

from django.core.management.base import BaseCommand
from django.db import connections
from django.contrib.auth.models import User
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Setup Review System untuk SITI FATIMAH (007522) dengan section selection'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-tables',
            action='store_true',
            help='Create review tables jika belum ada',
        )
        parser.add_argument(
            '--init-data',
            action='store_true',
            help='Initialize approved pengajuan untuk review',
        )
        parser.add_argument(
            '--test-sections',
            action='store_true',
            help='Test section data untuk distribusi',
        )
        parser.add_argument(
            '--create-user',
            action='store_true',
            help='Create user 007522 jika belum ada',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== SETUP REVIEW SYSTEM SITI FATIMAH ==='))
        
        # 1. CHECK/CREATE USER 007522
        if options['create_user']:
            self.stdout.write('\n1. Setting up user 007522 (SITI FATIMAH)...')
            self.setup_user_007522()
        
        # 2. CREATE REVIEW TABLES
        if options['create_tables']:
            self.stdout.write('\n2. Creating review tables...')
            self.create_review_tables()
        
        # 3. TEST SECTION DATA
        if options['test_sections']:
            self.stdout.write('\n3. Testing section data...')
            self.test_section_data()
        
        # 4. INITIALIZE DATA
        if options['init_data']:
            self.stdout.write('\n4. Initializing approved pengajuan for review...')
            self.init_review_data()
        
        # 5. SHOW SUMMARY
        self.stdout.write('\n5. System Summary...')
        self.show_system_summary()
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✅ Review System Setup Completed!'))
        self.stdout.write('')
        self.stdout.write('🎯 SITI FATIMAH (007522) can now:')
        self.stdout.write('  • Review approved pengajuan')
        self.stdout.write('  • Select final section for distribution')
        self.stdout.write('  • Auto-assign to section supervisors')
        self.stdout.write('')
        self.stdout.write('🔗 Access URLs:')
        self.stdout.write('  Review Dashboard: /wo-maintenance/review/dashboard/')
        self.stdout.write('  Review List: /wo-maintenance/review/pengajuan/')
        self.stdout.write('  Daftar Mode Approved: /wo-maintenance/daftar/?mode=approved')
    
    def setup_user_007522(self):
        """Setup user 007522 SITI FATIMAH"""
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
                self.stdout.write(self.style.SUCCESS('  ✅ User 007522 created successfully'))
                self.stdout.write('  🔑 Default password: 007522')
            else:
                self.stdout.write(self.style.SUCCESS('  ✅ User 007522 already exists'))
            
            # Ensure user is active and staff
            if not user.is_active or not user.is_staff:
                user.is_active = True
                user.is_staff = True
                user.save()
                self.stdout.write('  🔄 Updated user permissions')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error setting up user: {e}'))
    
    def create_review_tables(self):
        """Create review tables"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # 1. Add review columns to tabel_pengajuan
                self.stdout.write('  Creating review columns...')
                
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                  WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = 'review_status')
                    BEGIN
                        ALTER TABLE tabel_pengajuan ADD review_status varchar(1) NULL DEFAULT '0'
                    END
                """)
                
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                  WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = 'reviewed_by')
                    BEGIN
                        ALTER TABLE tabel_pengajuan ADD reviewed_by varchar(50) NULL
                    END
                """)
                
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                  WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = 'review_date')
                    BEGIN
                        ALTER TABLE tabel_pengajuan ADD review_date datetime NULL
                    END
                """)
                
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                  WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = 'review_notes')
                    BEGIN
                        ALTER TABLE tabel_pengajuan ADD review_notes varchar(max) NULL
                    END
                """)
                
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                  WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = 'final_section_id')
                    BEGIN
                        ALTER TABLE tabel_pengajuan ADD final_section_id float NULL
                    END
                """)
                
                # 2. Create review log table
                self.stdout.write('  Creating review log table...')
                
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tabel_review_log' AND xtype='U')
                    BEGIN
                        CREATE TABLE [dbo].[tabel_review_log](
                            [id] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
                            [history_id] [varchar](15) NULL,
                            [reviewer_employee] [varchar](50) NULL,
                            [action] [varchar](10) NULL,
                            [final_section_id] [float] NULL,
                            [review_notes] [varchar](max) NULL,
                            [review_date] [datetime] NULL,
                            [priority_level] [varchar](20) NULL DEFAULT 'normal'
                        )
                    END
                """)
                
                # 3. Create assignment table  
                self.stdout.write('  Creating assignment table...')
                
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tabel_pengajuan_assignment' AND xtype='U')
                    BEGIN
                        CREATE TABLE [dbo].[tabel_pengajuan_assignment](
                            [id] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
                            [history_id] [varchar](15) NULL,
                            [assigned_to_employee] [varchar](50) NULL,
                            [assigned_by_employee] [varchar](50) NULL,
                            [assignment_date] [datetime] NULL,
                            [notes] [varchar](max) NULL,
                            [assignment_type] [varchar](20) NULL DEFAULT 'MANUAL',
                            [is_active] [bit] NULL DEFAULT 1
                        )
                    END
                """)
                
                self.stdout.write(self.style.SUCCESS('  ✅ Review tables created successfully'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error creating tables: {e}'))
    
    def test_section_data(self):
        """Test available sections for distribution"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT id_section, seksi 
                    FROM tabel_msection 
                    WHERE (status = 'A' OR status IS NULL) AND seksi IS NOT NULL
                    ORDER BY seksi
                """)
                
                sections = cursor.fetchall()
                self.stdout.write(f'  Found {len(sections)} available sections:')
                
                # Categorize sections
                categories = {
                    'IT': [],
                    'Elektrik': [],
                    'Mekanik': [],
                    'Utility': [],
                    'Other': []
                }
                
                for section in sections:
                    section_id = int(float(section[0]))
                    section_name = str(section[1]).strip()
                    
                    # Categorize
                    if any(keyword in section_name.upper() for keyword in ['IT', 'INFORMATION', 'SYSTEM']):
                        categories['IT'].append((section_id, section_name))
                    elif any(keyword in section_name.upper() for keyword in ['ELEKTRIK', 'ELECTRIC', 'LISTRIK']):
                        categories['Elektrik'].append((section_id, section_name))
                    elif any(keyword in section_name.upper() for keyword in ['MEKANIK', 'MECHANIC', 'MECHANICAL']):
                        categories['Mekanik'].append((section_id, section_name))
                    elif any(keyword in section_name.upper() for keyword in ['UTILITY', 'UTILITIES', 'UMUM']):
                        categories['Utility'].append((section_id, section_name))
                    else:
                        categories['Other'].append((section_id, section_name))
                
                # Display by category
                for category, sections in categories.items():
                    if sections:
                        icon = {'IT': '💻', 'Elektrik': '⚡', 'Mekanik': '🔧', 'Utility': '🏭', 'Other': '📋'}[category]
                        self.stdout.write(f'    {icon} {category} ({len(sections)}):')
                        for section_id, section_name in sections[:3]:  # Show first 3
                            self.stdout.write(f'      {section_id}: {section_name}')
                        if len(sections) > 3:
                            self.stdout.write(f'      ... and {len(sections)-3} more')
                
                self.stdout.write(self.style.SUCCESS('  ✅ Section data test completed'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error testing sections: {e}'))
    
    def init_review_data(self):
        """Initialize approved pengajuan for review"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Initialize approved pengajuan for review
                cursor.execute("""
                    UPDATE tabel_pengajuan 
                    SET review_status = '0'
                    WHERE status = '1' AND approve = '1' 
                        AND (review_status IS NULL OR review_status = '')
                """)
                
                updated_count = cursor.rowcount
                self.stdout.write(f'  ✅ Initialized {updated_count} approved pengajuan for review')
                
                # Get some stats
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = '1' AND approve = '1' AND review_status = '0'
                """)
                pending_review = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = '1' AND approve = '1'
                """)
                total_approved = cursor.fetchone()[0]
                
                self.stdout.write(f'  📊 Pending Review: {pending_review}/{total_approved} approved pengajuan')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error initializing data: {e}'))
    
    def show_system_summary(self):
        """Show system summary"""
        try:
            # Check user
            try:
                user = User.objects.get(username='007522')
                user_status = f"✅ Active (Staff: {user.is_staff})"
            except User.DoesNotExist:
                user_status = "❌ Not Found"
            
            # Check tables
            tables_status = {}
            try:
                with connections['DB_Maintenance'].cursor() as cursor:
                    # Check review columns
                    cursor.execute("""
                        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = 'review_status'
                    """)
                    tables_status['review_columns'] = "✅ Exists" if cursor.fetchone()[0] > 0 else "❌ Missing"
                    
                    # Check review log table
                    cursor.execute("""
                        SELECT COUNT(*) FROM sysobjects WHERE name='tabel_review_log' AND xtype='U'
                    """)
                    tables_status['review_log'] = "✅ Exists" if cursor.fetchone()[0] > 0 else "❌ Missing"
                    
                    # Check assignment table
                    cursor.execute("""
                        SELECT COUNT(*) FROM sysobjects WHERE name='tabel_pengajuan_assignment' AND xtype='U'
                    """)
                    tables_status['assignment_table'] = "✅ Exists" if cursor.fetchone()[0] > 0 else "❌ Missing"
                    
                    # Check data
                    cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE status = '1' AND approve = '1'")
                    total_approved = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE review_status = '0'")
                    pending_review = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(DISTINCT id_section) FROM tabel_msection WHERE (status = 'A' OR status IS NULL)")
                    available_sections = cursor.fetchone()[0]
                    
            except Exception as e:
                tables_status['error'] = f"❌ Database Error: {e}"
            
            # Display summary
            self.stdout.write('  📋 System Status:')
            self.stdout.write(f'    User 007522: {user_status}')
            for table, status in tables_status.items():
                self.stdout.write(f'    {table}: {status}')
            
            if 'error' not in tables_status:
                self.stdout.write('')
                self.stdout.write('  📊 Data Summary:')
                self.stdout.write(f'    Total Approved: {total_approved}')
                self.stdout.write(f'    Pending Review: {pending_review}')
                self.stdout.write(f'    Available Sections: {available_sections}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error getting summary: {e}'))


# USAGE EXAMPLES:
# python manage.py setup_review_system --create-tables --create-user
# python manage.py setup_review_system --init-data --test-sections  
# python manage.py setup_review_system --create-tables --create-user --init-data --test-sections
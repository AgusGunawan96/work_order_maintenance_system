# wo_maintenance_app/management/commands/setup_review_system.py
# Create this directory structure: wo_maintenance_app/management/commands/

from django.core.management.base import BaseCommand
from django.db import connections
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Setup Review System Database Tables and Initialize Data for SITI FATIMAH'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force execution even if tables already exist',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS('=== Setting up Review System for SITI FATIMAH ==='))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No actual changes will be made'))
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # 1. Add review columns to tabel_pengajuan
                self.stdout.write('1. Checking tabel_pengajuan columns...')
                
                review_columns = [
                    {
                        'name': 'review_status',
                        'type': 'varchar(1)',
                        'default': "'0'",
                        'description': '0=Pending Review, 1=Reviewed Approved, 2=Reviewed Rejected'
                    },
                    {
                        'name': 'reviewed_by',
                        'type': 'varchar(50)',
                        'default': 'NULL',
                        'description': 'Employee number of reviewer (007522)'
                    },
                    {
                        'name': 'review_date',
                        'type': 'datetime',
                        'default': 'NULL',
                        'description': 'Date when review was completed'
                    },
                    {
                        'name': 'review_notes',
                        'type': 'varchar(max)',
                        'default': 'NULL',
                        'description': 'Review notes from reviewer'
                    },
                    {
                        'name': 'final_section_id',
                        'type': 'float',
                        'default': 'NULL',
                        'description': 'Final section assigned by reviewer'
                    }
                ]
                
                for column in review_columns:
                    # Check if column exists
                    cursor.execute("""
                        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = %s
                    """, [column['name']])
                    
                    exists = cursor.fetchone()[0] > 0
                    
                    if not exists or force:
                        sql = f"""
                            ALTER TABLE tabel_pengajuan 
                            ADD {column['name']} {column['type']} DEFAULT {column['default']}
                        """
                        
                        if dry_run:
                            self.stdout.write(f"  Would add column: {column['name']} ({column['description']})")
                        else:
                            try:
                                if not exists:
                                    cursor.execute(sql)
                                    self.stdout.write(
                                        self.style.SUCCESS(f"  ✅ Added column: {column['name']}")
                                    )
                                else:
                                    self.stdout.write(f"  ⚠️  Column {column['name']} already exists (forced)")
                            except Exception as e:
                                self.stdout.write(
                                    self.style.ERROR(f"  ❌ Failed to add {column['name']}: {e}")
                                )
                    else:
                        self.stdout.write(f"  ✓ Column {column['name']} already exists")
                
                # 2. Create tabel_review_log
                self.stdout.write('\n2. Checking tabel_review_log...')
                
                cursor.execute("""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'tabel_review_log'
                """)
                
                table_exists = cursor.fetchone()[0] > 0
                
                if not table_exists or force:
                    create_table_sql = """
                        CREATE TABLE [dbo].[tabel_review_log](
                            [id] [int] IDENTITY(1,1) NOT NULL,
                            [history_id] [varchar](15) NULL,
                            [reviewer_employee] [varchar](50) NULL,
                            [action] [varchar](10) NULL,
                            [final_section_id] [float] NULL,
                            [review_notes] [varchar](max) NULL,
                            [review_date] [datetime] NULL,
                            CONSTRAINT [PK_tabel_review_log] PRIMARY KEY CLUSTERED ([id] ASC)
                        ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
                    """
                    
                    if dry_run:
                        self.stdout.write("  Would create table: tabel_review_log")
                    else:
                        try:
                            if not table_exists:
                                cursor.execute(create_table_sql)
                                self.stdout.write(
                                    self.style.SUCCESS("  ✅ Created table: tabel_review_log")
                                )
                            else:
                                self.stdout.write("  ⚠️  Table tabel_review_log already exists (forced)")
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f"  ❌ Failed to create tabel_review_log: {e}")
                            )
                else:
                    self.stdout.write("  ✓ Table tabel_review_log already exists")
                
                # 3. Initialize existing approved pengajuan for review
                self.stdout.write('\n3. Initializing existing approved pengajuan...')
                
                if not dry_run:
                    try:
                        # Set review_status = '0' untuk pengajuan yang sudah approved tapi belum review
                        cursor.execute("""
                            UPDATE tabel_pengajuan 
                            SET review_status = '0'
                            WHERE status = '1' AND approve = '1' 
                                AND (review_status IS NULL OR review_status = '')
                        """)
                        
                        updated_count = cursor.rowcount
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✅ Initialized {updated_count} existing approved pengajuan for review")
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"  ❌ Failed to initialize existing pengajuan: {e}")
                        )
                else:
                    cursor.execute("""
                        SELECT COUNT(*) FROM tabel_pengajuan 
                        WHERE status = '1' AND approve = '1' 
                            AND (review_status IS NULL OR review_status = '')
                    """)
                    count = cursor.fetchone()[0]
                    self.stdout.write(f"  Would initialize {count} existing approved pengajuan")
                
                # 4. Create reviewer user if not exists
                self.stdout.write('\n4. Checking reviewer user (SITI FATIMAH)...')
                
                try:
                    reviewer_user, created = User.objects.get_or_create(
                        username='007522',
                        defaults={
                            'first_name': 'SITI',
                            'last_name': 'FATIMAH',
                            'is_active': True,
                            'is_staff': True
                        }
                    )
                    
                    if created and not dry_run:
                        reviewer_user.set_password('007522')  # Default password
                        reviewer_user.save()
                        self.stdout.write(
                            self.style.SUCCESS("  ✅ Created reviewer user: 007522 (SITI FATIMAH)")
                        )
                        self.stdout.write(
                            self.style.WARNING("  ⚠️  Default password set to: 007522 (please change)")
                        )
                    elif created and dry_run:
                        self.stdout.write("  Would create reviewer user: 007522 (SITI FATIMAH)")
                    else:
                        self.stdout.write("  ✓ Reviewer user already exists: 007522 (SITI FATIMAH)")
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  ❌ Failed to create reviewer user: {e}")
                    )
                
                # 5. Check pengajuan yang siap review
                self.stdout.write('\n5. Checking pengajuan ready for review...')
                
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = '1' AND approve = '1' 
                        AND (review_status = '0' OR review_status IS NULL)
                """)
                ready_count = cursor.fetchone()[0]
                
                self.stdout.write(f"  📋 Found {ready_count} pengajuan ready for review by SITI FATIMAH")
                
                if ready_count > 0:
                    cursor.execute("""
                        SELECT TOP 5 history_id, oleh, tgl_insert 
                        FROM tabel_pengajuan 
                        WHERE status = '1' AND approve = '1' 
                            AND (review_status = '0' OR review_status IS NULL)
                        ORDER BY tgl_insert ASC
                    """)
                    sample_pengajuan = cursor.fetchall()
                    
                    self.stdout.write("  Recent pengajuan ready for review:")
                    for pengajuan in sample_pengajuan:
                        self.stdout.write(f"    - {pengajuan[0]} by {pengajuan[1]} on {pengajuan[2]}")
                
                self.stdout.write('\n' + '='*60)
                
                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS('DRY RUN COMPLETED - No actual changes were made')
                    )
                    self.stdout.write('Run without --dry-run to apply changes')
                else:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Review System setup completed successfully!')
                    )
                    self.stdout.write('\nNext steps:')
                    self.stdout.write('1. Login as user 007522 (SITI FATIMAH) to access review system')
                    self.stdout.write('2. Navigate to /wo-maintenance/review/ for review dashboard')
                    self.stdout.write('3. Review and distribute pending pengajuan')
                    self.stdout.write(f'4. {ready_count} pengajuan are ready for review')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error setting up review system: {e}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())


# USAGE:
# python manage.py setup_review_system --dry-run  # Preview changes
# python manage.py setup_review_system             # Apply changes
# python manage.py setup_review_system --force     # Force recreation of existing objects
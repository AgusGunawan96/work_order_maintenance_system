# wo_maintenance_app/management/commands/setup_sdbm_integration.py

from django.core.management.base import BaseCommand
from django.db import connections
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Setup SDBM Integration for WO Maintenance App with Enhanced Assignment System'
    
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
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Only validate SDBM connection and mapping',
        )
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Create test assignment data for development',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        validate_only = options['validate_only']
        create_test_data = options['create_test_data']
        
        self.stdout.write(self.style.SUCCESS('=== Setting up SDBM Integration for WO Maintenance ==='))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No actual changes will be made'))
        
        try:
            # 1. Validate SDBM Connection
            self.stdout.write('\n1. Testing SDBM Connection...')
            sdbm_valid = self.test_sdbm_connection()
            
            if not sdbm_valid:
                self.stdout.write(self.style.ERROR('❌ SDBM connection failed. Cannot proceed.'))
                return
            
            # 2. Validate Section Mapping
            self.stdout.write('\n2. Validating SDBM Section Mapping...')
            mapping_valid = self.validate_section_mapping()
            
            if validate_only:
                self.stdout.write(self.style.SUCCESS('✅ Validation completed.'))
                return
            
            # 3. Create/Update Database Tables
            self.stdout.write('\n3. Setting up Enhanced Assignment Tables...')
            self.setup_enhanced_tables(dry_run, force)
            
            # 4. Setup Review System Integration
            self.stdout.write('\n4. Integrating with Review System...')
            self.setup_review_integration(dry_run, force)
            
            # 5. Initialize SDBM Data
            self.stdout.write('\n5. Initializing SDBM Integration Data...')
            self.initialize_sdbm_data(dry_run)
            
            # 6. Create Test Data (if requested)
            if create_test_data and not dry_run:
                self.stdout.write('\n6. Creating Test Assignment Data...')
                self.create_test_assignment_data()
            
            # 7. Final Validation
            self.stdout.write('\n7. Final Integration Validation...')
            self.final_validation()
            
            self.stdout.write('\n' + '='*60)
            
            if dry_run:
                self.stdout.write(self.style.SUCCESS('DRY RUN COMPLETED - No actual changes were made'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ SDBM Integration setup completed successfully!'))
                self.print_next_steps()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error setting up SDBM integration: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())
    
    def test_sdbm_connection(self):
        """Test SDBM database connection and basic queries"""
        try:
            with connections['SDBM'].cursor() as cursor:
                # Test basic connection
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS('  ✓ SDBM database connection: OK'))
                
                # Test employees table
                cursor.execute("SELECT COUNT(*) FROM [hrbp].[employees] WHERE is_active = 1")
                active_employees = cursor.fetchone()[0]
                self.stdout.write(f'  ✓ Active employees: {active_employees}')
                
                # Test department table
                cursor.execute("SELECT COUNT(*) FROM [hr].[department] WHERE name = 'ENGINEERING'")
                engineering_dept = cursor.fetchone()[0]
                if engineering_dept > 0:
                    self.stdout.write('  ✓ ENGINEERING department found')
                else:
                    self.stdout.write(self.style.WARNING('  ⚠️  ENGINEERING department not found'))
                
                # Test section table
                cursor.execute("""
                    SELECT COUNT(*) FROM [hr].[section] 
                    WHERE name LIKE 'ENGINEERING-%'
                """)
                engineering_sections = cursor.fetchone()[0]
                self.stdout.write(f'  ✓ ENGINEERING sections found: {engineering_sections}')
                
                # Test titles with supervisor flags
                cursor.execute("""
                    SELECT COUNT(*) FROM [hr].[title] 
                    WHERE is_supervisor = 1 OR is_manager = 1 OR is_generalManager = 1
                """)
                supervisor_titles = cursor.fetchone()[0]
                self.stdout.write(f'  ✓ Supervisor/Manager titles: {supervisor_titles}')
                
                return True
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ SDBM connection error: {e}'))
            return False
    
    def validate_section_mapping(self):
        """Validate SDBM section mapping"""
        try:
            from wo_maintenance_app.utils import get_sdbm_section_mapping, validate_sdbm_section_mapping
            
            # Get mapping
            section_mapping = get_sdbm_section_mapping()
            self.stdout.write(f'  📋 Section mapping loaded: {len(section_mapping)} sections')
            
            # Validate each section
            validation = validate_sdbm_section_mapping()
            
            if validation['valid']:
                self.stdout.write(self.style.SUCCESS('  ✅ All section mappings are valid'))
            else:
                self.stdout.write(self.style.WARNING('  ⚠️  Some section mappings have issues:'))
                
                if validation['missing_departments']:
                    self.stdout.write(f'    Missing departments: {", ".join(validation["missing_departments"])}')
                
                if validation['missing_sections']:
                    self.stdout.write(f'    Missing sections: {", ".join(validation["missing_sections"])}')
            
            # Show supervisor counts
            for section, info in validation['found_supervisors'].items():
                count = info['count']
                status = '✅' if count > 0 else '⚠️'
                self.stdout.write(f'  {status} {section}: {count} supervisors')
            
            return validation['valid']
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Section mapping validation error: {e}'))
            return False
    
    def setup_enhanced_tables(self, dry_run, force):
        """Setup enhanced assignment tables dengan SDBM integration"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # 1. Enhanced assignment table
                table_sql = """
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tabel_pengajuan_assignment' AND xtype='U')
                    BEGIN
                        CREATE TABLE [dbo].[tabel_pengajuan_assignment](
                            [id] [int] IDENTITY(1,1) NOT NULL,
                            [history_id] [varchar](15) NULL,
                            [assigned_to_employee] [varchar](50) NULL,
                            [assigned_by_employee] [varchar](50) NULL,
                            [assignment_date] [datetime] NULL,
                            [is_active] [bit] NULL DEFAULT 1,
                            [notes] [varchar](max) NULL,
                            [assignment_type] [varchar](20) NULL,
                            [target_section] [varchar](20) NULL,
                            [department_name] [varchar](100) NULL,
                            [section_name] [varchar](100) NULL,
                            [priority_level] [varchar](20) NULL DEFAULT 'normal',
                            [created_by_system] [varchar](50) NULL,
                            CONSTRAINT [PK_tabel_pengajuan_assignment] PRIMARY KEY CLUSTERED ([id] ASC)
                        ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
                    END
                """
                
                if dry_run:
                    self.stdout.write('  Would create/verify: tabel_pengajuan_assignment')
                else:
                    cursor.execute(table_sql)
                    self.stdout.write(self.style.SUCCESS('  ✅ Enhanced assignment table created/verified'))
                
                # 2. Add new columns if they don't exist
                new_columns = [
                    ('assignment_type', 'varchar(20)', 'NULL'),
                    ('target_section', 'varchar(20)', 'NULL'),
                    ('department_name', 'varchar(100)', 'NULL'),
                    ('section_name', 'varchar(100)', 'NULL'),
                    ('priority_level', 'varchar(20)', "'normal'"),
                    ('created_by_system', 'varchar(50)', 'NULL')
                ]
                
                for column_name, column_type, default_value in new_columns:
                    column_sql = f"""
                        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                      WHERE TABLE_NAME = 'tabel_pengajuan_assignment' AND COLUMN_NAME = '{column_name}')
                        BEGIN
                            ALTER TABLE tabel_pengajuan_assignment ADD {column_name} {column_type} DEFAULT {default_value}
                        END
                    """
                    
                    if dry_run:
                        self.stdout.write(f'  Would add column: {column_name}')
                    else:
                        cursor.execute(column_sql)
                        self.stdout.write(f'  ✓ Column added/verified: {column_name}')
                
                # 3. Enhanced review log table
                review_log_sql = """
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tabel_review_log' AND xtype='U')
                    BEGIN
                        CREATE TABLE [dbo].[tabel_review_log](
                            [id] [int] IDENTITY(1,1) NOT NULL,
                            [history_id] [varchar](15) NULL,
                            [reviewer_employee] [varchar](50) NULL,
                            [action] [varchar](10) NULL,
                            [final_section_id] [float] NULL,
                            [review_notes] [varchar](max) NULL,
                            [review_date] [datetime] NULL,
                            [priority_level] [varchar](20) NULL,
                            [target_section] [varchar](20) NULL,
                            [assigned_supervisor_count] [int] NULL DEFAULT 0,
                            [sdbm_integration_status] [varchar](20) NULL DEFAULT 'pending',
                            CONSTRAINT [PK_tabel_review_log] PRIMARY KEY CLUSTERED ([id] ASC)
                        ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
                    END
                """
                
                if dry_run:
                    self.stdout.write('  Would create/verify: tabel_review_log (enhanced)')
                else:
                    cursor.execute(review_log_sql)
                    self.stdout.write(self.style.SUCCESS('  ✅ Enhanced review log table created/verified'))
                
                # 4. Create indexes for performance
                indexes = [
                    "CREATE NONCLUSTERED INDEX [IX_assignment_history_active] ON [tabel_pengajuan_assignment] ([history_id] ASC) WHERE [is_active] = 1",
                    "CREATE NONCLUSTERED INDEX [IX_assignment_employee_active] ON [tabel_pengajuan_assignment] ([assigned_to_employee] ASC) WHERE [is_active] = 1",
                    "CREATE NONCLUSTERED INDEX [IX_assignment_target_section] ON [tabel_pengajuan_assignment] ([target_section] ASC) WHERE [is_active] = 1",
                    "CREATE NONCLUSTERED INDEX [IX_review_log_history] ON [tabel_review_log] ([history_id] ASC)",
                    "CREATE NONCLUSTERED INDEX [IX_review_log_reviewer] ON [tabel_review_log] ([reviewer_employee] ASC)"
                ]
                
                for index_sql in indexes:
                    try:
                        if not dry_run:
                            cursor.execute(index_sql)
                        index_name = index_sql.split('[')[1].split(']')[0]
                        self.stdout.write(f'  ✓ Index created/verified: {index_name}')
                    except Exception:
                        # Index might already exist
                        pass
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error setting up enhanced tables: {e}'))
            raise
    
    def setup_review_integration(self, dry_run, force):
        """Setup review system integration dengan SDBM"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Add SDBM integration columns to tabel_pengajuan if needed
                sdbm_columns = [
                    ('sdbm_assignment_status', 'varchar(20)', "'pending'"),
                    ('sdbm_assigned_count', 'int', '0'),
                    ('sdbm_last_assignment_date', 'datetime', 'NULL')
                ]
                
                for column_name, column_type, default_value in sdbm_columns:
                    column_sql = f"""
                        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                      WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = '{column_name}')
                        BEGIN
                            ALTER TABLE tabel_pengajuan ADD {column_name} {column_type} DEFAULT {default_value}
                        END
                    """
                    
                    if dry_run:
                        self.stdout.write(f'  Would add SDBM column: {column_name}')
                    else:
                        cursor.execute(column_sql)
                        self.stdout.write(f'  ✓ SDBM column added/verified: {column_name}')
                
                # Update existing approved pengajuan untuk SDBM integration
                if not dry_run:
                    cursor.execute("""
                        UPDATE tabel_pengajuan 
                        SET sdbm_assignment_status = 'ready'
                        WHERE status = '1' AND approve = '1' 
                            AND (sdbm_assignment_status IS NULL OR sdbm_assignment_status = '')
                    """)
                    
                    updated_count = cursor.rowcount
                    self.stdout.write(f'  ✓ Updated {updated_count} pengajuan for SDBM integration')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error setting up review integration: {e}'))
            raise
    
    def initialize_sdbm_data(self, dry_run):
        """Initialize SDBM integration data"""
        try:
            from wo_maintenance_app.utils import get_sdbm_section_mapping, validate_sdbm_section_mapping
            
            # Test each section mapping
            section_mapping = get_sdbm_section_mapping()
            
            for section_key, section_info in section_mapping.items():
                try:
                    from wo_maintenance_app.utils import get_sdbm_supervisors_by_section_mapping
                    
                    supervisors = get_sdbm_supervisors_by_section_mapping(section_key)
                    
                    if dry_run:
                        self.stdout.write(f'  Would initialize {section_key}: {len(supervisors)} supervisors')
                    else:
                        self.stdout.write(f'  ✓ Initialized {section_key}: {len(supervisors)} supervisors found')
                        
                        # Log supervisor details
                        for supervisor in supervisors[:3]:  # Show first 3
                            self.stdout.write(f'    - {supervisor["fullname"]} ({supervisor["level_description"]})')
                        
                        if len(supervisors) > 3:
                            self.stdout.write(f'    - and {len(supervisors) - 3} more...')
                
                except Exception as section_error:
                    self.stdout.write(self.style.WARNING(f'  ⚠️  {section_key}: {section_error}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error initializing SDBM data: {e}'))
            raise
    
    def create_test_assignment_data(self):
        """Create test assignment data for development"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Get some approved pengajuan for testing
                cursor.execute("""
                    SELECT TOP 3 history_id 
                    FROM tabel_pengajuan 
                    WHERE status = '1' AND approve = '1'
                        AND NOT EXISTS (
                            SELECT 1 FROM tabel_pengajuan_assignment 
                            WHERE history_id = tabel_pengajuan.history_id AND is_active = 1
                        )
                    ORDER BY tgl_insert DESC
                """)
                
                test_pengajuan = cursor.fetchall()
                
                if test_pengajuan:
                    from wo_maintenance_app.utils import assign_pengajuan_after_siti_review
                    
                    test_sections = ['it', 'elektrik', 'mekanik']
                    
                    for i, (history_id,) in enumerate(test_pengajuan):
                        target_section = test_sections[i % len(test_sections)]
                        
                        result = assign_pengajuan_after_siti_review(
                            history_id,
                            target_section,
                            '007522',  # SITI FATIMAH
                            f'Test assignment untuk {target_section} section'
                        )
                        
                        assigned_count = len(result['assigned_employees'])
                        self.stdout.write(f'  ✓ Test assignment: {history_id} -> {target_section} ({assigned_count} supervisors)')
                    
                    self.stdout.write(f'  ✅ Created {len(test_pengajuan)} test assignments')
                else:
                    self.stdout.write('  ℹ️  No approved pengajuan available for test assignments')
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Error creating test data: {e}'))
    
    def final_validation(self):
        """Final validation of SDBM integration"""
        try:
            from wo_maintenance_app.utils import validate_sdbm_section_mapping
            
            validation = validate_sdbm_section_mapping()
            
            if validation['valid']:
                self.stdout.write(self.style.SUCCESS('  ✅ SDBM integration validation: PASSED'))
            else:
                self.stdout.write(self.style.WARNING('  ⚠️  SDBM integration validation: PARTIAL'))
            
            # Check assignment table
            try:
                with connections['DB_Maintenance'].cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan_assignment WHERE is_active = 1")
                    active_assignments = cursor.fetchone()[0]
                    self.stdout.write(f'  ℹ️  Active assignments: {active_assignments}')
                    
                    cursor.execute("SELECT COUNT(DISTINCT target_section) FROM tabel_pengajuan_assignment WHERE is_active = 1")
                    sections_with_assignments = cursor.fetchone()[0]
                    self.stdout.write(f'  ℹ️  Sections with assignments: {sections_with_assignments}')
                    
            except Exception:
                self.stdout.write('  ℹ️  Assignment table not fully initialized')
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Final validation error: {e}'))
    
    def print_next_steps(self):
        """Print next steps after setup"""
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Login as SITI FATIMAH (007522) to test review system')
        self.stdout.write('2. Navigate to /wo-maintenance/review/ for enhanced review dashboard')
        self.stdout.write('3. Test auto-assignment by reviewing approved pengajuan')
        self.stdout.write('4. Verify SDBM supervisors receive assignments in their view')
        self.stdout.write('5. Monitor assignment logs in tabel_pengajuan_assignment')
        self.stdout.write('\nDebug URLs (for superuser):')
        self.stdout.write('- /wo-maintenance/debug/sdbm-validation/ - Validation check')
        self.stdout.write('- /wo-maintenance/debug/sdbm-mapping/ - Section mapping debug')
        self.stdout.write('- /wo-maintenance/ajax/sdbm/get-supervisors/ - Supervisor lookup')


# Usage:
# python manage.py setup_sdbm_integration --dry-run              # Preview changes
# python manage.py setup_sdbm_integration                        # Apply setup
# python manage.py setup_sdbm_integration --validate-only        # Only validate SDBM
# python manage.py setup_sdbm_integration --create-test-data     # Include test assignments
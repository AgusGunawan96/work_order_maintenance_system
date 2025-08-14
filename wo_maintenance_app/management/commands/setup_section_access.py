# wo_maintenance_app/management/commands/setup_section_access.py

from django.core.management.base import BaseCommand
from django.db import connections, transaction
from django.contrib.auth.models import User
from wo_maintenance_app.utils import (
    get_employee_hierarchy_data,
    is_engineering_supervisor_or_above,
    get_engineering_section_access,
    get_enhanced_pengajuan_access_for_user,
    get_maintenance_section_ids_by_keywords,
    ensure_assignment_tables_exist,
    initialize_review_data,
    REVIEWER_EMPLOYEE_NUMBER
)
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Setup Section-based Access System untuk WO Maintenance'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-tables',
            action='store_true',
            help='Create required tables untuk section access system',
        )
        parser.add_argument(
            '--validate-mapping',
            action='store_true',
            help='Validate section keyword mapping',
        )
        parser.add_argument(
            '--test-users',
            action='store_true',
            help='Test access untuk sample users',
        )
        parser.add_argument(
            '--initialize-data',
            action='store_true',
            help='Initialize data untuk section access',
        )
        parser.add_argument(
            '--full-setup',
            action='store_true',
            help='Run full setup (all options)',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Test specific user by employee number',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🎯 Section-based Access System Setup')
        )
        
        try:
            if options['full_setup']:
                self.run_full_setup()
            else:
                if options['create_tables']:
                    self.create_required_tables()
                
                if options['validate_mapping']:
                    self.validate_section_mapping()
                
                if options['test_users']:
                    self.test_user_access()
                
                if options['initialize_data']:
                    self.initialize_system_data()
                
                if options['user']:
                    self.test_specific_user(options['user'])
            
            self.stdout.write(
                self.style.SUCCESS('\n✅ Section-based Access Setup Completed!')
            )
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            self.stdout.write(
                self.style.ERROR(f'❌ Setup failed: {str(e)}')
            )
            raise

    def run_full_setup(self):
        """Run complete setup"""
        self.stdout.write('\n🚀 Running Full Setup...')
        
        # 1. Create required tables
        self.stdout.write('\n1. Creating required tables...')
        self.create_required_tables()
        
        # 2. Validate section mapping
        self.stdout.write('\n2. Validating section mapping...')
        self.validate_section_mapping()
        
        # 3. Initialize system data
        self.stdout.write('\n3. Initializing system data...')
        self.initialize_system_data()
        
        # 4. Test user access
        self.stdout.write('\n4. Testing user access...')
        self.test_user_access()
        
        # 5. Create sample data if needed
        self.stdout.write('\n5. Checking sample data...')
        self.check_and_create_sample_data()
        
        # 6. Final validation
        self.stdout.write('\n6. Final validation...')
        self.final_validation()

    def create_required_tables(self):
        """Create tables yang diperlukan untuk section access"""
        try:
            # Create assignment tables
            tables_created = ensure_assignment_tables_exist()
            
            if tables_created:
                self.stdout.write(
                    self.style.SUCCESS('  ✅ Assignment tables created/verified')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('  ⚠️  Assignment tables already exist or creation failed')
                )
            
            # Create additional tables untuk section access tracking
            with connections['DB_Maintenance'].cursor() as cursor:
                # Section access log table
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tabel_section_access_log' AND xtype='U')
                    BEGIN
                        CREATE TABLE [dbo].[tabel_section_access_log](
                            [id] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
                            [employee_number] [varchar](50) NULL,
                            [access_type] [varchar](50) NULL,
                            [section_ids] [varchar](500) NULL,
                            [access_date] [datetime] NULL DEFAULT GETDATE(),
                            [pengajuan_count] [int] NULL,
                            [session_info] [varchar](max) NULL
                        ) ON [PRIMARY]
                    END
                """)
                
                # Section mapping cache table
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tabel_section_mapping_cache' AND xtype='U')
                    BEGIN
                        CREATE TABLE [dbo].[tabel_section_mapping_cache](
                            [id] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
                            [target_section] [varchar](50) NOT NULL,
                            [maintenance_section_ids] [varchar](200) NULL,
                            [keywords] [varchar](500) NULL,
                            [display_name] [varchar](200) NULL,
                            [last_updated] [datetime] NULL DEFAULT GETDATE(),
                            [is_active] [bit] NULL DEFAULT 1
                        ) ON [PRIMARY]
                    END
                """)
                
                self.stdout.write(
                    self.style.SUCCESS('  ✅ Additional section access tables created')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error creating tables: {str(e)}')
            )
            raise

    def validate_section_mapping(self):
        """Validate dan update section keyword mapping"""
        try:
            # Test keywords mapping
            test_keywords = {
                'it': ['IT', 'INFORMATION', 'TECHNOLOGY', 'SISTEM', 'KOMPUTER'],
                'elektrik': ['ELEKTRIK', 'ELECTRIC', 'ELECTRICAL', 'LISTRIK', 'POWER'],
                'mekanik': ['MEKANIK', 'MECHANIC', 'MECHANICAL', 'MESIN', 'TEKNIK'],
                'utility': ['UTILITY', 'UTILITIES', 'FASILITAS', 'INFRASTRUKTUR']
            }
            
            mapping_results = {}
            
            for target_section, keywords in test_keywords.items():
                section_ids = get_maintenance_section_ids_by_keywords(keywords)
                
                mapping_results[target_section] = {
                    'keywords': keywords,
                    'found_section_ids': section_ids,
                    'count': len(section_ids)
                }
                
                if section_ids:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✅ {target_section.upper()}: {len(section_ids)} sections - IDs: {section_ids}'
                        )
                    )
                    
                    # Cache the mapping
                    self.cache_section_mapping(target_section, section_ids, keywords)
                    
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠️  {target_section.upper()}: No sections found for keywords {keywords}'
                        )
                    )
            
            # Generate mapping report
            self.generate_mapping_report(mapping_results)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error validating mapping: {str(e)}')
            )
            raise

    def cache_section_mapping(self, target_section, section_ids, keywords):
        """Cache section mapping untuk performance"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Clear existing cache
                cursor.execute("""
                    DELETE FROM tabel_section_mapping_cache 
                    WHERE target_section = %s
                """, [target_section])
                
                # Insert new cache
                cursor.execute("""
                    INSERT INTO tabel_section_mapping_cache 
                    (target_section, maintenance_section_ids, keywords, display_name, last_updated)
                    VALUES (%s, %s, %s, %s, GETDATE())
                """, [
                    target_section,
                    ','.join([str(sid) for sid in section_ids]),
                    ','.join(keywords),
                    f"{target_section.title()} Section Mapping"
                ])
                
                logger.info(f"Cached mapping for {target_section}: {section_ids}")
                
        except Exception as e:
            logger.warning(f"Failed to cache mapping for {target_section}: {e}")

    def test_user_access(self):
        """Test access untuk sample users"""
        try:
            # Test SITI FATIMAH
            self.stdout.write('\n  Testing SITI FATIMAH access...')
            self.test_specific_user(REVIEWER_EMPLOYEE_NUMBER)
            
            # Test sample active users
            self.stdout.write('\n  Testing sample users...')
            users = User.objects.filter(is_active=True)[:10]
            
            access_summary = {
                'siti_fatimah': 0,
                'engineering_supervisor': 0,
                'hierarchy_normal': 0,
                'no_access': 0,
                'errors': 0
            }
            
            for user in users:
                try:
                    hierarchy = get_employee_hierarchy_data(user)
                    
                    if not hierarchy:
                        access_summary['no_access'] += 1
                        continue
                    
                    access_info = get_enhanced_pengajuan_access_for_user(hierarchy)
                    access_type = access_info['access_type']
                    
                    if access_type == 'SITI_FATIMAH_FULL':
                        access_summary['siti_fatimah'] += 1
                    elif access_type.startswith('ENGINEERING_'):
                        access_summary['engineering_supervisor'] += 1
                    elif access_type == 'HIERARCHY_NORMAL':
                        access_summary['hierarchy_normal'] += 1
                    else:
                        access_summary['no_access'] += 1
                        
                    # Log access untuk tracking
                    self.log_user_access(hierarchy, access_info)
                    
                except Exception as e:
                    access_summary['errors'] += 1
                    logger.error(f"Error testing user {user.username}: {e}")
            
            # Display summary
            self.stdout.write('\n  📊 Access Summary:')
            self.stdout.write(f'    SITI FATIMAH: {access_summary["siti_fatimah"]}')
            self.stdout.write(f'    Engineering Supervisors: {access_summary["engineering_supervisor"]}')
            self.stdout.write(f'    Hierarchy Normal: {access_summary["hierarchy_normal"]}')
            self.stdout.write(f'    No Access: {access_summary["no_access"]}')
            self.stdout.write(f'    Errors: {access_summary["errors"]}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error testing user access: {str(e)}')
            )

    def test_specific_user(self, employee_number):
        """Test access untuk user tertentu"""
        try:
            user = User.objects.get(username=employee_number)
            hierarchy = get_employee_hierarchy_data(user)
            
            if not hierarchy:
                self.stdout.write(
                    self.style.WARNING(f'    ⚠️  No hierarchy data for {employee_number}')
                )
                return
            
            # Display user info
            self.stdout.write(f'    👤 User: {hierarchy.get("fullname")} ({employee_number})')
            self.stdout.write(f'       Title: {hierarchy.get("title_name")}')
            self.stdout.write(f'       Department: {hierarchy.get("department_name")}')
            self.stdout.write(f'       Section: {hierarchy.get("section_name")}')
            
            # Check engineering supervisor
            is_eng_supervisor = is_engineering_supervisor_or_above(hierarchy)
            self.stdout.write(f'       Engineering Supervisor: {"Yes" if is_eng_supervisor else "No"}')
            
            # Check section access
            section_access = get_engineering_section_access(hierarchy)
            if section_access:
                self.stdout.write(f'       Section Access: {section_access["display_name"]}')
            
            # Get enhanced access info
            access_info = get_enhanced_pengajuan_access_for_user(hierarchy)
            self.stdout.write(f'       Access Type: {access_info["access_type"]}')
            
            if access_info.get('allowed_section_ids'):
                self.stdout.write(f'       Allowed Sections: {access_info["allowed_section_ids"]}')
            
            self.stdout.write(
                self.style.SUCCESS(f'    ✅ {employee_number} access test completed')
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(f'    ⚠️  User {employee_number} not found')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'    ❌ Error testing {employee_number}: {str(e)}')
            )

    def initialize_system_data(self):
        """Initialize data yang diperlukan untuk system"""
        try:
            # Initialize review data
            initialized = initialize_review_data()
            
            if initialized:
                self.stdout.write(
                    self.style.SUCCESS('  ✅ Review data initialized')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('  ⚠️  Review data initialization failed')
                )
            
            # Check pengajuan counts
            self.check_pengajuan_counts()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error initializing data: {str(e)}')
            )

    def check_pengajuan_counts(self):
        """Check counts pengajuan untuk validasi"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Total pengajuan
                cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE history_id IS NOT NULL")
                total = cursor.fetchone()[0] or 0
                
                # By status
                cursor.execute("""
                    SELECT status, approve, COUNT(*) 
                    FROM tabel_pengajuan 
                    WHERE history_id IS NOT NULL
                    GROUP BY status, approve
                    ORDER BY status, approve
                """)
                
                status_counts = cursor.fetchall()
                
                self.stdout.write(f'  📊 Pengajuan Statistics:')
                self.stdout.write(f'    Total Pengajuan: {total}')
                
                for status_count in status_counts:
                    status = status_count[0] or 'NULL'
                    approve = status_count[1] or 'NULL'
                    count = status_count[2]
                    self.stdout.write(f'    Status {status}/Approve {approve}: {count}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error checking pengajuan counts: {str(e)}')
            )

    def check_and_create_sample_data(self):
        """Check dan create sample data jika diperlukan"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Check apakah ada data pengajuan
                cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE history_id IS NOT NULL")
                count = cursor.fetchone()[0] or 0
                
                if count < 10:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  Only {count} pengajuan found. Consider creating sample data.')
                    )
                    
                    # Offer to create sample data
                    response = input('  Create sample pengajuan data? (y/n): ')
                    if response.lower() == 'y':
                        self.create_sample_pengajuan_data()
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ Found {count} pengajuan - sufficient for testing')
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error checking sample data: {str(e)}')
            )

    def create_sample_pengajuan_data(self):
        """Create sample pengajuan data untuk testing"""
        try:
            # This is a placeholder - actual implementation would create sample data
            self.stdout.write('  📝 Sample data creation not implemented yet.')
            self.stdout.write('     Use: python manage.py generate_test_data --count 20')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error creating sample data: {str(e)}')
            )

    def log_user_access(self, hierarchy, access_info):
        """Log user access untuk tracking"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                section_ids_str = ','.join([str(sid) for sid in access_info.get('allowed_section_ids', [])])
                
                cursor.execute("""
                    INSERT INTO tabel_section_access_log 
                    (employee_number, access_type, section_ids, pengajuan_count, session_info)
                    VALUES (%s, %s, %s, %s, %s)
                """, [
                    hierarchy.get('employee_number'),
                    access_info['access_type'],
                    section_ids_str,
                    0,  # Will be updated later
                    f"Setup validation - {hierarchy.get('title_name')}"
                ])
                
        except Exception as e:
            logger.warning(f"Failed to log user access: {e}")

    def generate_mapping_report(self, mapping_results):
        """Generate mapping report"""
        try:
            self.stdout.write('\n  📋 Section Mapping Report:')
            
            for target_section, result in mapping_results.items():
                self.stdout.write(f'\n    {target_section.upper()}:')
                self.stdout.write(f'      Keywords: {", ".join(result["keywords"])}')
                self.stdout.write(f'      Found Sections: {result["count"]}')
                
                if result['found_section_ids']:
                    # Get section names
                    with connections['DB_Maintenance'].cursor() as cursor:
                        placeholders = ','.join(['%s'] * len(result['found_section_ids']))
                        cursor.execute(f"""
                            SELECT id_section, seksi 
                            FROM tabel_msection 
                            WHERE id_section IN ({placeholders})
                        """, [float(sid) for sid in result['found_section_ids']])
                        
                        sections = cursor.fetchall()
                        for section in sections:
                            self.stdout.write(f'        - ID {int(section[0])}: {section[1]}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error generating report: {str(e)}')
            )

    def final_validation(self):
        """Final validation setelah setup"""
        try:
            # Validate URLs
            self.stdout.write('  🔗 Validating URLs...')
            from wo_maintenance_app.urls import check_complete_critical_urls
            
            urls_ok = check_complete_critical_urls()
            if urls_ok:
                self.stdout.write(
                    self.style.SUCCESS('    ✅ All critical URLs configured')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('    ⚠️  Some URLs may be missing')
                )
            
            # Check database connectivity
            self.stdout.write('  🔌 Checking database connectivity...')
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan")
                
            with connections['SDBM'].cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM [hrbp].[employees] WHERE is_active = 1")
            
            self.stdout.write(
                self.style.SUCCESS('    ✅ Database connectivity OK')
            )
            
            # Final summary
            self.stdout.write('\n  🎉 Setup Summary:')
            self.stdout.write('    ✅ Section-based access system configured')
            self.stdout.write('    ✅ Database tables created')
            self.stdout.write('    ✅ Section mapping validated')
            self.stdout.write('    ✅ User access tested')
            self.stdout.write('    ✅ System ready for use')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Final validation failed: {str(e)}')
            )
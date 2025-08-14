# wo_maintenance_app/management/commands/test_section_access.py
# Django Management Command untuk testing section access

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import connections
from wo_maintenance_app.utils import (
    get_employee_hierarchy_data,
    is_engineering_supervisor_or_above,
    get_engineering_section_access,
    get_enhanced_pengajuan_access_for_user,
    get_maintenance_section_ids_by_keywords,
    build_enhanced_pengajuan_query_conditions,
    get_access_statistics,
    REVIEWER_EMPLOYEE_NUMBER
)
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test dan validate section-based access system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user', 
            type=str, 
            help='Test specific username (employee number)'
        )
        parser.add_argument(
            '--all-users',
            action='store_true',
            help='Test all users in system'
        )
        parser.add_argument(
            '--validate-sections',
            action='store_true',
            help='Validate section mapping'
        )
        parser.add_argument(
            '--test-queries',
            action='store_true',
            help='Test query generation'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🎯 Section-based Access System Testing')
        )
        
        try:
            if options['validate_sections']:
                self.validate_section_mapping()
            
            if options['test_queries']:
                self.test_query_generation()
            
            if options['user']:
                self.test_specific_user(options['user'])
            
            if options['all_users']:
                self.test_all_users()
                
            if not any([options['validate_sections'], options['test_queries'], 
                       options['user'], options['all_users']]):
                self.run_comprehensive_test()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Test failed: {str(e)}')
            )
            raise

    def validate_section_mapping(self):
        """Validate section keyword mapping"""
        self.stdout.write('\n📋 Validating Section Mapping...')
        
        # Test keywords mapping
        test_keywords = {
            'MEKANIK': ['MEKANIK', 'MECHANIC', 'MECHANICAL'],
            'ELEKTRIK': ['ELEKTRIK', 'ELECTRIC', 'ELECTRICAL'],
            'IT': ['IT', 'INFORMATION', 'TECHNOLOGY'],
            'UTILITY': ['UTILITY', 'UTILITIES']
        }
        
        for section_type, keywords in test_keywords.items():
            section_ids = get_maintenance_section_ids_by_keywords(keywords)
            
            if section_ids:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✅ {section_type}: {len(section_ids)} sections found - IDs: {section_ids}'
                    )
                )
                
                # Get actual section names
                with connections['DB_Maintenance'].cursor() as cursor:
                    placeholders = ','.join(['%s'] * len(section_ids))
                    cursor.execute(f"""
                        SELECT id_section, seksi 
                        FROM tabel_msection 
                        WHERE id_section IN ({placeholders})
                    """, [float(sid) for sid in section_ids])
                    
                    sections = cursor.fetchall()
                    for section in sections:
                        self.stdout.write(f'     - ID {int(section[0])}: {section[1]}')
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  {section_type}: No sections found for keywords {keywords}')
                )

    def test_specific_user(self, username):
        """Test access untuk user specific"""
        self.stdout.write(f'\n👤 Testing User: {username}')
        
        try:
            user = User.objects.get(username=username)
            hierarchy = get_employee_hierarchy_data(user)
            
            if not hierarchy:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ No hierarchy data found for {username}')
                )
                return
            
            # Display user info
            self.stdout.write(f'  Name: {hierarchy.get("fullname")}')
            self.stdout.write(f'  Title: {hierarchy.get("title_name")}')
            self.stdout.write(f'  Department: {hierarchy.get("department_name")}')
            self.stdout.write(f'  Section: {hierarchy.get("section_name")}')
            
            # Test engineering supervisor check
            is_eng_supervisor = is_engineering_supervisor_or_above(hierarchy)
            self.stdout.write(f'  Engineering Supervisor: {is_eng_supervisor}')
            
            # Test section access
            section_access = get_engineering_section_access(hierarchy)
            if section_access:
                self.stdout.write(f'  Section Access: {section_access["display_name"]}')
                self.stdout.write(f'  Keywords: {section_access["maintenance_section_keywords"]}')
            
            # Test enhanced access
            access_info = get_enhanced_pengajuan_access_for_user(hierarchy)
            self.stdout.write(f'  Access Type: {access_info["access_type"]}')
            self.stdout.write(f'  Description: {access_info["access_description"]}')
            
            if access_info.get('allowed_section_ids'):
                self.stdout.write(f'  Allowed Sections: {access_info["allowed_section_ids"]}')
            
            if access_info.get('allowed_employee_numbers'):
                count = len(access_info["allowed_employee_numbers"])
                self.stdout.write(f'  Allowed Employees: {count} subordinates')
            
            # Test statistics
            stats = get_access_statistics(access_info)
            self.stdout.write(f'  Accessible Pengajuan: {stats["total_accessible"]}')
            
            self.stdout.write(
                self.style.SUCCESS(f'  ✅ User {username} test completed')
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'  ❌ User {username} not found')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error testing user {username}: {str(e)}')
            )

    def test_query_generation(self):
        """Test query generation untuk berbagai access types"""
        self.stdout.write('\n🔍 Testing Query Generation...')
        
        # Test cases
        test_cases = [
            {
                'name': 'SITI FATIMAH Full Access',
                'access_info': {
                    'access_type': 'SITI_FATIMAH_FULL',
                    'allowed_employee_numbers': ['*'],
                    'allowed_section_ids': ['*']
                }
            },
            {
                'name': 'Engineering Mechanic Supervisor',
                'access_info': {
                    'access_type': 'ENGINEERING_MECHANIC_SUPERVISOR',
                    'allowed_employee_numbers': [],
                    'allowed_section_ids': [3]
                }
            },
            {
                'name': 'Hierarchy Normal Access',
                'access_info': {
                    'access_type': 'HIERARCHY_NORMAL',
                    'allowed_employee_numbers': ['123456', '789012'],
                    'allowed_section_ids': []
                }
            }
        ]
        
        for test_case in test_cases:
            self.stdout.write(f'\n  Testing: {test_case["name"]}')
            
            try:
                where_conditions, query_params = build_enhanced_pengajuan_query_conditions(
                    test_case['access_info']
                )
                
                self.stdout.write(f'    WHERE conditions: {len(where_conditions)}')
                self.stdout.write(f'    Query params: {len(query_params)}')
                
                # Test actual query execution
                where_clause = "WHERE " + " AND ".join(where_conditions)
                
                with connections['DB_Maintenance'].cursor() as cursor:
                    test_query = f"""
                        SELECT COUNT(DISTINCT tp.history_id)
                        FROM tabel_pengajuan tp
                        {where_clause}
                    """
                    
                    cursor.execute(test_query, query_params)
                    count = cursor.fetchone()[0]
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'    ✅ Query executed: {count} records found')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'    ❌ Query test failed: {str(e)}')
                )

    def test_all_users(self):
        """Test access untuk semua users yang ada"""
        self.stdout.write('\n👥 Testing All Users...')
        
        # Get sample of users
        users = User.objects.filter(is_active=True)[:20]  # Limit to 20 untuk testing
        
        results = {
            'siti_fatimah': 0,
            'engineering_supervisors': 0,
            'hierarchy_normal': 0,
            'no_access': 0,
            'errors': 0
        }
        
        for user in users:
            try:
                hierarchy = get_employee_hierarchy_data(user)
                
                if not hierarchy:
                    results['no_access'] += 1
                    continue
                
                access_info = get_enhanced_pengajuan_access_for_user(hierarchy)
                access_type = access_info['access_type']
                
                if access_type == 'SITI_FATIMAH_FULL':
                    results['siti_fatimah'] += 1
                elif access_type.startswith('ENGINEERING_'):
                    results['engineering_supervisors'] += 1
                elif access_type == 'HIERARCHY_NORMAL':
                    results['hierarchy_normal'] += 1
                else:
                    results['no_access'] += 1
                    
            except Exception as e:
                results['errors'] += 1
                logger.error(f"Error testing user {user.username}: {e}")
        
        # Display results
        self.stdout.write('\n📊 Test Results Summary:')
        self.stdout.write(f'  SITI FATIMAH: {results["siti_fatimah"]}')
        self.stdout.write(f'  Engineering Supervisors: {results["engineering_supervisors"]}')
        self.stdout.write(f'  Hierarchy Normal: {results["hierarchy_normal"]}')
        self.stdout.write(f'  No Access: {results["no_access"]}')
        self.stdout.write(f'  Errors: {results["errors"]}')

    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        self.stdout.write('\n🚀 Running Comprehensive Test Suite...')
        
        # 1. Section mapping validation
        self.validate_section_mapping()
        
        # 2. Query generation test
        self.test_query_generation()
        
        # 3. Test SITI FATIMAH user
        self.test_specific_user(REVIEWER_EMPLOYEE_NUMBER)
        
        # 4. Database connectivity test
        self.test_database_connectivity()
        
        # 5. Performance test
        self.test_performance()
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ Comprehensive test completed!')
        )

    def test_database_connectivity(self):
        """Test database connectivity"""
        self.stdout.write('\n🔌 Testing Database Connectivity...')
        
        try:
            # Test DB_Maintenance
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan")
                pengajuan_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM tabel_msection")
                section_count = cursor.fetchone()[0]
                
                self.stdout.write(f'  DB_Maintenance: {pengajuan_count} pengajuan, {section_count} sections')
            
            # Test SDBM
            with connections['SDBM'].cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM [hrbp].[employees] WHERE is_active = 1")
                employee_count = cursor.fetchone()[0]
                
                self.stdout.write(f'  SDBM: {employee_count} active employees')
            
            self.stdout.write(
                self.style.SUCCESS('  ✅ Database connectivity OK')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Database connectivity failed: {str(e)}')
            )

    def test_performance(self):
        """Test performance metrics"""
        self.stdout.write('\n⚡ Testing Performance...')
        
        import time
        
        try:
            # Test user hierarchy lookup
            start_time = time.time()
            
            user = User.objects.filter(is_active=True).first()
            if user:
                hierarchy = get_employee_hierarchy_data(user)
                access_info = get_enhanced_pengajuan_access_for_user(hierarchy)
                stats = get_access_statistics(access_info)
                
                end_time = time.time()
                duration = end_time - start_time
                
                self.stdout.write(f'  Access Info Generation: {duration:.3f}s')
                
                if duration < 1.0:
                    self.stdout.write(
                        self.style.SUCCESS('  ✅ Performance: Good (< 1s)')
                    )
                elif duration < 3.0:
                    self.stdout.write(
                        self.style.WARNING('  ⚠️  Performance: Acceptable (< 3s)')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Performance: Slow ({duration:.3f}s)')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING('  ⚠️  No active users found for performance test')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Performance test failed: {str(e)}')
            )
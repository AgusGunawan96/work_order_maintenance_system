# wo_maintenance_app/management/commands/verify_section_access.py

from django.core.management.base import BaseCommand
from django.db import connections
from wo_maintenance_app.utils import get_employee_hierarchy_data, get_enhanced_pengajuan_access_for_user
from django.contrib.auth.models import User
import json

class Command(BaseCommand):
    help = 'Verify section-based access system untuk WO Maintenance'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Test specific user (employee_number)',
        )
        parser.add_argument(
            '--show-sections',
            action='store_true',
            help='Show all maintenance sections',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== VERIFY SECTION ACCESS SYSTEM ==='))
        
        # 1. Show maintenance sections
        if options['show_sections']:
            self.show_maintenance_sections()
        
        # 2. Test specific user or all engineering supervisors
        if options['user']:
            self.test_user_access(options['user'])
        else:
            self.test_engineering_supervisors()
        
        # 3. Test SITI FATIMAH
        self.test_siti_fatimah()
    
    def show_maintenance_sections(self):
        """Show all maintenance sections in database"""
        self.stdout.write('\n1. Maintenance Sections in Database:')
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT id_section, seksi, status
                    FROM tabel_msection
                    WHERE (status = 'A' OR status IS NULL)
                        AND seksi IS NOT NULL
                    ORDER BY id_section
                """)
                
                sections = cursor.fetchall()
                for section in sections:
                    section_id = int(float(section[0]))
                    section_name = section[1]
                    status = section[2] or 'Active'
                    
                    self.stdout.write(f"  ID {section_id}: {section_name} ({status})")
                    
                    # Check matching keywords
                    keywords_map = {
                        'MEKANIK': 'ENGINEERING-MECHANIC',
                        'MECHANIC': 'ENGINEERING-MECHANIC', 
                        'ELEKTRIK': 'ENGINEERING-ELECTRIC',
                        'ELECTRIC': 'ENGINEERING-ELECTRIC',
                        'IT': 'ENGINEERING-IT',
                        'UTILITY': 'ENGINEERING-UTILITY'
                    }
                    
                    section_upper = section_name.upper()
                    matched_types = []
                    for keyword, eng_type in keywords_map.items():
                        if keyword in section_upper:
                            matched_types.append(eng_type)
                    
                    if matched_types:
                        self.stdout.write(f"    → Matches: {', '.join(matched_types)}")
                        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
    
    def test_user_access(self, employee_number):
        """Test access for specific user"""
        self.stdout.write(f'\n2. Testing User Access: {employee_number}')
        
        try:
            # Create dummy user object
            user = User.objects.filter(username=employee_number).first()
            if not user:
                # Create temporary user for testing
                user = User(username=employee_number)
            
            # Get hierarchy data
            user_hierarchy = get_employee_hierarchy_data(user)
            
            if not user_hierarchy:
                self.stdout.write(self.style.ERROR(f"  ❌ User {employee_number} not found in SDBM"))
                return
            
            # Show user info
            self.stdout.write(f"  User: {user_hierarchy.get('fullname')}")
            self.stdout.write(f"  Department: {user_hierarchy.get('department_name')}")
            self.stdout.write(f"  Section: {user_hierarchy.get('section_name')}")
            self.stdout.write(f"  Title: {user_hierarchy.get('title_name')}")
            
            # Get access info
            access_info = get_enhanced_pengajuan_access_for_user(user_hierarchy)
            
            self.stdout.write(f"  Access Type: {access_info['access_type']}")
            self.stdout.write(f"  Description: {access_info['access_description']}")
            
            if access_info.get('allowed_section_ids'):
                self.stdout.write(f"  Allowed Section IDs: {access_info['allowed_section_ids']}")
            
            if access_info.get('section_keywords'):
                self.stdout.write(f"  Section Keywords: {access_info['section_keywords']}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error testing user: {e}"))
    
    def test_engineering_supervisors(self):
        """Test all engineering supervisors"""
        self.stdout.write('\n3. Testing All Engineering Supervisors:')
        
        try:
            with connections['SDBM'].cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT
                        e.employee_number,
                        e.fullname,
                        d.name as department_name,
                        s.name as section_name,
                        t.Name as title_name,
                        t.is_supervisor,
                        t.is_manager
                    FROM [hrbp].[employees] e
                    INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                    LEFT JOIN [hr].[department] d ON p.departmentId = d.id
                    LEFT JOIN [hr].[section] s ON p.sectionId = s.id
                    LEFT JOIN [hr].[title] t ON p.titleId = t.id
                    WHERE e.is_active = 1
                        AND p.is_active = 1
                        AND UPPER(d.name) LIKE '%ENGINEERING%'
                        AND UPPER(s.name) LIKE '%ENGINEERING-%'
                        AND (
                            t.is_supervisor = 1 OR 
                            t.is_manager = 1 OR
                            UPPER(t.Name) LIKE '%SUPERVISOR%' OR
                            UPPER(t.Name) LIKE '%MANAGER%'
                        )
                    ORDER BY s.name, t.Name
                """)
                
                supervisors = cursor.fetchall()
                
                for supervisor in supervisors:
                    self.stdout.write(f"\n  {supervisor[1]} ({supervisor[0]})")
                    self.stdout.write(f"    Section: {supervisor[3]}")
                    self.stdout.write(f"    Title: {supervisor[4]}")
                    
                    # Test access
                    self.test_user_access(supervisor[0])
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
    
    def test_siti_fatimah(self):
        """Test SITI FATIMAH access"""
        self.stdout.write('\n4. Testing SITI FATIMAH (007522):')
        self.test_user_access('007522')
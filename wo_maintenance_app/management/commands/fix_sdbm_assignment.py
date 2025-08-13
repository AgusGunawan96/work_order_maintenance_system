# wo_maintenance_app/management/commands/fix_sdbm_assignment.py

from django.core.management.base import BaseCommand
from django.db import connections
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix SDBM Assignment Issues - Database Schema dan Logic'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--fix-schema',
            action='store_true',
            help='Fix database schema issues',
        )
        parser.add_argument(
            '--fix-assignments',
            action='store_true',
            help='Fix existing assignment data',
        )
        parser.add_argument(
            '--debug-user',
            type=str,
            help='Debug specific user employee number',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        fix_schema = options['fix_schema']
        fix_assignments = options['fix_assignments']
        debug_user = options['debug_user']
        
        self.stdout.write(self.style.SUCCESS('=== Fixing SDBM Assignment Issues ==='))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No actual changes will be made'))
        
        try:
            # 1. Diagnose current issues
            self.stdout.write('\n1. Diagnosing current issues...')
            self.diagnose_issues()
            
            # 2. Fix database schema if requested
            if fix_schema or not any([fix_assignments, debug_user]):
                self.stdout.write('\n2. Fixing database schema...')
                self.fix_database_schema(dry_run)
            
            # 3. Fix existing assignments if requested
            if fix_assignments:
                self.stdout.write('\n3. Fixing existing assignments...')
                self.fix_existing_assignments(dry_run)
            
            # 4. Debug specific user if requested
            if debug_user:
                self.stdout.write(f'\n4. Debugging user {debug_user}...')
                self.debug_user_assignments(debug_user)
            
            # 5. Test SDBM supervisor lookup
            self.stdout.write('\n5. Testing SDBM supervisor lookup...')
            self.test_supervisor_lookup()
            
            # 6. Final validation
            self.stdout.write('\n6. Final validation...')
            self.final_validation()
            
            if not dry_run:
                self.stdout.write(self.style.SUCCESS('\n✅ SDBM Assignment issues fixed!'))
            else:
                self.stdout.write(self.style.SUCCESS('\n✅ Dry run completed - issues identified'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error fixing SDBM assignment: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())
    
    def diagnose_issues(self):
        """Diagnose current SDBM assignment issues"""
        try:
            issues = []
            
            # Check database schema
            with connections['DB_Maintenance'].cursor() as cursor:
                # Check if assignment table exists
                cursor.execute("""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'tabel_pengajuan_assignment'
                """)
                
                if cursor.fetchone()[0] == 0:
                    issues.append("❌ Assignment table doesn't exist")
                else:
                    self.stdout.write("  ✓ Assignment table exists")
                    
                    # Check for enhanced columns
                    enhanced_columns = ['assignment_type', 'target_section', 'department_name', 'section_name']
                    missing_columns = []
                    
                    for column in enhanced_columns:
                        cursor.execute("""
                            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                            WHERE TABLE_NAME = 'tabel_pengajuan_assignment' AND COLUMN_NAME = %s
                        """, [column])
                        
                        if cursor.fetchone()[0] == 0:
                            missing_columns.append(column)
                    
                    if missing_columns:
                        issues.append(f"❌ Missing enhanced columns: {', '.join(missing_columns)}")
                    else:
                        self.stdout.write("  ✓ All enhanced columns exist")
                    
                    # Check assignment data
                    cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan_assignment WHERE is_active = 1")
                    active_assignments = cursor.fetchone()[0]
                    self.stdout.write(f"  ℹ️  Active assignments: {active_assignments}")
            
            # Check SDBM connection
            try:
                with connections['SDBM'].cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM [hrbp].[employees] WHERE is_active = 1")
                    active_employees = cursor.fetchone()[0]
                    self.stdout.write(f"  ✓ SDBM connection OK - {active_employees} active employees")
                    
                    # Check specific section
                    cursor.execute("""
                        SELECT COUNT(*) FROM [hr].[section] 
                        WHERE name = 'ENGINEERING-ELECTRIC' AND (is_active IS NULL OR is_active = 1)
                    """)
                    electric_section = cursor.fetchone()[0]
                    self.stdout.write(f"  ℹ️  ENGINEERING-ELECTRIC section exists: {electric_section > 0}")
                    
                    # Check supervisors in ENGINEERING-ELECTRIC
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM [hrbp].[employees] e
                        INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                        INNER JOIN [hr].[section] s ON p.sectionId = s.id
                        INNER JOIN [hr].[title] t ON p.titleId = t.id
                        WHERE s.name = 'ENGINEERING-ELECTRIC'
                            AND e.is_active = 1
                            AND p.is_active = 1
                            AND (t.is_supervisor = 1 OR t.is_manager = 1 OR 
                                 t.Name LIKE '%SUPERVISOR%' OR t.Name LIKE '%MANAGER%')
                    """)
                    electric_supervisors = cursor.fetchone()[0]
                    self.stdout.write(f"  ℹ️  Supervisors in ENGINEERING-ELECTRIC: {electric_supervisors}")
                    
            except Exception as sdbm_error:
                issues.append(f"❌ SDBM connection issue: {sdbm_error}")
            
            if issues:
                self.stdout.write("  Issues found:")
                for issue in issues:
                    self.stdout.write(f"    {issue}")
            else:
                self.stdout.write("  ✓ No major issues detected")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error diagnosing issues: {e}"))
    
    def fix_database_schema(self, dry_run):
        """Fix database schema issues"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Create assignment table if doesn't exist
                create_table_sql = """
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
                            CONSTRAINT [PK_tabel_pengajuan_assignment] PRIMARY KEY CLUSTERED ([id] ASC)
                        ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
                    END
                """
                
                if dry_run:
                    self.stdout.write("  Would create assignment table if needed")
                else:
                    cursor.execute(create_table_sql)
                    self.stdout.write("  ✓ Assignment table verified/created")
                
                # Add enhanced columns
                enhanced_columns = [
                    ('assignment_type', 'varchar(20)', 'NULL', 'Type of assignment (SITI_REVIEW, etc.)'),
                    ('target_section', 'varchar(20)', 'NULL', 'Target section (it, elektrik, etc.)'),
                    ('department_name', 'varchar(100)', 'NULL', 'SDBM department name'),
                    ('section_name', 'varchar(100)', 'NULL', 'SDBM section name'),
                    ('priority_level', 'varchar(20)', "'normal'", 'Priority level'),
                    ('created_by_system', 'varchar(50)', 'NULL', 'System that created assignment'),
                    ('sdbm_employee_data', 'varchar(max)', 'NULL', 'JSON data of assigned employee from SDBM')
                ]
                
                for column_name, column_type, default_value, description in enhanced_columns:
                    column_sql = f"""
                        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                      WHERE TABLE_NAME = 'tabel_pengajuan_assignment' AND COLUMN_NAME = '{column_name}')
                        BEGIN
                            ALTER TABLE tabel_pengajuan_assignment ADD {column_name} {column_type} DEFAULT {default_value}
                        END
                    """
                    
                    if dry_run:
                        self.stdout.write(f"  Would add column: {column_name} - {description}")
                    else:
                        cursor.execute(column_sql)
                        self.stdout.write(f"  ✓ Column added/verified: {column_name}")
                
                # Create helpful indexes
                indexes = [
                    ("IX_assignment_history_target", "tabel_pengajuan_assignment", "(history_id, target_section)", "WHERE is_active = 1"),
                    ("IX_assignment_employee_section", "tabel_pengajuan_assignment", "(assigned_to_employee, section_name)", "WHERE is_active = 1"),
                    ("IX_assignment_type", "tabel_pengajuan_assignment", "(assignment_type, assignment_date)", "WHERE is_active = 1")
                ]
                
                for index_name, table_name, columns, where_clause in indexes:
                    index_sql = f"""
                        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = '{index_name}')
                        BEGIN
                            CREATE NONCLUSTERED INDEX [{index_name}] ON [{table_name}] {columns} {where_clause}
                        END
                    """
                    
                    if dry_run:
                        self.stdout.write(f"  Would create index: {index_name}")
                    else:
                        try:
                            cursor.execute(index_sql)
                            self.stdout.write(f"  ✓ Index created/verified: {index_name}")
                        except Exception as idx_error:
                            self.stdout.write(f"  ⚠️  Index {index_name} issue: {idx_error}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error fixing schema: {e}"))
            raise
    
    def fix_existing_assignments(self, dry_run):
        """Fix existing assignment data"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Update existing assignments with missing SDBM data
                cursor.execute("""
                    SELECT id, assigned_to_employee, history_id, notes
                    FROM tabel_pengajuan_assignment 
                    WHERE is_active = 1 
                        AND (target_section IS NULL OR department_name IS NULL)
                """)
                
                assignments_to_fix = cursor.fetchall()
                
                if not assignments_to_fix:
                    self.stdout.write("  ✓ No assignments need fixing")
                    return
                
                self.stdout.write(f"  Found {len(assignments_to_fix)} assignments to fix")
                
                for assignment_id, employee_number, history_id, notes in assignments_to_fix:
                    try:
                        # Get employee data from SDBM
                        sdbm_data = self.get_employee_sdbm_data(employee_number)
                        
                        if sdbm_data:
                            # Determine target section from section name
                            target_section = self.determine_target_section(sdbm_data['section_name'])
                            
                            update_sql = """
                                UPDATE tabel_pengajuan_assignment 
                                SET target_section = %s,
                                    department_name = %s,
                                    section_name = %s,
                                    assignment_type = 'SITI_REVIEW',
                                    created_by_system = 'MIGRATION_FIX',
                                    sdbm_employee_data = %s
                                WHERE id = %s
                            """
                            
                            import json
                            sdbm_json = json.dumps(sdbm_data)
                            
                            if dry_run:
                                self.stdout.write(f"    Would fix assignment {assignment_id}: {employee_number} -> {target_section}")
                            else:
                                cursor.execute(update_sql, [
                                    target_section,
                                    sdbm_data['department_name'],
                                    sdbm_data['section_name'],
                                    sdbm_json,
                                    assignment_id
                                ])
                                self.stdout.write(f"    ✓ Fixed assignment {assignment_id}: {employee_number} -> {target_section}")
                        else:
                            self.stdout.write(f"    ⚠️  No SDBM data found for employee {employee_number}")
                            
                    except Exception as fix_error:
                        self.stdout.write(f"    ❌ Error fixing assignment {assignment_id}: {fix_error}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error fixing assignments: {e}"))
    
    def get_employee_sdbm_data(self, employee_number):
        """Get employee data from SDBM"""
        try:
            with connections['SDBM'].cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        e.employee_number,
                        e.fullname,
                        e.nickname,
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
                    WHERE e.employee_number = %s
                        AND e.is_active = 1
                        AND p.is_active = 1
                    ORDER BY p.id DESC
                """, [employee_number])
                
                row = cursor.fetchone()
                if row:
                    return {
                        'employee_number': row[0],
                        'fullname': row[1],
                        'nickname': row[2],
                        'department_name': row[3],
                        'section_name': row[4],
                        'title_name': row[5],
                        'is_supervisor': row[6],
                        'is_manager': row[7]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting SDBM data for {employee_number}: {e}")
            return None
    
    def determine_target_section(self, section_name):
        """Determine target section from SDBM section name"""
        if not section_name:
            return None
        
        section_upper = section_name.upper()
        
        if 'IT' in section_upper or 'INFORMATION' in section_upper:
            return 'it'
        elif 'ELECTRIC' in section_upper or 'ELEKTRIK' in section_upper:
            return 'elektrik'
        elif 'MECHANIC' in section_upper or 'MEKANIK' in section_upper:
            return 'mekanik'
        elif 'UTILITY' in section_upper or 'UTILITIES' in section_upper:
            return 'utility'
        
        return None
    
    def debug_user_assignments(self, employee_number):
        """Debug specific user assignments"""
        try:
            self.stdout.write(f"  Debugging user: {employee_number}")
            
            # Get SDBM data
            sdbm_data = self.get_employee_sdbm_data(employee_number)
            if sdbm_data:
                self.stdout.write(f"    ✓ SDBM Data:")
                self.stdout.write(f"      Name: {sdbm_data['fullname']}")
                self.stdout.write(f"      Department: {sdbm_data['department_name']}")
                self.stdout.write(f"      Section: {sdbm_data['section_name']}")
                self.stdout.write(f"      Title: {sdbm_data['title_name']}")
                self.stdout.write(f"      Is Supervisor: {sdbm_data['is_supervisor']}")
                self.stdout.write(f"      Is Manager: {sdbm_data['is_manager']}")
            else:
                self.stdout.write(f"    ❌ No SDBM data found")
                return
            
            # Check assignments
            try:
                with connections['DB_Maintenance'].cursor() as cursor:
                    cursor.execute("""
                        SELECT history_id, assignment_date, target_section, 
                               section_name, assignment_type, notes
                        FROM tabel_pengajuan_assignment 
                        WHERE assigned_to_employee = %s AND is_active = 1
                        ORDER BY assignment_date DESC
                    """, [employee_number])
                    
                    assignments = cursor.fetchall()
                    
                    if assignments:
                        self.stdout.write(f"    ✓ Found {len(assignments)} assignments:")
                        for assignment in assignments:
                            self.stdout.write(f"      - {assignment[0]} | {assignment[1]} | {assignment[2]} | {assignment[3]}")
                    else:
                        self.stdout.write(f"    ⚠️  No assignments found")
                        
                        # Check if there are assignments for their section
                        section_name = sdbm_data['section_name']
                        cursor.execute("""
                            SELECT COUNT(*) FROM tabel_pengajuan_assignment 
                            WHERE section_name = %s AND is_active = 1
                        """, [section_name])
                        
                        section_assignments = cursor.fetchone()[0]
                        self.stdout.write(f"    ℹ️  Total assignments for section {section_name}: {section_assignments}")
                        
            except Exception as assign_error:
                self.stdout.write(f"    ❌ Error checking assignments: {assign_error}")
            
            # Test if they should have access to any pengajuan
            try:
                from wo_maintenance_app.utils import get_assigned_pengajuan_for_sdbm_user
                assigned_pengajuan = get_assigned_pengajuan_for_sdbm_user(employee_number)
                self.stdout.write(f"    ℹ️  Assigned pengajuan count: {len(assigned_pengajuan)}")
                
            except Exception as util_error:
                self.stdout.write(f"    ❌ Error getting assigned pengajuan: {util_error}")
                
        except Exception as e:
            self.stdout.write(f"    ❌ Error debugging user: {e}")
    
    def test_supervisor_lookup(self):
        """Test SDBM supervisor lookup for all sections"""
        test_sections = ['it', 'elektrik', 'mekanik', 'utility']
        
        for section in test_sections:
            try:
                from wo_maintenance_app.utils import get_sdbm_supervisors_by_section_mapping
                
                supervisors = get_sdbm_supervisors_by_section_mapping(section)
                self.stdout.write(f"  {section.upper()}: {len(supervisors)} supervisors")
                
                if supervisors:
                    for supervisor in supervisors[:2]:  # Show first 2
                        self.stdout.write(f"    - {supervisor['fullname']} ({supervisor['section_name']})")
                    if len(supervisors) > 2:
                        self.stdout.write(f"    - and {len(supervisors) - 2} more...")
                else:
                    # Debug why no supervisors found
                    from wo_maintenance_app.utils import get_sdbm_section_mapping
                    section_mapping = get_sdbm_section_mapping()
                    section_info = section_mapping.get(section, {})
                    
                    if section_info:
                        dept_name = section_info['department_name']
                        sect_name = section_info['section_name']
                        
                        with connections['SDBM'].cursor() as cursor:
                            # Check if department exists
                            cursor.execute("""
                                SELECT COUNT(*) FROM [hr].[department] 
                                WHERE UPPER(name) = UPPER(%s)
                            """, [dept_name])
                            dept_count = cursor.fetchone()[0]
                            
                            # Check if section exists
                            cursor.execute("""
                                SELECT COUNT(*) FROM [hr].[section] 
                                WHERE UPPER(name) = UPPER(%s)
                            """, [sect_name])
                            sect_count = cursor.fetchone()[0]
                            
                            # Check employees in this dept/section
                            cursor.execute("""
                                SELECT COUNT(*) 
                                FROM [hrbp].[employees] e
                                INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                                INNER JOIN [hr].[department] d ON p.departmentId = d.id
                                INNER JOIN [hr].[section] s ON p.sectionId = s.id
                                WHERE UPPER(d.name) = UPPER(%s)
                                    AND UPPER(s.name) = UPPER(%s)
                                    AND e.is_active = 1
                            """, [dept_name, sect_name])
                            emp_count = cursor.fetchone()[0]
                            
                            self.stdout.write(f"    Debug: Dept={dept_count}, Sect={sect_count}, Emp={emp_count}")
                
            except Exception as lookup_error:
                self.stdout.write(f"  {section.upper()}: ERROR - {lookup_error}")
    
    def final_validation(self):
        """Final validation of fixes"""
        try:
            issues_fixed = 0
            remaining_issues = 0
            
            # Check schema
            with connections['DB_Maintenance'].cursor() as cursor:
                enhanced_columns = ['assignment_type', 'target_section', 'department_name', 'section_name']
                for column in enhanced_columns:
                    cursor.execute("""
                        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'tabel_pengajuan_assignment' AND COLUMN_NAME = %s
                    """, [column])
                    
                    if cursor.fetchone()[0] > 0:
                        issues_fixed += 1
                    else:
                        remaining_issues += 1
                        self.stdout.write(f"  ❌ Column still missing: {column}")
                
                # Check assignment data quality
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan_assignment 
                    WHERE is_active = 1 
                        AND target_section IS NOT NULL 
                        AND section_name IS NOT NULL
                """)
                good_assignments = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan_assignment WHERE is_active = 1")
                total_assignments = cursor.fetchone()[0]
                
                self.stdout.write(f"  ✓ Assignment data quality: {good_assignments}/{total_assignments}")
            
            # Test one assignment creation
            try:
                from wo_maintenance_app.utils import assign_pengajuan_after_siti_review
                self.stdout.write("  ✓ Assignment function available")
            except Exception as func_error:
                remaining_issues += 1
                self.stdout.write(f"  ❌ Assignment function error: {func_error}")
            
            self.stdout.write(f"  Summary: {issues_fixed} issues fixed, {remaining_issues} remaining")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Validation error: {e}"))


# Usage:
# python manage.py fix_sdbm_assignment --dry-run                    # Preview fixes
# python manage.py fix_sdbm_assignment --fix-schema                 # Fix database schema  
# python manage.py fix_sdbm_assignment --fix-assignments            # Fix existing data
# python manage.py fix_sdbm_assignment --debug-user 001605          # Debug specific user
# python manage.py fix_sdbm_assignment --fix-schema --fix-assignments  # Fix everything
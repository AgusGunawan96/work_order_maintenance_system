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

    def get_available_sections_for_review():
        """
        Get daftar section yang tersedia untuk distribusi pengajuan
        Dengan prioritas untuk IT, Elektrik, Mekanik, Utility
        """
        try:
            sections = []
            
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT id_section, seksi 
                    FROM tabel_msection 
                    WHERE (status = 'A' OR status IS NULL) 
                        AND seksi IS NOT NULL
                        AND seksi != ''
                        AND LEN(LTRIM(RTRIM(seksi))) > 0
                    ORDER BY 
                        CASE 
                            WHEN seksi LIKE '%IT%' OR seksi LIKE '%INFORMATION%' THEN 1
                            WHEN seksi LIKE '%ELEKTRIK%' OR seksi LIKE '%ELECTRIC%' THEN 2
                            WHEN seksi LIKE '%MEKANIK%' OR seksi LIKE '%MECHANIC%' THEN 3
                            WHEN seksi LIKE '%UTILITY%' OR seksi LIKE '%UTILITIES%' THEN 4
                            ELSE 5
                        END,
                        seksi
                """)
                
                for row in cursor.fetchall():
                    section_id = int(float(row[0]))
                    section_name = str(row[1]).strip()
                    
                    # Determine category and icon
                    category = "Other"
                    icon = "🔧"
                    
                    if any(keyword in section_name.upper() for keyword in ['IT', 'INFORMATION', 'SYSTEM', 'TEKNOLOGI']):
                        category = "IT"
                        icon = "💻"
                    elif any(keyword in section_name.upper() for keyword in ['ELEKTRIK', 'ELECTRIC', 'LISTRIK']):
                        category = "Elektrik"
                        icon = "⚡"
                    elif any(keyword in section_name.upper() for keyword in ['MEKANIK', 'MECHANIC', 'MECHANICAL']):
                        category = "Mekanik"
                        icon = "🔧"
                    elif any(keyword in section_name.upper() for keyword in ['UTILITY', 'UTILITIES', 'UMUM']):
                        category = "Utility"
                        icon = "🏭"
                    
                    sections.append({
                        'id': section_id,
                        'name': section_name,
                        'category': category,
                        'icon': icon,
                        'display_name': f"{icon} {section_name}"
                    })
            
            logger.info(f"Retrieved {len(sections)} sections for review distribution")
            return sections
            
        except Exception as e:
            logger.error(f"Error getting available sections for review: {e}")
            return [
                {'id': 1, 'name': 'IT', 'category': 'IT', 'icon': '💻', 'display_name': '💻 IT'},
                {'id': 2, 'name': 'Elektrik', 'category': 'Elektrik', 'icon': '⚡', 'display_name': '⚡ Elektrik'},
                {'id': 3, 'name': 'Mekanik', 'category': 'Mekanik', 'icon': '🔧', 'display_name': '🔧 Mekanik'},
                {'id': 4, 'name': 'Utility', 'category': 'Utility', 'icon': '🏭', 'display_name': '🏭 Utility'}
            ]
        
    def get_section_supervisors_for_assignment(section_id):
        """
        Get supervisors di section tertentu untuk auto-assignment setelah review
        """
        try:
            supervisors = []
            
            with connections['SDBM'].cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT
                        e.employee_number,
                        e.fullname,
                        e.nickname,
                        d.name as department_name,
                        s.name as section_name,
                        t.Name as title_name,
                        t.is_supervisor,
                        t.is_manager,
                        t.is_generalManager
                    FROM hrbp.employees e
                    INNER JOIN hrbp.position p ON e.id = p.employeeId
                    LEFT JOIN hr.department d ON p.departmentId = d.id
                    LEFT JOIN hr.section s ON p.sectionId = s.id
                    LEFT JOIN hr.title t ON p.titleId = t.id
                    WHERE e.is_active = 1
                        AND p.is_active = 1
                        AND (t.is_supervisor = 1 OR t.is_manager = 1 OR 
                            t.Name LIKE '%SUPERVISOR%' OR t.Name LIKE '%MANAGER%' OR 
                            t.Name LIKE '%SPV%' OR t.Name LIKE '%MGR%')
                        AND s.name IS NOT NULL
                    ORDER BY 
                        CASE 
                            WHEN t.is_manager = 1 THEN 1
                            WHEN t.is_supervisor = 1 THEN 2
                            ELSE 3
                        END,
                        e.fullname
                """)
                
                for row in cursor.fetchall():
                    supervisor = {
                        'employee_number': row[0],
                        'fullname': row[1],
                        'nickname': row[2],
                        'department_name': row[3],
                        'section_name': row[4],
                        'title_name': row[5],
                        'is_supervisor': row[6],
                        'is_manager': row[7],
                        'is_general_manager': row[8],
                        'level': 'Manager' if row[7] else 'Supervisor'
                    }
                    supervisors.append(supervisor)
            
            logger.info(f"Found {len(supervisors)} supervisors for section assignment")
            return supervisors
            
        except Exception as e:
            logger.error(f"Error getting section supervisors: {e}")
            return []


def assign_pengajuan_after_review(history_id, final_section_id, reviewer_employee):
    """
    Auto-assign pengajuan ke supervisors di final section setelah review SITI FATIMAH
    """
    try:
        assigned_count = 0
        
        # Get supervisors di final section
        supervisors = get_section_supervisors_for_assignment(final_section_id)
        
        if not supervisors:
            logger.warning(f"No supervisors found for auto-assignment to section {final_section_id}")
            return []
        
        # Ensure assignment table exists
        ensure_assignment_tables_exist()
        
        assigned_employees = []
        
        with connections['DB_Maintenance'].cursor() as cursor:
            for supervisor in supervisors:
                try:
                    # Check if already assigned
                    cursor.execute("""
                        SELECT COUNT(*) FROM tabel_pengajuan_assignment
                        WHERE history_id = %s AND assigned_to_employee = %s AND is_active = 1
                    """, [history_id, supervisor['employee_number']])
                    
                    if cursor.fetchone()[0] > 0:
                        logger.debug(f"Pengajuan {history_id} already assigned to {supervisor['employee_number']}")
                        continue
                    
                    # Insert assignment
                    cursor.execute("""
                        INSERT INTO tabel_pengajuan_assignment 
                        (history_id, assigned_to_employee, assigned_by_employee, assignment_date, 
                         notes, assignment_type, is_active)
                        VALUES (%s, %s, %s, GETDATE(), %s, %s, 1)
                    """, [
                        history_id,
                        supervisor['employee_number'],
                        reviewer_employee,
                        f'Auto-assigned after review to {supervisor["level"]} in {supervisor["section_name"]}',
                        'AUTO_REVIEW'
                    ])
                    
                    assigned_employees.append(supervisor['employee_number'])
                    assigned_count += 1
                    
                    logger.info(f"Auto-assigned pengajuan {history_id} to {supervisor['fullname']} ({supervisor['employee_number']})")
                    
                except Exception as assign_error:
                    logger.error(f"Error assigning to {supervisor['employee_number']}: {assign_error}")
                    continue
        
        logger.info(f"Successfully auto-assigned pengajuan {history_id} to {assigned_count} supervisors in section {final_section_id}")
        return assigned_employees
        
    except Exception as e:
        logger.error(f"Error in assign_pengajuan_after_review: {e}")
        return []


def log_review_action(history_id, reviewer_employee, action, final_section_id=None, review_notes=None, priority_level='normal'):
    """
    Log review action untuk audit trail
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Ensure review log table exists
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
                        [priority_level] [varchar](20) NULL
                    )
                END
            """)
            
            # Insert log
            cursor.execute("""
                INSERT INTO tabel_review_log 
                (history_id, reviewer_employee, action, final_section_id, review_notes, review_date, priority_level)
                VALUES (%s, %s, %s, %s, %s, GETDATE(), %s)
            """, [history_id, reviewer_employee, action, final_section_id, review_notes, priority_level])
            
            logger.info(f"Review action logged: {history_id} - {action} by {reviewer_employee}")
            return True
            
    except Exception as e:
        logger.error(f"Error logging review action: {e}")
        return False


def get_review_statistics_for_siti():
    """
    Get statistik review khusus untuk SITI FATIMAH dashboard
    """
    try:
        stats = {}
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Total approved pengajuan
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_pengajuan 
                WHERE status = '1' AND approve = '1'
            """)
            stats['total_approved'] = cursor.fetchone()[0] or 0
            
            # Pending review
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_pengajuan 
                WHERE status = '1' AND approve = '1' 
                    AND (review_status IS NULL OR review_status = '0')
            """)
            stats['pending_review'] = cursor.fetchone()[0] or 0
            
            # Already reviewed
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_pengajuan 
                WHERE reviewed_by = %s
            """, [REVIEWER_EMPLOYEE_NUMBER])
            stats['total_reviewed'] = cursor.fetchone()[0] or 0
            
            # Reviewed today
            today = timezone.now().date()
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_pengajuan 
                WHERE reviewed_by = %s 
                    AND CAST(review_date AS DATE) = %s
            """, [REVIEWER_EMPLOYEE_NUMBER, today])
            stats['reviewed_today'] = cursor.fetchone()[0] or 0
            
            # Review breakdown by action
            cursor.execute("""
                SELECT review_status, COUNT(*) 
                FROM tabel_pengajuan 
                WHERE reviewed_by = %s
                GROUP BY review_status
            """, [REVIEWER_EMPLOYEE_NUMBER])
            
            review_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
            stats['approved_count'] = review_breakdown.get('1', 0)
            stats['rejected_count'] = review_breakdown.get('2', 0)
            
            # Distribution by section
            cursor.execute("""
                SELECT ms.seksi, COUNT(*) 
                FROM tabel_pengajuan tp
                INNER JOIN tabel_msection ms ON tp.final_section_id = ms.id_section
                WHERE tp.reviewed_by = %s AND tp.review_status = '1'
                GROUP BY ms.seksi
                ORDER BY COUNT(*) DESC
            """, [REVIEWER_EMPLOYEE_NUMBER])
            
            stats['section_distribution'] = [
                {'section': row[0], 'count': row[1]} 
                for row in cursor.fetchall()
            ]
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting review statistics: {e}")
        return {
            'total_approved': 0,
            'pending_review': 0,
            'total_reviewed': 0,
            'reviewed_today': 0,
            'approved_count': 0,
            'rejected_count': 0,
            'section_distribution': []
        }



# USAGE:
# python manage.py setup_review_system --dry-run  # Preview changes
# python manage.py setup_review_system             # Apply changes
# python manage.py setup_review_system --force     # Force recreation of existing objects
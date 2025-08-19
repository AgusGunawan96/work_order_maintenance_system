# wo_maintenance_app/utils.py - FIXED VERSION dengan Enhanced SITI FATIMAH Access
from django.db import connections
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

# ===== UPDATED STATUS CONSTANTS sesuai requirement baru =====
STATUS_PENDING = '0'          # Pending (belum di-approve atasan)
STATUS_APPROVED = 'B'         # UPDATED: Approved oleh atasan (siap untuk review SITI)
STATUS_REVIEWED = 'A'         # UPDATED: Sudah diproses review oleh SITI FATIMAH (final)
STATUS_REJECTED = '2'         # Rejected
STATUS_IN_PROGRESS = '3'      # In Progress
STATUS_COMPLETED = '4'        # Completed

APPROVE_NO = '0'              # Not Approved
APPROVE_YES = 'N'             # UPDATED: Approved oleh atasan (siap untuk review SITI)
APPROVE_REVIEWED = 'Y'        # UPDATED: Sudah diproses review oleh SITI FATIMAH (final)
APPROVE_REJECTED = '2'        # Rejected

# ===== REVIEWER CONSTANTS =====
REVIEWER_EMPLOYEE_NUMBER = '007522'  # SITI FATIMAH
REVIEWER_FULLNAME = 'SITI FATIMAH'

# ===== REVIEW STATUS CONSTANTS =====
REVIEW_PENDING = '0'       # Review pending
REVIEW_APPROVED = '1'      # Review approved 
REVIEW_REJECTED = '2'      # Review rejected

def is_pengajuan_approved_for_review(status, approve):
    """
    UPDATED: Check apakah pengajuan approved oleh atasan dan ready for review SITI
    Status='B' dan Approve='N' = sudah approved atasan, siap review SITI
    """
    # Primary check: B and N (approved oleh atasan, siap review)
    if status == STATUS_APPROVED and approve == APPROVE_YES:
        return True
    
    # Legacy support jika masih ada data lama
    if status == '1' and approve == '1':
        logger.warning(f"Using legacy status format: status=1, approve=1")
        return True
    
    return False

def is_pengajuan_final_processed(status, approve):
    """
    NEW: Check apakah pengajuan sudah final diproses oleh SITI FATIMAH
    Status='A' dan Approve='Y' = sudah final diproses, tidak perlu ditampilkan di daftar
    """
    return status == STATUS_REVIEWED and approve == APPROVE_REVIEWED

def assign_pengajuan_after_siti_review(history_id, target_section, reviewer_employee_number, review_notes):
    """
    FIXED: Assign pengajuan setelah review oleh SITI FATIMAH dengan SDBM integration
    
    Args:
        history_id (str): ID pengajuan
        target_section (str): Target section (it, elektrik, utility, mekanik)
        reviewer_employee_number (str): Employee number reviewer (SITI FATIMAH)
        review_notes (str): Catatan review
        
    Returns:
        dict: Result of assignment process
    """
    try:
        logger.info(f"SITI REVIEW ASSIGNMENT: Starting assignment for {history_id} to {target_section}")
        
        # Section mapping
        section_mapping = {
            'it': {
                'display_name': '💻 IT',
                'maintenance_section_id': 1,
                'department_name': 'ENGINEERING',
                'section_name': 'ENGINEERING-IT'
            },
            'elektrik': {
                'display_name': '⚡ Elektrik',
                'maintenance_section_id': 2,
                'department_name': 'ENGINEERING',
                'section_name': 'ENGINEERING-ELECTRIC'
            },
            'utility': {
                'display_name': '🏭 Utility',
                'maintenance_section_id': 4,
                'department_name': 'ENGINEERING',
                'section_name': 'ENGINEERING-UTILITY'
            },
            'mekanik': {
                'display_name': '🔧 Mekanik',
                'maintenance_section_id': 3,
                'department_name': 'ENGINEERING',
                'section_name': 'ENGINEERING-MECHANIC'
            }
        }
        
        section_info = section_mapping.get(target_section)
        if not section_info:
            return {
                'success': False,
                'error': f'Unknown target section: {target_section}',
                'assigned_employees': []
            }
        
        result = {
            'success': True,
            'assigned_employees': [],
            'section_updated': False,
            'new_section_id': None,
            'error': None
        }
        
        # Update final_section_id di pengajuan
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    UPDATE tabel_pengajuan
                    SET final_section_id = %s
                    WHERE history_id = %s
                """, [float(section_info['maintenance_section_id']), history_id])
                
                if cursor.rowcount > 0:
                    result['section_updated'] = True
                    result['new_section_id'] = section_info['maintenance_section_id']
                    logger.info(f"SITI REVIEW: Updated final_section_id to {section_info['maintenance_section_id']} for {history_id}")
                
        except Exception as update_error:
            logger.error(f"SITI REVIEW: Error updating section: {update_error}")
            result['error'] = f'Failed to update section: {str(update_error)}'
        
        # Get SDBM supervisors untuk target section
        try:
            supervisors = get_sdbm_supervisors_by_section_mapping(target_section)
            
            if supervisors:
                # Create assignment table if not exists
                ensure_assignment_tables_exist()
                
                # Assign ke supervisors
                with connections['DB_Maintenance'].cursor() as cursor:
                    for supervisor in supervisors:
                        try:
                            cursor.execute("""
                                INSERT INTO tabel_pengajuan_assignment
                                (history_id, assigned_to_employee, assigned_by_employee, assignment_date, is_active, notes, assignment_type)
                                VALUES (%s, %s, %s, GETDATE(), 1, %s, 'SITI_REVIEW')
                            """, [
                                history_id,
                                supervisor['employee_number'],
                                reviewer_employee_number,
                                f"SITI FATIMAH Review: Assigned to {section_info['display_name']} - {supervisor['title_name']}. Notes: {review_notes}"
                            ])
                            
                            result['assigned_employees'].append({
                                'employee_number': supervisor['employee_number'],
                                'fullname': supervisor['fullname'],
                                'title_name': supervisor['title_name'],
                                'level_description': supervisor.get('level_description', 'Supervisor')
                            })
                            
                            logger.info(f"SITI REVIEW: Assigned {history_id} to {supervisor['fullname']} ({supervisor['employee_number']})")
                            
                        except Exception as assign_error:
                            logger.error(f"SITI REVIEW: Error assigning to {supervisor['employee_number']}: {assign_error}")
                            continue
                
                logger.info(f"SITI REVIEW: Successfully assigned {history_id} to {len(result['assigned_employees'])} supervisors in {target_section}")
                
            else:
                logger.warning(f"SITI REVIEW: No supervisors found for {target_section}")
                result['error'] = f'No supervisors found for {target_section}'
                
        except Exception as sdbm_error:
            logger.error(f"SITI REVIEW: SDBM assignment error: {sdbm_error}")
            result['error'] = f'SDBM assignment failed: {str(sdbm_error)}'
        
        return result
        
    except Exception as e:
        logger.error(f"SITI REVIEW: Critical error in assignment: {e}")
        return {
            'success': False,
            'error': str(e),
            'assigned_employees': [],
            'section_updated': False
        }

def get_sdbm_supervisors_by_section_mapping(target_section):
    """
    Get SDBM supervisors berdasarkan target section mapping
    
    Args:
        target_section (str): Target section key (it, elektrik, utility, mekanik)
        
    Returns:
        list: List of supervisors dari SDBM
    """
    try:
        section_mapping = {
            'it': {
                'department_name': 'ENGINEERING',
                'section_name': 'ENGINEERING-IT'
            },
            'elektrik': {
                'department_name': 'ENGINEERING',
                'section_name': 'ENGINEERING-ELECTRIC'
            },
            'utility': {
                'department_name': 'ENGINEERING',
                'section_name': 'ENGINEERING-UTILITY'
            },
            'mekanik': {
                'department_name': 'ENGINEERING',
                'section_name': 'ENGINEERING-MECHANIC'
            }
        }
        
        section_info = section_mapping.get(target_section)
        if not section_info:
            logger.warning(f"Unknown target section: {target_section}")
            return []
        
        supervisors = []
        
        with connections['SDBM'].cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT
                    e.employee_number,
                    e.fullname,
                    e.nickname,
                    t.Name as title_name,
                    t.is_supervisor,
                    t.is_manager,
                    t.is_generalManager,
                    t.is_bod,
                    s.name as section_name,
                    d.name as department_name,
                    e.job_status
                    
                FROM [hrbp].[employees] e
                INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                LEFT JOIN [hr].[department] d ON p.departmentId = d.id
                LEFT JOIN [hr].[section] s ON p.sectionId = s.id
                LEFT JOIN [hr].[title] t ON p.titleId = t.id
                
                WHERE e.is_active = 1
                    AND p.is_active = 1
                    AND (d.is_active IS NULL OR d.is_active = 1)
                    AND (s.is_active IS NULL OR s.is_active = 1)
                    AND (t.is_active IS NULL OR t.is_active = 1)
                    AND UPPER(d.name) = UPPER(%s)
                    AND UPPER(s.name) = UPPER(%s)
                    AND (
                        t.is_supervisor = 1 OR 
                        t.is_manager = 1 OR 
                        t.is_generalManager = 1 OR 
                        t.is_bod = 1 OR
                        UPPER(t.Name) LIKE '%SUPERVISOR%' OR
                        UPPER(t.Name) LIKE '%MANAGER%'
                    )
                    AND e.employee_number != %s
                    
                ORDER BY 
                    CASE 
                        WHEN t.is_bod = 1 OR UPPER(t.Name) LIKE '%DIRECTOR%' THEN 15
                        WHEN t.is_generalManager = 1 OR UPPER(t.Name) LIKE '%GENERAL%' THEN 13
                        WHEN t.is_manager = 1 OR UPPER(t.Name) LIKE '%MANAGER%' THEN 12
                        WHEN t.is_supervisor = 1 OR UPPER(t.Name) LIKE '%SUPERVISOR%' THEN 9
                        ELSE 8
                    END DESC,
                    e.fullname
            """, [section_info['department_name'], section_info['section_name'], REVIEWER_EMPLOYEE_NUMBER])
            
            rows = cursor.fetchall()
            
            for row in rows:
                # Determine level based on title
                title_name = str(row[3] or '').upper()
                level = get_title_level(title_name)
                
                supervisors.append({
                    'employee_number': row[0],
                    'fullname': row[1],
                    'nickname': row[2],
                    'title_name': row[3],
                    'is_supervisor': row[4],
                    'is_manager': row[5],
                    'is_general_manager': row[6],
                    'is_bod': row[7],
                    'section_name': row[8],
                    'department_name': row[9],
                    'job_status': row[10],
                    'level': level,
                    'level_description': get_level_description(level)
                })
                
        logger.info(f"Found {len(supervisors)} supervisors for {target_section} in {section_info['department_name']}/{section_info['section_name']}")
        return supervisors
        
    except Exception as e:
        logger.error(f"Error getting SDBM supervisors for {target_section}: {e}")
        return []
    
def get_employee_hierarchy_data(user):
    """
    Mendapatkan data hierarchy employee dari database SDBM berdasarkan user yang login
    UPDATED: Better error handling and timeout protection
    
    Returns:
        dict: Data hierarchy employee atau None jika tidak ditemukan
    """
    if not user or not user.is_authenticated:
        return None
    
    try:
        with connections['SDBM'].cursor() as cursor:
            # Simplified query dengan timeout protection
            cursor.execute("""
                SELECT DISTINCT TOP 1
                    e.id as employee_id,
                    e.fullname,
                    e.nickname,
                    e.employee_number,
                    e.job_status,
                    e.level_user,
                    
                    -- Position data
                    p.id as position_id,
                    p.departmentId,
                    p.sectionId,
                    p.subsectionId,
                    p.titleId,
                    
                    -- Department info
                    d.name as department_name,
                    
                    -- Section info
                    s.name as section_name,
                    
                    -- Title info
                    t.Name as title_name,
                    t.is_manager,
                    t.is_supervisor,
                    t.is_generalManager,
                    t.is_bod
                    
                FROM [hrbp].[employees] e
                INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                LEFT JOIN [hr].[department] d ON p.departmentId = d.id
                LEFT JOIN [hr].[section] s ON p.sectionId = s.id  
                LEFT JOIN [hr].[title] t ON p.titleId = t.id
                
                WHERE e.employee_number = %s 
                    AND e.is_active = 1
                    AND p.is_active = 1
                    
                ORDER BY p.id DESC
            """, [user.username])
            
            row = cursor.fetchone()
            
            if row:
                employee_data = {
                    'employee_id': row[0],
                    'fullname': row[1],
                    'nickname': row[2],
                    'employee_number': row[3],
                    'job_status': row[4],
                    'level_user': row[5],
                    'position_id': row[6],
                    'department_id': row[7],
                    'section_id': row[8],
                    'subsection_id': row[9],
                    'title_id': row[10],
                    'department_name': row[11],
                    'section_name': row[12],
                    'title_name': row[13],
                    'is_manager': row[14],
                    'is_supervisor': row[15],
                    'is_general_manager': row[16],
                    'is_bod': row[17]
                }
                
                # ENHANCED: Special privileges untuk SITI FATIMAH
                if employee_data['employee_number'] == REVIEWER_EMPLOYEE_NUMBER:
                    employee_data.update({
                        'is_reviewer': True,
                        'has_full_access': True,
                        'can_access_approved_pengajuan': True,  # UPDATED: access ke status B/N
                        'review_authority': 'ALL_SECTIONS',
                        'special_role': 'REVIEWER_SITI_FATIMAH'
                    })
                    logger.info(f"Enhanced privileges granted to SITI FATIMAH: {employee_data['fullname']}")
                
                return employee_data
            else:
                logger.warning(f"Employee data not found for user: {user.username}")
                return None
                
    except Exception as e:
        logger.error(f"Error getting employee hierarchy data for user {user.username}: {e}")
        return None

# Helper function untuk convert status values
def normalize_status_value(status_value):
    """
    Normalize status value untuk compatibility
    """
    if status_value in ['1', 1]:
        return STATUS_APPROVED  # 'A'
    elif status_value in ['0', 0]:
        return STATUS_PENDING   # '0'
    elif status_value in ['2', 2]:
        return STATUS_REJECTED  # '2'
    else:
        return str(status_value)


def normalize_approve_value(approve_value):
    """
    Normalize approve value untuk compatibility
    """
    if approve_value in ['1', 1]:
        return APPROVE_YES      # 'Y'
    elif approve_value in ['0', 0]:
        return APPROVE_NO       # '0'
    elif approve_value in ['2', 2]:
        return APPROVE_REJECTED # '2'
    else:
        return str(approve_value)

def can_user_approve(user_hierarchy, target_user_hierarchy):
    """
    Mengecek apakah user dapat melakukan approve terhadap target user berdasarkan hierarchy
    UPDATED: Special handling untuk SITI FATIMAH dan new status logic
    
    Args:
        user_hierarchy (dict): Data hierarchy user yang akan melakukan approve
        target_user_hierarchy (dict): Data hierarchy target user (pembuat pengajuan)
    
    Returns:
        bool: True jika dapat approve, False jika tidak
    """
    if not user_hierarchy or not target_user_hierarchy:
        return False
    
    # UPDATED: SITI FATIMAH dapat approve semua pengajuan yang sudah approved atasan (status B/N)
    if user_hierarchy.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER:
        logger.info(f"SITI FATIMAH approval privilege granted for user: {target_user_hierarchy.get('fullname')}")
        return True
    
    # Rest of the approval logic remains same for regular supervisors/managers
    user_title = str(user_hierarchy.get('title_name', '')).upper()
    is_supervisor = user_hierarchy.get('is_supervisor', False)
    is_manager = user_hierarchy.get('is_manager', False) 
    is_general_manager = user_hierarchy.get('is_general_manager', False)
    is_bod = user_hierarchy.get('is_bod', False)
    
    # Cek apakah user memiliki role approval
    has_approval_role = (
        is_supervisor or is_manager or is_general_manager or is_bod or
        'SUPERVISOR' in user_title or 'MANAGER' in user_title or 
        'SPV' in user_title or 'MGR' in user_title
    )
    
    if not has_approval_role:
        return False
    
    # Level hierarchy validation (same as before)
    approval_levels = {
        'OPERATOR': 1,
        'ASSISTANT LEADER': 2,
        'LEADER': 3,
        'FOREMAN': 4,
        'JUNIOR STAFF': 5,
        'STAFF': 6,
        'SENIOR STAFF': 7,
        'ASSISTANT SUPERVISOR': 8,
        'SUPERVISOR': 9,
        'SPV': 9,
        'SENIOR SUPERVISOR': 10,
        'ASSISTANT MANAGER': 11,
        'MANAGER': 12,
        'MGR': 12,
        'GENERAL MANAGER': 13,
        'GM': 13,
        'DIRECTOR': 14,
        'PRESIDENT DIRECTOR': 15,
        'BOD': 15
    }
    
    # Calculate user level
    user_level = 0
    for title, level in approval_levels.items():
        if title in user_title:
            user_level = max(user_level, level)
    
    if is_manager:
        user_level = max(user_level, 12)
    elif is_supervisor:
        user_level = max(user_level, 9)
    elif is_general_manager:
        user_level = max(user_level, 13)
    elif is_bod:
        user_level = max(user_level, 15)
    
    # Calculate target level
    target_title = str(target_user_hierarchy.get('title_name', '')).upper()
    target_is_supervisor = target_user_hierarchy.get('is_supervisor', False)
    target_is_manager = target_user_hierarchy.get('is_manager', False)
    
    target_level = 0
    for title, level in approval_levels.items():
        if title in target_title:
            target_level = max(target_level, level)
    
    if target_is_manager:
        target_level = max(target_level, 12)
    elif target_is_supervisor:
        target_level = max(target_level, 9)
    
    # User dapat approve jika levelnya lebih tinggi dari target
    level_check = user_level > target_level
    
    # Hierarchy department/section check
    same_department = user_hierarchy.get('department_id') == target_user_hierarchy.get('department_id')
    same_section = user_hierarchy.get('section_id') == target_user_hierarchy.get('section_id')
    
    if is_manager or is_general_manager or is_bod or 'MANAGER' in user_title:
        hierarchy_check = same_department
    else:
        hierarchy_check = same_section
    
    result = level_check and hierarchy_check
    
    logger.debug(f"Approval check - User: {user_hierarchy.get('fullname')} (Level: {user_level}) -> "
                f"Target: {target_user_hierarchy.get('fullname')} (Level: {target_level}) = {result}")
    
    return result


def get_subordinate_employee_numbers(user_hierarchy):
    """
    Mendapatkan daftar employee_number dari bawahan berdasarkan hierarchy
    UPDATED: SITI FATIMAH dapat akses semua pengajuan yang belum final processed
    
    Args:
        user_hierarchy (dict): Data hierarchy user
        
    Returns:
        list: Daftar employee_number yang dapat di-manage oleh user
    """
    if not user_hierarchy:
        return []
    
    # UPDATED: SITI FATIMAH dapat mengakses SEMUA pengajuan yang belum final processed
    if user_hierarchy.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER:
        try:
            logger.info(f"SITI FATIMAH granted access to review approved pengajuan")
            return ['*']  # Special indicator untuk review access
                
        except Exception as e:
            logger.error(f"Error getting access for SITI FATIMAH: {e}")
            return ['*']  # Fallback untuk ensure access
    
    # Rest of the hierarchy logic remains same for other users
    try:
        employee_numbers = []
        
        with connections['SDBM'].cursor() as cursor:
            user_title = str(user_hierarchy.get('title_name', '')).upper()
            is_manager = user_hierarchy.get('is_manager', False)
            is_supervisor = user_hierarchy.get('is_supervisor', False) 
            is_general_manager = user_hierarchy.get('is_general_manager', False)
            is_bod = user_hierarchy.get('is_bod', False)
            
            if is_bod or 'BOD' in user_title:
                cursor.execute("""
                    SELECT DISTINCT e.employee_number
                    FROM [hrbp].[employees] e
                    WHERE e.is_active = 1
                """)
                
            elif is_general_manager or 'GENERAL' in user_title or 'GM' in user_title:
                cursor.execute("""
                    SELECT DISTINCT e.employee_number
                    FROM [hrbp].[employees] e
                    WHERE e.is_active = 1
                """)
                
            elif is_manager or 'MANAGER' in user_title or 'MGR' in user_title:
                cursor.execute("""
                    SELECT DISTINCT e.employee_number
                    FROM [hrbp].[employees] e
                    INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                    WHERE e.is_active = 1 
                        AND p.is_active = 1
                        AND p.departmentId = %s
                """, [user_hierarchy.get('department_id')])
                
            elif is_supervisor or 'SUPERVISOR' in user_title or 'SPV' in user_title:
                cursor.execute("""
                    SELECT DISTINCT e.employee_number
                    FROM [hrbp].[employees] e
                    INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                    WHERE e.is_active = 1 
                        AND p.is_active = 1
                        AND p.sectionId = %s
                """, [user_hierarchy.get('section_id')])
                
            else:
                return [user_hierarchy.get('employee_number')]
            
            rows = cursor.fetchall()
            employee_numbers = [row[0] for row in rows if row[0]]
            
            if user_hierarchy.get('employee_number') not in employee_numbers:
                employee_numbers.append(user_hierarchy.get('employee_number'))
            
            logger.debug(f"Found {len(employee_numbers)} subordinates for {user_hierarchy.get('fullname')}")
            
            return employee_numbers
            
    except Exception as e:
        logger.error(f"Error getting subordinate employees for {user_hierarchy.get('fullname')}: {e}")
        return [user_hierarchy.get('employee_number')] if user_hierarchy.get('employee_number') else []


def get_employee_by_number(employee_number):
    """
    Mendapatkan data employee berdasarkan employee_number
    
    Args:
        employee_number (str): Nomor employee
        
    Returns:
        dict: Data employee atau None jika tidak ditemukan
    """
    if not employee_number:
        return None
        
    try:
        with connections['SDBM'].cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT
                    e.id as employee_id,
                    e.fullname,
                    e.nickname, 
                    e.employee_number,
                    e.job_status,
                    e.level_user,
                    
                    -- Position data
                    p.id as position_id,
                    p.departmentId,
                    p.sectionId,
                    p.subsectionId,
                    p.titleId,
                    p.divisionId,
                    
                    -- Department info
                    d.name as department_name,
                    
                    -- Section info
                    s.name as section_name,
                    
                    -- Subsection info
                    sub.name as subsection_name,
                    
                    -- Title info
                    t.Name as title_name,
                    t.is_manager,
                    t.is_supervisor,
                    t.is_generalManager,
                    t.is_bod
                    
                FROM [hrbp].[employees] e
                INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                LEFT JOIN [hr].[department] d ON p.departmentId = d.id
                LEFT JOIN [hr].[section] s ON p.sectionId = s.id  
                LEFT JOIN [hr].[subsection] sub ON p.subsectionId = sub.id
                LEFT JOIN [hr].[title] t ON p.titleId = t.id
                
                WHERE e.employee_number = %s 
                    AND e.is_active = 1
                    AND p.is_active = 1
                    
                ORDER BY p.id DESC
            """, [employee_number])
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'employee_id': row[0],
                    'fullname': row[1],
                    'nickname': row[2],
                    'employee_number': row[3],
                    'job_status': row[4],
                    'level_user': row[5],
                    'position_id': row[6],
                    'department_id': row[7],
                    'section_id': row[8],
                    'subsection_id': row[9],
                    'title_id': row[10],
                    'division_id': row[11],
                    'department_name': row[12],
                    'section_name': row[13],
                    'subsection_name': row[14],
                    'title_name': row[15],
                    'is_manager': row[16],
                    'is_supervisor': row[17],
                    'is_general_manager': row[18],
                    'is_bod': row[19]
                }
            else:
                return None
                
    except Exception as e:
        logger.error(f"Error getting employee by number {employee_number}: {e}")
        return None


def get_supervisors_by_section_and_level(section_mapping_key, min_level='assistant_supervisor'):
    """
    Mendapatkan supervisors berdasarkan section mapping dan minimum level
    ENHANCED: Untuk mendukung SITI FATIMAH assignment berdasarkan level
    
    Args:
        section_mapping_key (str): Key section mapping (it, elektrik, mekanik, utility)
        min_level (str): Minimum level supervisor yang dibutuhkan
        
    Returns:
        list: Daftar supervisors yang memenuhi kriteria
    """
    if not section_mapping_key:
        return []
    
    try:
        # Get section mapping
        section_mapping = get_sdbm_section_mapping()
        target_mapping = section_mapping.get(section_mapping_key)
        
        if not target_mapping:
            logger.warning(f"No section mapping found for: {section_mapping_key}")
            return []
        
        department_name = target_mapping['department_name']
        section_name = target_mapping['section_name']
        
        # Define minimum levels
        level_hierarchy = {
            'assistant_supervisor': 8,
            'supervisor': 9,
            'senior_supervisor': 10,
            'manager': 12,
            'general_manager': 13,
            'director': 14
        }
        
        min_level_value = level_hierarchy.get(min_level, 8)
        
        supervisors = []
        
        with connections['SDBM'].cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT
                    e.employee_number,
                    e.fullname,
                    e.nickname,
                    t.Name as title_name,
                    t.is_supervisor,
                    t.is_manager,
                    t.is_generalManager,
                    t.is_bod,
                    s.name as section_name,
                    d.name as department_name,
                    e.job_status
                    
                FROM [hrbp].[employees] e
                INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                LEFT JOIN [hr].[department] d ON p.departmentId = d.id
                LEFT JOIN [hr].[section] s ON p.sectionId = s.id
                LEFT JOIN [hr].[title] t ON p.titleId = t.id
                
                WHERE e.is_active = 1
                    AND p.is_active = 1
                    AND (d.is_active IS NULL OR d.is_active = 1)
                    AND (s.is_active IS NULL OR s.is_active = 1)
                    AND (t.is_active IS NULL OR t.is_active = 1)
                    AND UPPER(d.name) = UPPER(%s)
                    AND UPPER(s.name) = UPPER(%s)
                    AND (
                        t.is_supervisor = 1 OR 
                        t.is_manager = 1 OR 
                        t.is_generalManager = 1 OR 
                        t.is_bod = 1 OR
                        UPPER(t.Name) LIKE '%SUPERVISOR%' OR
                        UPPER(t.Name) LIKE '%MANAGER%' OR
                        UPPER(t.Name) LIKE '%DIRECTOR%' OR
                        UPPER(t.Name) LIKE '%SPV%' OR
                        UPPER(t.Name) LIKE '%MGR%' OR
                        UPPER(t.Name) LIKE '%ASSISTANT SUPERVISOR%'
                    )
                    
                ORDER BY 
                    CASE 
                        WHEN t.is_bod = 1 OR UPPER(t.Name) LIKE '%DIRECTOR%' THEN 15
                        WHEN t.is_generalManager = 1 OR UPPER(t.Name) LIKE '%GENERAL%' THEN 13
                        WHEN t.is_manager = 1 OR UPPER(t.Name) LIKE '%MANAGER%' THEN 12
                        WHEN UPPER(t.Name) LIKE '%SENIOR SUPERVISOR%' THEN 10
                        WHEN t.is_supervisor = 1 OR UPPER(t.Name) LIKE '%SUPERVISOR%' THEN 9
                        WHEN UPPER(t.Name) LIKE '%ASSISTANT SUPERVISOR%' THEN 8
                        ELSE 8
                    END DESC,
                    e.fullname
            """, [department_name, section_name])
            
            rows = cursor.fetchall()
            
            for row in rows:
                # Tentukan level berdasarkan title
                title_name = str(row[3] or '').upper()
                level = get_title_level(title_name)
                
                # Filter berdasarkan minimum level
                if level >= min_level_value:
                    supervisors.append({
                        'employee_number': row[0],
                        'fullname': row[1],
                        'nickname': row[2],
                        'title_name': row[3],
                        'is_supervisor': row[4],
                        'is_manager': row[5],
                        'is_general_manager': row[6],
                        'is_bod': row[7],
                        'section_name': row[8],
                        'department_name': row[9],
                        'job_status': row[10],
                        'level': level,
                        'level_description': get_level_description(level),
                        'section_mapping_key': section_mapping_key
                    })
                    
            logger.info(f"Found {len(supervisors)} supervisors (min level: {min_level}) for {section_mapping_key} in {department_name}/{section_name}")
            return supervisors
            
    except Exception as e:
        logger.error(f"Error getting supervisors for section {section_mapping_key} with min level {min_level}: {e}")
        return []


def get_target_section_supervisors(section_tujuan_id, exclude_employee_numbers=None, min_level='assistant_supervisor'):
    """
    Mendapatkan daftar assistant supervisor+ di section tujuan untuk assignment pengajuan
    ENHANCED: dengan minimum level filtering
    
    Args:
        section_tujuan_id (int): ID section tujuan (IT, Elektrik, Mekanik, Utility)
        exclude_employee_numbers (list): List employee number yang dikecualikan
        min_level (str): Minimum level supervisor yang dibutuhkan
        
    Returns:
        list: Daftar employee dengan level minimum yang ditentukan di section tujuan
    """
    if not section_tujuan_id:
        return []
        
    if exclude_employee_numbers is None:
        exclude_employee_numbers = []
    
    try:
        supervisors = []
        
        # Level hierarchy
        level_hierarchy = {
            'assistant_supervisor': 8,
            'supervisor': 9,
            'senior_supervisor': 10,
            'manager': 12,
            'general_manager': 13,
            'director': 14
        }
        
        min_level_value = level_hierarchy.get(min_level, 8)
        
        with connections['SDBM'].cursor() as cursor:
            # Query untuk mendapatkan supervisor+ di section tujuan
            exclude_clause = ""
            query_params = [section_tujuan_id]
            
            if exclude_employee_numbers:
                exclude_placeholders = ','.join(['%s'] * len(exclude_employee_numbers))
                exclude_clause = f"AND e.employee_number NOT IN ({exclude_placeholders})"
                query_params.extend(exclude_employee_numbers)
            
            cursor.execute(f"""
                SELECT DISTINCT
                    e.employee_number,
                    e.fullname,
                    e.nickname,
                    t.Name as title_name,
                    t.is_supervisor,
                    t.is_manager,
                    t.is_generalManager,
                    t.is_bod,
                    s.name as section_name,
                    d.name as department_name
                    
                FROM [hrbp].[employees] e
                INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                LEFT JOIN [hr].[department] d ON p.departmentId = d.id
                LEFT JOIN [hr].[section] s ON p.sectionId = s.id
                LEFT JOIN [hr].[title] t ON p.titleId = t.id
                
                WHERE p.sectionId = %s
                    AND e.is_active = 1
                    AND p.is_active = 1
                    AND (
                        t.is_supervisor = 1 OR 
                        t.is_manager = 1 OR 
                        t.is_generalManager = 1 OR 
                        t.is_bod = 1 OR
                        UPPER(t.Name) LIKE '%%SUPERVISOR%%' OR
                        UPPER(t.Name) LIKE '%%MANAGER%%' OR
                        UPPER(t.Name) LIKE '%%DIRECTOR%%' OR
                        UPPER(t.Name) LIKE '%%SPV%%' OR
                        UPPER(t.Name) LIKE '%%MGR%%' OR
                        UPPER(t.Name) LIKE '%%ASSISTANT SUPERVISOR%%'
                    )
                    {exclude_clause}
                    
                ORDER BY 
                    CASE 
                        WHEN t.is_bod = 1 OR UPPER(t.Name) LIKE '%%DIRECTOR%%' THEN 15
                        WHEN t.is_generalManager = 1 OR UPPER(t.Name) LIKE '%%GENERAL%%' THEN 13
                        WHEN t.is_manager = 1 OR UPPER(t.Name) LIKE '%%MANAGER%%' THEN 12
                        WHEN UPPER(t.Name) LIKE '%%SENIOR SUPERVISOR%%' THEN 10
                        WHEN t.is_supervisor = 1 OR UPPER(t.Name) LIKE '%%SUPERVISOR%%' THEN 9
                        WHEN UPPER(t.Name) LIKE '%%ASSISTANT SUPERVISOR%%' THEN 8
                        ELSE 8
                    END DESC
            """, query_params)
            
            rows = cursor.fetchall()
            
            for row in rows:
                # Tentukan level berdasarkan title
                title_name = str(row[3] or '').upper()
                level = get_title_level(title_name)
                
                # Filter berdasarkan minimum level
                if level >= min_level_value:
                    supervisors.append({
                        'employee_number': row[0],
                        'fullname': row[1],
                        'nickname': row[2],
                        'title_name': row[3],
                        'is_supervisor': row[4],
                        'is_manager': row[5],
                        'is_general_manager': row[6],
                        'is_bod': row[7],
                        'section_name': row[8],
                        'department_name': row[9],
                        'level': level,
                        'level_description': get_level_description(level)
                    })
                    
            logger.debug(f"Found {len(supervisors)} supervisors (min level: {min_level}) in section {section_tujuan_id}")
            return supervisors
            
    except Exception as e:
        logger.error(f"Error getting target section supervisors for section {section_tujuan_id}: {e}")
        return []


def get_title_level(title_name):
    """
    Mendapatkan level berdasarkan title name
    
    Args:
        title_name (str): Nama title
        
    Returns:
        int: Level hierarchy
    """
    title_upper = str(title_name or '').upper()
    
    # Cek level berdasarkan keyword dalam title
    level_keywords = {
        'PRESIDENT DIRECTOR': 15,
        'DIRECTOR': 14,
        'GENERAL MANAGER': 13,
        'MANAGER': 12,
        'ASSISTANT MANAGER': 11,
        'SENIOR SUPERVISOR': 10,
        'SUPERVISOR': 9,
        'ASSISTANT SUPERVISOR': 8,
        'SENIOR STAFF': 7,
        'STAFF': 6,
        'JUNIOR STAFF': 5,
        'FOREMAN': 4,
        'LEADER': 3,
        'ASSISTANT LEADER': 2,
        'OPERATOR': 1,
    }
    
    # Cek keyword yang paling spesifik dulu
    for keyword, level in level_keywords.items():
        if keyword in title_upper:
            return level
    
    # Fallback untuk alias
    if 'SPV' in title_upper:
        return 9
    elif 'MGR' in title_upper:
        return 12
    elif 'GM' in title_upper:
        return 13
    elif 'BOD' in title_upper:
        return 15
    
    # Default level jika tidak dikenali
    return 1


def get_level_description(level):
    """
    Get description berdasarkan level hierarchy
    
    Args:
        level (int): Level hierarchy
        
    Returns:
        str: Description level
    """
    level_descriptions = {
        15: 'President Director/BOD',
        14: 'Director', 
        13: 'General Manager',
        12: 'Manager',
        11: 'Assistant Manager',
        10: 'Senior Supervisor',
        9: 'Supervisor',
        8: 'Assistant Supervisor',
        7: 'Senior Staff',
        6: 'Staff',
        5: 'Junior Staff',
        4: 'Foreman',
        3: 'Leader',
        2: 'Assistant Leader',
        1: 'Operator'
    }
    
    return level_descriptions.get(level, f'Level {level}')


def assign_pengajuan_to_section_supervisors(history_id, section_tujuan_id, approved_by_employee_number, min_level='assistant_supervisor'):
    """
    Assign pengajuan yang sudah di-approve ke supervisor berdasarkan level minimum di section tujuan
    ENHANCED: dengan minimum level filtering dan graceful fallback
    
    Args:
        history_id (str): ID pengajuan
        section_tujuan_id (int): ID section tujuan
        approved_by_employee_number (str): Employee number yang meng-approve
        min_level (str): Minimum level supervisor untuk assignment
        
    Returns:
        list: Daftar employee number yang di-assign pengajuan
    """
    try:
        logger.info(f"Starting assignment process for {history_id} to section {section_tujuan_id} (min level: {min_level})")
        
        # ===== CEK DAN BUAT TABLE JIKA PERLU =====
        table_created = ensure_assignment_tables_exist()
        if not table_created:
            logger.error("Failed to create assignment tables")
            return []
        
        # Dapatkan daftar supervisor berdasarkan minimum level di section tujuan
        target_supervisors = get_target_section_supervisors(
            section_tujuan_id, 
            exclude_employee_numbers=[approved_by_employee_number],
            min_level=min_level
        )
        
        if not target_supervisors:
            logger.warning(f"No supervisors (min level: {min_level}) found in section {section_tujuan_id} for assignment")
            return []
        
        logger.info(f"Found {len(target_supervisors)} potential targets (min level: {min_level}): {[s['employee_number'] for s in target_supervisors]}")
        
        assigned_employees = []
        
        # Insert assignment ke database
        with connections['DB_Maintenance'].cursor() as cursor:
            # Cek apakah sudah ada assignment untuk pengajuan ini
            cursor.execute("""
                SELECT COUNT(*) FROM [DB_Maintenance].[dbo].[tabel_pengajuan_assignment]
                WHERE history_id = %s AND is_active = 1
            """, [history_id])
            
            existing_assignments = cursor.fetchone()[0]
            if existing_assignments > 0:
                logger.warning(f"Pengajuan {history_id} already has {existing_assignments} active assignments")
                # Return existing assignments
                cursor.execute("""
                    SELECT assigned_to_employee FROM [DB_Maintenance].[dbo].[tabel_pengajuan_assignment]
                    WHERE history_id = %s AND is_active = 1
                """, [history_id])
                existing_employees = [row[0] for row in cursor.fetchall()]
                return existing_employees
            
            # Assign ke setiap supervisor berdasarkan level minimum di section tujuan
            for supervisor in target_supervisors:
                try:
                    cursor.execute("""
                        INSERT INTO [DB_Maintenance].[dbo].[tabel_pengajuan_assignment]
                        (history_id, assigned_to_employee, assigned_by_employee, assignment_date, is_active, notes)
                        VALUES (%s, %s, %s, GETDATE(), 1, %s)
                    """, [
                        history_id,
                        supervisor['employee_number'],
                        approved_by_employee_number,
                        f"Auto-assigned after approval to {supervisor['section_name']} {supervisor['title_name']} (Level: {supervisor['level_description']})"
                    ])
                    
                    assigned_employees.append(supervisor['employee_number'])
                    
                    logger.info(f"Successfully assigned pengajuan {history_id} to {supervisor['fullname']} ({supervisor['employee_number']}) - {supervisor['level_description']}")
                    
                except Exception as assign_error:
                    logger.error(f"Error assigning to {supervisor['employee_number']}: {assign_error}")
                    continue
        
        logger.info(f"Successfully assigned pengajuan {history_id} to {len(assigned_employees)} supervisors (min level: {min_level}) in section {section_tujuan_id}")
        return assigned_employees
        
    except Exception as e:
        logger.error(f"Error in assign_pengajuan_to_section_supervisors: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []


def ensure_assignment_tables_exist():
    """
    Memastikan assignment tables ada, jika tidak ada maka buat
    
    Returns:
        bool: True jika berhasil, False jika gagal
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # 1. Create assignment table
            cursor.execute("""
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
                        [assignment_type] [varchar](50) NULL DEFAULT 'MANUAL',
                        CONSTRAINT [PK_tabel_pengajuan_assignment] PRIMARY KEY CLUSTERED ([id] ASC)
                    ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
                END
            """)
            
            # 2. Create review log table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tabel_review_log' AND xtype='U')
                BEGIN
                    CREATE TABLE [dbo].[tabel_review_log](
                        [id] [int] IDENTITY(1,1) NOT NULL,
                        [history_id] [varchar](15) NULL,
                        [reviewer_employee] [varchar](50) NULL,
                        [action] [varchar](10) NULL,
                        [target_section] [varchar](50) NULL,
                        [review_notes] [varchar](max) NULL,
                        [priority_level] [varchar](20) NULL,
                        [review_date] [datetime] NULL,
                        CONSTRAINT [PK_tabel_review_log] PRIMARY KEY CLUSTERED ([id] ASC)
                    ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
                END
            """)
            
            # 3. Add missing review columns to main table
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
            
            # 4. Create indexes for performance
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_tabel_pengajuan_assignment_history_id')
                BEGIN
                    CREATE NONCLUSTERED INDEX [IX_tabel_pengajuan_assignment_history_id] 
                    ON [dbo].[tabel_pengajuan_assignment] ([history_id] ASC)
                END
            """)
            
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_tabel_pengajuan_assignment_assigned_to')
                BEGIN
                    CREATE NONCLUSTERED INDEX [IX_tabel_pengajuan_assignment_assigned_to] 
                    ON [dbo].[tabel_pengajuan_assignment] ([assigned_to_employee] ASC)
                    WHERE [is_active] = 1
                END
            """)
            
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_tabel_pengajuan_review_status')
                BEGIN
                    CREATE NONCLUSTERED INDEX [IX_tabel_pengajuan_review_status] 
                    ON [dbo].[tabel_pengajuan] ([review_status] ASC)
                    WHERE [status] = 'A' AND [approve] = 'Y'
                END
            """)
            
            logger.info("Assignment and review tables created/verified successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error creating assignment tables: {e}")
        return False
    
def log_enhanced_review_action(history_id, reviewer_employee, action, target_section, review_notes, priority_level):
    """
    Log enhanced review action ke database
    
    Args:
        history_id (str): ID pengajuan
        reviewer_employee (str): Employee number reviewer
        action (str): Action (process/reject)
        target_section (str): Target section
        review_notes (str): Review notes
        priority_level (str): Priority level
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                INSERT INTO tabel_review_log
                (history_id, reviewer_employee, action, target_section, review_notes, priority_level, review_date)
                VALUES (%s, %s, %s, %s, %s, %s, GETDATE())
            """, [
                history_id,
                reviewer_employee,
                action,
                target_section,
                review_notes,
                priority_level
            ])
            
            logger.info(f"Logged review action: {history_id} - {action} by {reviewer_employee}")
            
    except Exception as e:
        logger.error(f"Error logging review action: {e}")

def get_assigned_pengajuan_for_user(employee_number):
    """
    Mendapatkan daftar pengajuan yang di-assign ke user
    UPDATED: SITI FATIMAH mendapat akses ke pengajuan yang siap review (status B/N)
    
    Args:
        employee_number (str): Employee number user
        
    Returns:
        list: Daftar history_id pengajuan yang di-assign
    """
    if not employee_number:
        return []
    
    # UPDATED: SITI FATIMAH mendapat akses ke semua pengajuan yang sudah approved atasan
    if employee_number == REVIEWER_EMPLOYEE_NUMBER:
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # UPDATED: Query dengan status B dan approve N (siap review)
                cursor.execute("""
                    SELECT DISTINCT history_id
                    FROM [DB_Maintenance].[dbo].[tabel_pengajuan]
                    WHERE status = %s AND approve = %s
                    ORDER BY tgl_insert DESC
                """, [STATUS_APPROVED, APPROVE_YES])
                
                approved_pengajuan = [row[0] for row in cursor.fetchall() if row[0]]
                logger.info(f"SITI FATIMAH granted access to {len(approved_pengajuan)} approved pengajuan (status=B, approve=N)")
                return approved_pengajuan
                
        except Exception as e:
            logger.error(f"Error getting approved pengajuan for SITI FATIMAH: {e}")
            return []
    
    # For other users - same logic as before
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'tabel_pengajuan_assignment'
            """)
            
            table_exists = cursor.fetchone()[0] > 0
            
            if not table_exists:
                logger.debug(f"Assignment table does not exist - returning empty list for {employee_number}")
                return []
            
            cursor.execute("""
                SELECT DISTINCT history_id
                FROM [DB_Maintenance].[dbo].[tabel_pengajuan_assignment]
                WHERE assigned_to_employee = %s 
                    AND is_active = 1
            """, [employee_number])
            
            rows = cursor.fetchall()
            assigned_history_ids = [row[0] for row in rows if row[0]]
            
            logger.debug(f"Found {len(assigned_history_ids)} assigned pengajuan for {employee_number}")
            
            return assigned_history_ids
        
    except Exception as e:
        logger.error(f"Error getting assigned pengajuan for {employee_number}: {e}")
        return []


def get_sdbm_section_mapping():
    """
    Get mapping section target ke department/section di SDBM
    
    Returns:
        dict: Mapping target section ke department dan section SDBM
    """
    return {
        'it': {
            'department_name': 'ENGINEERING',
            'section_name': 'ENGINEERING-IT',
            'display_name': '💻 IT (ENGINEERING-IT)'
        },
        'elektrik': {
            'department_name': 'ENGINEERING', 
            'section_name': 'ENGINEERING-ELECTRIC',
            'display_name': '⚡ Elektrik (ENGINEERING-ELECTRIC)'
        },
        'mekanik': {
            'department_name': 'ENGINEERING',
            'section_name': 'ENGINEERING-MECHANIC', 
            'display_name': '🔧 Mekanik (ENGINEERING-MECHANIC)'
        },
        'utility': {
            'department_name': 'ENGINEERING',
            'section_name': 'ENGINEERING-UTILITY',
            'display_name': '🏭 Utility (ENGINEERING-UTILITY)'
        }
    }


def get_assigned_pengajuan_for_sdbm_user(employee_number):
    """
    Get pengajuan yang di-assign ke user berdasarkan SDBM employee number
    FIXED: Better error handling and simplified query
    
    Args:
        employee_number (str): Employee number user
        
    Returns:
        list: Daftar pengajuan yang di-assign
    """
    if not employee_number:
        return []
    
    # ENHANCED: SITI FATIMAH mendapat akses ke semua approved pengajuan
    if employee_number == REVIEWER_EMPLOYEE_NUMBER:
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # FIXED: Query dengan status A dan approve Y - SIMPLIFIED
                cursor.execute("""
                    SELECT DISTINCT 
                        tp.history_id,
                        tp.tgl_insert
                    FROM tabel_pengajuan tp
                    WHERE tp.status = %s AND tp.approve = %s
                    ORDER BY tp.tgl_insert DESC
                """, [STATUS_APPROVED, APPROVE_YES])
                
                rows = cursor.fetchall()
                
                assigned_pengajuan = []
                for row in rows:
                    assigned_pengajuan.append({
                        'history_id': row[0],
                        'assignment_type': 'SITI_REVIEWER',
                        'target_section': 'all',
                        'department_name': 'QC',
                        'section_name': 'Quality Control',
                        'assignment_date': row[1]
                    })
                
                logger.info(f"SITI FATIMAH granted access to {len(assigned_pengajuan)} approved pengajuan via special privilege")
                return assigned_pengajuan
                
        except Exception as e:
            logger.error(f"Error getting SDBM assignments for SITI FATIMAH: {e}")
            return []
    
    # For other users - simplified approach
    try:
        assigned_history_ids = []
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Check if assignment table exists
            try:
                cursor.execute("""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'tabel_pengajuan_assignment'
                """)
                
                table_exists = cursor.fetchone()[0] > 0
                
                if table_exists:
                    # Simplified query
                    cursor.execute("""
                        SELECT DISTINCT 
                            history_id,
                            assignment_date,
                            ISNULL(notes, '') as notes
                        FROM tabel_pengajuan_assignment
                        WHERE assigned_to_employee = %s 
                            AND is_active = 1
                        ORDER BY assignment_date DESC
                    """, [employee_number])
                    
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        assigned_history_ids.append({
                            'history_id': row[0],
                            'assignment_type': 'SDBM_ASSIGNMENT',
                            'target_section': None,
                            'department_name': None,
                            'section_name': None,
                            'assignment_date': row[1],
                            'notes': row[2]
                        })
                
                else:
                    logger.debug(f"Assignment table not found - no assignments for {employee_number}")
                
                logger.debug(f"Found {len(assigned_history_ids)} assignments for {employee_number}")
                return assigned_history_ids
            
            except Exception as table_error:
                logger.warning(f"Error checking assignment table for {employee_number}: {table_error}")
                return []
        
    except Exception as e:
        logger.error(f"Error getting SDBM assignments for {employee_number}: {e}")
        return []


# ===== Helper Functions untuk Status Conversion =====

def convert_legacy_status_to_actual(legacy_status):
    """
    Convert legacy status values (1,2,3,4) ke actual values (A,2,3,4)
    
    Args:
        legacy_status (str): Legacy status value
        
    Returns:
        str: Actual status value untuk database
    """
    conversion_map = {
        '1': STATUS_APPROVED,    # '1' -> 'A'
        '0': STATUS_PENDING,     # '0' -> '0'
        '2': STATUS_REJECTED,    # '2' -> '2'
        '3': STATUS_IN_PROGRESS, # '3' -> '3'
        '4': STATUS_COMPLETED    # '4' -> '4'
    }
    
    return conversion_map.get(legacy_status, legacy_status)


def convert_legacy_approve_to_actual(legacy_approve):
    """
    Convert legacy approve values (1,2,0) ke actual values (Y,2,0)
    
    Args:
        legacy_approve (str): Legacy approve value
        
    Returns:
        str: Actual approve value untuk database
    """
    conversion_map = {
        '1': APPROVE_YES,        # '1' -> 'Y'
        '0': APPROVE_NO,         # '0' -> '0'
        '2': APPROVE_REJECTED    # '2' -> '2'
    }
    
    return conversion_map.get(legacy_approve, legacy_approve)

# wo_maintenance_app/utils.py - FIXED initialize_review_data function

def initialize_review_data():
    """
    Auto-initialize pengajuan approved untuk review dengan status yang benar
    UPDATED: menggunakan status B dan approve N (approved oleh atasan, siap review)
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Ensure review columns exist first
            try:
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
                
                logger.info("Review columns verified/created successfully")
                
            except Exception as col_error:
                logger.warning(f"Error ensuring review columns: {col_error}")
            
            # Check table structure
            cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = 'review_status'")
            
            if cursor.fetchone()[0] == 0:
                logger.warning("Review columns not found. Please run: python manage.py setup_review_system")
                return False
            
            # UPDATED: Initialize approved pengajuan untuk review dengan status B dan approve N
            cursor.execute("""
                UPDATE tabel_pengajuan 
                SET review_status = '0'
                WHERE status = %s AND approve = %s 
                    AND (review_status IS NULL OR review_status = '')
            """, [STATUS_APPROVED, APPROVE_YES])
            
            updated_count = cursor.rowcount
            
            if updated_count > 0:
                logger.info(f"Auto-initialized {updated_count} approved pengajuan for review (status=B, approve=N)")
            
            # Log current status for debugging
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_approved,
                    SUM(CASE WHEN review_status IS NULL OR review_status = '0' THEN 1 ELSE 0 END) as pending_review,
                    SUM(CASE WHEN review_status = '1' THEN 1 ELSE 0 END) as reviewed_processed,
                    SUM(CASE WHEN review_status = '2' THEN 1 ELSE 0 END) as reviewed_rejected
                FROM tabel_pengajuan 
                WHERE status = %s AND approve = %s
            """, [STATUS_APPROVED, APPROVE_YES])
            
            stats = cursor.fetchone()
            logger.info(f"Review system stats - Total approved: {stats[0]}, Pending review: {stats[1]}, Processed: {stats[2]}, Rejected: {stats[3]}")
            
            return True
            
    except Exception as e:
        logger.error(f"Error initializing review data: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def ensure_review_system_for_siti():
    """
    Special function to ensure review system is ready for SITI FATIMAH
    Called when SITI FATIMAH accesses the system
    """
    try:
        logger.info("Ensuring review system is ready for SITI FATIMAH...")
        
        # Initialize review data
        initialized = initialize_review_data()
        
        if not initialized:
            logger.error("Failed to initialize review system for SITI FATIMAH")
            return False
        
        # Check current workload
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_pengajuan 
                WHERE status = %s AND approve = %s 
                    AND (review_status IS NULL OR review_status = '0')
            """, [STATUS_APPROVED, APPROVE_YES])
            
            pending_count = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_pengajuan 
                WHERE reviewed_by = %s 
                    AND CAST(review_date AS DATE) = CAST(GETDATE() AS DATE)
            """, [REVIEWER_EMPLOYEE_NUMBER])
            
            reviewed_today = cursor.fetchone()[0] or 0
            
            logger.info(f"SITI FATIMAH workload - Pending review: {pending_count}, Reviewed today: {reviewed_today}")
            
            return {
                'ready': True,
                'pending_review': pending_count,
                'reviewed_today': reviewed_today,
                'can_review': pending_count > 0
            }
        
    except Exception as e:
        logger.error(f"Error ensuring review system for SITI FATIMAH: {e}")
        return {
            'ready': False,
            'error': str(e),
            'pending_review': 0,
            'reviewed_today': 0,
            'can_review': False
        }


def get_review_ready_pengajuan_for_siti():
    """
    Get list of pengajuan that are ready for review by SITI FATIMAH
    """
    try:
        pengajuan_list = []
        
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT 
                    tp.history_id,
                    tp.oleh,
                    tp.tgl_insert,
                    tm.mesin,
                    tms.seksi,
                    tp.deskripsi_perbaikan,
                    tp.status,
                    tp.approve,
                    tp.review_status
                FROM tabel_pengajuan tp
                LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
                LEFT JOIN tabel_msection tms ON tp.id_section = tms.id_section
                WHERE tp.status = %s 
                    AND tp.approve = %s 
                    AND (tp.review_status IS NULL OR tp.review_status = '0')
                ORDER BY tp.tgl_insert ASC
            """, [STATUS_APPROVED, APPROVE_YES])
            
            for row in cursor.fetchall():
                pengajuan_list.append({
                    'history_id': row[0],
                    'oleh': row[1],
                    'tgl_insert': row[2],
                    'mesin': row[3],
                    'seksi': row[4],
                    'deskripsi_perbaikan': row[5],
                    'status': row[6],
                    'approve': row[7],
                    'review_status': row[8]
                })
        
        logger.info(f"Found {len(pengajuan_list)} pengajuan ready for SITI FATIMAH review")
        return pengajuan_list
        
    except Exception as e:
        logger.error(f"Error getting review-ready pengajuan: {e}")
        return []


def debug_review_system_status():
    """
    Debug function to check review system status
    """
    try:
        debug_info = {
            'timestamp': timezone.now().isoformat(),
            'constants': {
                'STATUS_APPROVED': STATUS_APPROVED,
                'APPROVE_YES': APPROVE_YES,
                'REVIEWER_EMPLOYEE_NUMBER': REVIEWER_EMPLOYEE_NUMBER
            },
            'database_check': {},
            'pengajuan_status': {}
        }
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Check review columns
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'tabel_pengajuan' 
                    AND COLUMN_NAME IN ('review_status', 'reviewed_by', 'review_date', 'review_notes', 'final_section_id')
            """)
            
            existing_columns = [row[0] for row in cursor.fetchall()]
            debug_info['database_check']['review_columns'] = existing_columns
            debug_info['database_check']['all_columns_exist'] = len(existing_columns) == 5
            
            # Check pengajuan counts
            cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan")
            debug_info['pengajuan_status']['total'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE status = %s", [STATUS_APPROVED])
            debug_info['pengajuan_status']['status_approved'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE approve = %s", [APPROVE_YES])
            debug_info['pengajuan_status']['approve_yes'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE status = %s AND approve = %s", [STATUS_APPROVED, APPROVE_YES])
            debug_info['pengajuan_status']['fully_approved'] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_pengajuan 
                WHERE status = %s AND approve = %s 
                    AND (review_status IS NULL OR review_status = '0')
            """, [STATUS_APPROVED, APPROVE_YES])
            debug_info['pengajuan_status']['pending_review'] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_pengajuan 
                WHERE reviewed_by = %s
            """, [REVIEWER_EMPLOYEE_NUMBER])
            debug_info['pengajuan_status']['reviewed_by_siti'] = cursor.fetchone()[0]
            
            # Sample data
            cursor.execute("""
                SELECT TOP 5 history_id, status, approve, review_status
                FROM tabel_pengajuan 
                WHERE status = %s AND approve = %s
                ORDER BY tgl_insert DESC
            """, [STATUS_APPROVED, APPROVE_YES])
            
            debug_info['sample_data'] = [
                {
                    'history_id': row[0],
                    'status': row[1],
                    'approve': row[2],
                    'review_status': row[3]
                } for row in cursor.fetchall()
            ]
        
        return debug_info
        
    except Exception as e:
        return {
            'error': str(e),
            'traceback': traceback.format_exc()
        }

# Export all functions and constants
__all__ = [
    'get_employee_hierarchy_data',
    'can_user_approve', 
    'get_subordinate_employee_numbers',
    'get_employee_by_number',
    'get_supervisors_by_section_and_level',
    'get_target_section_supervisors',
    'get_title_level',
    'get_level_description',
    'assign_pengajuan_to_section_supervisors',
    'ensure_assignment_tables_exist',
    'get_assigned_pengajuan_for_user',
    'is_pengajuan_final_processed',  # NEW
    'initialize_review_data',
    'is_pengajuan_approved_for_review',
    'get_sdbm_section_mapping',
    'get_assigned_pengajuan_for_sdbm_user',
    'convert_legacy_status_to_actual',
    'convert_legacy_approve_to_actual',
    'STATUS_PENDING',
    'STATUS_APPROVED',
    'STATUS_REVIEWED', 
    'STATUS_REJECTED',
    'STATUS_IN_PROGRESS', 
    'STATUS_COMPLETED',
    'APPROVE_NO',
    'APPROVE_YES',
    'APPROVE_REVIEWED', 
    'APPROVE_REJECTED',
    'REVIEWER_EMPLOYEE_NUMBER',
    'REVIEWER_FULLNAME'
]

def get_target_section_to_maintenance_mapping():
    """
    Enhanced mapping dari target section pilihan SITI FATIMAH ke id_section database
    
    Returns:
        dict: Mapping target section ke maintenance section info
    """
    return {
        'it': {
            'maintenance_section_id': 1,  # ID di tabel_msection untuk IT
            'display_name': '💻 IT (Information Technology)',
            'department_name': 'ENGINEERING',
            'section_name': 'ENGINEERING-IT',
            'keywords': ['IT', 'INFORMATION', 'TECHNOLOGY', 'SISTEM', 'KOMPUTER']
        },
        'elektrik': {
            'maintenance_section_id': 2,  # ID di tabel_msection untuk Elektrik
            'display_name': '⚡ Elektrik (Electrical Engineering)',
            'department_name': 'ENGINEERING', 
            'section_name': 'ENGINEERING-ELECTRIC',
            'keywords': ['ELEKTRIK', 'ELECTRIC', 'ELECTRICAL', 'LISTRIK', 'POWER']
        },
        'mekanik': {
            'maintenance_section_id': 3,  # ID di tabel_msection untuk Mekanik
            'display_name': '🔧 Mekanik (Mechanical Engineering)',
            'department_name': 'ENGINEERING',
            'section_name': 'ENGINEERING-MECHANIC',
            'keywords': ['MEKANIK', 'MECHANIC', 'MECHANICAL', 'MESIN', 'TEKNIK']
        },
        'utility': {
            'maintenance_section_id': 4,  # ID di tabel_msection untuk Utility
            'display_name': '🏭 Utility (Utility Systems)',
            'department_name': 'ENGINEERING',
            'section_name': 'ENGINEERING-UTILITY', 
            'keywords': ['UTILITY', 'UTILITIES', 'FASILITAS', 'INFRASTRUKTUR']
        },
        'civil': {
            'maintenance_section_id': 5,  # ID di tabel_msection untuk Civil
            'display_name': '🏗️ Civil (Civil Engineering)',
            'department_name': 'ENGINEERING',
            'section_name': 'ENGINEERING-CIVIL',
            'keywords': ['CIVIL', 'SIPIL', 'KONSTRUKSI', 'BANGUNAN']
        }
    }

def auto_discover_maintenance_sections():
    """
    Auto-discover section IDs dari database untuk mapping yang akurat
    
    Returns:
        dict: Mapping target section ke actual section IDs dari database
    """
    try:
        section_mapping = get_target_section_to_maintenance_mapping()
        discovered_mapping = {}
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Get all sections dari database
            cursor.execute("""
                SELECT id_section, seksi 
                FROM tabel_msection 
                WHERE (status = 'A' OR status IS NULL) 
                    AND seksi IS NOT NULL 
                    AND seksi != ''
                ORDER BY id_section
            """)
            
            db_sections = cursor.fetchall()
            
            # Match dengan keywords
            for target_section, mapping_info in section_mapping.items():
                keywords = mapping_info['keywords']
                
                for db_row in db_sections:
                    section_id = int(float(db_row[0]))
                    section_name = str(db_row[1]).upper()
                    
                    # Check if any keyword matches
                    if any(keyword in section_name for keyword in keywords):
                        discovered_mapping[target_section] = {
                            'id_section': section_id,
                            'section_name': db_row[1],
                            'display_name': mapping_info['display_name'],
                            'matched_keyword': next(k for k in keywords if k in section_name)
                        }
                        logger.info(f"Auto-discovered: {target_section} -> ID {section_id} ({db_row[1]})")
                        break
                
                # Fallback ke default mapping jika tidak ditemukan
                if target_section not in discovered_mapping:
                    discovered_mapping[target_section] = {
                        'id_section': mapping_info['maintenance_section_id'],
                        'section_name': f"Section {mapping_info['maintenance_section_id']}",
                        'display_name': mapping_info['display_name'],
                        'matched_keyword': 'fallback'
                    }
                    logger.warning(f"Fallback mapping: {target_section} -> ID {mapping_info['maintenance_section_id']}")
        
        return discovered_mapping
        
    except Exception as e:
        logger.error(f"Error auto-discovering sections: {e}")
        # Return default mapping
        default_mapping = get_target_section_to_maintenance_mapping()
        return {
            target: {
                'id_section': info['maintenance_section_id'],
                'section_name': f"Section {info['maintenance_section_id']}",
                'display_name': info['display_name'],
                'matched_keyword': 'default'
            }
            for target, info in default_mapping.items()
        }

def assign_pengajuan_after_siti_review_enhanced(history_id, target_section, reviewer_employee_number, review_notes):
    """
    ENHANCED: Assign pengajuan setelah review oleh SITI FATIMAH dengan update section tujuan
    
    Args:
        history_id (str): ID pengajuan
        target_section (str): Target section yang dipilih SITI FATIMAH (it, elektrik, utility, mekanik)
        reviewer_employee_number (str): Employee number reviewer (SITI FATIMAH)
        review_notes (str): Catatan review
        
    Returns:
        dict: Result of assignment process with section update info
    """
    try:
        logger.info(f"SITI REVIEW ENHANCED: Starting assignment for {history_id} to {target_section}")
        
        # Get auto-discovered section mapping
        section_mapping = auto_discover_maintenance_sections()
        section_info = section_mapping.get(target_section)
        
        if not section_info:
            return {
                'success': False,
                'error': f'Unknown target section: {target_section}',
                'assigned_employees': [],
                'section_updated': False,
                'original_section': None,
                'new_section': None
            }
        
        result = {
            'success': True,
            'assigned_employees': [],
            'section_updated': False,
            'section_changed': False,
            'original_section': None,
            'new_section': None,
            'final_section_updated': False,
            'error': None
        }
        
        # STEP 1: Get original section info
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT tp.id_section, ms.seksi as current_section_name
                    FROM tabel_pengajuan tp
                    LEFT JOIN tabel_msection ms ON tp.id_section = ms.id_section
                    WHERE tp.history_id = %s
                """, [history_id])
                
                original_row = cursor.fetchone()
                if original_row:
                    original_section_id = int(float(original_row[0])) if original_row[0] else None
                    original_section_name = original_row[1] or 'Unknown'
                    
                    result['original_section'] = {
                        'id': original_section_id,
                        'name': original_section_name
                    }
                    
                    logger.info(f"SITI REVIEW: Original section - ID: {original_section_id}, Name: {original_section_name}")
        
        except Exception as get_error:
            logger.error(f"SITI REVIEW: Error getting original section: {get_error}")
            result['error'] = f'Failed to get original section: {str(get_error)}'
        
        # STEP 2: Update id_section (section tujuan) DAN final_section_id
        try:
            new_section_id = section_info['id_section']
            
            with connections['DB_Maintenance'].cursor() as cursor:
                # ENHANCED: Update BOTH id_section AND final_section_id
                cursor.execute("""
                    UPDATE tabel_pengajuan
                    SET id_section = %s,
                        final_section_id = %s
                    WHERE history_id = %s
                """, [float(new_section_id), float(new_section_id), history_id])
                
                if cursor.rowcount > 0:
                    result['section_updated'] = True
                    result['final_section_updated'] = True
                    result['section_changed'] = (
                        result['original_section'] and 
                        result['original_section']['id'] != new_section_id
                    )
                    
                    result['new_section'] = {
                        'id': new_section_id,
                        'name': section_info['section_name'],
                        'display_name': section_info['display_name']
                    }
                    
                    logger.info(f"SITI REVIEW: Updated section tujuan from ID {result['original_section']['id'] if result['original_section'] else 'Unknown'} to ID {new_section_id}")
                    
                    # Verify update
                    cursor.execute("""
                        SELECT tp.id_section, ms.seksi, tp.final_section_id
                        FROM tabel_pengajuan tp
                        LEFT JOIN tabel_msection ms ON tp.id_section = ms.id_section
                        WHERE tp.history_id = %s
                    """, [history_id])
                    
                    verify_row = cursor.fetchone()
                    if verify_row:
                        logger.info(f"SITI REVIEW: Verification - New section ID: {verify_row[0]}, Name: {verify_row[1]}, Final ID: {verify_row[2]}")
                
        except Exception as update_error:
            logger.error(f"SITI REVIEW: Error updating sections: {update_error}")
            result['error'] = f'Failed to update sections: {str(update_error)}'
        
        # STEP 3: SDBM Assignment ke supervisors
        try:
            supervisors = get_sdbm_supervisors_by_section_mapping(target_section)
            
            if supervisors:
                # Create assignment table if not exists
                ensure_assignment_tables_exist()
                
                # Assign ke supervisors
                with connections['DB_Maintenance'].cursor() as cursor:
                    for supervisor in supervisors:
                        try:
                            cursor.execute("""
                                INSERT INTO tabel_pengajuan_assignment
                                (history_id, assigned_to_employee, assigned_by_employee, assignment_date, is_active, notes, assignment_type)
                                VALUES (%s, %s, %s, GETDATE(), 1, %s, 'SITI_REVIEW_ENHANCED')
                            """, [
                                history_id,
                                supervisor['employee_number'],
                                reviewer_employee_number,
                                f"SITI FATIMAH Enhanced Review: Section changed to {section_info['display_name']}. Assigned to {supervisor['title_name']}. Notes: {review_notes}"
                            ])
                            
                            result['assigned_employees'].append({
                                'employee_number': supervisor['employee_number'],
                                'fullname': supervisor['fullname'],
                                'title_name': supervisor['title_name'],
                                'level_description': supervisor.get('level_description', 'Supervisor')
                            })
                            
                            logger.info(f"SITI REVIEW: Assigned {history_id} to {supervisor['fullname']} ({supervisor['employee_number']})")
                            
                        except Exception as assign_error:
                            logger.error(f"SITI REVIEW: Error assigning to {supervisor['employee_number']}: {assign_error}")
                            continue
                
                logger.info(f"SITI REVIEW: Successfully assigned {history_id} to {len(result['assigned_employees'])} supervisors in {target_section}")
                
            else:
                logger.warning(f"SITI REVIEW: No supervisors found for {target_section}")
                result['error'] = f'No supervisors found for {target_section} but section was updated'
                
        except Exception as sdbm_error:
            logger.error(f"SITI REVIEW: SDBM assignment error: {sdbm_error}")
            result['error'] = f'Section updated successfully but SDBM assignment failed: {str(sdbm_error)}'
        
        # STEP 4: Enhanced logging
        try:
            log_enhanced_section_change(
                history_id,
                reviewer_employee_number,
                target_section,
                result['original_section'],
                result['new_section'],
                review_notes
            )
        except Exception as log_error:
            logger.warning(f"SITI REVIEW: Logging error: {log_error}")
        
        return result
        
    except Exception as e:
        logger.error(f"SITI REVIEW: Critical error in enhanced assignment: {e}")
        return {
            'success': False,
            'error': str(e),
            'assigned_employees': [],
            'section_updated': False,
            'section_changed': False,
            'original_section': None,
            'new_section': None
        }
    
def log_enhanced_section_change(history_id, reviewer_employee, target_section, original_section, new_section, review_notes):
    """
    Log perubahan section untuk audit trail
    
    Args:
        history_id (str): ID pengajuan
        reviewer_employee (str): Employee number reviewer
        target_section (str): Target section yang dipilih
        original_section (dict): Section info sebelum perubahan
        new_section (dict): Section info setelah perubahan
        review_notes (str): Review notes
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Enhanced review log with section change info
            cursor.execute("""
                INSERT INTO tabel_review_log
                (history_id, reviewer_employee, action, target_section, review_notes, review_date, 
                 original_section_id, new_section_id, section_changed)
                VALUES (%s, %s, %s, %s, %s, GETDATE(), %s, %s, %s)
            """, [
                history_id,
                reviewer_employee,
                'process_with_section_change',
                target_section,
                f"Section changed from '{original_section['name'] if original_section else 'Unknown'}' to '{new_section['display_name'] if new_section else 'Unknown'}'. {review_notes}",
                original_section['id'] if original_section else None,
                new_section['id'] if new_section else None,
                1 if (original_section and new_section and original_section['id'] != new_section['id']) else 0
            ])
            
            logger.info(f"Enhanced section change logged for {history_id}")
            
    except Exception as e:
        logger.error(f"Error logging enhanced section change: {e}")


def ensure_enhanced_review_tables_exist():
    """
    Enhanced version: Pastikan review tables memiliki kolom untuk section change tracking
    
    Returns:
        bool: True jika berhasil, False jika gagal
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Base tables from original function
            ensure_assignment_tables_exist()
            
            # Enhanced review log table with section change tracking
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tabel_review_log' AND xtype='U')
                BEGIN
                    CREATE TABLE [dbo].[tabel_review_log](
                        [id] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
                        [history_id] [varchar](15) NULL,
                        [reviewer_employee] [varchar](50) NULL,
                        [action] [varchar](50) NULL,
                        [target_section] [varchar](50) NULL,
                        [review_notes] [varchar](max) NULL,
                        [priority_level] [varchar](20) NULL,
                        [review_date] [datetime] NULL,
                        [original_section_id] [float] NULL,
                        [new_section_id] [float] NULL,
                        [section_changed] [bit] NULL DEFAULT 0
                    ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
                END
            """)
            
            # Add missing columns to existing table
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                  WHERE TABLE_NAME = 'tabel_review_log' AND COLUMN_NAME = 'original_section_id')
                    BEGIN
                        ALTER TABLE tabel_review_log ADD original_section_id float NULL
                    END
                """)
                
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                  WHERE TABLE_NAME = 'tabel_review_log' AND COLUMN_NAME = 'new_section_id')
                    BEGIN
                        ALTER TABLE tabel_review_log ADD new_section_id float NULL
                    END
                """)
                
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                  WHERE TABLE_NAME = 'tabel_review_log' AND COLUMN_NAME = 'section_changed')
                    BEGIN
                        ALTER TABLE tabel_review_log ADD section_changed bit NULL DEFAULT 0
                    END
                """)
                
            except Exception as col_error:
                logger.warning(f"Column addition warning: {col_error}")
            
            # Create indexes for enhanced performance
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_tabel_review_log_section_changed')
                BEGIN
                    CREATE NONCLUSTERED INDEX [IX_tabel_review_log_section_changed] 
                    ON [dbo].[tabel_review_log] ([section_changed] ASC, [review_date] DESC)
                    WHERE [section_changed] = 1
                END
            """)
            
            logger.info("Enhanced review tables created/verified successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error creating enhanced review tables: {e}")
        return False


def get_section_change_history(history_id):
    """
    Get history perubahan section untuk pengajuan tertentu
    
    Args:
        history_id (str): ID pengajuan
        
    Returns:
        list: List of section changes
    """
    try:
        changes = []
        
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT 
                    rl.review_date,
                    rl.reviewer_employee,
                    rl.target_section,
                    rl.original_section_id,
                    rl.new_section_id,
                    rl.section_changed,
                    rl.review_notes,
                    orig_sec.seksi as original_section_name,
                    new_sec.seksi as new_section_name
                FROM tabel_review_log rl
                LEFT JOIN tabel_msection orig_sec ON rl.original_section_id = orig_sec.id_section
                LEFT JOIN tabel_msection new_sec ON rl.new_section_id = new_sec.id_section
                WHERE rl.history_id = %s 
                    AND rl.section_changed = 1
                ORDER BY rl.review_date DESC
            """, [history_id])
            
            for row in cursor.fetchall():
                changes.append({
                    'review_date': row[0],
                    'reviewer_employee': row[1],
                    'target_section': row[2],
                    'original_section': {
                        'id': row[3],
                        'name': row[7]
                    },
                    'new_section': {
                        'id': row[4],
                        'name': row[8]
                    },
                    'review_notes': row[6]
                })
        
        return changes
        
    except Exception as e:
        logger.error(f"Error getting section change history: {e}")
        return []


# Export enhanced functions
__all__ = [
    'get_target_section_to_maintenance_mapping',
    'auto_discover_maintenance_sections',
    'assign_pengajuan_after_siti_review_enhanced',
    'log_enhanced_section_change',
    'ensure_enhanced_review_tables_exist',
    'get_section_change_history'
]
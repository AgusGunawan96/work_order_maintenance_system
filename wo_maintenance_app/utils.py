# wo_maintenance_app/utils.py
from django.db import connections
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

def get_employee_hierarchy_data(user):
    """
    Mendapatkan data hierarchy employee dari database SDBM berdasarkan user yang login
    
    Returns:
        dict: Data hierarchy employee atau None jika tidak ditemukan
    """
    if not user or not user.is_authenticated:
        return None
    
    try:
        with connections['SDBM'].cursor() as cursor:
            # Query untuk mendapatkan data employee lengkap dengan hierarchy
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
                    AND (d.is_active IS NULL OR d.is_active = 1)
                    AND (s.is_active IS NULL OR s.is_active = 1)
                    AND (sub.is_active IS NULL OR sub.is_active = 1)
                    AND (t.is_active IS NULL OR t.is_active = 1)
                    
                ORDER BY p.id DESC
            """, [user.username])
            
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
                logger.warning(f"Employee data not found for user: {user.username}")
                return None
                
    except Exception as e:
        logger.error(f"Error getting employee hierarchy data for user {user.username}: {e}")
        return None


def can_user_approve(user_hierarchy, target_user_hierarchy):
    """
    Mengecek apakah user dapat melakukan approve terhadap target user berdasarkan hierarchy
    
    Args:
        user_hierarchy (dict): Data hierarchy user yang akan melakukan approve
        target_user_hierarchy (dict): Data hierarchy target user (pembuat pengajuan)
    
    Returns:
        bool: True jika dapat approve, False jika tidak
    """
    if not user_hierarchy or not target_user_hierarchy:
        return False
    
    # Supervisor/Manager/GM/BOD dapat approve
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
    
    # Target user title untuk validasi hierarchy
    target_title = str(target_user_hierarchy.get('title_name', '')).upper()
    target_is_supervisor = target_user_hierarchy.get('is_supervisor', False)
    target_is_manager = target_user_hierarchy.get('is_manager', False)
    
    # Level hierarchy (semakin tinggi angka, semakin tinggi level) - UPDATED
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
        'SPV': 9,  # Alias untuk SUPERVISOR
        'SENIOR SUPERVISOR': 10,
        'ASSISTANT MANAGER': 11,
        'MANAGER': 12,
        'MGR': 12,  # Alias untuk MANAGER
        'GENERAL MANAGER': 13,
        'GM': 13,  # Alias untuk GENERAL MANAGER
        'DIRECTOR': 14,
        'PRESIDENT DIRECTOR': 15,
        'BOD': 15  # Alias untuk PRESIDENT DIRECTOR
    }
    
    # Tentukan level user yang akan approve
    user_level = 0
    for title, level in approval_levels.items():
        if title in user_title:
            user_level = max(user_level, level)
    
    # Jika user adalah manager/supervisor berdasarkan flag database
    if is_manager:
        user_level = max(user_level, 7)
    elif is_supervisor:
        user_level = max(user_level, 6)
    elif is_general_manager:
        user_level = max(user_level, 8)
    elif is_bod:
        user_level = max(user_level, 9)
    
    # Tentukan level target user
    target_level = 0
    for title, level in approval_levels.items():
        if title in target_title:
            target_level = max(target_level, level)
    
    if target_is_manager:
        target_level = max(target_level, 7)
    elif target_is_supervisor:
        target_level = max(target_level, 6)
    
    # User dapat approve jika levelnya lebih tinggi dari target
    level_check = user_level > target_level
    
    # Cek hierarchy department/section juga
    same_department = user_hierarchy.get('department_id') == target_user_hierarchy.get('department_id')
    same_section = user_hierarchy.get('section_id') == target_user_hierarchy.get('section_id')
    
    # Manager dapat approve semua dalam department yang sama
    # Supervisor dapat approve dalam section yang sama
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
    
    Args:
        user_hierarchy (dict): Data hierarchy user
        
    Returns:
        list: Daftar employee_number yang dapat di-manage oleh user
    """
    if not user_hierarchy:
        return []
    
    try:
        employee_numbers = []
        
        with connections['SDBM'].cursor() as cursor:
            # Tentukan filter berdasarkan level user
            user_title = str(user_hierarchy.get('title_name', '')).upper()
            is_manager = user_hierarchy.get('is_manager', False)
            is_supervisor = user_hierarchy.get('is_supervisor', False) 
            is_general_manager = user_hierarchy.get('is_general_manager', False)
            is_bod = user_hierarchy.get('is_bod', False)
            
            if is_bod or 'BOD' in user_title:
                # BOD dapat melihat semua pengajuan
                cursor.execute("""
                    SELECT DISTINCT e.employee_number
                    FROM [hrbp].[employees] e
                    INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                    WHERE e.is_active = 1 AND p.is_active = 1
                """)
                
            elif is_general_manager or 'GENERAL' in user_title or 'GM' in user_title:
                # GM dapat melihat semua dalam company
                cursor.execute("""
                    SELECT DISTINCT e.employee_number
                    FROM [hrbp].[employees] e
                    INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                    WHERE e.is_active = 1 AND p.is_active = 1
                """)
                
            elif is_manager or 'MANAGER' in user_title or 'MGR' in user_title:
                # Manager dapat melihat semua dalam department yang sama
                cursor.execute("""
                    SELECT DISTINCT e.employee_number
                    FROM [hrbp].[employees] e
                    INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                    LEFT JOIN [hr].[title] t ON p.titleId = t.id
                    WHERE e.is_active = 1 
                        AND p.is_active = 1
                        AND p.departmentId = %s
                        AND (
                            (t.is_manager IS NULL OR t.is_manager = 0) OR
                            (t.Name IS NULL OR 
                             (UPPER(t.Name) NOT LIKE '%%MANAGER%%' AND UPPER(t.Name) NOT LIKE '%%MGR%%'))
                        )
                """, [user_hierarchy.get('department_id')])
                
            elif is_supervisor or 'SUPERVISOR' in user_title or 'SPV' in user_title:
                # Supervisor dapat melihat dalam section yang sama (exclude manager level)
                cursor.execute("""
                    SELECT DISTINCT e.employee_number
                    FROM [hrbp].[employees] e
                    INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                    LEFT JOIN [hr].[title] t ON p.titleId = t.id
                    WHERE e.is_active = 1 
                        AND p.is_active = 1
                        AND p.sectionId = %s
                        AND (
                            (t.is_manager IS NULL OR t.is_manager = 0) AND
                            (t.is_supervisor IS NULL OR t.is_supervisor = 0) OR
                            (t.Name IS NULL OR 
                             (UPPER(t.Name) NOT LIKE '%%MANAGER%%' AND 
                              UPPER(t.Name) NOT LIKE '%%MGR%%' AND
                              UPPER(t.Name) NOT LIKE '%%SUPERVISOR%%' AND
                              UPPER(t.Name) NOT LIKE '%%SPV%%'))
                        )
                """, [user_hierarchy.get('section_id')])
                
            else:
                # User biasa hanya melihat pengajuan sendiri
                return [user_hierarchy.get('employee_number')]
            
            rows = cursor.fetchall()
            employee_numbers = [row[0] for row in rows if row[0]]
            
            # Selalu tambahkan employee number user sendiri
            if user_hierarchy.get('employee_number') not in employee_numbers:
                employee_numbers.append(user_hierarchy.get('employee_number'))
            
            logger.debug(f"Found {len(employee_numbers)} subordinates for {user_hierarchy.get('fullname')}")
            
            return employee_numbers
            
    except Exception as e:
        logger.error(f"Error getting subordinate employees for {user_hierarchy.get('fullname')}: {e}")
        # Fallback: return only own employee number
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


def get_target_section_supervisors(section_tujuan_id, exclude_employee_numbers=None):
    """
    Mendapatkan daftar assistant supervisor+ di section tujuan untuk assignment pengajuan
    
    Args:
        section_tujuan_id (int): ID section tujuan (IT, Elektrik, Mekanik, Utility)
        exclude_employee_numbers (list): List employee number yang dikecualikan
        
    Returns:
        list: Daftar employee dengan level assistant supervisor ke atas di section tujuan
    """
    if not section_tujuan_id:
        return []
        
    if exclude_employee_numbers is None:
        exclude_employee_numbers = []
    
    try:
        supervisors = []
        
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
                
                # Hanya ambil yang level assistant supervisor ke atas (>= 8)
                if level >= 8:
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
                        'level': level
                    })
                    
            logger.debug(f"Found {len(supervisors)} assistant supervisors+ in section {section_tujuan_id}")
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


def assign_pengajuan_to_section_supervisors(history_id, section_tujuan_id, approved_by_employee_number):
    """
    Assign pengajuan yang sudah di-approve ke assistant supervisor+ di section tujuan
    GRACEFUL FALLBACK: Auto-create table jika belum ada
    
    Args:
        history_id (str): ID pengajuan
        section_tujuan_id (int): ID section tujuan
        approved_by_employee_number (str): Employee number yang meng-approve
        
    Returns:
        list: Daftar employee number yang di-assign pengajuan
    """
    try:
        logger.info(f"Starting assignment process for {history_id} to section {section_tujuan_id}")
        
        # ===== CEK DAN BUAT TABLE JIKA PERLU =====
        table_created = ensure_assignment_tables_exist()
        if not table_created:
            logger.error("Failed to create assignment tables")
            return []
        
        # Dapatkan daftar assistant supervisor+ di section tujuan
        target_supervisors = get_target_section_supervisors(
            section_tujuan_id, 
            exclude_employee_numbers=[approved_by_employee_number]
        )
        
        if not target_supervisors:
            logger.warning(f"No assistant supervisors+ found in section {section_tujuan_id} for assignment")
            return []
        
        logger.info(f"Found {len(target_supervisors)} potential targets: {[s['employee_number'] for s in target_supervisors]}")
        
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
            
            # Assign ke setiap assistant supervisor+ di section tujuan
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
                        f"Auto-assigned after approval to {supervisor['section_name']} {supervisor['title_name']}"
                    ])
                    
                    assigned_employees.append(supervisor['employee_number'])
                    
                    logger.info(f"Successfully assigned pengajuan {history_id} to {supervisor['fullname']} ({supervisor['employee_number']})")
                    
                except Exception as assign_error:
                    logger.error(f"Error assigning to {supervisor['employee_number']}: {assign_error}")
                    continue
        
        logger.info(f"Successfully assigned pengajuan {history_id} to {len(assigned_employees)} assistant supervisors+ in section {section_tujuan_id}")
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
                        CONSTRAINT [PK_tabel_pengajuan_assignment] PRIMARY KEY CLUSTERED ([id] ASC)
                    ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
                END
            """)
            
            # 2. Create approval log table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tabel_approval_log' AND xtype='U')
                BEGIN
                    CREATE TABLE [dbo].[tabel_approval_log](
                        [id] [int] IDENTITY(1,1) NOT NULL,
                        [history_id] [varchar](15) NULL,
                        [approver_user] [varchar](50) NULL,
                        [action] [varchar](10) NULL,
                        [keterangan] [varchar](max) NULL,
                        [tgl_approval] [datetime] NULL,
                        CONSTRAINT [PK_tabel_approval_log] PRIMARY KEY CLUSTERED ([id] ASC)
                    ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
                END
            """)
            
            # 3. Create indexes
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
            
            logger.info("Assignment tables created successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error creating assignment tables: {e}")
        return False


def get_assigned_pengajuan_for_user(employee_number):
    """
    Mendapatkan daftar pengajuan yang di-assign ke user
    GRACEFUL FALLBACK: Return empty list jika table tidak ada
    
    Args:
        employee_number (str): Employee number user
        
    Returns:
        list: Daftar history_id pengajuan yang di-assign
    """
    if not employee_number:
        return []
    
    try:
        # Cek apakah table assignment ada
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'tabel_pengajuan_assignment'
            """)
            
            table_exists = cursor.fetchone()[0] > 0
            
            if not table_exists:
                logger.debug(f"Assignment table does not exist - returning empty list for {employee_number}")
                return []
            
            # Table ada, ambil assignments
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
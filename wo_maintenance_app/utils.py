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

# wo_maintenance_app/utils.py - ADD enhanced review functions

def ensure_enhanced_review_tables():
    """
    Memastikan review tables sudah enhanced dengan kolom target_section
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Add target_section column to review log if not exists
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                              WHERE TABLE_NAME = 'tabel_review_log' AND COLUMN_NAME = 'target_section')
                BEGIN
                    ALTER TABLE tabel_review_log ADD target_section varchar(20) NULL
                END
            """)
            
            logger.info("Enhanced review tables verified/created successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error ensuring enhanced review tables: {e}")
        return False


def get_section_id_from_target(target_section):
    """
    Get section ID dari target section (it, elektrik, utility, mekanik)
    """
    if not target_section:
        return None
    
    try:
        section_mapping = {}
        
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT id_section, seksi 
                FROM tabel_msection 
                WHERE (status = 'A' OR status IS NULL) 
                    AND seksi IS NOT NULL
                    AND seksi != ''
                ORDER BY seksi
            """)
            
            for row in cursor.fetchall():
                section_id = int(float(row[0]))
                section_name = str(row[1]).strip().upper()
                
                # Map section berdasarkan kata kunci
                if target_section == 'it' and any(keyword in section_name for keyword in ['IT', 'INFORMATION', 'SYSTEM', 'TEKNOLOGI']):
                    return section_id
                elif target_section == 'elektrik' and any(keyword in section_name for keyword in ['ELEKTRIK', 'ELECTRIC', 'LISTRIK']):
                    return section_id
                elif target_section == 'utility' and any(keyword in section_name for keyword in ['UTILITY', 'UTILITIES', 'UMUM']):
                    return section_id
                elif target_section == 'mekanik' and any(keyword in section_name for keyword in ['MEKANIK', 'MECHANIC', 'MECHANICAL']):
                    return section_id
        
        # Fallback mapping
        fallback_mapping = {
            'it': 1,
            'elektrik': 2,
            'mekanik': 3,
            'utility': 4
        }
        
        return fallback_mapping.get(target_section)
        
    except Exception as e:
        logger.error(f"Error getting section ID for {target_section}: {e}")
        return None


def log_enhanced_review_action(history_id, reviewer_employee, action, target_section=None, review_notes=None, priority_level='normal'):
    """
    Log enhanced review action dengan target section
    """
    try:
        # Ensure enhanced tables exist
        ensure_enhanced_review_tables()
        
        # Get final section ID
        final_section_id = get_section_id_from_target(target_section) if target_section else None
        
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                INSERT INTO tabel_review_log 
                (history_id, reviewer_employee, action, final_section_id, review_notes, review_date, priority_level, target_section)
                VALUES (%s, %s, %s, %s, %s, GETDATE(), %s, %s)
            """, [
                history_id, 
                reviewer_employee, 
                action, 
                float(final_section_id) if final_section_id else None, 
                review_notes, 
                priority_level,
                target_section
            ])
            
            logger.info(f"Enhanced review action logged: {history_id} - {action} by {reviewer_employee} -> {target_section}")
            return True
            
    except Exception as e:
        logger.error(f"Error logging enhanced review action: {e}")
        return False


def get_enhanced_review_statistics():
    """
    Get enhanced review statistics termasuk distribusi section
    """
    try:
        stats = {}
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Basic stats
            cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE status = '1' AND approve = '1'")
            stats['total_approved'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE status = '1' AND approve = '1' AND (review_status IS NULL OR review_status = '0')")
            stats['pending_review'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE reviewed_by = %s", [REVIEWER_EMPLOYEE_NUMBER])
            stats['total_reviewed'] = cursor.fetchone()[0] or 0
            
            # Enhanced stats - by target section
            cursor.execute("""
                SELECT target_section, COUNT(*) 
                FROM tabel_review_log 
                WHERE reviewer_employee = %s AND action = 'process'
                GROUP BY target_section
                ORDER BY COUNT(*) DESC
            """, [REVIEWER_EMPLOYEE_NUMBER])
            
            section_distribution = []
            for row in cursor.fetchall():
                target_section = row[0]
                count = row[1]
                
                section_info = {
                    'section': target_section or 'standard',
                    'count': count,
                    'display_name': {
                        'it': '💻 IT',
                        'elektrik': '⚡ Elektrik', 
                        'utility': '🏭 Utility',
                        'mekanik': '🔧 Mekanik'
                    }.get(target_section, '📋 Standard Process')
                }
                section_distribution.append(section_info)
            
            stats['section_distribution'] = section_distribution
            
            # Action breakdown
            cursor.execute("""
                SELECT action, COUNT(*) 
                FROM tabel_review_log 
                WHERE reviewer_employee = %s
                GROUP BY action
            """, [REVIEWER_EMPLOYEE_NUMBER])
            
            action_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
            stats['processed_count'] = action_breakdown.get('process', 0)
            stats['rejected_count'] = action_breakdown.get('reject', 0)
            
            # Recent activity
            cursor.execute("""
                SELECT TOP 5 history_id, action, target_section, review_date
                FROM tabel_review_log 
                WHERE reviewer_employee = %s
                ORDER BY review_date DESC
            """, [REVIEWER_EMPLOYEE_NUMBER])
            
            recent_activity = []
            for row in cursor.fetchall():
                activity = {
                    'history_id': row[0],
                    'action': row[1],
                    'target_section': row[2],
                    'review_date': row[3],
                    'display_text': f"{row[1].title()} -> {row[2] or 'Standard'}"
                }
                recent_activity.append(activity)
            
            stats['recent_activity'] = recent_activity
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting enhanced review statistics: {e}")
        return {
            'total_approved': 0,
            'pending_review': 0,
            'total_reviewed': 0,
            'processed_count': 0,
            'rejected_count': 0,
            'section_distribution': [],
            'recent_activity': []
        }


def get_target_section_display_name(target_section):
    """
    Get display name untuk target section
    """
    display_mapping = {
        'it': '💻 IT',
        'elektrik': '⚡ Elektrik',
        'utility': '🏭 Utility',
        'mekanik': '🔧 Mekanik'
    }
    
    return display_mapping.get(target_section, f'📋 {target_section.title()}' if target_section else '📋 Standard Process')


def validate_target_section(target_section):
    """
    Validate target section choice
    """
    valid_sections = ['it', 'elektrik', 'utility', 'mekanik']
    return target_section in valid_sections or target_section == ''


# Enhanced constants
REVIEW_ACTION_DISPLAY = {
    'process': 'Processed',
    'reject': 'Rejected'
}

TARGET_SECTION_CHOICES = [
    ('it', '💻 IT'),
    ('elektrik', '⚡ Elektrik'),
    ('utility', '🏭 Utility'),
    ('mekanik', '🔧 Mekanik'),
]

TARGET_SECTION_DESCRIPTIONS = {
    'it': 'Information Technology & Systems',
    'elektrik': 'Electrical & Power Systems',
    'utility': 'Utilities & General Maintenance',
    'mekanik': 'Mechanical & Engineering'
}

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

def get_maintenance_section_id_from_target(target_section):
    """
    Get section ID dari tabel_msection berdasarkan target section yang dipilih
    
    Args:
        target_section (str): Target section (it, elektrik, mekanik, utility)
        
    Returns:
        int: Section ID dari tabel_msection atau None
    """
    if not target_section:
        return None
    
    try:
        section_mapping = {}
        
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT id_section, seksi 
                FROM tabel_msection 
                WHERE (status = 'A' OR status IS NULL) 
                    AND seksi IS NOT NULL
                    AND seksi != ''
                ORDER BY seksi
            """)
            
            for row in cursor.fetchall():
                section_id = int(float(row[0]))
                section_name = str(row[1]).strip().upper()
                
                # Map section berdasarkan kata kunci
                if target_section == 'it' and any(keyword in section_name for keyword in ['IT', 'INFORMATION', 'SYSTEM', 'TEKNOLOGI']):
                    return section_id
                elif target_section == 'elektrik' and any(keyword in section_name for keyword in ['ELEKTRIK', 'ELECTRIC', 'LISTRIK']):
                    return section_id
                elif target_section == 'utility' and any(keyword in section_name for keyword in ['UTILITY', 'UTILITIES', 'UMUM']):
                    return section_id
                elif target_section == 'mekanik' and any(keyword in section_name for keyword in ['MEKANIK', 'MECHANIC', 'MECHANICAL']):
                    return section_id
        
        # Fallback mapping jika tidak ditemukan di database
        fallback_mapping = {
            'it': 1,
            'elektrik': 2,
            'mekanik': 3,
            'utility': 4
        }
        
        return fallback_mapping.get(target_section)
        
    except Exception as e:
        logger.error(f"Error getting maintenance section ID for {target_section}: {e}")
        return None

def get_sdbm_supervisors_by_section_mapping(target_section, exclude_employee_numbers=None):
    """
    Get assistant supervisor+ dari SDBM berdasarkan mapping department/section
    
    Args:
        target_section (str): Target section (it, elektrik, mekanik, utility)
        exclude_employee_numbers (list): Employee numbers yang dikecualikan
        
    Returns:
        list: Daftar supervisors dari SDBM
    """
    if not target_section:
        return []
        
    if exclude_employee_numbers is None:
        exclude_employee_numbers = []
    
    try:
        # Get mapping untuk target section
        section_mapping = get_sdbm_section_mapping()
        target_mapping = section_mapping.get(target_section)
        
        if not target_mapping:
            logger.warning(f"No SDBM mapping found for target section: {target_section}")
            return []
        
        department_name = target_mapping['department_name']
        section_name = target_mapping['section_name']
        
        supervisors = []
        
        with connections['SDBM'].cursor() as cursor:
            # Build exclude clause
            exclude_clause = ""
            query_params = [department_name, section_name]
            
            if exclude_employee_numbers:
                exclude_placeholders = ','.join(['%s'] * len(exclude_employee_numbers))
                exclude_clause = f"AND e.employee_number NOT IN ({exclude_placeholders})"
                query_params.extend(exclude_employee_numbers)
            
            # Query untuk mendapatkan assistant supervisor+ di department dan section yang sesuai
            query = f"""
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
                    END DESC,
                    e.fullname
            """
            
            cursor.execute(query, query_params)
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
                        'job_status': row[10],
                        'level': level,
                        'level_description': get_level_description(level),
                        'target_section': target_section
                    })
                    
            logger.info(f"Found {len(supervisors)} SDBM supervisors+ for {target_section} in {department_name}/{section_name}")
            return supervisors
            
    except Exception as e:
        logger.error(f"Error getting SDBM supervisors for target section {target_section}: {e}")
        return []
    
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

def assign_pengajuan_after_siti_review(history_id, target_section, reviewer_employee, review_notes=None):
    """
    Auto-assign pengajuan ke SDBM supervisors setelah review oleh SITI FATIMAH
    FIXED: Dengan handling untuk missing columns dan enhanced supervisor search
    
    Args:
        history_id (str): ID pengajuan
        target_section (str): Target section (it, elektrik, mekanik, utility)  
        reviewer_employee (str): Employee number reviewer (SITI FATIMAH)
        review_notes (str): Catatan review
        
    Returns:
        dict: Result dengan info assignment dan section update
    """
    try:
        logger.info(f"FIXED: Starting SITI review assignment for {history_id} to {target_section}")
        
        result = {
            'assigned_employees': [],
            'section_updated': False,
            'new_section_id': None,
            'target_section': target_section,
            'supervisors_found': 0,
            'error': None
        }
        
        # ===== STEP 1: Update Section Tujuan di tabel_pengajuan =====
        new_section_id = get_maintenance_section_id_from_target(target_section)
        
        if new_section_id:
            try:
                with connections['DB_Maintenance'].cursor() as cursor:
                    cursor.execute("""
                        UPDATE tabel_pengajuan 
                        SET id_section = %s,
                            final_section_id = %s
                        WHERE history_id = %s
                    """, [float(new_section_id), float(new_section_id), history_id])
                    
                    result['section_updated'] = True
                    result['new_section_id'] = new_section_id
                    
                    logger.info(f"FIXED: Updated section for {history_id} to section ID {new_section_id}")
                    
            except Exception as section_error:
                logger.error(f"FIXED: Error updating section for {history_id}: {section_error}")
                result['error'] = f"Section update failed: {section_error}"
        
        # ===== STEP 2: Get SDBM Supervisors dengan Enhanced Search =====
        sdbm_supervisors = get_sdbm_supervisors_by_section_mapping_enhanced(
            target_section, 
            exclude_employee_numbers=[reviewer_employee]
        )
        
        result['supervisors_found'] = len(sdbm_supervisors)
        
        if not sdbm_supervisors:
            logger.warning(f"FIXED: No SDBM supervisors found for {target_section}")
            result['error'] = f"No supervisors found for section {target_section}"
            return result
        
        # ===== STEP 3: Ensure Assignment Tables dengan Error Handling =====
        table_ready = ensure_assignment_tables_exist_safe()
        if not table_ready:
            logger.error(f"FIXED: Assignment table not ready")
            result['error'] = "Assignment table not ready"
            return result
        
        # ===== STEP 4: Create Assignments dengan Enhanced Data =====
        assigned_employees = []
        section_mapping = get_sdbm_section_mapping()
        target_info = section_mapping.get(target_section, {})
        
        with connections['DB_Maintenance'].cursor() as cursor:
            for supervisor in sdbm_supervisors:
                try:
                    # Check if already assigned
                    cursor.execute("""
                        SELECT COUNT(*) FROM tabel_pengajuan_assignment
                        WHERE history_id = %s AND assigned_to_employee = %s AND is_active = 1
                    """, [history_id, supervisor['employee_number']])
                    
                    if cursor.fetchone()[0] > 0:
                        logger.debug(f"FIXED: Pengajuan {history_id} already assigned to {supervisor['employee_number']}")
                        continue
                    
                    # Create assignment note
                    assignment_note = (
                        f"Enhanced SITI FATIMAH review assignment to {supervisor['level_description']} "
                        f"in {target_info.get('display_name', target_section)}. "
                        f"Target: {supervisor['department_name']}/{supervisor['section_name']}"
                    )
                    
                    if review_notes:
                        assignment_note += f". Review notes: {review_notes[:100]}..."
                    
                    # Check if enhanced columns exist
                    cursor.execute("""
                        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'tabel_pengajuan_assignment' AND COLUMN_NAME = 'target_section'
                    """)
                    
                    has_enhanced_columns = cursor.fetchone()[0] > 0
                    
                    if has_enhanced_columns:
                        # Insert with enhanced columns
                        cursor.execute("""
                            INSERT INTO tabel_pengajuan_assignment 
                            (history_id, assigned_to_employee, assigned_by_employee, assignment_date, 
                             notes, assignment_type, is_active, target_section, department_name, section_name,
                             created_by_system)
                            VALUES (%s, %s, %s, GETDATE(), %s, %s, 1, %s, %s, %s, %s)
                        """, [
                            history_id,
                            supervisor['employee_number'],
                            reviewer_employee,
                            assignment_note,
                            'SITI_REVIEW_ENHANCED',
                            target_section,
                            supervisor['department_name'],
                            supervisor['section_name'],
                            'ENHANCED_SDBM_v2'
                        ])
                    else:
                        # Insert with basic columns only
                        cursor.execute("""
                            INSERT INTO tabel_pengajuan_assignment 
                            (history_id, assigned_to_employee, assigned_by_employee, assignment_date, 
                             notes, is_active)
                            VALUES (%s, %s, %s, GETDATE(), %s, 1)
                        """, [
                            history_id,
                            supervisor['employee_number'],
                            reviewer_employee,
                            assignment_note
                        ])
                    
                    assigned_employees.append({
                        'employee_number': supervisor['employee_number'],
                        'fullname': supervisor['fullname'],
                        'title_name': supervisor['title_name'],
                        'department_name': supervisor['department_name'],
                        'section_name': supervisor['section_name'],
                        'level_description': supervisor['level_description']
                    })
                    
                    logger.info(f"FIXED: Assigned {history_id} to {supervisor['fullname']} ({supervisor['employee_number']}) - {supervisor['title_name']}")
                    
                except Exception as assign_error:
                    logger.error(f"FIXED: Error in assignment to {supervisor['employee_number']}: {assign_error}")
                    continue
        
        result['assigned_employees'] = assigned_employees
        
        logger.info(f"FIXED: Review completed: {history_id} -> {target_section}, {len(assigned_employees)} assignments, section updated: {result['section_updated']}")
        
        return result
        
    except Exception as e:
        logger.error(f"FIXED: Error in assign_pengajuan_after_siti_review: {e}")
        import traceback
        logger.error(f"FIXED: Traceback: {traceback.format_exc()}")
        
        return {
            'assigned_employees': [],
            'section_updated': False,
            'new_section_id': None,
            'target_section': target_section,
            'supervisors_found': 0,
            'error': str(e)
        }

def get_sdbm_supervisors_by_section_mapping_enhanced(target_section, exclude_employee_numbers=None):
    """
    Enhanced version dengan debugging dan fallback searching
    
    Args:
        target_section (str): Target section (it, elektrik, mekanik, utility)
        exclude_employee_numbers (list): Employee numbers yang dikecualikan
        
    Returns:
        list: Daftar supervisors dari SDBM
    """
    if not target_section:
        return []
        
    if exclude_employee_numbers is None:
        exclude_employee_numbers = []
    
    try:
        # Get mapping untuk target section
        section_mapping = get_sdbm_section_mapping()
        target_mapping = section_mapping.get(target_section)
        
        if not target_mapping:
            logger.error(f"ENHANCED: No SDBM mapping found for target section: {target_section}")
            return []
        
        department_name = target_mapping['department_name']
        section_name = target_mapping['section_name']
        
        logger.info(f"ENHANCED: Searching supervisors for {target_section} -> {department_name}/{section_name}")
        
        supervisors = []
        
        with connections['SDBM'].cursor() as cursor:
            # Build exclude clause
            exclude_clause = ""
            query_params = [department_name, section_name]
            
            if exclude_employee_numbers:
                exclude_placeholders = ','.join(['%s'] * len(exclude_employee_numbers))
                exclude_clause = f"AND e.employee_number NOT IN ({exclude_placeholders})"
                query_params.extend(exclude_employee_numbers)
            
            # Enhanced query dengan multiple fallbacks
            queries_to_try = [
                # Query 1: Exact match
                f"""
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
                        {exclude_clause}
                """,
                # Query 2: Section name contains keyword
                f"""
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
                        AND UPPER(d.name) = UPPER(%s)
                        AND UPPER(s.name) LIKE '%{target_section.upper()}%'
                        AND (
                            t.is_supervisor = 1 OR 
                            t.is_manager = 1 OR
                            UPPER(t.Name) LIKE '%SUPERVISOR%' OR
                            UPPER(t.Name) LIKE '%MANAGER%'
                        )
                        {exclude_clause}
                """
            ]
            
            for i, query in enumerate(queries_to_try, 1):
                try:
                    logger.debug(f"ENHANCED: Trying query {i} for {target_section}")
                    cursor.execute(query, query_params)
                    rows = cursor.fetchall()
                    
                    if rows:
                        logger.info(f"ENHANCED: Query {i} found {len(rows)} supervisors for {target_section}")
                        break
                    else:
                        logger.debug(f"ENHANCED: Query {i} found no results for {target_section}")
                        
                except Exception as query_error:
                    logger.warning(f"ENHANCED: Query {i} failed for {target_section}: {query_error}")
                    continue
            
            if not rows:
                logger.warning(f"ENHANCED: No supervisors found with any query for {target_section}")
                return []
            
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
                        'job_status': row[10],
                        'level': level,
                        'level_description': get_level_description(level),
                        'target_section': target_section
                    })
                    
            logger.info(f"ENHANCED: Found {len(supervisors)} qualified supervisors for {target_section} in {department_name}/{section_name}")
            return supervisors
            
    except Exception as e:
        logger.error(f"ENHANCED: Error getting supervisors for target section {target_section}: {e}")
        return []

def ensure_assignment_tables_exist_safe():
    """
    Safely ensure assignment tables exist dengan error handling
    
    Returns:
        bool: True jika berhasil atau sudah ada, False jika gagal
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Check if table exists
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'tabel_pengajuan_assignment'
            """)
            
            table_exists = cursor.fetchone()[0] > 0
            
            if not table_exists:
                # Create basic table
                cursor.execute("""
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
                """)
                
                logger.info("SAFE: Created basic assignment table")
            
            return True
            
    except Exception as e:
        logger.error(f"SAFE: Error ensuring assignment table: {e}")
        return False
def debug_sdbm_section_search(target_section):
    """
    Debug function untuk troubleshoot SDBM section search
    
    Args:
        target_section (str): Target section to debug
        
    Returns:
        dict: Debug information
    """
    debug_info = {
        'target_section': target_section,
        'mapping_info': {},
        'database_check': {},
        'supervisor_search': {},
        'errors': []
    }
    
    try:
        # 1. Check mapping
        section_mapping = get_sdbm_section_mapping()
        target_mapping = section_mapping.get(target_section, {})
        debug_info['mapping_info'] = target_mapping
        
        if not target_mapping:
            debug_info['errors'].append(f"No mapping found for {target_section}")
            return debug_info
        
        department_name = target_mapping['department_name']
        section_name = target_mapping['section_name']
        
        # 2. Check database
        with connections['SDBM'].cursor() as cursor:
            # Check department
            cursor.execute("""
                SELECT COUNT(*) FROM [hr].[department] 
                WHERE UPPER(name) = UPPER(%s)
            """, [department_name])
            dept_count = cursor.fetchone()[0]
            
            # Check section
            cursor.execute("""
                SELECT COUNT(*) FROM [hr].[section] 
                WHERE UPPER(name) = UPPER(%s)
            """, [section_name])
            sect_count = cursor.fetchone()[0]
            
            # Check employees in dept/section
            cursor.execute("""
                SELECT COUNT(*) 
                FROM [hrbp].[employees] e
                INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                INNER JOIN [hr].[department] d ON p.departmentId = d.id
                INNER JOIN [hr].[section] s ON p.sectionId = s.id
                WHERE UPPER(d.name) = UPPER(%s)
                    AND UPPER(s.name) = UPPER(%s)
                    AND e.is_active = 1
            """, [department_name, section_name])
            emp_count = cursor.fetchone()[0]
            
            # Check supervisors
            cursor.execute("""
                SELECT COUNT(*) 
                FROM [hrbp].[employees] e
                INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                INNER JOIN [hr].[department] d ON p.departmentId = d.id
                INNER JOIN [hr].[section] s ON p.sectionId = s.id
                INNER JOIN [hr].[title] t ON p.titleId = t.id
                WHERE UPPER(d.name) = UPPER(%s)
                    AND UPPER(s.name) = UPPER(%s)
                    AND e.is_active = 1
                    AND (t.is_supervisor = 1 OR t.is_manager = 1 OR 
                         UPPER(t.Name) LIKE '%SUPERVISOR%' OR UPPER(t.Name) LIKE '%MANAGER%')
            """, [department_name, section_name])
            supervisor_count = cursor.fetchone()[0]
            
            debug_info['database_check'] = {
                'department_exists': dept_count > 0,
                'section_exists': sect_count > 0,
                'total_employees': emp_count,
                'supervisor_count': supervisor_count
            }
            
            # Get sample data
            if supervisor_count > 0:
                cursor.execute("""
                    SELECT TOP 3
                        e.employee_number,
                        e.fullname,
                        t.Name as title_name,
                        s.name as section_name
                    FROM [hrbp].[employees] e
                    INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                    INNER JOIN [hr].[department] d ON p.departmentId = d.id
                    INNER JOIN [hr].[section] s ON p.sectionId = s.id
                    INNER JOIN [hr].[title] t ON p.titleId = t.id
                    WHERE UPPER(d.name) = UPPER(%s)
                        AND UPPER(s.name) = UPPER(%s)
                        AND e.is_active = 1
                        AND (t.is_supervisor = 1 OR t.is_manager = 1 OR 
                             UPPER(t.Name) LIKE '%SUPERVISOR%' OR UPPER(t.Name) LIKE '%MANAGER%')
                    ORDER BY t.is_manager DESC, t.is_supervisor DESC
                """, [department_name, section_name])
                
                sample_supervisors = cursor.fetchall()
                debug_info['supervisor_search']['sample_supervisors'] = [
                    {
                        'employee_number': row[0],
                        'fullname': row[1],
                        'title_name': row[2],
                        'section_name': row[3]
                    } for row in sample_supervisors
                ]
        
        return debug_info
        
    except Exception as e:
        debug_info['errors'].append(f"Debug error: {e}")
        return debug_info
    
def ensure_enhanced_assignment_tables():
    """
    Memastikan assignment tables ada dengan kolom enhanced untuk SDBM mapping
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Ensure assignment table exists dengan kolom baru
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
                        [assignment_type] [varchar](20) NULL,
                        [target_section] [varchar](20) NULL,
                        [department_name] [varchar](100) NULL,
                        [section_name] [varchar](100) NULL,
                        CONSTRAINT [PK_tabel_pengajuan_assignment] PRIMARY KEY CLUSTERED ([id] ASC)
                    ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
                END
            """)
            
            # Add new columns if they don't exist
            new_columns = [
                ('assignment_type', 'varchar(20)', 'NULL'),
                ('target_section', 'varchar(20)', 'NULL'),
                ('department_name', 'varchar(100)', 'NULL'),
                ('section_name', 'varchar(100)', 'NULL')
            ]
            
            for column_name, column_type, default_value in new_columns:
                cursor.execute(f"""
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                  WHERE TABLE_NAME = 'tabel_pengajuan_assignment' AND COLUMN_NAME = '{column_name}')
                    BEGIN
                        ALTER TABLE tabel_pengajuan_assignment ADD {column_name} {column_type} DEFAULT {default_value}
                    END
                """)
            
            logger.info("Enhanced assignment tables with SDBM mapping verified/created successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error ensuring enhanced assignment tables: {e}")
        return False


def get_assigned_pengajuan_for_sdbm_user(employee_number):
    """
    Get pengajuan yang di-assign ke user berdasarkan SDBM employee number
    FIXED: Dengan fallback untuk tabel yang belum enhanced
    
    Args:
        employee_number (str): Employee number user
        
    Returns:
        list: Daftar history_id pengajuan yang di-assign
    """
    if not employee_number:
        return []
    
    try:
        assigned_history_ids = []
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Cek apakah table assignment ada
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'tabel_pengajuan_assignment'
            """)
            
            table_exists = cursor.fetchone()[0] > 0
            
            if table_exists:
                # Check if enhanced columns exist
                cursor.execute("""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'tabel_pengajuan_assignment' AND COLUMN_NAME = 'target_section'
                """)
                
                has_enhanced_columns = cursor.fetchone()[0] > 0
                
                if has_enhanced_columns:
                    # Use enhanced query
                    cursor.execute("""
                        SELECT DISTINCT 
                            history_id,
                            assignment_type,
                            target_section,
                            department_name,
                            section_name,
                            assignment_date
                        FROM tabel_pengajuan_assignment
                        WHERE assigned_to_employee = %s 
                            AND is_active = 1
                        ORDER BY assignment_date DESC
                    """, [employee_number])
                    
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        assigned_history_ids.append({
                            'history_id': row[0],
                            'assignment_type': row[1],
                            'target_section': row[2], 
                            'department_name': row[3],
                            'section_name': row[4],
                            'assignment_date': row[5]
                        })
                
                else:
                    # Fallback to basic query
                    cursor.execute("""
                        SELECT DISTINCT history_id, assignment_date, notes
                        FROM tabel_pengajuan_assignment
                        WHERE assigned_to_employee = %s 
                            AND is_active = 1
                        ORDER BY assignment_date DESC
                    """, [employee_number])
                    
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        assigned_history_ids.append({
                            'history_id': row[0],
                            'assignment_type': 'LEGACY',
                            'target_section': None,
                            'department_name': None,
                            'section_name': None,
                            'assignment_date': row[1],
                            'notes': row[2]
                        })
                
                logger.debug(f"Found {len(assigned_history_ids)} assignments for {employee_number} (enhanced: {has_enhanced_columns})")
            
            else:
                logger.debug(f"Assignment table not found - no assignments for {employee_number}")
            
            # ENHANCED: Also check if user should have access based on section mapping
            additional_assignments = get_section_based_assignments(employee_number)
            
            # Merge without duplicates
            existing_history_ids = {item['history_id'] for item in assigned_history_ids if isinstance(item, dict)}
            
            for additional in additional_assignments:
                if additional['history_id'] not in existing_history_ids:
                    assigned_history_ids.append(additional)
            
            return assigned_history_ids
        
    except Exception as e:
        logger.error(f"Error getting SDBM assignments for {employee_number}: {e}")
        return []

def get_section_based_assignments(employee_number):
    """
    Get pengajuan berdasarkan section mapping tanpa tabel assignment
    Untuk kasus dimana pengajuan sudah di-redirect ke section tapi belum di-assign
    
    Args:
        employee_number (str): Employee number user
        
    Returns:
        list: Daftar pengajuan yang seharusnya accessible
    """
    try:
        # Get employee SDBM data
        employee_data = get_employee_by_number(employee_number)
        if not employee_data:
            return []
        
        section_name = employee_data.get('section_name', '')
        department_name = employee_data.get('department_name', '')
        
        # Check if this is supervisor level
        is_supervisor = employee_data.get('is_supervisor', False)
        is_manager = employee_data.get('is_manager', False)
        title_name = str(employee_data.get('title_name', '')).upper()
        
        has_supervisor_role = (
            is_supervisor or is_manager or
            'SUPERVISOR' in title_name or 'MANAGER' in title_name or
            'SPV' in title_name or 'MGR' in title_name or
            'ASSISTANT SUPERVISOR' in title_name
        )
        
        if not has_supervisor_role:
            return []
        
        # Map SDBM section to target section
        target_section = None
        if section_name:
            section_upper = section_name.upper()
            if 'IT' in section_upper or 'INFORMATION' in section_upper:
                target_section = 'it'
            elif 'ELECTRIC' in section_upper or 'ELEKTRIK' in section_upper:
                target_section = 'elektrik'
            elif 'MECHANIC' in section_upper or 'MEKANIK' in section_upper:
                target_section = 'mekanik'
            elif 'UTILITY' in section_upper or 'UTILITIES' in section_upper:
                target_section = 'utility'
        
        if not target_section:
            return []
        
        # Get maintenance section ID untuk target section
        maintenance_section_id = get_maintenance_section_id_from_target(target_section)
        if not maintenance_section_id:
            return []
        
        section_assignments = []
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Find pengajuan yang section-nya sudah di-update ke target section ini
            # tapi belum ada assignment explicit
            cursor.execute("""
                SELECT DISTINCT tp.history_id, tp.tgl_insert, tp.review_date
                FROM tabel_pengajuan tp
                WHERE (tp.id_section = %s OR tp.final_section_id = %s)
                    AND tp.status = '1' 
                    AND tp.approve = '1'
                    AND tp.review_status = '1'
                    AND NOT EXISTS (
                        SELECT 1 FROM tabel_pengajuan_assignment pa 
                        WHERE pa.history_id = tp.history_id 
                            AND pa.assigned_to_employee = %s 
                            AND pa.is_active = 1
                    )
                ORDER BY tp.review_date DESC, tp.tgl_insert DESC
            """, [float(maintenance_section_id), float(maintenance_section_id), employee_number])
            
            rows = cursor.fetchall()
            
            for row in rows:
                section_assignments.append({
                    'history_id': row[0],
                    'assignment_type': 'SECTION_MAPPING',
                    'target_section': target_section,
                    'department_name': department_name,
                    'section_name': section_name,
                    'assignment_date': row[2] or row[1],  # Use review_date or tgl_insert
                    'notes': f'Auto-accessible via section mapping to {section_name}'
                })
        
        logger.info(f"Found {len(section_assignments)} section-based assignments for {employee_number} in {section_name}")
        return section_assignments
        
    except Exception as e:
        logger.error(f"Error getting section-based assignments for {employee_number}: {e}")
        return []

def validate_sdbm_section_mapping():
    """
    Validate mapping section target dengan data actual di SDBM
    
    Returns:
        dict: Validation result
    """
    try:
        validation_result = {
            'valid': True,
            'missing_departments': [],
            'missing_sections': [],
            'found_supervisors': {}
        }
        
        section_mapping = get_sdbm_section_mapping()
        
        with connections['SDBM'].cursor() as cursor:
            for target, mapping in section_mapping.items():
                department_name = mapping['department_name']
                section_name = mapping['section_name']
                
                # Check department exists
                cursor.execute("""
                    SELECT COUNT(*) FROM [hr].[department] 
                    WHERE UPPER(name) = UPPER(%s) AND (is_active IS NULL OR is_active = 1)
                """, [department_name])
                
                dept_exists = cursor.fetchone()[0] > 0
                if not dept_exists:
                    validation_result['missing_departments'].append(department_name)
                    validation_result['valid'] = False
                
                # Check section exists
                cursor.execute("""
                    SELECT COUNT(*) FROM [hr].[section] 
                    WHERE UPPER(name) = UPPER(%s) AND (is_active IS NULL OR is_active = 1)
                """, [section_name])
                
                section_exists = cursor.fetchone()[0] > 0
                if not section_exists:
                    validation_result['missing_sections'].append(section_name)
                    validation_result['valid'] = False
                
                # Count supervisors
                if dept_exists and section_exists:
                    supervisors = get_sdbm_supervisors_by_section_mapping(target)
                    validation_result['found_supervisors'][target] = {
                        'count': len(supervisors),
                        'department': department_name,
                        'section': section_name
                    }
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Error validating SDBM section mapping: {e}")
        return {
            'valid': False,
            'error': str(e),
            'missing_departments': [],
            'missing_sections': [],
            'found_supervisors': {}
        }
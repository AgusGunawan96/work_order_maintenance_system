# wo_maintenance_app/views.py - Debug Version
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db import connections, transaction
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import json, traceback
import logging
from functools import wraps
from django.http import JsonResponse


from wo_maintenance_app.forms import PengajuanMaintenanceForm, PengajuanFilterForm, ApprovalForm, ReviewForm, ReviewFilterForm
from wo_maintenance_app.utils import (
    get_employee_hierarchy_data, 
    can_user_approve, 
    get_subordinate_employee_numbers,
    get_employee_by_number,
    assign_pengajuan_to_section_supervisors,
    get_assigned_pengajuan_for_user,
    get_target_section_supervisors,
    STATUS_PENDING,
    STATUS_APPROVED,    # B
    STATUS_REVIEWED,    # A  
    STATUS_REJECTED,
    APPROVE_NO,
    APPROVE_YES,        # N
    APPROVE_REVIEWED,   # Y
    APPROVE_REJECTED,
    REVIEWER_EMPLOYEE_NUMBER,
    REVIEWER_FULLNAME,
    REVIEW_PENDING,
    REVIEW_APPROVED,
    REVIEW_REJECTED,
     is_pengajuan_approved_for_review,
     is_pengajuan_final_processed,  # NEW
    initialize_review_data,
    get_enhanced_pengajuan_access_for_user,
    get_access_statistics,
    get_maintenance_section_ids_by_keywords,
    get_engineering_section_access,
    is_engineering_supervisor_or_above,
    build_enhanced_pengajuan_query_conditions
)

# Setup logging
logger = logging.getLogger(__name__)

# ===== REVIEW SYSTEM CONSTANTS =====
REVIEWER_EMPLOYEE_NUMBER = '007522'  # SITI FATIMAH
REVIEWER_FULLNAME = 'SITI FATIMAH'

# ===== FIXED STATUS CONSTANTS - Konsisten dengan Database =====
# IMPORTANT: Pastikan nilai ini sesuai dengan data actual di database
# STATUS_APPROVED = 'A'      # Status approved - pastikan di DB menggunakan 'A'
# STATUS_PENDING = '0'       # Status pending 
# STATUS_REJECTED = '2'      # Status rejected

# APPROVE_YES = 'Y'          # Approve approved - pastikan di DB menggunakan 'Y'  
# APPROVE_NO = '0'           # Approve not approved
# APPROVE_REJECTED = '2'     # Approve rejected

# # ===== REVIEW STATUS CONSTANTS =====
# REVIEW_PENDING = '0'       # Review pending
# REVIEW_APPROVED = '1'      # Review approved 
# REVIEW_REJECTED = '2'      # Review rejected

# ===== FIXED REVIEWER FUNCTIONS =====

def is_reviewer_fixed(request):
    """
    Check if user is the designated reviewer (SITI FATIMAH)
    """
    if not request.user.is_authenticated:
        return False
    
    if request.user.username == REVIEWER_EMPLOYEE_NUMBER:
        logger.debug(f"REVIEWER CHECK: Username match for {request.user.username}")
        return True
    
    try:
        employee_data = request.session.get('employee_data')
        if employee_data and employee_data.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER:
            logger.debug(f"REVIEWER CHECK: Session match for {employee_data.get('employee_number')}")
            return True
    except Exception as e:
        logger.warning(f"REVIEWER CHECK: Session check failed: {e}")
    
    try:
        from authentication import SDBMAuthenticationBackend
        backend = SDBMAuthenticationBackend()
        employee_data = backend.get_employee_from_sdbm(request.user.username)
        
        if employee_data and employee_data.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER:
            request.session['employee_data'] = employee_data
            logger.debug(f"REVIEWER CHECK: SDBM match for {employee_data.get('employee_number')}")
            return True
    except Exception as e:
        logger.warning(f"REVIEWER CHECK: SDBM check failed: {e}")
    
    reviewer_usernames = ['007522', 'siti.fatimah', 'sitifatimah']
    if request.user.username.lower() in [u.lower() for u in reviewer_usernames]:
        logger.debug(f"REVIEWER CHECK: Alternative username match for {request.user.username}")
        return True
    
    logger.debug(f"REVIEWER CHECK: No match found for {request.user.username}")
    return False

def reviewer_required_fixed(view_func):
    """
    Decorator untuk memastikan hanya reviewer yang dapat akses
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Silakan login terlebih dahulu.')
            return redirect('login')
        
        if not is_reviewer_fixed(request):
            employee_data = request.session.get('employee_data', {})
            user_name = employee_data.get('fullname', request.user.get_full_name() or request.user.username)
            
            logger.error(f"REVIEWER ACCESS DENIED: User {request.user.username} ({user_name}) tried to access reviewer function")
            
            messages.error(
                request, 
                f'Akses ditolak. Halaman review hanya untuk {REVIEWER_FULLNAME}. '
                f'Anda login sebagai: {user_name}'
            )
            
            if request.method == 'POST':
                try:
                    if 'nomor_pengajuan' in kwargs:
                        return redirect('wo_maintenance_app:review_pengajuan_detail', nomor_pengajuan=kwargs['nomor_pengajuan'])
                    else:
                        return redirect('wo_maintenance_app:review_pengajuan_list')
                except:
                    return redirect('wo_maintenance_app:dashboard')
            else:
                return redirect('wo_maintenance_app:dashboard')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

def get_employee_data_for_request_fixed(request):
    """
    Get employee data untuk request dengan better session handling
    """
    employee_data = request.session.get('employee_data')
    if employee_data and employee_data.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER:
        logger.debug("EMPLOYEE DATA: Using session data")
        return employee_data
    
    try:
        from authentication import SDBMAuthenticationBackend
        backend = SDBMAuthenticationBackend()
        employee_data = backend.get_employee_from_sdbm(request.user.username)
        
        if employee_data and employee_data.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER:
            request.session['employee_data'] = employee_data
            request.session.modified = True
            logger.debug("EMPLOYEE DATA: Using SDBM data and updated session")
            return employee_data
    except Exception as e:
        logger.error(f"EMPLOYEE DATA: SDBM error: {e}")
    
    if request.user.username == REVIEWER_EMPLOYEE_NUMBER:
        fallback_data = {
            'employee_number': REVIEWER_EMPLOYEE_NUMBER,
            'fullname': REVIEWER_FULLNAME,
            'nickname': 'SITI',
            'department_name': 'QC',
            'section_name': 'Quality Control',
            'title_name': 'REVIEWER',
            'is_reviewer': True,
            'has_approval_role': True
        }
        
        request.session['employee_data'] = fallback_data
        request.session.modified = True
        logger.debug("EMPLOYEE DATA: Using fallback data")
        return fallback_data
    
    logger.error(f"EMPLOYEE DATA: No data found for {request.user.username}")
    return None

# ===== FUNCTION UNTUK VALIDATE STATUS VALUES =====
def validate_status_constants():
    """
    Function untuk validate apakah status constants sesuai dengan data di database
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Check status values yang actually ada di database
            cursor.execute("""
                SELECT DISTINCT status, approve, review_status
                FROM tabel_pengajuan 
                WHERE history_id IS NOT NULL
                ORDER BY status, approve, review_status
            """)
            
            actual_values = cursor.fetchall()
            
            logger.info("=== STATUS VALIDATION ===")
            logger.info(f"Expected STATUS_APPROVED: {STATUS_APPROVED}")
            logger.info(f"Expected APPROVE_YES: {APPROVE_YES}")
            logger.info("Actual values in database:")
            
            for row in actual_values:
                if row[0] or row[1] or row[2]:  # Skip NULL values
                    logger.info(f"  Status: {row[0]}, Approve: {row[1]}, Review: {row[2]}")
            
            logger.info("=== END VALIDATION ===")
            
            return True
            
    except Exception as e:
        logger.error(f"Error validating status constants: {e}")
        return False
# ===== COMPATIBILITY FUNCTION =====
def get_database_status_mapping():
    """
    Function untuk get actual status values dari database untuk compatibility
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Get actual approved values
            cursor.execute("""
                SELECT DISTINCT status, approve 
                FROM tabel_pengajuan 
                WHERE status IS NOT NULL AND approve IS NOT NULL
                ORDER BY status, approve
            """)
            
            status_mapping = {
                'approved_status_values': [],
                'approved_approve_values': [],
                'all_combinations': []
            }
            
            for row in cursor.fetchall():
                status_val = row[0]
                approve_val = row[1]
                
                if status_val not in status_mapping['approved_status_values']:
                    status_mapping['approved_status_values'].append(status_val)
                
                if approve_val not in status_mapping['approved_approve_values']:
                    status_mapping['approved_approve_values'].append(approve_val)
                
                status_mapping['all_combinations'].append({
                    'status': status_val,
                    'approve': approve_val
                })
            
            return status_mapping
            
    except Exception as e:
        logger.error(f"Error getting database status mapping: {e}")
        return None

# ===== ENHANCED STATUS CHECKER FUNCTION =====
def is_pengajuan_approved_for_review(status, approve):
    """
    Enhanced function untuk check apakah pengajuan approved dan ready for review
    Support multiple status formats untuk compatibility
    """
    # Primary check: A and Y (new format)
    if status == STATUS_APPROVED and approve == APPROVE_YES:
        return True
    
    # Legacy support: 1 and 1 (old format)
    if status == '1' and approve == '1':
        logger.warning(f"Using legacy status format: status=1, approve=1")
        return True
    
    # Additional compatibility checks
    approved_combinations = [
        ('A', 'Y'),  # New format
        ('1', '1'),  # Legacy format
        ('A', '1'),  # Mixed format 1
        ('1', 'Y')   # Mixed format 2
    ]
    
    for s, a in approved_combinations:
        if status == s and approve == a:
            logger.info(f"Pengajuan approved with format: status={s}, approve={a}")
            return True
    
    return False

def is_siti_fatimah_user(user):
    """
    Enhanced function untuk check apakah user adalah SITI FATIMAH
    """
    if not user.is_authenticated:
        return False
    
    # Primary check: username
    if user.username == REVIEWER_EMPLOYEE_NUMBER:
        return True
    
    # Alternative checks
    alternative_usernames = ['007522', 'siti.fatimah', 'sitifatimah']
    if user.username.lower() in [u.lower() for u in alternative_usernames]:
        logger.info(f"SITI FATIMAH detected with alternative username: {user.username}")
        return True
    
    # Check dari session employee_data
    try:
        if hasattr(user, 'request') and user.request:
            employee_data = user.request.session.get('employee_data')
            if employee_data and employee_data.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER:
                return True
    except:
        pass
    
    return False

# Run validation saat module loaded (untuk debugging)
if __name__ != '__main__':
    try:
        validate_status_constants()
    except:
        pass  # Jangan break aplikasi kalau validation gagal

def is_reviewer(user):
    """
    Check if user is the designated reviewer (SITI FATIMAH)
    UPDATED: Menggunakan SDBM authentication
    """
    if not user.is_authenticated:
        return False
    
    # Method 1: Check username (employee_number)
    if user.username == REVIEWER_EMPLOYEE_NUMBER:
        return True
    
    # Method 2: Check dari session employee_data
    try:
        employee_data = user.request.session.get('employee_data') if hasattr(user, 'request') else None
        if employee_data and employee_data.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER:
            return True
    except:
        pass
    
    # Method 3: Check dari SDBM langsung
    try:
        from authentication import SDBMAuthenticationBackend
        backend = SDBMAuthenticationBackend()
        employee_data = backend.get_employee_from_sdbm(user.username)
        
        if employee_data and employee_data.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER:
            return True
    except:
        pass
    
    return False

def reviewer_required(view_func):
    """
    Decorator untuk memastikan hanya reviewer yang dapat akses
    UPDATED: Better error handling dan redirect
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Silakan login terlebih dahulu.')
            return redirect('login')
        
        # Check if user is reviewer
        if not is_reviewer(request.user):
            # Get employee data untuk pesan error yang lebih informatif
            employee_data = request.session.get('employee_data', {})
            user_name = employee_data.get('fullname', request.user.get_full_name() or request.user.username)
            
            messages.error(
                request, 
                f'Akses ditolak. Halaman review hanya untuk {REVIEWER_FULLNAME}. '
                f'Anda login sebagai: {user_name}'
            )
            return redirect('wo_maintenance_app:dashboard')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
# ===== REVIEW DASHBOARD =====

@login_required
@reviewer_required_fixed
def review_dashboard(request):
    """
    Dashboard review untuk SITI FATIMAH
    UPDATED: Stats dengan status B/N untuk pending, A/Y untuk processed
    """
    try:
        employee_data = get_employee_data_for_request_fixed(request)
        
        if not employee_data:
            messages.error(request, 'Data employee tidak ditemukan. Silakan login ulang.')
            return redirect('login')
        
        initialize_review_data()
        
        # UPDATED: Statistik review dengan status baru
        with connections['DB_Maintenance'].cursor() as cursor:
            # Total pengajuan pending review - status B/N
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_pengajuan 
                WHERE status = %s AND approve = %s 
                    AND (review_status IS NULL OR review_status = '0')
            """, [STATUS_APPROVED, APPROVE_YES])
            pending_review_count = cursor.fetchone()[0] or 0
            
            # Total sudah diproses (final A/Y) hari ini
            today = timezone.now().date()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_pengajuan 
                WHERE reviewed_by = %s 
                    AND CAST(review_date AS DATE) = %s
                    AND status = %s AND approve = %s
            """, [REVIEWER_EMPLOYEE_NUMBER, today, STATUS_REVIEWED, APPROVE_REVIEWED])
            reviewed_today_count = cursor.fetchone()[0] or 0
        
        context = {
            'pending_review_count': pending_review_count,
            'reviewed_today_count': reviewed_today_count,
            'reviewer_name': employee_data.get('fullname', REVIEWER_FULLNAME),
            'employee_data': employee_data,
            'page_title': f'Review Dashboard - {employee_data.get("fullname", REVIEWER_FULLNAME)}'
        }
        
        return render(request, 'wo_maintenance_app/review_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in review dashboard: {e}")
        messages.error(request, 'Terjadi kesalahan saat memuat dashboard review.')
        return redirect('wo_maintenance_app:dashboard')


@login_required
@reviewer_required_fixed
def review_pengajuan_list(request):
    """
    Halaman daftar pengajuan yang perlu direview oleh SITI FATIMAH
    UPDATED: Query pengajuan dengan status B dan approve N
    """
    try:
        employee_data = get_employee_data_for_request_fixed(request)
        
        initialize_review_data()
        
        filter_form = ReviewFilterForm(request.GET or None)
        search_query = request.GET.get('search', '').strip()
        
        # UPDATED: Query pengajuan yang perlu direview dengan status B/N
        pengajuan_list = []
        total_records = 0
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # UPDATED: Base WHERE conditions dengan status B dan approve N
            where_conditions = [
                "tp.status = %s",     # B - approved oleh atasan
                "tp.approve = %s",    # N - approved oleh atasan
                "(tp.review_status IS NULL OR tp.review_status = '0')"  # Pending review
            ]
            query_params = [STATUS_APPROVED, APPROVE_YES]
            
            # Apply filters
            if filter_form.is_valid():
                tanggal_dari = filter_form.cleaned_data.get('tanggal_dari')
                tanggal_sampai = filter_form.cleaned_data.get('tanggal_sampai')
                
                if tanggal_dari:
                    where_conditions.append("CAST(tp.tgl_insert AS DATE) >= %s")
                    query_params.append(tanggal_dari)
                
                if tanggal_sampai:
                    where_conditions.append("CAST(tp.tgl_insert AS DATE) <= %s")
                    query_params.append(tanggal_sampai)
            
            # Search conditions
            if search_query:
                search_conditions = [
                    "tp.history_id LIKE %s",
                    "tp.oleh LIKE %s",
                    "tm.mesin LIKE %s",
                    "tp.deskripsi_perbaikan LIKE %s"
                ]
                where_conditions.append(f"({' OR '.join(search_conditions)})")
                search_param = f"%{search_query}%"
                query_params.extend([search_param] * len(search_conditions))
            
            # Build WHERE clause
            where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Count total records
            count_query = f"""
                SELECT COUNT(DISTINCT tp.history_id)
                FROM tabel_pengajuan tp
                LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
                {where_clause}
            """
            
            cursor.execute(count_query, query_params)
            total_records = cursor.fetchone()[0] or 0
            
            # Pagination
            page_size = 20
            page_number = int(request.GET.get('page', 1))
            offset = (page_number - 1) * page_size
            
            # Main query
            main_query = f"""
                SELECT DISTINCT
                    tp.history_id,           -- 0
                    tp.oleh,                 -- 1 (pengaju)
                    tm.mesin,                -- 2 (nama mesin)
                    tms.seksi,               -- 3 (section tujuan)
                    tpek.pekerjaan,          -- 4 (jenis pekerjaan)
                    tp.deskripsi_perbaikan,  -- 5 (deskripsi)
                    tp.status,               -- 6
                    tp.tgl_insert,           -- 7
                    tp.user_insert,          -- 8
                    tp.number_wo,            -- 9
                    tl.line,                 -- 10 (line name)
                    tp.approve,              -- 11
                    tp.review_status,        -- 12
                    tp.reviewed_by,          -- 13
                    tp.review_date           -- 14
                FROM tabel_pengajuan tp
                LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
                LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
                LEFT JOIN tabel_msection tms ON tp.id_section = tms.id_section
                LEFT JOIN tabel_pekerjaan tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
                {where_clause}
                ORDER BY tp.tgl_insert ASC, tp.history_id ASC
                OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
            """
            
            final_params = query_params + [offset, page_size]
            cursor.execute(main_query, final_params)
            pengajuan_list = cursor.fetchall()
            
            logger.info(f"Found {total_records} pengajuan for review by {employee_data.get('fullname', REVIEWER_FULLNAME)} (status=B, approve=N)")
        
        context = {
            'pengajuan_list': pengajuan_list,
            'filter_form': filter_form,
            'search_query': search_query,
            'total_records': total_records,
            'reviewer_name': employee_data.get('fullname', REVIEWER_FULLNAME),
            'employee_data': employee_data,
            'page_title': 'Daftar Pengajuan untuk Review',
            
            # UPDATED: Status info untuk template
            'STATUS_APPROVED': STATUS_APPROVED,     # B
            'APPROVE_YES': APPROVE_YES              # N
        }
        
        return render(request, 'wo_maintenance_app/review_pengajuan_list.html', context)
        
    except Exception as e:
        logger.error(f"Error in review pengajuan list: {e}")
        messages.error(request, 'Terjadi kesalahan saat memuat daftar pengajuan.')
        return redirect('wo_maintenance_app:review_dashboard')

# ===== HELPER FUNCTIONS - NEW =====

def get_employee_data_for_request(request):
    """
    Get employee data untuk request, prioritas dari session lalu SDBM
    """
    # Method 1: Dari session
    employee_data = request.session.get('employee_data')
    if employee_data and employee_data.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER:
        return employee_data
    
    # Method 2: Dari SDBM langsung
    try:
        from authentication import SDBMAuthenticationBackend
        backend = SDBMAuthenticationBackend()
        employee_data = backend.get_employee_from_sdbm(request.user.username)
        
        if employee_data and employee_data.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER:
            # Update session
            request.session['employee_data'] = employee_data
            return employee_data
    except Exception as e:
        logger.error(f"Error getting employee data from SDBM: {e}")
    
    # Method 3: Fallback untuk SITI FATIMAH
    if request.user.username == REVIEWER_EMPLOYEE_NUMBER:
        return {
            'employee_number': REVIEWER_EMPLOYEE_NUMBER,
            'fullname': REVIEWER_FULLNAME,
            'nickname': 'SITI',
            'department_name': 'QC',
            'section_name': 'Quality Control',
            'title_name': 'REVIEWER',
            'is_reviewer': True,
            'has_approval_role': True
        }
    
    return None

def initialize_review_data():
    """
    Auto-initialize pengajuan approved untuk review - FIXED
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Ensure review columns exist
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = 'review_status'
            """)
            
            if cursor.fetchone()[0] == 0:
                logger.warning("Review columns not found. Please run: python manage.py setup_review_system")
                return False
            
            # FIXED: Initialize approved pengajuan untuk review dengan status A dan approve Y
            cursor.execute("""
                UPDATE tabel_pengajuan 
                SET review_status = '0'
                WHERE status = %s AND approve = %s 
                    AND (review_status IS NULL OR review_status = '')
            """, [STATUS_APPROVED, APPROVE_YES])
            
            updated_count = cursor.rowcount
            if updated_count > 0:
                logger.info(f"Auto-initialized {updated_count} approved pengajuan for review (status=A, approve=Y)")
            
            return True
            
    except Exception as e:
        logger.error(f"Error initializing review data: {e}")
        return False

@login_required
def debug_reviewer_status(request):
    """
    Debug endpoint untuk check reviewer status - SUPERUSER ONLY
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        debug_info = {
            'timestamp': timezone.now().isoformat(),
            'user': {
                'username': request.user.username,
                'is_authenticated': request.user.is_authenticated,
                'is_superuser': request.user.is_superuser
            },
            'reviewer_checks': {
                'is_reviewer_fixed': is_reviewer_fixed(request),
                'session_data': request.session.get('employee_data', {}),
                'expected_employee_number': REVIEWER_EMPLOYEE_NUMBER
            },
            'session_info': {
                'session_key': request.session.session_key,
                'session_modified': getattr(request.session, 'modified', False),
                'session_accessed': getattr(request.session, 'accessed', False)
            }
        }
        
        return JsonResponse(debug_info, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


# Export the fixed functions
__all__ = [
    'is_reviewer_fixed',
    'reviewer_required_fixed', 
    'get_employee_data_for_request_fixed',
    'review_dashboard',
    'review_pengajuan_list',
    'review_pengajuan_detail',
    'initialize_review_data',
    'debug_reviewer_status'
]

# wo_maintenance_app/views.py - UPDATE review_pengajuan_detail view

# wo_maintenance_app/views.py - FIXED review_pengajuan_detail dengan Section Change

@login_required
@reviewer_required_fixed
def review_pengajuan_detail(request, nomor_pengajuan):
    """
    Detail pengajuan untuk review oleh SITI FATIMAH
    UPDATED: dengan automatic section update berdasarkan target_section
    """
    try:
        logger.info(f"REVIEW: Starting review for {nomor_pengajuan} by {request.user.username}")
        
        employee_data = get_employee_data_for_request_fixed(request)
        
        if not employee_data:
            logger.error(f"REVIEW: No employee data for {request.user.username}")
            messages.error(request, 'Data employee tidak ditemukan. Silakan login ulang.')
            return redirect('login')
        
        # Ambil data pengajuan
        pengajuan = None
        
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT 
                    tp.history_id,
                    tp.number_wo,
                    tp.tgl_insert,
                    tp.oleh,
                    tp.user_insert,
                    tm.mesin,
                    tms.seksi as section_tujuan,
                    tpek.pekerjaan,
                    tp.deskripsi_perbaikan,
                    tp.status,
                    tp.approve,
                    tl.line as line_name,
                    tp.tgl_his,
                    tp.jam_his,
                    tp.review_status,
                    tp.reviewed_by,
                    tp.review_date,
                    tp.review_notes,
                    tp.final_section_id,
                    final_section.seksi as final_section_name,
                    tp.status_pekerjaan,
                    tp.id_section as current_section_id
                FROM tabel_pengajuan tp
                LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
                LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
                LEFT JOIN tabel_msection tms ON tp.id_section = tms.id_section
                LEFT JOIN tabel_pekerjaan tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
                LEFT JOIN tabel_msection final_section ON tp.final_section_id = final_section.id_section
                WHERE tp.history_id = %s
            """, [nomor_pengajuan])
            
            row = cursor.fetchone()
            
            if not row:
                logger.error(f"REVIEW: Pengajuan {nomor_pengajuan} not found")
                messages.error(request, 'Pengajuan tidak ditemukan.')
                return redirect('wo_maintenance_app:review_pengajuan_list')
            
            pengajuan = {
                'history_id': row[0],
                'number_wo': row[1],
                'tgl_insert': row[2],
                'oleh': row[3],
                'user_insert': row[4],
                'mesin': row[5],
                'section_tujuan': row[6],
                'pekerjaan': row[7],
                'deskripsi_perbaikan': row[8],
                'status': row[9],
                'approve': row[10],
                'line_name': row[11],
                'tgl_his': row[12],
                'jam_his': row[13],
                'review_status': row[14],
                'reviewed_by': row[15],
                'review_date': row[16],
                'review_notes': row[17],
                'final_section_id': row[18],
                'final_section_name': row[19],
                'status_pekerjaan': row[20],
                'current_section_id': row[21]
            }
        
        # Cek apakah pengajuan sudah di-approve dan belum direview
        if pengajuan['status'] != STATUS_APPROVED or pengajuan['approve'] != APPROVE_YES:
            logger.warning(f"REVIEW: Pengajuan {nomor_pengajuan} not ready for review")
            messages.warning(request, 'Pengajuan ini belum siap untuk review.')
            return redirect('wo_maintenance_app:review_pengajuan_list')
        
        # Cek apakah sudah direview
        already_reviewed = pengajuan['review_status'] in ['1', '2']
        
        # Handle review form submission
        if request.method == 'POST' and not already_reviewed:
            logger.info(f"REVIEW: Processing POST request for {nomor_pengajuan}")
            
            request.session.modified = True
            
            review_form = ReviewForm(request.POST)
            
            if review_form.is_valid():
                action = review_form.cleaned_data['action']
                target_section = review_form.cleaned_data.get('target_section', '')
                review_notes = review_form.cleaned_data['review_notes']
                
                logger.info(f"REVIEW: Form valid - Action: {action}, Target: {target_section}")
                
                try:
                    with connections['DB_Maintenance'].cursor() as cursor:
                        if action == 'process':
                            # STEP 1: Update review status dan final processing
                            cursor.execute("""
                                UPDATE tabel_pengajuan
                                SET review_status = '1',
                                    reviewed_by = %s,
                                    review_date = GETDATE(),
                                    review_notes = %s,
                                    status = %s,
                                    approve = %s
                                WHERE history_id = %s
                            """, [
                                REVIEWER_EMPLOYEE_NUMBER, 
                                review_notes,
                                STATUS_REVIEWED,    # A - final processed
                                APPROVE_REVIEWED,   # Y - final processed
                                nomor_pengajuan
                            ])
                            
                            logger.info(f"REVIEW: Successfully processed {nomor_pengajuan} - final status A/Y")
                            
                            # STEP 2: Update section tujuan jika target_section dipilih
                            section_updated = False
                            section_changed = False
                            original_section = None
                            new_section = None
                            
                            if target_section:
                                logger.info(f"REVIEW: Processing section change to {target_section}")
                                
                                # Get section mapping
                                from .utils import auto_discover_maintenance_sections
                                section_mapping = auto_discover_maintenance_sections()
                                section_info = section_mapping.get(target_section)
                                
                                if section_info:
                                    # Get original section info
                                    cursor.execute("""
                                        SELECT tp.id_section, ms.seksi as current_section_name
                                        FROM tabel_pengajuan tp
                                        LEFT JOIN tabel_msection ms ON tp.id_section = ms.id_section
                                        WHERE tp.history_id = %s
                                    """, [nomor_pengajuan])
                                    
                                    original_row = cursor.fetchone()
                                    if original_row:
                                        original_section_id = int(float(original_row[0])) if original_row[0] else None
                                        original_section_name = original_row[1] or 'Unknown'
                                        
                                        original_section = {
                                            'id': original_section_id,
                                            'name': original_section_name
                                        }
                                    
                                    # Update section tujuan
                                    new_section_id = section_info['id_section']
                                    
                                    cursor.execute("""
                                        UPDATE tabel_pengajuan
                                        SET id_section = %s,
                                            final_section_id = %s
                                        WHERE history_id = %s
                                    """, [float(new_section_id), float(new_section_id), nomor_pengajuan])
                                    
                                    if cursor.rowcount > 0:
                                        section_updated = True
                                        section_changed = (
                                            original_section and 
                                            original_section['id'] != new_section_id
                                        )
                                        
                                        new_section = {
                                            'id': new_section_id,
                                            'name': section_info['section_name'],
                                            'display_name': section_info['display_name']
                                        }
                                        
                                        logger.info(f"REVIEW: Updated section from ID {original_section['id'] if original_section else 'Unknown'} to ID {new_section_id}")
                                    
                                    # STEP 3: SDBM Assignment ke supervisors
                                    try:
                                        from .utils import get_sdbm_supervisors_by_section_mapping, ensure_assignment_tables_exist
                                        
                                        supervisors = get_sdbm_supervisors_by_section_mapping(target_section)
                                        
                                        if supervisors:
                                            # Create assignment table if not exists
                                            ensure_assignment_tables_exist()
                                            
                                            assigned_count = 0
                                            # Assign ke supervisors
                                            for supervisor in supervisors:
                                                try:
                                                    cursor.execute("""
                                                        INSERT INTO tabel_pengajuan_assignment
                                                        (history_id, assigned_to_employee, assigned_by_employee, assignment_date, is_active, notes, assignment_type)
                                                        VALUES (%s, %s, %s, GETDATE(), 1, %s, 'SITI_REVIEW')
                                                    """, [
                                                        nomor_pengajuan,
                                                        supervisor['employee_number'],
                                                        REVIEWER_EMPLOYEE_NUMBER,
                                                        f"SITI FATIMAH Review: Section changed to {section_info['display_name']}. Assigned to {supervisor['title_name']}. Notes: {review_notes}"
                                                    ])
                                                    
                                                    assigned_count += 1
                                                    logger.info(f"REVIEW: Assigned {nomor_pengajuan} to {supervisor['fullname']} ({supervisor['employee_number']})")
                                                    
                                                except Exception as assign_error:
                                                    logger.error(f"REVIEW: Error assigning to {supervisor['employee_number']}: {assign_error}")
                                                    continue
                                            
                                            logger.info(f"REVIEW: Successfully assigned {nomor_pengajuan} to {assigned_count} supervisors in {target_section}")
                                        
                                    except Exception as sdbm_error:
                                        logger.error(f"REVIEW: SDBM assignment error: {sdbm_error}")
                                
                                else:
                                    logger.warning(f"REVIEW: Unknown target section: {target_section}")
                            
                            # Generate success message
                            success_parts = []
                            success_parts.append(f'✅ Pengajuan {nomor_pengajuan} berhasil diproses dan diselesaikan!')
                            success_parts.append(f'Status: Final Processed (A/Y)')
                            
                            if section_updated:
                                if section_changed and original_section and new_section:
                                    success_parts.append(f'🎯 Section tujuan berubah dari "{original_section["name"]}" ke "{new_section["display_name"]}"')
                                elif new_section:
                                    success_parts.append(f'🎯 Section tujuan dikonfirmasi ke "{new_section["display_name"]}"')
                            
                            messages.success(request, '\n'.join(success_parts))
                            
                        elif action == 'reject':
                            # Update pengajuan dengan review rejection
                            cursor.execute("""
                                UPDATE tabel_pengajuan
                                SET review_status = '2',
                                    reviewed_by = %s,
                                    review_date = GETDATE(),
                                    review_notes = %s,
                                    status = %s
                                WHERE history_id = %s
                            """, [REVIEWER_EMPLOYEE_NUMBER, review_notes, STATUS_REJECTED, nomor_pengajuan])
                            
                            logger.info(f"REVIEW: Rejected pengajuan {nomor_pengajuan}")
                            messages.success(request, f'❌ Pengajuan {nomor_pengajuan} berhasil ditolak. Alasan: {review_notes}')
                    
                    logger.info(f"REVIEW: Successfully processed review for {nomor_pengajuan}")
                    
                    request.session.modified = True
                    request.session.save()
                    
                    return redirect('wo_maintenance_app:review_pengajuan_detail', nomor_pengajuan=nomor_pengajuan)
                    
                except Exception as update_error:
                    logger.error(f"REVIEW: Error processing review for {nomor_pengajuan}: {update_error}")
                    messages.error(request, f'Terjadi kesalahan saat memproses review: {str(update_error)}')
            else:
                logger.warning(f"REVIEW: Form validation failed for {nomor_pengajuan}: {review_form.errors}")
                messages.error(request, 'Form review tidak valid. Periksa kembali input Anda.')
        else:
            review_form = ReviewForm()
        
        # Basic available sections
        available_sections = [
            {'key': 'it', 'name': '💻 IT', 'section_id': 1},
            {'key': 'elektrik', 'name': '⚡ Elektrik', 'section_id': 2},
            {'key': 'utility', 'name': '🏭 Utility', 'section_id': 4},
            {'key': 'mekanik', 'name': '🔧 Mekanik', 'section_id': 3}
        ]
        
        context = {
            'pengajuan': pengajuan,
            'review_form': review_form,
            'already_reviewed': already_reviewed,
            'reviewer_name': employee_data.get('fullname', REVIEWER_FULLNAME),
            'available_sections': available_sections,
            'employee_data': employee_data,
            'page_title': f'Review Pengajuan {nomor_pengajuan}',
            
            # Status constants untuk template
            'STATUS_APPROVED': STATUS_APPROVED,     # B
            'STATUS_REVIEWED': STATUS_REVIEWED,     # A
            'APPROVE_YES': APPROVE_YES,             # N
            'APPROVE_REVIEWED': APPROVE_REVIEWED    # Y
        }
        
        logger.info(f"REVIEW: Rendering template for {nomor_pengajuan}")
        return render(request, 'wo_maintenance_app/review_pengajuan_detail.html', context)
        
    except Exception as e:
        logger.error(f"REVIEW: Critical error for {nomor_pengajuan}: {e}")
        import traceback
        logger.error(f"REVIEW: Traceback: {traceback.format_exc()}")
        messages.error(request, 'Terjadi kesalahan saat memuat detail pengajuan.')
        return redirect('wo_maintenance_app:review_pengajuan_list')

# ===== NEW: Enhanced Daftar Laporan dengan SDBM Assignment Filter =====

# wo_maintenance_app/views.py - FIXED untuk tombol review SITI FATIMAH

@login_required
def enhanced_daftar_laporan(request):
    """
    Enhanced view untuk menampilkan daftar pengajuan dengan SDBM integration
    UPDATED: Exclude pengajuan yang sudah final processed (status=A & approve=Y)
    """
    try:
        # ===== AMBIL DATA HIERARCHY USER =====
        user_hierarchy = get_employee_hierarchy_data(request.user)
        
        if not user_hierarchy:
            logger.warning(f"User {request.user.username} tidak ditemukan di database SDBM")
            messages.error(request, 'Data karyawan tidak ditemukan. Hubungi administrator.')
            return redirect('wo_maintenance_app:dashboard')
        
        # ===== CEK APAKAH USER ADALAH 007522 (SITI FATIMAH) =====
        is_siti_fatimah = (
            user_hierarchy.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER or 
            request.user.username == REVIEWER_EMPLOYEE_NUMBER or
            request.user.username == '007522'
        )
        
        # ===== ENHANCED: SITI FATIMAH AUTO-INITIALIZE REVIEW SYSTEM =====
        if is_siti_fatimah:
            try:
                initialize_review_data()
                logger.info(f"SITI FATIMAH ({request.user.username}) accessing enhanced daftar laporan")
            except Exception as init_error:
                logger.warning(f"Review system initialization warning: {init_error}")
        
        # ===== FILTER MODE =====
        view_mode = request.GET.get('mode', 'normal')
        
        # ===== FILTER FORM =====
        filter_form = PengajuanFilterForm(request.GET or None)
        search_query = request.GET.get('search', '').strip()
        
        # ===== QUERY DATABASE dengan NEW STATUS LOGIC =====
        pengajuan_list = []
        total_records = 0
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # ===== BASE CONDITIONS: EXCLUDE FINAL PROCESSED =====
                base_conditions = [
                    "tp.history_id IS NOT NULL",
                    "NOT (tp.status = %s AND tp.approve = %s)"  # UPDATED: Exclude final processed
                ]
                query_params = [STATUS_REVIEWED, APPROVE_REVIEWED]  # A, Y
                
                if is_siti_fatimah and view_mode == 'approved':
                    # SITI FATIMAH - Only pengajuan siap review (status B, approve N)
                    base_conditions.extend([
                        "tp.status = %s",
                        "tp.approve = %s"
                    ])
                    query_params.extend([STATUS_APPROVED, APPROVE_YES])  # B, N
                    logger.info("SITI FATIMAH mode: querying pengajuan ready for review (status=B, approve=N)")
                    
                elif is_siti_fatimah:
                    # ENHANCED: SITI FATIMAH normal mode - show pengajuan ready for review
                    base_conditions.extend([
                        "tp.status = %s",
                        "tp.approve = %s"
                    ])
                    query_params.extend([STATUS_APPROVED, APPROVE_YES])  # B, N
                    logger.info("SITI FATIMAH mode: accessing pengajuan ready for review")
                    
                else:
                    # Mode normal: hierarchy filter untuk user lain
                    allowed_employee_numbers = get_subordinate_employee_numbers(user_hierarchy)
                    
                    if not allowed_employee_numbers:
                        allowed_employee_numbers = [user_hierarchy.get('employee_number')]
                    
                    # Simplified access control
                    if allowed_employee_numbers:
                        placeholders = ','.join(['%s'] * len(allowed_employee_numbers))
                        base_conditions.append(f"tp.user_insert IN ({placeholders})")
                        query_params.extend(allowed_employee_numbers)
                
                # ===== FORM FILTERS =====
                if filter_form.is_valid():
                    tanggal_dari = filter_form.cleaned_data.get('tanggal_dari')
                    if tanggal_dari:
                        base_conditions.append("CAST(tp.tgl_insert AS DATE) >= %s")
                        query_params.append(tanggal_dari)
                    
                    tanggal_sampai = filter_form.cleaned_data.get('tanggal_sampai')
                    if tanggal_sampai:
                        base_conditions.append("CAST(tp.tgl_insert AS DATE) <= %s")
                        query_params.append(tanggal_sampai)
                    
                    # Status filter - skip untuk SITI FATIMAH approved mode
                    if not (is_siti_fatimah and view_mode == 'approved'):
                        status_filter = filter_form.cleaned_data.get('status')
                        if status_filter:
                            base_conditions.append("tp.status = %s")
                            query_params.append(status_filter)
                    
                    pengaju_filter = filter_form.cleaned_data.get('pengaju')
                    if pengaju_filter:
                        base_conditions.append("tp.oleh LIKE %s")
                        query_params.append(f"%{pengaju_filter}%")
                    
                    history_id_filter = filter_form.cleaned_data.get('history_id')
                    if history_id_filter:
                        base_conditions.append("tp.history_id LIKE %s")
                        query_params.append(f"%{history_id_filter}%")
                
                # ===== SEARCH =====
                if search_query:
                    search_conditions = [
                        "tp.history_id LIKE %s",
                        "tp.oleh LIKE %s",
                        "tp.deskripsi_perbaikan LIKE %s",
                        "tp.number_wo LIKE %s"
                    ]
                    base_conditions.append(f"({' OR '.join(search_conditions)})")
                    search_param = f"%{search_query}%"
                    query_params.extend([search_param] * len(search_conditions))
                
                # ===== BUILD WHERE CLAUSE =====
                where_clause = ""
                if base_conditions:
                    where_clause = "WHERE " + " AND ".join(base_conditions)
                
                # ===== COUNT QUERY =====
                count_query = f"""
                    SELECT COUNT(DISTINCT tp.history_id)
                    FROM tabel_pengajuan tp
                    LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
                    LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
                    LEFT JOIN tabel_msection tms ON tp.id_section = tms.id_section
                    LEFT JOIN tabel_pekerjaan tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
                    {where_clause}
                """
                
                cursor.execute(count_query, query_params)
                total_records = cursor.fetchone()[0] or 0
                
                # ===== PAGINATION =====
                page_size = 20
                page_number = int(request.GET.get('page', 1))
                
                total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
                has_previous = page_number > 1
                has_next = page_number < total_pages
                previous_page_number = page_number - 1 if has_previous else None
                next_page_number = page_number + 1 if has_next else None
                
                # ===== MAIN QUERY =====
                offset = (page_number - 1) * page_size
                
                # Determine access type
                access_type_sql = "'HIERARCHY'"
                if is_siti_fatimah:
                    access_type_sql = "'SITI_FATIMAH'"
                
                main_query = f"""
                    SELECT DISTINCT
                        tp.history_id,                    -- 0
                        tp.oleh,                          -- 1
                        ISNULL(tm.mesin, 'N/A'),          -- 2
                        ISNULL(tms.seksi, 'N/A'),         -- 3
                        ISNULL(tpek.pekerjaan, 'N/A'),    -- 4
                        tp.deskripsi_perbaikan,           -- 5
                        tp.status,                        -- 6
                        tp.tgl_insert,                    -- 7
                        tp.user_insert,                   -- 8
                        tp.number_wo,                     -- 9
                        ISNULL(tl.line, 'N/A'),           -- 10
                        tp.approve,                       -- 11
                        tp.tgl_his,                       -- 12
                        tp.jam_his,                       -- 13
                        tp.status_pekerjaan,              -- 14
                        ISNULL(tp.review_status, '0'),    -- 15
                        tp.reviewed_by,                   -- 16
                        tp.review_date,                   -- 17
                        ISNULL(tms.seksi, 'N/A'),         -- 18
                        {access_type_sql} as access_type, -- 19
                        -- UPDATED: Enhanced status flags
                        CASE 
                            WHEN tp.status = %s AND tp.approve = %s THEN 1 
                            ELSE 0 
                        END as is_approved_for_review,   -- 20 (status B, approve N)
                        CASE 
                            WHEN tp.status = %s AND tp.approve = %s AND (tp.review_status IS NULL OR tp.review_status = '0') THEN 1 
                            ELSE 0 
                        END as needs_review              -- 21
                    FROM tabel_pengajuan tp
                    LEFT JOIN (
                        SELECT DISTINCT id_mesin, mesin 
                        FROM tabel_mesin 
                        WHERE mesin IS NOT NULL
                    ) tm ON tp.id_mesin = tm.id_mesin
                    LEFT JOIN (
                        SELECT DISTINCT id_line, line 
                        FROM tabel_line 
                        WHERE line IS NOT NULL
                    ) tl ON tp.id_line = tl.id_line
                    LEFT JOIN (
                        SELECT DISTINCT id_section, seksi 
                        FROM tabel_msection 
                        WHERE seksi IS NOT NULL
                    ) tms ON tp.id_section = tms.id_section
                    LEFT JOIN (
                        SELECT DISTINCT id_pekerjaan, pekerjaan 
                        FROM tabel_pekerjaan 
                        WHERE pekerjaan IS NOT NULL
                    ) tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
                    {where_clause}
                    ORDER BY tp.tgl_insert DESC, tp.history_id DESC
                    OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
                """
                
                # UPDATED: Add STATUS constants untuk CASE statements
                final_params = [STATUS_APPROVED, APPROVE_YES, STATUS_APPROVED, APPROVE_YES] + query_params + [offset, page_size]
                cursor.execute(main_query, final_params)
                
                pengajuan_list = cursor.fetchall()
                
                logger.info(f"Enhanced query executed successfully - Found {total_records} records for view_mode: {view_mode}")
                
        except Exception as db_error:
            logger.error(f"Database error in enhanced daftar_laporan: {db_error}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            messages.error(request, f'Terjadi kesalahan database: Silakan coba lagi atau hubungi administrator.')
            pengajuan_list = []
            total_records = 0
            total_pages = 1
            has_previous = False
            has_next = False
            previous_page_number = None
            next_page_number = None
            page_number = 1
        
        # ===== ENHANCED STATS UNTUK SITI FATIMAH =====
        siti_stats = {}
        if is_siti_fatimah:
            try:
                with connections['DB_Maintenance'].cursor() as cursor:
                    # Total pengajuan siap review (status B, approve N)
                    cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE status = %s AND approve = %s", 
                                 [STATUS_APPROVED, APPROVE_YES])
                    siti_stats['total_approved'] = cursor.fetchone()[0] or 0
                    
                    # Pending review count
                    cursor.execute("""SELECT COUNT(*) FROM tabel_pengajuan 
                                    WHERE status = %s AND approve = %s 
                                        AND (review_status IS NULL OR review_status = '0')""", 
                                 [STATUS_APPROVED, APPROVE_YES])
                    siti_stats['pending_review'] = cursor.fetchone()[0] or 0
                    
                    # Already reviewed count
                    cursor.execute("""SELECT COUNT(*) FROM tabel_pengajuan 
                                    WHERE status = %s AND approve = %s 
                                        AND review_status IN ('1', '2')""", 
                                 [STATUS_APPROVED, APPROVE_YES])
                    siti_stats['already_reviewed'] = cursor.fetchone()[0] or 0
                    
                    # Final processed count (status A, approve Y)
                    cursor.execute("""SELECT COUNT(*) FROM tabel_pengajuan 
                                    WHERE status = %s AND approve = %s""", 
                                 [STATUS_REVIEWED, APPROVE_REVIEWED])
                    siti_stats['final_processed'] = cursor.fetchone()[0] or 0
                    
                    logger.info(f"SITI FATIMAH stats: {siti_stats}")
                        
            except Exception as stats_error:
                logger.error(f"Error getting SITI stats: {stats_error}")
                siti_stats = {
                    'total_approved': 0,
                    'pending_review': 0,
                    'already_reviewed': 0,
                    'final_processed': 0
                }
        
        # ===== ENHANCED CONTEXT =====
        context = {
            'pengajuan_list': pengajuan_list,
            'filter_form': filter_form,
            'search_query': search_query,
            'total_records': total_records,
            'total_pages': total_pages,
            'page_number': page_number,
            'has_previous': has_previous,
            'has_next': has_next,
            'previous_page_number': previous_page_number,
            'next_page_number': next_page_number,
            'can_approve': True,
            'user_hierarchy': user_hierarchy,
            'employee_data': user_hierarchy,
            'is_siti_fatimah': is_siti_fatimah,
            'view_mode': view_mode,
            'siti_stats': siti_stats,
            
            # Enhanced dengan info status
            'assigned_count': 0,
            'access_methods': {
                'hierarchy': len(get_subordinate_employee_numbers(user_hierarchy)) if view_mode == 'normal' and not is_siti_fatimah else 0,
                'sdbm_assigned': 0
            },
            
            # ENHANCED: Review info untuk SITI FATIMAH
            'show_review_buttons': is_siti_fatimah,
            'reviewer_employee_number': REVIEWER_EMPLOYEE_NUMBER,
            
            # UPDATED: Status constants untuk template
            'STATUS_PENDING': STATUS_PENDING,       # 0
            'STATUS_APPROVED': STATUS_APPROVED,     # B - approved atasan
            'STATUS_REVIEWED': STATUS_REVIEWED,     # A - reviewed SITI
            'APPROVE_NO': APPROVE_NO,               # 0
            'APPROVE_YES': APPROVE_YES,             # N - approved atasan  
            'APPROVE_REVIEWED': APPROVE_REVIEWED,   # Y - reviewed SITI
            
            # Debug info
            'debug_info': {
                'sdbm_integration': True,
                'view_mode': view_mode,
                'is_siti_fatimah': is_siti_fatimah,
                'user_role': f"{user_hierarchy.get('title_name', 'Unknown')}",
                'status_values': {
                    'pending': STATUS_PENDING,
                    'approved': STATUS_APPROVED,
                    'reviewed': STATUS_REVIEWED,
                    'approve_yes': APPROVE_YES,
                    'approve_reviewed': APPROVE_REVIEWED
                },
                'review_stats': siti_stats,
                'total_pengajuan_loaded': len(pengajuan_list),
                'excluded_final_processed': 'Yes'  # NEW: Indicator
            } if request.user.is_superuser else None
        }
        
        return render(request, 'wo_maintenance_app/enhanced_daftar_laporan.html', context)
        
    except Exception as e:
        logger.error(f"Critical error in enhanced daftar_laporan: {e}")
        import traceback
        logger.error(f"Critical traceback: {traceback.format_exc()}")
        messages.error(request, 'Terjadi kesalahan sistem. Silakan coba lagi.')
        return redirect('wo_maintenance_app:dashboard')

    
# ===== NEW: SDBM Validation & Debug Views =====

@login_required
def validate_sdbm_integration(request):
    """
    View untuk validasi SDBM integration - SUPERUSER ONLY
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        from .utils import validate_sdbm_section_mapping, get_sdbm_section_mapping
        
        # Validate mapping
        validation_result = validate_sdbm_section_mapping()
        section_mapping = get_sdbm_section_mapping()
        
        debug_info = {
            'timestamp': timezone.now().isoformat(),
            'validation_result': validation_result,
            'section_mapping': section_mapping,
            'sdbm_connection_test': True
        }
        
        # Test SDBM connection
        try:
            with connections['SDBM'].cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM [hrbp].[employees] WHERE is_active = 1")
                active_employees = cursor.fetchone()[0]
                debug_info['sdbm_active_employees'] = active_employees
                
                cursor.execute("SELECT COUNT(*) FROM [hr].[department] WHERE is_active = 1 OR is_active IS NULL")
                active_departments = cursor.fetchone()[0] 
                debug_info['sdbm_active_departments'] = active_departments
                
                cursor.execute("SELECT COUNT(*) FROM [hr].[section] WHERE is_active = 1 OR is_active IS NULL")
                active_sections = cursor.fetchone()[0]
                debug_info['sdbm_active_sections'] = active_sections
                
        except Exception as sdbm_error:
            debug_info['sdbm_connection_test'] = False
            debug_info['sdbm_error'] = str(sdbm_error)
        
        return JsonResponse(debug_info, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@login_required
def test_sdbm_assignment(request, target_section):
    """
    Test SDBM assignment untuk target section - SUPERUSER ONLY
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        from .utils import get_sdbm_supervisors_by_section_mapping, get_sdbm_section_mapping
        
        # Get supervisors
        supervisors = get_sdbm_supervisors_by_section_mapping(target_section)
        section_mapping = get_sdbm_section_mapping()
        
        test_result = {
            'target_section': target_section,
            'section_mapping': section_mapping.get(target_section, {}),
            'supervisors_found': len(supervisors),
            'supervisors': [
                {
                    'employee_number': s['employee_number'],
                    'fullname': s['fullname'],
                    'title_name': s['title_name'],
                    'department_name': s['department_name'],
                    'section_name': s['section_name'],
                    'level_description': s['level_description']
                } for s in supervisors
            ]
        }
        
        return JsonResponse(test_result, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)

@login_required
@reviewer_required
def review_history(request):
    """
    History review yang sudah dilakukan oleh SITI FATIMAH
    """
    try:
        # Filter dan search
        filter_form = ReviewFilterForm(request.GET or None)
        search_query = request.GET.get('search', '').strip()
        
        # Query history review
        pengajuan_list = []
        total_records = 0
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Base WHERE conditions untuk history
            where_conditions = [
                "tp.reviewed_by = %s"  # Only reviewed by SITI FATIMAH
            ]
            query_params = [REVIEWER_EMPLOYEE_NUMBER]
            
            # Apply filters
            if filter_form.is_valid():
                # Filter tanggal
                tanggal_dari = filter_form.cleaned_data.get('tanggal_dari')
                tanggal_sampai = filter_form.cleaned_data.get('tanggal_sampai')
                
                if tanggal_dari:
                    where_conditions.append("CAST(tp.review_date AS DATE) >= %s")
                    query_params.append(tanggal_dari)
                
                if tanggal_sampai:
                    where_conditions.append("CAST(tp.review_date AS DATE) <= %s")
                    query_params.append(tanggal_sampai)
                
                # Filter review status
                review_status_filter = filter_form.cleaned_data.get('review_status')
                if review_status_filter in ['1', '2']:
                    where_conditions.append("tp.review_status = %s")
                    query_params.append(review_status_filter)
            
            # Search conditions
            if search_query:
                search_conditions = [
                    "tp.history_id LIKE %s",
                    "tp.oleh LIKE %s",
                    "tm.mesin LIKE %s"
                ]
                where_conditions.append(f"({' OR '.join(search_conditions)})")
                search_param = f"%{search_query}%"
                query_params.extend([search_param] * len(search_conditions))
            
            # Build WHERE clause
            where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Count total records
            count_query = f"""
                SELECT COUNT(DISTINCT tp.history_id)
                FROM tabel_pengajuan tp
                LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
                {where_clause}
            """
            
            cursor.execute(count_query, query_params)
            total_records = cursor.fetchone()[0] or 0
            
            # Pagination
            page_size = 20
            page_number = int(request.GET.get('page', 1))
            offset = (page_number - 1) * page_size
            
            total_pages = (total_records + page_size - 1) // page_size
            has_previous = page_number > 1
            has_next = page_number < total_pages
            previous_page_number = page_number - 1 if has_previous else None
            next_page_number = page_number + 1 if has_next else None
            
            # Main query dengan pagination
            main_query = f"""
                SELECT DISTINCT
                    tp.history_id,           -- 0
                    tp.oleh,                 -- 1 (pengaju)
                    tm.mesin,                -- 2 (nama mesin)
                    tms.seksi,               -- 3 (section tujuan original)
                    tpek.pekerjaan,          -- 4 (jenis pekerjaan)
                    tp.deskripsi_perbaikan,  -- 5 (deskripsi)
                    tp.review_status,        -- 6
                    tp.review_date,          -- 7
                    tp.review_notes,         -- 8
                    final_section.seksi,     -- 9 (final section name)
                    tp.tgl_insert            -- 10
                FROM tabel_pengajuan tp
                LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
                LEFT JOIN tabel_msection tms ON tp.id_section = tms.id_section
                LEFT JOIN tabel_pekerjaan tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
                LEFT JOIN tabel_msection final_section ON tp.final_section_id = final_section.id_section
                {where_clause}
                ORDER BY tp.review_date DESC, tp.history_id DESC
                OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
            """
            
            final_params = query_params + [offset, page_size]
            cursor.execute(main_query, final_params)
            pengajuan_list = cursor.fetchall()
        
        context = {
            'pengajuan_list': pengajuan_list,
            'filter_form': filter_form,
            'search_query': search_query,
            'total_records': total_records,
            'total_pages': total_pages,
            'page_number': page_number,
            'has_previous': has_previous,
            'has_next': has_next,
            'previous_page_number': previous_page_number,
            'next_page_number': next_page_number,
            'reviewer_name': REVIEWER_FULLNAME,
            'page_title': 'History Review Pengajuan'
        }
        
        return render(request, 'wo_maintenance_app/review_history.html', context)
        
    except Exception as e:
        logger.error(f"Error in review history: {e}")
        messages.error(request, 'Terjadi kesalahan saat memuat history review.')
        return redirect('wo_maintenance_app:review_dashboard')


# ===== REVIEW SYSTEM HELPER FUNCTIONS =====

def ensure_review_tables_exist():
    """
    Memastikan review tables ada di database
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Create review log table if not exists
            cursor.execute("""
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
                        CONSTRAINT [PK_tabel_review_log] PRIMARY KEY CLUSTERED ([id] ASC)
                    ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
                END
            """)
            
            # Add review columns to tabel_pengajuan if not exists
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
            
            logger.info("Review tables and columns verified/created successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error ensuring review tables exist: {e}")
        return False


# ===== DASHBOARD & OVERVIEW =====

@login_required
def dashboard_index(request):
    """Dashboard utama WO Maintenance dengan data dari DB_Maintenance"""
    
    employee_data = request.session.get('employee_data', {})
    
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Total pengajuan (exclude yang sudah final processed)
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_pengajuan 
                WHERE history_id IS NOT NULL 
                    AND NOT (status = %s AND approve = %s)
            """, [STATUS_REVIEWED, APPROVE_REVIEWED])
            total_pengajuan = cursor.fetchone()[0] or 0
            
            # Pengajuan berdasarkan status (exclude final processed)
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM tabel_pengajuan 
                WHERE history_id IS NOT NULL
                    AND NOT (status = %s AND approve = %s)
                GROUP BY status
            """, [STATUS_REVIEWED, APPROVE_REVIEWED])
            status_data = cursor.fetchall()
            
            # Pengajuan hari ini (exclude final processed)
            today = timezone.now().date()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_pengajuan 
                WHERE CAST(tgl_insert AS DATE) = %s
                    AND history_id IS NOT NULL
                    AND NOT (status = %s AND approve = %s)
            """, [today, STATUS_REVIEWED, APPROVE_REVIEWED])
            pengajuan_today = cursor.fetchone()[0] or 0
            
            # Recent pengajuan (exclude final processed)
            cursor.execute("""
                SELECT TOP 5 
                    tp.history_id, tm.mesin, tp.oleh, 
                    tp.status, tp.tgl_insert, tl.line
                FROM tabel_pengajuan tp
                LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
                LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
                WHERE tp.history_id IS NOT NULL
                    AND NOT (tp.status = %s AND tp.approve = %s)
                ORDER BY tp.tgl_insert DESC
            """, [STATUS_REVIEWED, APPROVE_REVIEWED])
            recent_pengajuan = cursor.fetchall()
            
    except Exception as e:
        logger.error(f"Error loading dashboard data: {e}")
        total_pengajuan = 0
        status_data = []
        pengajuan_today = 0
        recent_pengajuan = []
    
    # Process status data
    status_counts = {}
    for status, count in status_data:
        status_counts[str(status) if status else '0'] = count
    
    context = {
        'employee_data': employee_data,
        'total_pengajuan': total_pengajuan,
        'pengajuan_pending': status_counts.get('0', 0),
        'pengajuan_approved': status_counts.get('B', 0),  # UPDATED: B for atasan approved
        'pengajuan_reviewed': status_counts.get('A', 0),  # UPDATED: A for SITI reviewed  
        'pengajuan_today': pengajuan_today,
        'recent_pengajuan': recent_pengajuan,
        'page_title': 'Dashboard WO Maintenance'
    }
    
    return render(request, 'wo_maintenance_app/dashboard.html', context)


# ===== INPUT LAPORAN =====

# FIXED input_laporan - Bagian untuk mengganti di wo_maintenance_app/views.py

@login_required
def input_laporan(request):
    """View untuk input pengajuan maintenance baru"""
    
    employee_data = request.session.get('employee_data', {})
    
    if not employee_data:
        messages.error(request, 'Data employee tidak ditemukan. Silakan login ulang.')
        return redirect('login')
    
    if request.method == 'POST':
        form = PengajuanMaintenanceForm(
            request.POST, 
            user=request.user,
            employee_data=employee_data
        )
        
        if form.is_valid():
            try:
                validated_data = form.cleaned_data
                
                with connections['DB_Maintenance'].cursor() as cursor:
                    # Generate history_id
                    today = datetime.now()
                    prefix = f"WO{today.strftime('%Y%m%d')}"
                    
                    cursor.execute("""
                        SELECT TOP 1 history_id 
                        FROM tabel_pengajuan 
                        WHERE history_id LIKE %s 
                        ORDER BY history_id DESC
                    """, [f"{prefix}%"])
                    
                    result = cursor.fetchone()
                    if result:
                        last_number = int(result[0][-3:])
                        history_id = f"{prefix}{str(last_number + 1).zfill(3)}"
                    else:
                        history_id = f"{prefix}001"
                    
                    # Generate number_wo
                    number_wo = f"WO{today.strftime('%y%m%d%H%M%S')}"
                    if len(number_wo) > 15:
                        number_wo = number_wo[:15]
                    
                    # Get next id_pengajuan
                    cursor.execute("SELECT ISNULL(MAX(id_pengajuan), 0) + 1 FROM tabel_pengajuan")
                    next_id_pengajuan = cursor.fetchone()[0]
                    
                    # Convert data
                    line_id_int = int(validated_data['line_section'])
                    mesin_id_int = int(validated_data['nama_mesin'])
                    section_id_int = int(validated_data['section_tujuan'])
                    pekerjaan_id_int = int(validated_data['jenis_pekerjaan'])
                    
                    # Get actual line_id
                    cursor.execute("""
                        SELECT id_line FROM tabel_line 
                        WHERE CAST(id_line AS int) = %s AND status = 'A'
                    """, [line_id_int])
                    
                    line_result = cursor.fetchone()
                    if not line_result:
                        raise ValueError(f"Line ID {line_id_int} tidak ditemukan")
                    
                    actual_line_id = line_result[0]
                    
                    # Prepare data
                    user_insert = str(request.user.username)[:50]
                    oleh = str(employee_data.get('fullname', request.user.username))[:500]
                    deskripsi = str(validated_data['deskripsi_pekerjaan'])[:2000]
                    
                    # Insert dengan status pending
                    cursor.execute("""
                        INSERT INTO tabel_pengajuan 
                        (history_id, tgl_his, jam_his, id_line, id_mesin, number_wo, 
                         deskripsi_perbaikan, status, user_insert, tgl_insert, oleh, 
                         approve, id_section, id_pekerjaan, id_pengajuan, idpengajuan)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        history_id,
                        today,
                        today.strftime('%H:%M:%S'),
                        actual_line_id,
                        float(mesin_id_int),
                        number_wo,
                        deskripsi,
                        STATUS_PENDING,  # '0' - pending
                        user_insert,
                        today,
                        oleh,
                        APPROVE_NO,      # '0' - not approved
                        float(section_id_int),
                        float(pekerjaan_id_int),
                        next_id_pengajuan,
                        float(next_id_pengajuan)
                    ])
                
                logger.info(f"SUCCESS: Pengajuan {history_id} berhasil disimpan")
                messages.success(
                    request, 
                    f'Pengajuan berhasil dibuat dengan ID: {history_id}'
                )
                return redirect('wo_maintenance_app:daftar_laporan')
                
            except Exception as e:
                logger.error(f"ERROR saving pengajuan: {e}")
                messages.error(request, f'Terjadi kesalahan saat menyimpan data: {str(e)}')
        else:
            logger.error(f"Form validation errors: {form.errors}")
            messages.error(request, 'Mohon periksa kembali form yang Anda isi.')
    else:
        form = PengajuanMaintenanceForm(user=request.user, employee_data=employee_data)
    
    context = {
        'form': form,
        'employee_data': employee_data,
        'page_title': 'Input Pengajuan Maintenance'
    }
    
    return render(request, 'wo_maintenance_app/input_laporan.html', context)


@login_required
def debug_form_validation(request):
    """
    Debug view untuk troubleshooting form validation
    ONLY FOR SUPERUSER
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    line_id = request.GET.get('line_id', '')
    mesin_id = request.GET.get('mesin_id', '')
    
    debug_info = {
        'timestamp': datetime.now().isoformat(),
        'line_id': line_id,
        'mesin_id': mesin_id,
        'validation_results': {}
    }
    
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # 1. Test line exists
            if line_id:
                cursor.execute("""
                    SELECT id_line, line, status 
                    FROM tabel_line 
                    WHERE CAST(id_line AS int) = %s
                """, [int(line_id)])
                line_result = cursor.fetchone()
                debug_info['validation_results']['line_exists'] = {
                    'found': line_result is not None,
                    'data': line_result
                }
            
            # 2. Test mesin exists
            if mesin_id:
                cursor.execute("""
                    SELECT id_mesin, mesin, id_line, status 
                    FROM tabel_mesin 
                    WHERE id_mesin = %s
                """, [int(mesin_id)])
                mesin_result = cursor.fetchone()
                debug_info['validation_results']['mesin_exists'] = {
                    'found': mesin_result is not None,
                    'data': mesin_result
                }
            
            # 3. Test line-mesin relationship
            if line_id and mesin_id:
                cursor.execute("""
                    SELECT tm.id_mesin, tm.mesin, tl.line, 
                           tm.id_line as mesin_line_id, 
                           tl.id_line as line_table_id
                    FROM tabel_mesin tm
                    INNER JOIN tabel_line tl ON CAST(tl.id_line AS varchar(10)) = tm.id_line
                    WHERE tm.id_mesin = %s 
                        AND CAST(tl.id_line AS int) = %s
                        AND tm.mesin IS NOT NULL 
                        AND tm.mesin != ''
                        AND (tm.status IS NULL OR tm.status != '0')
                        AND tl.status = 'A'
                """, [int(mesin_id), int(line_id)])
                relationship_result = cursor.fetchone()
                debug_info['validation_results']['line_mesin_relationship'] = {
                    'valid': relationship_result is not None,
                    'data': relationship_result
                }
            
            # 4. Get all mesins for line
            if line_id:
                cursor.execute("""
                    SELECT tm.id_mesin, tm.mesin, tm.id_line
                    FROM tabel_mesin tm
                    INNER JOIN tabel_line tl ON CAST(tl.id_line AS varchar(10)) = tm.id_line
                    WHERE CAST(tl.id_line AS int) = %s
                        AND tm.mesin IS NOT NULL 
                        AND tm.mesin != ''
                        AND (tm.status IS NULL OR tm.status != '0')
                        AND tl.status = 'A'
                    ORDER BY tm.mesin
                """, [int(line_id)])
                all_mesins = cursor.fetchall()
                debug_info['validation_results']['all_mesins_for_line'] = {
                    'count': len(all_mesins),
                    'mesins': [{'id': row[0], 'name': row[1], 'line_id': row[2]} for row in all_mesins]
                }
    
    except Exception as e:
        debug_info['error'] = str(e)
        debug_info['traceback'] = traceback.format_exc()
    
    return JsonResponse(debug_info, indent=2)


@login_required
def debug_ajax_mesin_response(request):
    """
    Debug view untuk test response AJAX get_mesin_by_line
    ONLY FOR SUPERUSER
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    line_id = request.GET.get('line_id', '')
    
    if not line_id:
        return JsonResponse({'error': 'line_id required'})
    
    # Call the actual AJAX function and capture response
    try:
        # Simulate the AJAX request
        from django.test import RequestFactory
        factory = RequestFactory()
        ajax_request = factory.get('/wo-maintenance/ajax/get-mesin/', {'line_id': line_id})
        ajax_request.user = request.user
        
        # Call the actual function
        ajax_response = get_mesin_by_line(ajax_request)
        ajax_data = json.loads(ajax_response.content.decode('utf-8'))
        
        debug_info = {
            'timestamp': datetime.now().isoformat(),
            'line_id': line_id,
            'ajax_response': ajax_data,
            'analysis': {
                'success': ajax_data.get('success', False),
                'mesins_count': len(ajax_data.get('mesins', [])),
                'mesins_ids': [m.get('id') for m in ajax_data.get('mesins', [])],
                'line_name': ajax_data.get('line_name'),
                'debug_data': ajax_data.get('debug', {})
            }
        }
        
        return JsonResponse(debug_info, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@login_required  
def debug_form_choices(request):
    """
    Debug view untuk melihat form choices yang di-generate
    ONLY FOR SUPERUSER
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        employee_data = request.session.get('employee_data', {})
        
        # Create form instance
        form = PengajuanMaintenanceForm(user=request.user, employee_data=employee_data)
        
        debug_info = {
            'timestamp': datetime.now().isoformat(),
            'form_choices': {
                'line_section': {
                    'count': len(form.fields['line_section'].choices),
                    'choices': form.fields['line_section'].choices
                },
                'section_tujuan': {
                    'count': len(form.fields['section_tujuan'].choices),
                    'choices': form.fields['section_tujuan'].choices
                },
                'jenis_pekerjaan': {
                    'count': len(form.fields['jenis_pekerjaan'].choices),
                    'choices': form.fields['jenis_pekerjaan'].choices
                }
            },
            'nama_mesin_field_type': str(type(form.fields['nama_mesin'])),
            'nama_mesin_widget_attrs': form.fields['nama_mesin'].widget.attrs
        }
        
        return JsonResponse(debug_info, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


# ===== DAFTAR LAPORAN =====
def check_assignment_table_exists():
    """
    Helper function untuk check apakah assignment table ada
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'tabel_pengajuan_assignment'
            """)
            return cursor.fetchone()[0] > 0
    except Exception as e:
        logger.error(f"Error checking assignment table: {e}")
        return False
    
# wo_maintenance_app/views.py - FIXED daftar_laporan function

@login_required
def daftar_laporan(request):
    """
    View untuk menampilkan daftar pengajuan maintenance 
    FIXED VERSION - dengan proper JOIN dan alias untuk semua kolom
    """
    try:
        # ===== AMBIL DATA HIERARCHY USER =====
        user_hierarchy = get_employee_hierarchy_data(request.user)
        
        if not user_hierarchy:
            logger.warning(f"User {request.user.username} tidak ditemukan di database SDBM")
            messages.error(request, 'Data karyawan tidak ditemukan. Hubungi administrator.')
            return redirect('wo_maintenance_app:dashboard')
        
        # ===== CEK APAKAH USER ADALAH 007522 (SITI FATIMAH) =====
        is_siti_fatimah = (
            user_hierarchy.get('employee_number') == '007522' or 
            request.user.username == '007522'
        )
        
        # ===== FILTER MODE =====
        view_mode = request.GET.get('mode', 'normal')
        
        if is_siti_fatimah:
            logger.info(f"User SITI FATIMAH (007522) accessing daftar laporan - Mode: {view_mode}")
        
        # ===== FILTER FORM =====
        filter_form = PengajuanFilterForm(request.GET or None)
        search_query = request.GET.get('search', '').strip()
        
        # ===== QUERY DATABASE - FIXED WITH PROPER JOINS =====
        pengajuan_list = []
        total_records = 0
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # ===== BUILD WHERE CONDITIONS =====
                where_conditions = ["tp.history_id IS NOT NULL"]
                query_params = []
                
                if is_siti_fatimah and view_mode == 'approved':
                    # Mode approved untuk SITI FATIMAH: semua approved
                    where_conditions.extend([
                        "tp.status = '1'",
                        "tp.approve = '1'"
                    ])
                    logger.info("SITI FATIMAH mode: querying ALL approved pengajuan")
                    
                else:
                    # Mode normal: hierarchy filter sederhana
                    allowed_employee_numbers = get_subordinate_employee_numbers(user_hierarchy)
                    
                    if not allowed_employee_numbers:
                        allowed_employee_numbers = [user_hierarchy.get('employee_number')]
                    
                    # Limit ke 10 employee untuk menghindari query terlalu panjang
                    if len(allowed_employee_numbers) > 10:
                        allowed_employee_numbers = allowed_employee_numbers[:10]
                    
                    # Simple IN condition
                    if allowed_employee_numbers:
                        placeholders = ','.join(['%s'] * len(allowed_employee_numbers))
                        where_conditions.append(f"tp.user_insert IN ({placeholders})")
                        query_params.extend(allowed_employee_numbers)
                
                # ===== FORM FILTERS =====
                if filter_form.is_valid():
                    tanggal_dari = filter_form.cleaned_data.get('tanggal_dari')
                    if tanggal_dari:
                        where_conditions.append("CAST(tp.tgl_insert AS DATE) >= %s")
                        query_params.append(tanggal_dari)
                    
                    tanggal_sampai = filter_form.cleaned_data.get('tanggal_sampai')
                    if tanggal_sampai:
                        where_conditions.append("CAST(tp.tgl_insert AS DATE) <= %s")
                        query_params.append(tanggal_sampai)
                    
                    # Status filter - skip untuk mode approved
                    if not (is_siti_fatimah and view_mode == 'approved'):
                        status_filter = filter_form.cleaned_data.get('status')
                        if status_filter:
                            where_conditions.append("tp.status = %s")
                            query_params.append(status_filter)
                    
                    pengaju_filter = filter_form.cleaned_data.get('pengaju')
                    if pengaju_filter:
                        where_conditions.append("tp.oleh LIKE %s")
                        query_params.append(f"%{pengaju_filter}%")
                    
                    history_id_filter = filter_form.cleaned_data.get('history_id')
                    if history_id_filter:
                        where_conditions.append("tp.history_id LIKE %s")
                        query_params.append(f"%{history_id_filter}%")
                
                # ===== SEARCH =====
                if search_query:
                    search_conditions = [
                        "tp.history_id LIKE %s",
                        "tp.oleh LIKE %s",
                        "tp.deskripsi_perbaikan LIKE %s",
                        "tp.number_wo LIKE %s",
                        "tm.mesin LIKE %s"
                    ]
                    where_conditions.append(f"({' OR '.join(search_conditions)})")
                    search_param = f"%{search_query}%"
                    query_params.extend([search_param] * len(search_conditions))
                
                # ===== BUILD WHERE CLAUSE =====
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                
                # ===== COUNT QUERY - PROPER WITH JOINS =====
                count_query = f"""
                    SELECT COUNT(DISTINCT tp.history_id)
                    FROM tabel_pengajuan tp
                    LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
                    LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
                    LEFT JOIN tabel_msection tms ON tp.id_section = tms.id_section
                    LEFT JOIN tabel_pekerjaan tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
                    LEFT JOIN tabel_msection final_section ON tp.final_section_id = final_section.id_section
                    {where_clause}
                """
                
                cursor.execute(count_query, query_params)
                total_records = cursor.fetchone()[0] or 0
                
                # ===== PAGINATION =====
                page_size = 20
                page_number = int(request.GET.get('page', 1))
                
                total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
                has_previous = page_number > 1
                has_next = page_number < total_pages
                previous_page_number = page_number - 1 if has_previous else None
                next_page_number = page_number + 1 if has_next else None
                
                # ===== MAIN QUERY - FIXED tanpa duplikasi =====
                page_size = 20
                offset = (page_number - 1) * page_size
                
                # Query langsung dengan DISTINCT untuk menghindari duplikasi
                main_query = f"""
                    SELECT DISTINCT
                        tp.history_id,                    -- 0
                        tp.oleh,                          -- 1
                        ISNULL(tm.mesin, 'N/A'),          -- 2
                        ISNULL(tms.seksi, 'N/A'),         -- 3
                        ISNULL(tpek.pekerjaan, 'N/A'),    -- 4
                        tp.deskripsi_perbaikan,           -- 5
                        tp.status,                        -- 6
                        tp.tgl_insert,                    -- 7
                        tp.user_insert,                   -- 8
                        tp.number_wo,                     -- 9
                        ISNULL(tl.line, 'N/A'),           -- 10
                        tp.approve,                       -- 11
                        tp.tgl_his,                       -- 12
                        tp.jam_his,                       -- 13
                        tp.status_pekerjaan,              -- 14
                        tp.review_status,                 -- 15
                        tp.reviewed_by,                   -- 16
                        tp.review_date,                   -- 17
                        ISNULL(final_section.seksi, 'N/A'), -- 18
                        'NORMAL'                          -- 19 (access type)
                    FROM tabel_pengajuan tp
                    LEFT JOIN (
                        SELECT DISTINCT id_mesin, mesin 
                        FROM tabel_mesin 
                        WHERE mesin IS NOT NULL
                    ) tm ON tp.id_mesin = tm.id_mesin
                    LEFT JOIN (
                        SELECT DISTINCT id_line, line 
                        FROM tabel_line 
                        WHERE line IS NOT NULL
                    ) tl ON tp.id_line = tl.id_line
                    LEFT JOIN (
                        SELECT DISTINCT id_section, seksi 
                        FROM tabel_msection 
                        WHERE seksi IS NOT NULL
                    ) tms ON tp.id_section = tms.id_section
                    LEFT JOIN (
                        SELECT DISTINCT id_pekerjaan, pekerjaan 
                        FROM tabel_pekerjaan 
                        WHERE pekerjaan IS NOT NULL
                    ) tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
                    LEFT JOIN (
                        SELECT DISTINCT id_section, seksi 
                        FROM tabel_msection 
                        WHERE seksi IS NOT NULL
                    ) final_section ON tp.final_section_id = final_section.id_section
                    {where_clause}
                    ORDER BY tp.tgl_insert DESC, tp.history_id DESC
                    OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
                """
                
                final_params = query_params + [offset, page_size]
                cursor.execute(main_query, final_params)
                
                pengajuan_list = cursor.fetchall()
                
                logger.info(f"Fixed query executed successfully - Found {total_records} records")
                
        except Exception as db_error:
            logger.error(f"Database error in fixed daftar_laporan: {db_error}")
            messages.error(request, f'Terjadi kesalahan database: {str(db_error)}')
            pengajuan_list = []
            total_records = 0
            total_pages = 1
            has_previous = False
            has_next = False
            previous_page_number = None
            next_page_number = None
            page_number = 1
        
        # ===== STATS UNTUK SITI FATIMAH =====
        siti_stats = {}
        if is_siti_fatimah:
            try:
                with connections['DB_Maintenance'].cursor() as cursor:
                    # Simple count queries
                    cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE status = '1' AND approve = '1'")
                    siti_stats['total_approved'] = cursor.fetchone()[0] or 0
                    
                    cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE status = '1' AND approve = '1' AND (review_status IS NULL OR review_status = '0')")
                    siti_stats['pending_review'] = cursor.fetchone()[0] or 0
                    
                    cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE status = '1' AND approve = '1' AND review_status IN ('1', '2')")
                    siti_stats['already_reviewed'] = cursor.fetchone()[0] or 0
                    
                    cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE status = '1' AND approve = '1' AND CAST(tgl_insert AS DATE) = CAST(GETDATE() AS DATE)")
                    siti_stats['approved_today'] = cursor.fetchone()[0] or 0
                    
            except Exception as stats_error:
                logger.error(f"Error getting SITI stats: {stats_error}")
                siti_stats = {
                    'total_approved': 0,
                    'pending_review': 0,
                    'already_reviewed': 0,
                    'approved_today': 0
                }
        
        # ===== CONTEXT =====
        context = {
            'pengajuan_list': pengajuan_list,
            'filter_form': filter_form,
            'search_query': search_query,
            'total_records': total_records,
            'total_pages': total_pages,
            'page_number': page_number,
            'has_previous': has_previous,
            'has_next': has_next,
            'previous_page_number': previous_page_number,
            'next_page_number': next_page_number,
            'can_approve': True,
            'user_hierarchy': user_hierarchy,
            'employee_data': user_hierarchy,
            'is_siti_fatimah': is_siti_fatimah,
            'view_mode': view_mode,
            'siti_stats': siti_stats,
            'special_query_mode': 'all_approved' if (is_siti_fatimah and view_mode == 'approved') else 'normal',
            
            # Debug info
            'debug_info': {
                'allowed_employee_count': 1,
                'assigned_pengajuan_count': 0,
                'user_role': f"{user_hierarchy.get('title_name', 'Unknown')}",
                'can_approve': True,
                'special_query_mode': 'all_approved' if (is_siti_fatimah and view_mode == 'approved') else 'normal',
                'is_siti_fatimah': is_siti_fatimah,
                'view_mode': view_mode,
                'fixed_query_mode': True
            } if request.user.is_superuser else None
        }
        
        return render(request, 'wo_maintenance_app/daftar_laporan.html', context)
        
    except Exception as e:
        logger.error(f"Critical error in fixed daftar_laporan: {e}")
        messages.error(request, 'Terjadi kesalahan sistem. Silakan coba lagi.')
        return redirect('wo_maintenance_app:dashboard')
    
# wo_maintenance_app/views.py - DEBUG TEST VERSION 

@login_required
def debug_test_view(request):
    """
    DEBUG VIEW untuk test minimal query
    Gunakan ini untuk debugging database compatibility
    """
    try:
        # Test connection dan minimal query
        debug_results = {}
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Test 1: Basic connection
            try:
                cursor.execute("SELECT 1 as test")
                debug_results['connection'] = 'OK'
            except Exception as e:
                debug_results['connection'] = f'ERROR: {e}'
            
            # Test 2: Basic count
            try:
                cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan")
                count = cursor.fetchone()[0]
                debug_results['basic_count'] = f'OK: {count} records'
            except Exception as e:
                debug_results['basic_count'] = f'ERROR: {e}'
            
            # Test 3: Simple SELECT
            try:
                cursor.execute("""
                    SELECT TOP 5 
                        history_id, 
                        oleh, 
                        status, 
                        approve,
                        tgl_insert
                    FROM tabel_pengajuan 
                    WHERE history_id IS NOT NULL
                    ORDER BY tgl_insert DESC
                """)
                rows = cursor.fetchall()
                debug_results['simple_select'] = f'OK: {len(rows)} rows returned'
                debug_results['sample_data'] = rows
            except Exception as e:
                debug_results['simple_select'] = f'ERROR: {e}'
            
            # Test 4: Approved count
            try:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM tabel_pengajuan 
                    WHERE status = '1' AND approve = '1'
                """)
                approved_count = cursor.fetchone()[0]
                debug_results['approved_count'] = f'OK: {approved_count} approved records'
            except Exception as e:
                debug_results['approved_count'] = f'ERROR: {e}'
            
            # Test 5: User check
            try:
                user_employee_number = request.user.username
                debug_results['current_user'] = user_employee_number
                debug_results['is_007522'] = 'YES' if user_employee_number == '007522' else 'NO'
            except Exception as e:
                debug_results['current_user'] = f'ERROR: {e}'
        
        # Return debug template
        context = {
            'debug_results': debug_results,
            'page_title': 'Database Debug Test'
        }
        
        return render(request, 'wo_maintenance_app/debug_test.html', context)
        
    except Exception as e:
        logger.error(f"Debug test error: {e}")
        return HttpResponse(f"Debug Error: {e}")


@login_required  
def minimal_approved_view(request):
    """
    MINIMAL VIEW khusus untuk user 007522
    Hanya menampilkan approved pengajuan dengan query paling sederhana
    """
    try:
        # Check user 007522
        if request.user.username != '007522':
            messages.error(request, 'Halaman ini khusus untuk user 007522 (SITI FATIMAH)')
            return redirect('wo_maintenance_app:dashboard')
        
        # Minimal query untuk approved pengajuan
        pengajuan_list = []
        total_approved = 0
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Count approved
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM tabel_pengajuan 
                    WHERE status = '1' AND approve = '1'
                """)
                total_approved = cursor.fetchone()[0] or 0
                
                # Get approved data - minimal
                cursor.execute("""
                    SELECT TOP 50
                        history_id,
                        oleh,
                        deskripsi_perbaikan,
                        status,
                        approve,
                        tgl_insert,
                        user_insert,
                        number_wo,
                        review_status
                    FROM tabel_pengajuan 
                    WHERE status = '1' AND approve = '1'
                    ORDER BY tgl_insert DESC
                """)
                
                pengajuan_list = cursor.fetchall()
                
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
            messages.error(request, f'Database error: {str(db_error)}')
        
        context = {
            'pengajuan_list': pengajuan_list,
            'total_approved': total_approved,
            'page_title': 'Minimal Approved View - SITI FATIMAH'
        }
        
        return render(request, 'wo_maintenance_app/minimal_approved.html', context)
        
    except Exception as e:
        logger.error(f"Error in minimal approved view: {e}")
        return HttpResponse(f"Error: {e}")


# ===== DETAIL LAPORAN =====

@login_required
def detail_laporan(request, nomor_pengajuan):
    """
    View untuk menampilkan detail pengajuan dengan sistem approval hierarchy
    UPDATED: approval set status=B dan approve=N (siap untuk review SITI)
    """
    try:
        # ===== AMBIL DATA HIERARCHY USER =====
        user_hierarchy = get_employee_hierarchy_data(request.user)
        
        if not user_hierarchy:
            messages.error(request, 'Data karyawan tidak ditemukan. Hubungi administrator.')
            return redirect('wo_maintenance_app:daftar_laporan')
        
        # ===== AMBIL DATA PENGAJUAN =====
        pengajuan = None
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        tp.history_id,
                        tp.number_wo,
                        tp.tgl_insert,
                        tp.oleh,
                        tp.user_insert,
                        tmes.mesin,
                        tms.seksi as section_tujuan,
                        tpek.pekerjaan,
                        tp.deskripsi_perbaikan,
                        tp.status,
                        tp.approve,
                        tl.line as line_name,
                        tp.tgl_his,
                        tp.jam_his,
                        tp.status_pekerjaan
                    FROM [DB_Maintenance].[dbo].[tabel_pengajuan] tp
                    LEFT JOIN [DB_Maintenance].[dbo].[tabel_mesin] tmes ON tp.id_mesin = tmes.id_mesin
                    LEFT JOIN [DB_Maintenance].[dbo].[tabel_line] tl ON tp.id_line = tl.id_line
                    LEFT JOIN [DB_Maintenance].[dbo].[tabel_msection] tms ON tp.id_section = tms.id_section
                    LEFT JOIN [DB_Maintenance].[dbo].[tabel_pekerjaan] tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
                    WHERE tp.history_id = %s
                """, [nomor_pengajuan])
                
                row = cursor.fetchone()
                
                if not row:
                    messages.error(request, 'Pengajuan tidak ditemukan.')
                    return redirect('wo_maintenance_app:daftar_laporan')
                
                pengajuan = {
                    'history_id': row[0],
                    'number_wo': row[1],
                    'tgl_insert': row[2],
                    'oleh': row[3],
                    'user_insert': row[4],
                    'mesin': row[5],
                    'section_tujuan': row[6],
                    'pekerjaan': row[7],
                    'deskripsi_perbaikan': row[8],
                    'status': row[9],
                    'approve': row[10],
                    'line_name': row[11],
                    'tgl_his': row[12],
                    'jam_his': row[13],
                    'status_pekerjaan': row[14]
                }
                
        except Exception as db_error:
            logger.error(f"Database error in detail_laporan: {db_error}")
            messages.error(request, 'Terjadi kesalahan saat mengambil data pengajuan.')
            return redirect('wo_maintenance_app:daftar_laporan')
        
        # ===== CEK ACCESS PERMISSION =====
        is_siti_fatimah = user_hierarchy.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER
        
        if is_siti_fatimah:
            # SITI FATIMAH dapat melihat semua pengajuan
            can_view = True
        else:
            # User lain: cek hierarchy
            allowed_employee_numbers = get_subordinate_employee_numbers(user_hierarchy)
            assigned_history_ids = get_assigned_pengajuan_for_user(user_hierarchy.get('employee_number'))
            
            can_view = (
                pengajuan['user_insert'] in allowed_employee_numbers or 
                pengajuan['history_id'] in assigned_history_ids
            )
        
        if not can_view:
            logger.warning(f"User {user_hierarchy.get('fullname')} tried to access unauthorized pengajuan {nomor_pengajuan}")
            messages.error(request, 'Anda tidak memiliki akses ke pengajuan ini.')
            return redirect('wo_maintenance_app:daftar_laporan')
        
        # ===== CEK APPROVAL CAPABILITY =====
        pengaju_hierarchy = get_employee_by_number(pengajuan['user_insert'])
        can_approve = False
        
        # UPDATED: Check status pending dengan nilai yang benar
        if pengaju_hierarchy and pengajuan['status'] == STATUS_PENDING:  # Status pending = '0'
            can_approve = can_user_approve(user_hierarchy, pengaju_hierarchy)
        
         # ===== HANDLE APPROVAL FORM =====
        approval_form = ApprovalForm()
        
        if request.method == 'POST' and can_approve:
            approval_form = ApprovalForm(request.POST)
            
            if approval_form.is_valid():
                action = approval_form.cleaned_data['action']
                keterangan = approval_form.cleaned_data['keterangan']
                
                try:
                    with connections['DB_Maintenance'].cursor() as cursor:
                        # UPDATED: Approval logic dengan status baru
                        if action == '1':  # Approve
                            new_status = STATUS_APPROVED      # 'B' - approved oleh atasan
                            new_approve = APPROVE_YES          # 'N' - approved oleh atasan
                        else:  # Reject
                            new_status = STATUS_REJECTED       # '2' 
                            new_approve = APPROVE_REJECTED     # '2'
                        
                        cursor.execute("""
                            UPDATE [DB_Maintenance].[dbo].[tabel_pengajuan]
                            SET status = %s, approve = %s
                            WHERE history_id = %s
                        """, [new_status, new_approve, nomor_pengajuan])
                        
                        # ===== REVIEW SYSTEM INTEGRATION =====
                        if action == '1':  # Jika di-approve
                            # STEP 1: Set status untuk review oleh SITI FATIMAH
                            cursor.execute("""
                                UPDATE [DB_Maintenance].[dbo].[tabel_pengajuan]
                                SET review_status = '0'
                                WHERE history_id = %s
                            """, [nomor_pengajuan])
                            
                            logger.info(f"Pengajuan {nomor_pengajuan} approved by {user_hierarchy.get('fullname')} - sent to review queue (status={new_status}, approve={new_approve})")
                            
                            messages.success(request, 
                                f'Pengajuan {nomor_pengajuan} berhasil di-approve! '
                                f'Pengajuan akan direview oleh {REVIEWER_FULLNAME} untuk distribusi ke section yang tepat.'
                            )
                            
                        else:
                            # Rejection - langsung final
                            logger.info(f"Pengajuan {nomor_pengajuan} rejected by {user_hierarchy.get('fullname')} (status={new_status}, approve={new_approve})")
                            messages.success(request, f'Pengajuan {nomor_pengajuan} berhasil ditolak.')
                        
                        # Log approval action
                        try:
                            cursor.execute("""
                                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tabel_approval_log' AND xtype='U')
                                CREATE TABLE [dbo].[tabel_approval_log](
                                    [id] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
                                    [history_id] [varchar](15) NULL,
                                    [approver_user] [varchar](50) NULL,
                                    [action] [varchar](10) NULL,
                                    [keterangan] [varchar](max) NULL,
                                    [tgl_approval] [datetime] NULL
                                )
                            """)
                            
                            cursor.execute("""
                                INSERT INTO [DB_Maintenance].[dbo].[tabel_approval_log] 
                                (history_id, approver_user, action, keterangan, tgl_approval)
                                VALUES (%s, %s, %s, %s, GETDATE())
                            """, [nomor_pengajuan, user_hierarchy.get('employee_number'), action, keterangan])
                        except Exception as log_error:
                            logger.warning(f"Failed to log approval action: {log_error}")
                    
                    action_text = 'disetujui' if action == '1' else 'ditolak'
                    
                    logger.info(f"Pengajuan {nomor_pengajuan} {action_text} by {user_hierarchy.get('fullname')}")
                    
                    return redirect('wo_maintenance_app:detail_laporan', nomor_pengajuan=nomor_pengajuan)
                    
                except Exception as update_error:
                    logger.error(f"Error updating approval for {nomor_pengajuan}: {update_error}")
                    messages.error(request, 'Terjadi kesalahan saat memproses approval.')
        
        # ===== CONTEXT =====
        context = {
            'pengajuan': pengajuan,
            'can_approve': can_approve,
            'approval_form': approval_form,
            'user_hierarchy': user_hierarchy,
            'employee_data': user_hierarchy,
            'pengaju_hierarchy': pengaju_hierarchy,
            'is_siti_fatimah': is_siti_fatimah,
            
            # UPDATED: Status constants untuk template
            'STATUS_PENDING': STATUS_PENDING,       # 0
            'STATUS_APPROVED': STATUS_APPROVED,     # B
            'STATUS_REVIEWED': STATUS_REVIEWED,     # A
            'APPROVE_NO': APPROVE_NO,               # 0
            'APPROVE_YES': APPROVE_YES,             # N
            'APPROVE_REVIEWED': APPROVE_REVIEWED    # Y
        }
        
        return render(request, 'wo_maintenance_app/detail_laporan.html', context)
        
    except Exception as e:
        logger.error(f"Critical error in detail_laporan: {e}")
        messages.error(request, 'Terjadi kesalahan sistem. Silakan coba lagi.')
        return redirect('wo_maintenance_app:daftar_laporan')


@login_required 
def create_assignment_tables(request):
    """
    View untuk membuat assignment tables secara manual - SUPERUSER ONLY
    """
    if not request.user.is_superuser:
        messages.error(request, 'Unauthorized access.')
        return redirect('wo_maintenance_app:daftar_laporan')
    
    try:
        from wo_maintenance_app.utils import ensure_assignment_tables_exist
        
        success = ensure_assignment_tables_exist()
        
        if success:
            messages.success(request, 'Assignment tables berhasil dibuat!')
            logger.info(f"Assignment tables created by {request.user.username}")
        else:
            messages.error(request, 'Gagal membuat assignment tables. Check logs untuk detail.')
            
    except Exception as e:
        logger.error(f"Error creating assignment tables: {e}")
        messages.error(request, f'Error creating tables: {str(e)}')
    
    return redirect('wo_maintenance_app:daftar_laporan')

@login_required
def debug_assignment_status(request):
    """
    Debug view untuk mengecek status assignment - FOR DEBUGGING ONLY
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        debug_info = {}
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # ===== CEK TABEL ASSIGNMENT =====
            try:
                cursor.execute("SELECT COUNT(*) FROM [DB_Maintenance].[dbo].[tabel_pengajuan_assignment]")
                assignment_count = cursor.fetchone()[0]
                debug_info['assignment_table_exists'] = True
                debug_info['assignment_count'] = assignment_count
            except Exception as e:
                debug_info['assignment_table_exists'] = False
                debug_info['assignment_count'] = 0
                debug_info['assignment_table_error'] = str(e)
            
            # ===== CEK PENGAJUAN APPROVED =====
            try:
                cursor.execute("""
                    SELECT history_id, status, approve, id_section 
                    FROM [DB_Maintenance].[dbo].[tabel_pengajuan] 
                    WHERE status = '1' 
                    ORDER BY tgl_insert DESC
                """)
                approved_pengajuan = cursor.fetchall()
                debug_info['approved_pengajuan'] = [
                    {
                        'history_id': row[0],
                        'status': row[1], 
                        'approve': row[2],
                        'id_section': row[3]
                    } for row in approved_pengajuan[:10]  # Top 10
                ]
            except Exception as e:
                debug_info['approved_pengajuan_error'] = str(e)
                debug_info['approved_pengajuan'] = []
            
            # ===== CEK ASSIGNMENT AKTIF UNTUK PENGAJUAN APPROVED =====
            if debug_info.get('assignment_table_exists'):
                try:
                    cursor.execute("""
                        SELECT pa.history_id, pa.assigned_to_employee, pa.assignment_date
                        FROM [DB_Maintenance].[dbo].[tabel_pengajuan_assignment] pa
                        INNER JOIN [DB_Maintenance].[dbo].[tabel_pengajuan] tp 
                            ON pa.history_id = tp.history_id
                        WHERE tp.status = '1' AND pa.is_active = 1
                        ORDER BY pa.assignment_date DESC
                    """)
                    assignments = cursor.fetchall()
                    debug_info['recent_assignments'] = [
                        {
                            'history_id': row[0],
                            'assigned_to': row[1],
                            'assignment_date': row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else None
                        } for row in assignments[:20]  # Top 20
                    ]
                except Exception as e:
                    debug_info['recent_assignments_error'] = str(e)
                    debug_info['recent_assignments'] = []
            else:
                debug_info['recent_assignments'] = []
                debug_info['recent_assignments_info'] = 'Assignment table not found'
        
        return JsonResponse({'success': True, 'debug_info': debug_info})
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

            
@login_required
def debug_test_assignment(request, history_id, section_id, approver):
    """
    Debug view untuk test assignment manual - FOR DEBUGGING ONLY
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        from wo_maintenance_app.utils import assign_pengajuan_to_section_supervisors, get_target_section_supervisors
        
        logger.info(f"DEBUG: Manual test assignment - {history_id} to section {section_id} by {approver}")
        
        # Test get target supervisors
        supervisors = get_target_section_supervisors(section_id)
        
        # Test assignment
        assigned = assign_pengajuan_to_section_supervisors(history_id, section_id, approver)
        
        return JsonResponse({
            'success': True,
            'history_id': history_id,
            'section_id': section_id,
            'approver': approver,
            'found_supervisors': len(supervisors),
            'supervisors': [
                {
                    'employee_number': s['employee_number'],
                    'fullname': s['fullname'],
                    'title_name': s['title_name'],
                    'level': s['level']
                } for s in supervisors
            ],
            'assigned_count': len(assigned),
            'assigned_employees': assigned
        })
        
    except Exception as e:
        logger.error(f"Debug test assignment error: {e}")
        return JsonResponse({'error': str(e)}, status=500)



@login_required
def debug_section_supervisors(request, section_id):
    """
    Debug view untuk cek supervisors di section - FOR DEBUGGING ONLY
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        from wo_maintenance_app.utils import get_target_section_supervisors
        
        supervisors = get_target_section_supervisors(section_id)
        
        return JsonResponse({
            'section_id': section_id,
            'found_count': len(supervisors),
            'supervisors': [
                {
                    'employee_number': s['employee_number'],
                    'fullname': s['fullname'],
                    'title_name': s['title_name'],
                    'section_name': s['section_name'],
                    'department_name': s['department_name'],
                    'level': s['level'],
                    'is_supervisor': s['is_supervisor'],
                    'is_manager': s['is_manager']
                } for s in supervisors
            ]
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ===== AJAX VIEWS =====

@login_required
def get_mesin_by_line(request):
    """AJAX view untuk mendapatkan mesin berdasarkan line"""
    
    line_id = str(request.GET.get('line_id', '')).strip()
    
    logger.debug(f"AJAX: Getting mesin for line_id: '{line_id}'")
    
    if not line_id:
        return JsonResponse({
            'success': False,
            'mesins': [],
            'message': 'Line ID tidak ditemukan'
        })
    
    try:
        try:
            line_id_int = int(line_id)
        except ValueError:
            return JsonResponse({
                'success': False,
                'mesins': [],
                'message': f'Line ID tidak valid: {line_id}'
            })
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Validasi line exists
            cursor.execute("""
                SELECT id_line, line 
                FROM tabel_line 
                WHERE CAST(id_line AS int) = %s AND status = 'A'
            """, [line_id_int])
            
            line_data = cursor.fetchone()
            if not line_data:
                return JsonResponse({
                    'success': False,
                    'mesins': [],
                    'message': f'Line ID {line_id} tidak ditemukan atau tidak aktif'
                })
            
            line_name = line_data[1]
            logger.debug(f"AJAX: Valid line found - {line_name}")
            
            # Get mesin
            cursor.execute("""
                SELECT tm.id_mesin, tm.mesin, tm.nomer
                FROM tabel_mesin tm
                INNER JOIN tabel_line tl ON CAST(tl.id_line AS varchar(10)) = tm.id_line
                WHERE CAST(tl.id_line AS int) = %s
                    AND tl.status = 'A'
                    AND tm.mesin IS NOT NULL 
                    AND tm.mesin != ''
                    AND (tm.status IS NULL OR tm.status != '0')
                ORDER BY tm.mesin, tm.nomer
            """, [line_id_int])
            
            mesins = cursor.fetchall()
            logger.debug(f"AJAX: Found {len(mesins)} mesins for line {line_id}")
            
            # Build response
            mesin_list = []
            seen_ids = set()
            
            for mesin in mesins:
                try:
                    id_mesin = int(float(mesin[0]))
                    mesin_name = str(mesin[1] or '').strip()
                    mesin_nomer = str(mesin[2] or '').strip()
                    
                    if id_mesin in seen_ids or not mesin_name:
                        continue
                    
                    display_name = mesin_name
                    if mesin_nomer:
                        display_name += f" ({mesin_nomer})"
                    
                    mesin_list.append({
                        'id': str(id_mesin),
                        'text': display_name
                    })
                    seen_ids.add(id_mesin)
                    
                    logger.debug(f"AJAX: Added mesin - ID={id_mesin}, Name={display_name}")
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"AJAX: Skipping invalid mesin data: {e}")
                    continue
            
            response = {
                'success': True,
                'mesins': mesin_list,
                'line_name': line_name,
                'message': f'Ditemukan {len(mesin_list)} mesin untuk {line_name}'
            }
            
            logger.debug(f"AJAX: Response prepared - {len(mesin_list)} mesins")
            return JsonResponse(response)
        
    except Exception as e:
        logger.error(f"AJAX Error in get_mesin_by_line: {e}")
        import traceback
        logger.error(f"AJAX Traceback: {traceback.format_exc()}")
        
        return JsonResponse({
            'success': False,
            'error': str(e),
            'mesins': [],
            'message': 'Error loading mesin data - hubungi administrator'
        })



@login_required 
def debug_database_structure(request):
    """Debug view untuk mengecek struktur dan data database"""
    
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Check tabel_line structure dan data
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'tabel_line'
                ORDER BY ORDINAL_POSITION
            """)
            line_structure = cursor.fetchall()
            
            # Check tabel_mesin structure
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'tabel_mesin'
                ORDER BY ORDINAL_POSITION
            """)
            mesin_structure = cursor.fetchall()
            
            # Sample data dari tabel_line
            cursor.execute("SELECT TOP 5 id_line, line, status FROM tabel_line WHERE status = 'A' ORDER BY line")
            line_samples = cursor.fetchall()
            
            # Sample data dari tabel_mesin dengan tipe data id_line
            cursor.execute("""
                SELECT TOP 10 id_mesin, mesin, id_line, nomer, status, 
                       SQL_VARIANT_PROPERTY(id_line, 'BaseType') as id_line_type,
                       LEN(CAST(id_line AS varchar)) as id_line_length
                FROM tabel_mesin 
                WHERE mesin IS NOT NULL
                ORDER BY id_line, mesin
            """)
            mesin_samples = cursor.fetchall()
            
            # Analisis ketidakcocokan tipe data
            cursor.execute("""
                SELECT DISTINCT 
                    tl.id_line as line_id_float,
                    tl.line,
                    CAST(tl.id_line AS varchar) as line_id_as_string,
                    COUNT(tm.id_mesin) as mesin_count,
                    STRING_AGG(tm.id_line, ', ') as mesin_id_line_values
                FROM tabel_line tl
                LEFT JOIN tabel_mesin tm ON CAST(tl.id_line AS varchar(10)) = tm.id_line
                WHERE tl.status = 'A' AND tl.line IS NOT NULL
                GROUP BY tl.id_line, tl.line
                ORDER BY tl.id_line
            """)
            type_mismatch_analysis = cursor.fetchall()
            
            response = {
                'success': True,
                'line_structure': line_structure,
                'mesin_structure': mesin_structure,
                'line_samples': line_samples,
                'mesin_samples': mesin_samples,
                'type_mismatch_analysis': type_mismatch_analysis,
                'analysis': {
                    'issue': 'tabel_line.id_line is float, tabel_mesin.id_line is varchar(10)',
                    'solution': 'Use CAST() in queries to convert types for matching'
                }
            }
            
    except Exception as e:
        import traceback
        response = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }
    
    return JsonResponse(response)


@login_required
def search_mesin_ajax(request):
    """AJAX view untuk search mesin dengan Select2 - FIXED VERSION"""
    
    search_term = str(request.GET.get('q', '')).strip()
    page = int(request.GET.get('page', 1))
    line_id = str(request.GET.get('line_id', '')).strip()
    page_size = 20
    
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            offset = (page - 1) * page_size
            
            # Base conditions
            where_conditions = [
                "tm.mesin IS NOT NULL",
                "tm.mesin != ''",
                "(tm.status IS NULL OR tm.status != '0')"
            ]
            params = []
            
            # Add line filter if provided
            if line_id:
                try:
                    line_id_int = int(line_id)
                    where_conditions.append("CAST(tl.id_line AS int) = %s")
                    where_conditions.append("tl.status = 'A'")
                    params.append(line_id_int)
                except ValueError:
                    logger.warning(f"Invalid line_id in search: {line_id}")
            
            # Add search filter if provided
            if search_term:
                where_conditions.append("(tm.mesin LIKE %s OR ISNULL(tm.nomer, '') LIKE %s)")
                search_param = f"%{search_term}%"
                params.extend([search_param, search_param])
            
            # Build query with proper JOIN
            base_query = """
                SELECT DISTINCT tm.id_mesin, tm.mesin, tm.nomer
                FROM tabel_mesin tm
            """
            
            if line_id:
                base_query += " INNER JOIN tabel_line tl ON CAST(tl.id_line AS varchar(10)) = tm.id_line"
            
            where_clause = " WHERE " + " AND ".join(where_conditions)
            order_clause = " ORDER BY tm.mesin, tm.nomer"
            limit_clause = f" OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY"
            
            final_query = base_query + where_clause + order_clause + limit_clause
            
            logger.debug(f"Search mesin query: {final_query}")
            logger.debug(f"Search mesin params: {params}")
            
            cursor.execute(final_query, params)
            mesins = cursor.fetchall()
            
            mesin_list = []
            seen_ids = set()
            
            for mesin in mesins:
                try:
                    id_mesin = int(float(mesin[0]))
                    mesin_name = str(mesin[1] or '').strip()
                    mesin_nomer = str(mesin[2] or '').strip()
                    
                    if id_mesin in seen_ids or not mesin_name:
                        continue
                    
                    display_name = mesin_name
                    if mesin_nomer:
                        display_name += f" ({mesin_nomer})"
                    
                    mesin_list.append({
                        'id': str(id_mesin),
                        'text': display_name
                    })
                    seen_ids.add(id_mesin)
                    
                except (ValueError, TypeError):
                    continue
            
            has_more = len(mesin_list) == page_size
            
            return JsonResponse({
                'results': mesin_list,
                'pagination': {'more': has_more}
            })
        
    except Exception as e:
        logger.error(f"Error in search_mesin_ajax: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'results': [],
            'pagination': {'more': False}
        }, status=500)


@login_required
def test_mesin_connection(request):
    """View untuk test koneksi dan tipe data"""
    
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Test basic counts
            cursor.execute("SELECT COUNT(*) FROM tabel_mesin WHERE mesin IS NOT NULL")
            total_mesin = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tabel_line WHERE status = 'A'")
            active_lines = cursor.fetchone()[0]
            
            # Test join dengan berbagai metode konversi tipe
            test_results = {}
            
            # Method 1: CAST float to varchar
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_line tl
                INNER JOIN tabel_mesin tm ON CAST(tl.id_line AS varchar(10)) = tm.id_line
                WHERE tl.status = 'A' AND tm.mesin IS NOT NULL
            """)
            test_results['method_1_cast_float_to_varchar'] = cursor.fetchone()[0]
            
            # Method 2: CAST varchar to float (akan error jika varchar tidak bisa dikonversi)
            try:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM tabel_line tl
                    INNER JOIN tabel_mesin tm ON tl.id_line = TRY_CAST(tm.id_line AS float)
                    WHERE tl.status = 'A' AND tm.mesin IS NOT NULL
                """)
                test_results['method_2_cast_varchar_to_float'] = cursor.fetchone()[0]
            except:
                test_results['method_2_cast_varchar_to_float'] = 'ERROR: Cannot cast varchar to float'
            
            # Sample matched data
            cursor.execute("""
                SELECT TOP 10 
                    tl.id_line as line_id_float,
                    tl.line,
                    tm.id_line as mesin_id_line_varchar,
                    tm.mesin,
                    tm.nomer
                FROM tabel_line tl
                INNER JOIN tabel_mesin tm ON CAST(tl.id_line AS varchar(10)) = tm.id_line
                WHERE tl.status = 'A' AND tm.mesin IS NOT NULL
                ORDER BY tl.line, tm.mesin
            """)
            sample_matched_data = cursor.fetchall()
            
            response = {
                'success': True,
                'total_mesin': total_mesin,
                'active_lines': active_lines,
                'test_results': test_results,
                'sample_matched_data': [[str(x) if x is not None else '' for x in row] for row in sample_matched_data],
                'recommendation': 'Use Method 1 (CAST float to varchar) for the join'
            }
            
    except Exception as e:
        import traceback
        response = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }
    
    return JsonResponse(response)


@login_required
def get_mesin_by_line_simple(request):
    """Simplified version untuk testing"""
    
    line_id = request.GET.get('line_id', '')
    print(f"SIMPLE TEST: Received line_id = {line_id}")
    
    if not line_id:
        return JsonResponse({
            'success': False,
            'message': 'line_id kosong',
            'debug': f'Received: {request.GET}'
        })
    
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Test query sederhana dulu
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_mesin tm
                INNER JOIN tabel_line tl ON CAST(tl.id_line AS varchar(10)) = tm.id_line
                WHERE CAST(tl.id_line AS int) = %s
                    AND tl.status = 'A'
                    AND tm.mesin IS NOT NULL
            """, [int(line_id)])
            
            count = cursor.fetchone()[0]
            print(f"SIMPLE TEST: Found {count} mesins for line {line_id}")
            
            if count > 0:
                cursor.execute("""
                    SELECT tm.id_mesin, tm.mesin, tm.nomer
                    FROM tabel_mesin tm
                    INNER JOIN tabel_line tl ON CAST(tl.id_line AS varchar(10)) = tm.id_line
                    WHERE CAST(tl.id_line AS int) = %s
                        AND tl.status = 'A'
                        AND tm.mesin IS NOT NULL
                    ORDER BY tm.mesin
                """, [int(line_id)])
                
                mesins = cursor.fetchall()
                mesin_list = []
                
                for mesin in mesins:
                    display_name = mesin[1]
                    if mesin[2]:  # jika ada nomer
                        display_name += f" ({mesin[2]})"
                    
                    mesin_list.append({
                        'id': str(int(mesin[0])),
                        'text': display_name
                    })
                
                return JsonResponse({
                    'success': True,
                    'mesins': mesin_list,
                    'message': f'Found {len(mesin_list)} mesins',
                    'debug': f'line_id={line_id}, count={count}'
                })
            else:
                return JsonResponse({
                    'success': True,
                    'mesins': [],
                    'message': 'No mesins found',
                    'debug': f'line_id={line_id}, count=0'
                })
                
    except Exception as e:
        print(f"SIMPLE TEST ERROR: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Database error',
            'debug': f'line_id={line_id}'
        })
    
@login_required
def update_pengajuan_status(request):
    """AJAX view untuk update status pengajuan"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            history_id = str(data.get('history_id', '')).strip()
            new_status = str(data.get('status', '')).strip()
            
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    UPDATE tabel_pengajuan 
                    SET status = %s
                    WHERE history_id = %s
                """, [new_status, history_id])
            
            return JsonResponse({
                'success': True,
                'message': f'Status pengajuan {history_id} berhasil diubah'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# Tambahkan ke wo_maintenance_app/views.py - AJAX VIEWS untuk Review System

@login_required
def get_pending_review_count(request):
    """
    AJAX view untuk mendapatkan jumlah pengajuan yang pending review
    UPDATED: Check dengan status B/N
    """
    if not is_reviewer_fixed(request):
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    try:
        initialize_review_data()
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # UPDATED: Query dengan status B dan approve N
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_pengajuan 
                WHERE status = %s AND approve = %s 
                    AND (review_status IS NULL OR review_status = '0')
            """, [STATUS_APPROVED, APPROVE_YES])
            count = cursor.fetchone()[0] or 0
            
            employee_data = get_employee_data_for_request_fixed(request)
            reviewer_name = employee_data.get('fullname', REVIEWER_FULLNAME) if employee_data else REVIEWER_FULLNAME
            
            return JsonResponse({
                'success': True,
                'count': count,
                'reviewer': reviewer_name,
                'status_info': {
                    'status_approved': STATUS_APPROVED,   # B
                    'approve_yes': APPROVE_YES            # N
                }
            })
            
    except Exception as e:
        logger.error(f"Error getting pending review count: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def force_review_initialization(request):
    """
    Force initialize review system untuk SITI FATIMAH
    FIXED: dengan status A dan approve Y
    """
    if not is_reviewer(request.user):
        return JsonResponse({'error': 'Unauthorized - Only SITI FATIMAH can access this'}, status=403)
    
    try:
        success = initialize_review_data()
        
        if success:
            with connections['DB_Maintenance'].cursor() as cursor:
                # FIXED: Get count of ready pengajuan dengan status A dan approve Y
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = %s AND approve = %s 
                        AND review_status = '0'
                """, [STATUS_APPROVED, APPROVE_YES])
                ready_count = cursor.fetchone()[0]
                
                return JsonResponse({
                    'success': True,
                    'ready_for_review_count': ready_count,
                    'message': f'Successfully initialized review system. {ready_count} pengajuan ready for review (status=A, approve=Y).',
                    'status_info': {
                        'status_approved': STATUS_APPROVED,
                        'approve_yes': APPROVE_YES
                    }
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to initialize review system. Check logs for details.'
            })
            
    except Exception as e:
        logger.error(f"Error in force review initialization: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@reviewer_required
def quick_review_stats(request):
    """
    AJAX view untuk statistik review cepat
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Pending review count
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_pengajuan 
                WHERE status = '1' AND approve = '1' 
                    AND (review_status IS NULL OR review_status = '0')
            """)
            pending_count = cursor.fetchone()[0] or 0
            
            # Reviewed today
            today = timezone.now().date()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_pengajuan 
                WHERE reviewed_by = %s 
                    AND CAST(review_date AS DATE) = %s
            """, [REVIEWER_EMPLOYEE_NUMBER, today])
            reviewed_today = cursor.fetchone()[0] or 0
            
            # Total reviewed this month
            month_start = today.replace(day=1)
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_pengajuan 
                WHERE reviewed_by = %s 
                    AND CAST(review_date AS DATE) >= %s
            """, [REVIEWER_EMPLOYEE_NUMBER, month_start])
            reviewed_month = cursor.fetchone()[0] or 0
            
            return JsonResponse({
                'success': True,
                'stats': {
                    'pending_review': pending_count,
                    'reviewed_today': reviewed_today,
                    'reviewed_month': reviewed_month,
                    'reviewer': REVIEWER_FULLNAME
                }
            })
            
    except Exception as e:
        logger.error(f"Error getting review stats: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


# ===== UTILITY FUNCTIONS =====

def check_and_setup_review_system():
    """
    Function untuk memastikan review system sudah setup dengan benar
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Check if review columns exist
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = 'review_status'
            """)
            
            review_column_exists = cursor.fetchone()[0] > 0
            
            if not review_column_exists:
                logger.warning("Review system not setup. Please run: python manage.py setup_review_system")
                return False
            
            # Initialize approved pengajuan if needed
            cursor.execute("""
                UPDATE tabel_pengajuan 
                SET review_status = '0'
                WHERE status = '1' AND approve = '1' 
                    AND (review_status IS NULL OR review_status = '')
            """)
            
            updated_count = cursor.rowcount
            if updated_count > 0:
                logger.info(f"Auto-initialized {updated_count} approved pengajuan for review")
            
            return True
            
    except Exception as e:
        logger.error(f"Error checking review system setup: {e}")
        return False


@login_required
def debug_review_flow(request, history_id):
    """
    Debug view untuk mengecek flow review pengajuan tertentu
    SUPERUSER ONLY
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Get pengajuan details
            cursor.execute("""
                SELECT 
                    history_id, oleh, status, approve, 
                    review_status, reviewed_by, review_date,
                    tgl_insert, final_section_id
                FROM tabel_pengajuan 
                WHERE history_id = %s
            """, [history_id])
            
            pengajuan_data = cursor.fetchone()
            
            if not pengajuan_data:
                return JsonResponse({'error': 'Pengajuan not found'})
            
            # Get approval logs
            cursor.execute("""
                SELECT approver_user, action, tgl_approval, keterangan
                FROM tabel_approval_log 
                WHERE history_id = %s
                ORDER BY tgl_approval DESC
            """, [history_id])
            
            approval_logs = cursor.fetchall()
            
            # Get review logs
            cursor.execute("""
                SELECT reviewer_employee, action, review_date, review_notes
                FROM tabel_review_log 
                WHERE history_id = %s
                ORDER BY review_date DESC
            """, [history_id])
            
            review_logs = cursor.fetchall()
            
            debug_info = {
                'pengajuan': {
                    'history_id': pengajuan_data[0],
                    'oleh': pengajuan_data[1],
                    'status': pengajuan_data[2],
                    'approve': pengajuan_data[3],
                    'review_status': pengajuan_data[4],
                    'reviewed_by': pengajuan_data[5],
                    'review_date': pengajuan_data[6].isoformat() if pengajuan_data[6] else None,
                    'tgl_insert': pengajuan_data[7].isoformat() if pengajuan_data[7] else None,
                    'final_section_id': pengajuan_data[8]
                },
                'approval_logs': [
                    {
                        'approver': log[0],
                        'action': log[1],
                        'date': log[2].isoformat() if log[2] else None,
                        'keterangan': log[3]
                    } for log in approval_logs
                ],
                'review_logs': [
                    {
                        'reviewer': log[0],
                        'action': log[1],
                        'date': log[2].isoformat() if log[2] else None,
                        'notes': log[3]
                    } for log in review_logs
                ],
                'flow_analysis': {
                    'is_approved': pengajuan_data[2] == '1' and pengajuan_data[3] == '1',
                    'ready_for_review': (
                        pengajuan_data[2] == '1' and 
                        pengajuan_data[3] == '1' and 
                        (pengajuan_data[4] is None or pengajuan_data[4] == '0')
                    ),
                    'has_been_reviewed': pengajuan_data[4] in ['1', '2'],
                    'review_completed': pengajuan_data[5] == REVIEWER_EMPLOYEE_NUMBER
                }
            }
            
            return JsonResponse({'success': True, 'debug_info': debug_info})
            
    except Exception as e:
        logger.error(f"Error in debug review flow: {e}")
        return JsonResponse({'success': False, 'error': str(e)})
    
@login_required
def ajax_get_sdbm_supervisors(request):
    """
    AJAX view untuk mendapatkan supervisor SDBM berdasarkan target section
    """
    if not is_reviewer(request.user):
        return JsonResponse({'error': 'Unauthorized - Only SITI FATIMAH can access this'}, status=403)
    
    target_section = request.GET.get('target_section', '').strip()
    
    if not target_section:
        return JsonResponse({
            'success': False,
            'error': 'Target section required',
            'supervisors': []
        })
    
    try:
        from wo_maintenance_app.utils import get_sdbm_supervisors_by_section_mapping, get_sdbm_section_mapping
        
        # Get supervisors
        supervisors = get_sdbm_supervisors_by_section_mapping(target_section)
        section_mapping = get_sdbm_section_mapping()
        section_info = section_mapping.get(target_section, {})
        
        # Format supervisor data untuk frontend
        supervisor_list = []
        for supervisor in supervisors:
            supervisor_list.append({
                'employee_number': supervisor['employee_number'],
                'fullname': supervisor['fullname'],
                'nickname': supervisor['nickname'],
                'title_name': supervisor['title_name'],
                'department_name': supervisor['department_name'],
                'section_name': supervisor['section_name'],
                'level_description': supervisor['level_description'],
                'level': supervisor['level'],
                'is_manager': supervisor['is_manager'],
                'is_supervisor': supervisor['is_supervisor']
            })
        
        return JsonResponse({
            'success': True,
            'target_section': target_section,
            'section_info': {
                'display_name': section_info.get('display_name', target_section),
                'department_name': section_info.get('department_name'),
                'section_name': section_info.get('section_name')
            },
            'supervisors': supervisor_list,
            'supervisor_count': len(supervisor_list),
            'message': f'Found {len(supervisor_list)} supervisors for {section_info.get("display_name", target_section)}'
        })
        
    except Exception as e:
        logger.error(f"Error getting SDBM supervisors for {target_section}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'supervisors': [],
            'supervisor_count': 0
        })

@login_required
def ajax_validate_sdbm_section(request):
    """
    AJAX view untuk validasi SDBM section mapping
    """
    if not is_reviewer(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    target_section = request.GET.get('target_section', '').strip()
    
    try:
        from wo_maintenance_app.utils import validate_sdbm_section_mapping, get_sdbm_section_mapping
        
        if target_section:
            # Validate specific section
            section_mapping = get_sdbm_section_mapping()
            section_info = section_mapping.get(target_section)
            
            if not section_info:
                return JsonResponse({
                    'success': False,
                    'valid': False,
                    'error': f'Unknown target section: {target_section}',
                    'section_info': None
                })
            
            # Check SDBM for this specific section
            with connections['SDBM'].cursor() as cursor:
                department_name = section_info['department_name']
                section_name = section_info['section_name']
                
                # Check department exists
                cursor.execute("""
                    SELECT COUNT(*) FROM [hr].[department] 
                    WHERE UPPER(name) = UPPER(%s) AND (is_active IS NULL OR is_active = 1)
                """, [department_name])
                dept_exists = cursor.fetchone()[0] > 0
                
                # Check section exists
                cursor.execute("""
                    SELECT COUNT(*) FROM [hr].[section] 
                    WHERE UPPER(name) = UPPER(%s) AND (is_active IS NULL OR is_active = 1)
                """, [section_name])
                section_exists = cursor.fetchone()[0] > 0
                
                # Count supervisors
                supervisor_count = 0
                if dept_exists and section_exists:
                    from wo_maintenance_app.utils import get_sdbm_supervisors_by_section_mapping
                    supervisors = get_sdbm_supervisors_by_section_mapping(target_section)
                    supervisor_count = len(supervisors)
                
                return JsonResponse({
                    'success': True,
                    'valid': dept_exists and section_exists,
                    'target_section': target_section,
                    'section_info': section_info,
                    'validation': {
                        'department_exists': dept_exists,
                        'section_exists': section_exists,
                        'supervisor_count': supervisor_count
                    },
                    'message': f'Validation complete for {section_info["display_name"]}'
                })
        
        else:
            # Validate all sections
            validation_result = validate_sdbm_section_mapping()
            return JsonResponse({
                'success': True,
                'validation_result': validation_result,
                'message': 'Full SDBM validation complete'
            })
        
    except Exception as e:
        logger.error(f"Error validating SDBM section {target_section}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'valid': False
        })   

@login_required
def ajax_sdbm_assignment_status(request):
    """
    AJAX view untuk mendapatkan status assignment SDBM user
    """
    try:
        user_hierarchy = get_employee_hierarchy_data(request.user)
        
        if not user_hierarchy:
            return JsonResponse({
                'success': False,
                'error': 'Employee data not found',
                'assignments': []
            })
        
        from wo_maintenance_app.utils import get_assigned_pengajuan_for_sdbm_user
        
        employee_number = user_hierarchy.get('employee_number')
        assignments = get_assigned_pengajuan_for_sdbm_user(employee_number)
        
        # Format assignment data
        assignment_list = []
        for assignment in assignments:
            if isinstance(assignment, dict):
                assignment_list.append({
                    'history_id': assignment.get('history_id'),
                    'assignment_type': assignment.get('assignment_type'),
                    'target_section': assignment.get('target_section'),
                    'department_name': assignment.get('department_name'),
                    'section_name': assignment.get('section_name'),
                    'assignment_date': assignment.get('assignment_date').isoformat() if assignment.get('assignment_date') else None
                })
        
        return JsonResponse({
            'success': True,
            'employee_number': employee_number,
            'assignments': assignment_list,
            'assignment_count': len(assignment_list),
            'message': f'Found {len(assignment_list)} SDBM assignments'
        })
        
    except Exception as e:
        logger.error(f"Error getting SDBM assignment status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'assignments': []
        })


@login_required
def sdbm_supervisor_lookup(request, target_section):
    """
    Detailed supervisor lookup untuk target section
    """
    if not is_reviewer(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        from wo_maintenance_app.utils import get_sdbm_supervisors_by_section_mapping, get_sdbm_section_mapping
        
        # Get section mapping
        section_mapping = get_sdbm_section_mapping()
        section_info = section_mapping.get(target_section, {})
        
        if not section_info:
            return JsonResponse({
                'success': False,
                'error': f'Unknown target section: {target_section}',
                'supervisors': []
            })
        
        # Get supervisors dengan detail lengkap
        supervisors = get_sdbm_supervisors_by_section_mapping(target_section)
        
        # Enhanced supervisor info
        enhanced_supervisors = []
        for supervisor in supervisors:
            enhanced_supervisors.append({
                'employee_number': supervisor['employee_number'],
                'fullname': supervisor['fullname'],
                'nickname': supervisor['nickname'],
                'title_name': supervisor['title_name'],
                'department_name': supervisor['department_name'],
                'section_name': supervisor['section_name'],
                'level': supervisor['level'],
                'level_description': supervisor['level_description'],
                'is_manager': supervisor['is_manager'],
                'is_supervisor': supervisor['is_supervisor'],
                'is_general_manager': supervisor['is_general_manager'],
                'is_bod': supervisor['is_bod'],
                'job_status': supervisor.get('job_status'),
                'management_level': (
                    'BOD' if supervisor['is_bod'] else
                    'General Manager' if supervisor['is_general_manager'] else
                    'Manager' if supervisor['is_manager'] else
                    'Supervisor' if supervisor['is_supervisor'] else
                    'Staff'
                )
            })
        
        # Sort by level (highest first)
        enhanced_supervisors.sort(key=lambda x: x['level'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'target_section': target_section,
            'section_info': section_info,
            'supervisors': enhanced_supervisors,
            'supervisor_count': len(enhanced_supervisors),
            'summary': {
                'total_supervisors': len(enhanced_supervisors),
                'managers': len([s for s in enhanced_supervisors if s['is_manager']]),
                'supervisors': len([s for s in enhanced_supervisors if s['is_supervisor'] and not s['is_manager']]),
                'general_managers': len([s for s in enhanced_supervisors if s['is_general_manager']]),
                'bods': len([s for s in enhanced_supervisors if s['is_bod']])
            }
        })
        
    except Exception as e:
        logger.error(f"Error in supervisor lookup for {target_section}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'supervisors': []
        })


@login_required
def sdbm_assignment_preview(request):
    """
    Preview assignment yang akan dibuat untuk pengajuan tertentu
    """
    if not is_reviewer(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    history_id = request.GET.get('history_id', '').strip()
    target_section = request.GET.get('target_section', '').strip()
    
    if not history_id or not target_section:
        return JsonResponse({
            'success': False,
            'error': 'history_id and target_section required',
            'preview': None
        })
    
    try:
        from wo_maintenance_app.utils import get_sdbm_supervisors_by_section_mapping, get_sdbm_section_mapping, get_maintenance_section_id_from_target
        
        # Get section info
        section_mapping = get_sdbm_section_mapping()
        section_info = section_mapping.get(target_section, {})
        
        # Get maintenance section ID yang akan diupdate
        new_section_id = get_maintenance_section_id_from_target(target_section)
        
        # Get supervisors yang akan receive assignment
        supervisors = get_sdbm_supervisors_by_section_mapping(target_section, exclude_employee_numbers=[REVIEWER_EMPLOYEE_NUMBER])
        
        # Check existing assignments
        existing_assignments = []
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT assigned_to_employee, assignment_date, notes
                    FROM tabel_pengajuan_assignment
                    WHERE history_id = %s AND is_active = 1
                """, [history_id])
                
                existing_assignments = [
                    {
                        'employee_number': row[0],
                        'assignment_date': row[1].isoformat() if row[1] else None,
                        'notes': row[2]
                    } for row in cursor.fetchall()
                ]
        except Exception:
            # Table mungkin belum ada
            pass
        
        # Build preview
        preview = {
            'history_id': history_id,
            'target_section': target_section,
            'section_info': section_info,
            'changes': {
                'section_id_update': {
                    'will_update': new_section_id is not None,
                    'new_section_id': new_section_id,
                    'description': f'Section tujuan akan diperbarui ke ID {new_section_id}' if new_section_id else 'Section tujuan tidak akan diubah'
                },
                'assignments': {
                    'will_create': len(supervisors) > 0,
                    'supervisor_count': len(supervisors),
                    'supervisors': [
                        {
                            'employee_number': s['employee_number'],
                            'fullname': s['fullname'],
                            'title_name': s['title_name'],
                            'level_description': s['level_description']
                        } for s in supervisors[:5]  # Show first 5
                    ],
                    'existing_assignments': existing_assignments
                }
            },
            'warnings': []
        }
        
        # Add warnings
        if len(supervisors) == 0:
            preview['warnings'].append('Tidak ada supervisor ditemukan untuk auto-assignment')
        
        if len(existing_assignments) > 0:
            preview['warnings'].append(f'Sudah ada {len(existing_assignments)} assignment aktif')
        
        if not new_section_id:
            preview['warnings'].append('Section ID tidak dapat ditentukan dari target section')
        
        return JsonResponse({
            'success': True,
            'preview': preview,
            'message': f'Preview generated for {history_id} -> {target_section}'
        })
        
    except Exception as e:
        logger.error(f"Error generating assignment preview: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'preview': None
        })


# ===== ENHANCED DEBUG VIEWS untuk SDBM =====

@login_required
def debug_sdbm_mapping(request):
    """
    Debug view untuk SDBM section mapping - SUPERUSER ONLY
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        from .utils import get_sdbm_section_mapping, validate_sdbm_section_mapping
        
        # Get mapping dan validation
        section_mapping = get_sdbm_section_mapping()
        validation = validate_sdbm_section_mapping()
        
        # Test SDBM connection
        sdbm_test = {}
        try:
            with connections['SDBM'].cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM [hrbp].[employees] WHERE is_active = 1")
                sdbm_test['active_employees'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM [hr].[department]")
                sdbm_test['total_departments'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM [hr].[section]")
                sdbm_test['total_sections'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM [hr].[title] WHERE is_supervisor = 1 OR is_manager = 1")
                sdbm_test['supervisor_titles'] = cursor.fetchone()[0]
                
                sdbm_test['connection'] = 'OK'
                
        except Exception as sdbm_error:
            sdbm_test['connection'] = 'ERROR'
            sdbm_test['error'] = str(sdbm_error)
        
        debug_info = {
            'timestamp': timezone.now().isoformat(),
            'section_mapping': section_mapping,
            'validation_result': validation,
            'sdbm_connection_test': sdbm_test,
            'summary': {
                'total_sections': len(section_mapping),
                'valid_sections': len([s for s in validation['found_supervisors'].keys() if validation['found_supervisors'][s]['count'] > 0]),
                'total_supervisors': sum([validation['found_supervisors'][s]['count'] for s in validation['found_supervisors']]),
                'missing_departments': len(validation.get('missing_departments', [])),
                'missing_sections': len(validation.get('missing_sections', []))
            }
        }
        
        return JsonResponse(debug_info, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@login_required
def debug_sdbm_employees(request, target_section):
    """
    Debug view untuk employees di target section - SUPERUSER ONLY
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        from wo_maintenance_app.utils import get_sdbm_section_mapping
        
        section_mapping = get_sdbm_section_mapping()
        section_info = section_mapping.get(target_section, {})
        
        if not section_info:
            return JsonResponse({
                'error': f'Unknown target section: {target_section}',
                'available_sections': list(section_mapping.keys())
            })
        
        department_name = section_info['department_name']
        section_name = section_info['section_name']
        
        employees_data = {}
        
        with connections['SDBM'].cursor() as cursor:
            # Get all employees di department/section
            cursor.execute("""
                SELECT 
                    e.employee_number,
                    e.fullname,
                    e.nickname,
                    t.Name as title_name,
                    t.is_supervisor,
                    t.is_manager,
                    t.is_generalManager,
                    t.is_bod,
                    d.name as department_name,
                    s.name as section_name,
                    e.job_status,
                    e.is_active
                FROM [hrbp].[employees] e
                INNER JOIN [hrbp].[position] p ON e.id = p.employeeId
                LEFT JOIN [hr].[department] d ON p.departmentId = d.id
                LEFT JOIN [hr].[section] s ON p.sectionId = s.id
                LEFT JOIN [hr].[title] t ON p.titleId = t.id
                WHERE UPPER(d.name) = UPPER(%s)
                    AND UPPER(s.name) = UPPER(%s)
                    AND e.is_active = 1
                    AND p.is_active = 1
                ORDER BY 
                    CASE 
                        WHEN t.is_bod = 1 THEN 1
                        WHEN t.is_generalManager = 1 THEN 2
                        WHEN t.is_manager = 1 THEN 3
                        WHEN t.is_supervisor = 1 THEN 4
                        ELSE 5
                    END,
                    e.fullname
            """, [department_name, section_name])
            
            all_employees = []
            supervisors = []
            staff = []
            
            for row in cursor.fetchall():
                employee = {
                    'employee_number': row[0],
                    'fullname': row[1],
                    'nickname': row[2],
                    'title_name': row[3],
                    'is_supervisor': row[4],
                    'is_manager': row[5],
                    'is_general_manager': row[6],
                    'is_bod': row[7],
                    'department_name': row[8],
                    'section_name': row[9],
                    'job_status': row[10],
                    'is_active': row[11]
                }
                
                all_employees.append(employee)
                
                # Categorize
                if employee['is_supervisor'] or employee['is_manager'] or employee['is_general_manager'] or employee['is_bod']:
                    supervisors.append(employee)
                else:
                    staff.append(employee)
        
        employees_data = {
            'target_section': target_section,
            'section_info': section_info,
            'query_params': {
                'department_name': department_name,
                'section_name': section_name
            },
            'statistics': {
                'total_employees': len(all_employees),
                'total_supervisors': len(supervisors),
                'total_staff': len(staff),
                'managers': len([e for e in supervisors if e['is_manager']]),
                'supervisors_only': len([e for e in supervisors if e['is_supervisor'] and not e['is_manager']]),
                'general_managers': len([e for e in supervisors if e['is_general_manager']]),
                'bods': len([e for e in supervisors if e['is_bod']])
            },
            'employees': {
                'all': all_employees,
                'supervisors': supervisors,
                'staff': staff
            }
        }
        
        return JsonResponse(employees_data, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)

# wo_maintenance_app/views.py - ADD test review button view

@login_required
def test_review_button_visibility(request):
    """
    Test view untuk debug review button visibility untuk SITI FATIMAH
    ONLY for debugging purposes
    """
    if not request.user.is_superuser and request.user.username != '007522':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        from wo_maintenance_app.utils import (
            get_employee_hierarchy_data, 
            REVIEWER_EMPLOYEE_NUMBER, 
            STATUS_APPROVED, 
            APPROVE_YES,
            initialize_review_data
        )
        
        debug_info = {
            'timestamp': timezone.now().isoformat(),
            'user': {
                'username': request.user.username,
                'is_superuser': request.user.is_superuser,
                'is_authenticated': request.user.is_authenticated
            },
            'siti_detection': {},
            'pengajuan_data': {},
            'template_simulation': {},
            'recommendations': []
        }
        
        # 1. Test SITI FATIMAH detection
        user_hierarchy = get_employee_hierarchy_data(request.user)
        
        if user_hierarchy:
            is_siti_fatimah = (
                user_hierarchy.get('employee_number') == REVIEWER_EMPLOYEE_NUMBER or 
                request.user.username == REVIEWER_EMPLOYEE_NUMBER or
                request.user.username == '007522'
            )
            
            debug_info['siti_detection'] = {
                'user_hierarchy_found': True,
                'employee_number': user_hierarchy.get('employee_number'),
                'expected_employee_number': REVIEWER_EMPLOYEE_NUMBER,
                'username': request.user.username,
                'is_siti_fatimah': is_siti_fatimah,
                'fullname': user_hierarchy.get('fullname'),
                'department': user_hierarchy.get('department_name'),
                'title': user_hierarchy.get('title_name')
            }
        else:
            debug_info['siti_detection'] = {
                'user_hierarchy_found': False,
                'error': 'No SDBM employee data found'
            }
            debug_info['recommendations'].append('Check SDBM database connection and employee data')
        
        # 2. Check pengajuan data
        with connections['DB_Maintenance'].cursor() as cursor:
            # Check review columns
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = 'review_status'
            """)
            review_column_exists = cursor.fetchone()[0] > 0
            
            # Initialize review data if needed
            if review_column_exists:
                initialized = initialize_review_data()
                debug_info['review_initialization'] = initialized
            else:
                debug_info['review_initialization'] = False
                debug_info['recommendations'].append('Run: python manage.py setup_review_system')
            
            # Get pengajuan counts
            cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan")
            total_pengajuan = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE status = %s AND approve = %s", 
                         [STATUS_APPROVED, APPROVE_YES])
            fully_approved = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_pengajuan 
                WHERE status = %s AND approve = %s 
                    AND (review_status IS NULL OR review_status = '0')
            """, [STATUS_APPROVED, APPROVE_YES])
            pending_review = cursor.fetchone()[0]
            
            debug_info['pengajuan_data'] = {
                'total_pengajuan': total_pengajuan,
                'fully_approved': fully_approved,
                'pending_review': pending_review,
                'review_column_exists': review_column_exists,
                'constants': {
                    'STATUS_APPROVED': STATUS_APPROVED,
                    'APPROVE_YES': APPROVE_YES
                }
            }
            
            # Get sample pengajuan for template simulation
            if fully_approved > 0:
                cursor.execute("""
                    SELECT TOP 5 
                        history_id,                    -- 0
                        oleh,                          -- 1
                        'N/A',                         -- 2 (mesin placeholder)
                        'N/A',                         -- 3 (section placeholder)
                        'N/A',                         -- 4 (pekerjaan placeholder)
                        LEFT(deskripsi_perbaikan, 50), -- 5
                        status,                        -- 6
                        tgl_insert,                    -- 7
                        user_insert,                   -- 8
                        number_wo,                     -- 9
                        'N/A',                         -- 10 (line placeholder)
                        approve,                       -- 11
                        tgl_his,                       -- 12
                        jam_his,                       -- 13
                        status_pekerjaan,              -- 14
                        ISNULL(review_status, '0'),    -- 15
                        reviewed_by,                   -- 16
                        review_date,                   -- 17
                        'N/A',                         -- 18 (final_section placeholder)
                        'TEST'                         -- 19 (access_type)
                    FROM tabel_pengajuan 
                    WHERE status = %s AND approve = %s
                    ORDER BY tgl_insert DESC
                """, [STATUS_APPROVED, APPROVE_YES])
                
                sample_pengajuan = cursor.fetchall()
                
                # 3. Template simulation
                template_results = []
                for pengajuan in sample_pengajuan:
                    # Simulate template conditions
                    is_siti = debug_info['siti_detection'].get('is_siti_fatimah', False)
                    status = pengajuan[6]
                    approve = pengajuan[11]
                    review_status = pengajuan[15]
                    
                    # Primary condition: SITI FATIMAH + approved + not reviewed
                    should_show_review = (
                        is_siti and 
                        status == 'A' and 
                        approve == 'Y' and 
                        (review_status == '0' or review_status is None)
                    )
                    
                    template_results.append({
                        'history_id': pengajuan[0],
                        'oleh': pengajuan[1],
                        'status': status,
                        'approve': approve,
                        'review_status': review_status,
                        'should_show_review_button': should_show_review,
                        'conditions': {
                            'is_siti_fatimah': is_siti,
                            'status_approved': status == 'A',
                            'approve_yes': approve == 'Y',
                            'review_pending': review_status == '0' or review_status is None
                        }
                    })
                
                debug_info['template_simulation'] = {
                    'sample_count': len(template_results),
                    'review_buttons_should_show': len([r for r in template_results if r['should_show_review_button']]),
                    'sample_results': template_results
                }
                
                # Generate recommendations
                if debug_info['siti_detection'].get('is_siti_fatimah'):
                    if pending_review > 0:
                        buttons_should_show = len([r for r in template_results if r['should_show_review_button']])
                        if buttons_should_show > 0:
                            debug_info['recommendations'].append(f'✅ SUCCESS: {buttons_should_show} review buttons should appear')
                        else:
                            debug_info['recommendations'].append('❌ ERROR: Review buttons should appear but conditions not met')
                    else:
                        debug_info['recommendations'].append('⚠️ WARNING: No pengajuan pending review')
                else:
                    debug_info['recommendations'].append('❌ ERROR: SITI FATIMAH not detected properly')
            else:
                debug_info['template_simulation'] = {
                    'error': 'No approved pengajuan found for simulation'
                }
                debug_info['recommendations'].append('Create some approved pengajuan first')
        
        # 4. Action URLs test
        try:
            from django.urls import reverse
            debug_info['urls'] = {
                'review_dashboard': reverse('wo_maintenance_app:review_dashboard'),
                'review_pengajuan_list': reverse('wo_maintenance_app:review_pengajuan_list'),
                'enhanced_daftar_laporan': reverse('wo_maintenance_app:enhanced_daftar_laporan'),
            }
            
            # Test specific review detail URL if we have a sample
            if debug_info['template_simulation'].get('sample_results'):
                sample_id = debug_info['template_simulation']['sample_results'][0]['history_id']
                debug_info['urls']['sample_review_detail'] = reverse('wo_maintenance_app:review_pengajuan_detail', args=[sample_id])
        except Exception as url_error:
            debug_info['urls'] = {'error': str(url_error)}
        
        # 5. Final recommendation
        if debug_info['recommendations']:
            debug_info['summary'] = 'Issues found - see recommendations'
        else:
            debug_info['summary'] = 'All checks passed - review buttons should work'
        
        return JsonResponse(debug_info, indent=2)
        
    except Exception as e:
        logger.error(f"Error in test_review_button_visibility: {e}")
        import traceback
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@login_required  
def quick_fix_review_system(request):
    """
    Quick fix untuk review system - SUPERUSER or SITI FATIMAH only
    """
    if not (request.user.is_superuser or request.user.username == '007522'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        from wo_maintenance_app.utils import initialize_review_data, ensure_review_tables_exist
        
        fix_results = {
            'timestamp': timezone.now().isoformat(),
            'fixes_applied': [],
            'errors': []
        }
        
        # 1. Ensure review tables exist
        try:
            table_result = ensure_review_tables_exist()
            if table_result:
                fix_results['fixes_applied'].append('Review tables verified/created')
            else:
                fix_results['errors'].append('Failed to create review tables')
        except Exception as table_error:
            fix_results['errors'].append(f'Table creation error: {table_error}')
        
        # 2. Initialize review data
        try:
            init_result = initialize_review_data()
            if init_result:
                fix_results['fixes_applied'].append('Review data initialized')
            else:
                fix_results['errors'].append('Failed to initialize review data')
        except Exception as init_error:
            fix_results['errors'].append(f'Data initialization error: {init_error}')
        
        # 3. Check current status
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                from wo_maintenance_app.utils import STATUS_APPROVED, APPROVE_YES
                
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = %s AND approve = %s 
                        AND (review_status IS NULL OR review_status = '0')
                """, [STATUS_APPROVED, APPROVE_YES])
                
                pending_count = cursor.fetchone()[0]
                fix_results['current_status'] = {
                    'pending_review_count': pending_count,
                    'ready_for_siti': pending_count > 0
                }
                
                if pending_count > 0:
                    fix_results['fixes_applied'].append(f'Found {pending_count} pengajuan ready for review')
                
        except Exception as status_error:
            fix_results['errors'].append(f'Status check error: {status_error}')
        
        # 4. Final verification
        if len(fix_results['errors']) == 0:
            fix_results['success'] = True
            fix_results['message'] = 'Quick fix completed successfully'
        else:
            fix_results['success'] = False
            fix_results['message'] = f'Quick fix completed with {len(fix_results["errors"])} errors'
        
        return JsonResponse(fix_results, indent=2)
        
    except Exception as e:
        logger.error(f"Error in quick_fix_review_system: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
@login_required
def enhanced_pengajuan_detail(request, nomor_pengajuan):
    """
    Enhanced detail pengajuan dengan SDBM integration dan review info
    FIXED: Sebelumnya missing, sekarang added untuk redirect compatibility
    """
    try:
        # ===== AMBIL DATA HIERARCHY USER =====
        user_hierarchy = get_employee_hierarchy_data(request.user)
        
        if not user_hierarchy:
            messages.error(request, 'Data karyawan tidak ditemukan. Hubungi administrator.')
            return redirect('wo_maintenance_app:daftar_laporan')
        
        # ===== CEK APAKAH USER ADALAH SITI FATIMAH =====
        is_siti_fatimah = is_siti_fatimah_user(request.user)
        
        # ===== AMBIL DATA PENGAJUAN dengan Enhanced Info =====
        pengajuan = None
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        tp.history_id,
                        tp.number_wo,
                        tp.tgl_insert,
                        tp.oleh,
                        tp.user_insert,
                        tmes.mesin,
                        tms.seksi as section_tujuan,
                        tpek.pekerjaan,
                        tp.deskripsi_perbaikan,
                        tp.status,
                        tp.approve,
                        tl.line as line_name,
                        tp.tgl_his,
                        tp.jam_his,
                        tp.status_pekerjaan,
                        tp.review_status,
                        tp.reviewed_by,
                        tp.review_date,
                        tp.review_notes,
                        tp.final_section_id,
                        final_section.seksi as final_section_name
                    FROM tabel_pengajuan tp
                    LEFT JOIN tabel_mesin tmes ON tp.id_mesin = tmes.id_mesin
                    LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
                    LEFT JOIN tabel_msection tms ON tp.id_section = tms.id_section
                    LEFT JOIN tabel_pekerjaan tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
                    LEFT JOIN tabel_msection final_section ON tp.final_section_id = final_section.id_section
                    WHERE tp.history_id = %s
                """, [nomor_pengajuan])
                
                row = cursor.fetchone()
                
                if not row:
                    messages.error(request, 'Pengajuan tidak ditemukan.')
                    return redirect('wo_maintenance_app:daftar_laporan')
                
                pengajuan = {
                    'history_id': row[0],
                    'number_wo': row[1],
                    'tgl_insert': row[2],
                    'oleh': row[3],
                    'user_insert': row[4],
                    'mesin': row[5],
                    'section_tujuan': row[6],
                    'pekerjaan': row[7],
                    'deskripsi_perbaikan': row[8],
                    'status': row[9],
                    'approve': row[10],
                    'line_name': row[11],
                    'tgl_his': row[12],
                    'jam_his': row[13],
                    'status_pekerjaan': row[14],
                    'review_status': row[15],
                    'reviewed_by': row[16],
                    'review_date': row[17],
                    'review_notes': row[18],
                    'final_section_id': row[19],
                    'final_section_name': row[20]
                }
                
        except Exception as db_error:
            logger.error(f"Database error in enhanced_pengajuan_detail: {db_error}")
            messages.error(request, 'Terjadi kesalahan saat mengambil data pengajuan.')
            return redirect('wo_maintenance_app:daftar_laporan')
        
        # ===== CEK AKSES PERMISSION =====
        can_view = False
        
        if is_siti_fatimah:
            # SITI FATIMAH dapat melihat semua pengajuan
            can_view = True
        else:
            # User lain: cek hierarchy dan assignment
            allowed_employee_numbers = get_subordinate_employee_numbers(user_hierarchy)
            assigned_history_ids = get_assigned_pengajuan_for_user(user_hierarchy.get('employee_number'))
            
            can_view = (
                pengajuan['user_insert'] in allowed_employee_numbers or 
                pengajuan['history_id'] in assigned_history_ids
            )
        
        if not can_view:
            logger.warning(f"User {user_hierarchy.get('fullname')} tried to access unauthorized pengajuan {nomor_pengajuan}")
            messages.error(request, 'Anda tidak memiliki akses ke pengajuan ini.')
            return redirect('wo_maintenance_app:daftar_laporan')
        
        # ===== ENHANCED INFO =====
        # Check pengajuan status dengan enhanced function
        is_approved_for_review = is_pengajuan_approved_for_review(pengajuan['status'], pengajuan['approve'])
        
        # Get assignment info jika ada
        assignment_info = None
        try:
            assigned_history_ids = get_assigned_pengajuan_for_user(user_hierarchy.get('employee_number'))
            is_assigned_to_user = pengajuan['history_id'] in assigned_history_ids
            
            if is_assigned_to_user:
                with connections['DB_Maintenance'].cursor() as cursor:
                    cursor.execute("""
                        SELECT assigned_by_employee, assignment_date, notes, assignment_type
                        FROM tabel_pengajuan_assignment
                        WHERE history_id = %s AND assigned_to_employee = %s AND is_active = 1
                    """, [pengajuan['history_id'], user_hierarchy.get('employee_number')])
                    
                    assignment_row = cursor.fetchone()
                    if assignment_row:
                        assignment_info = {
                            'assigned_by': assignment_row[0],
                            'assignment_date': assignment_row[1],
                            'notes': assignment_row[2],
                            'assignment_type': assignment_row[3] or 'manual'
                        }
        except Exception as assignment_error:
            logger.error(f"Error getting assignment info: {assignment_error}")
        
        # ===== ENHANCED WORKFLOW STATUS =====
        workflow_status = {
            'submitted': True,  # Always true jika ada pengajuan
            'approved': is_approved_for_review,
            'reviewed': pengajuan['review_status'] in ['1', '2'],
            'review_approved': pengajuan['review_status'] == '1',
            'review_rejected': pengajuan['review_status'] == '2',
            'in_progress': pengajuan['status_pekerjaan'] not in [None, '0'],
            'completed': pengajuan['status_pekerjaan'] == '1'
        }
        
        # ===== CONTEXT =====
        context = {
            'pengajuan': pengajuan,
            'user_hierarchy': user_hierarchy,
            'employee_data': user_hierarchy,
            'is_siti_fatimah': is_siti_fatimah,
            'is_approved_for_review': is_approved_for_review,
            'assignment_info': assignment_info,
            'workflow_status': workflow_status,
            'can_review': is_siti_fatimah and is_approved_for_review and pengajuan['review_status'] not in ['1', '2'],
            'page_title': f'Enhanced Detail Pengajuan {nomor_pengajuan}',
            
            # Enhanced context
            'enhanced_mode': True,
            'sdbm_integration': True,
            
            # Status info untuk template
            'STATUS_APPROVED': STATUS_APPROVED,
            'APPROVE_YES': APPROVE_YES,
            'REVIEW_PENDING': REVIEW_PENDING,
            'REVIEW_APPROVED': REVIEW_APPROVED,
            'REVIEW_REJECTED': REVIEW_REJECTED
        }
        
        return render(request, 'wo_maintenance_app/enhanced_pengajuan_detail.html', context)
        
    except Exception as e:
        logger.error(f"Critical error in enhanced_pengajuan_detail: {e}")
        messages.error(request, 'Terjadi kesalahan sistem. Silakan coba lagi.')
        return redirect('wo_maintenance_app:daftar_laporan')

# ===== ADDITIONAL DEBUG VIEW untuk Status Validation =====
@login_required
def debug_status_validation(request):
    """
    Debug view untuk validate status values di database - SUPERUSER ONLY
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        validation_result = validate_status_constants()
        status_mapping = get_database_status_mapping()
        
        debug_info = {
            'timestamp': timezone.now().isoformat(),
            'constants': {
                'STATUS_APPROVED': STATUS_APPROVED,
                'APPROVE_YES': APPROVE_YES,
                'STATUS_PENDING': STATUS_PENDING,
                'APPROVE_NO': APPROVE_NO
            },
            'validation_result': validation_result,
            'database_mapping': status_mapping,
            'recommendations': []
        }
        
        # Add recommendations
        if status_mapping:
            if '1' in status_mapping['approved_status_values'] and 'A' not in status_mapping['approved_status_values']:
                debug_info['recommendations'].append('Database menggunakan status=1, pertimbangkan update constant ke STATUS_APPROVED=1')
            
            if '1' in status_mapping['approved_approve_values'] and 'Y' not in status_mapping['approved_approve_values']:
                debug_info['recommendations'].append('Database menggunakan approve=1, pertimbangkan update constant ke APPROVE_YES=1')
        
        # Test pengajuan approved check
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT TOP 5 history_id, status, approve, review_status
                FROM tabel_pengajuan 
                WHERE status IS NOT NULL AND approve IS NOT NULL
                ORDER BY tgl_insert DESC
            """)
            
            sample_pengajuan = []
            for row in cursor.fetchall():
                pengajuan_data = {
                    'history_id': row[0],
                    'status': row[1],
                    'approve': row[2],
                    'review_status': row[3],
                    'is_approved_for_review': is_pengajuan_approved_for_review(row[1], row[2])
                }
                sample_pengajuan.append(pengajuan_data)
            
            debug_info['sample_pengajuan'] = sample_pengajuan
        
        return JsonResponse(debug_info, indent=2)
        
    except Exception as e:
        logger.error(f"Error in debug_status_validation: {e}")
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)

def get_maintenance_section_mapping_for_sdbm_section(sdbm_section_id):
    """
    Helper function untuk mapping SDBM section ke maintenance section IDs
    
    Args:
        sdbm_section_id: Section ID dari SDBM
        
    Returns:
        list: List of maintenance section IDs yang sesuai
    """
    try:
        # Get section info dari SDBM
        with connections['SDBM'].cursor() as cursor:
            cursor.execute("""
                SELECT name, department_id FROM [hr].[section] 
                WHERE id = %s AND (is_active IS NULL OR is_active = 1)
            """, [sdbm_section_id])
            
            result = cursor.fetchone()
            if not result:
                return []
            
            section_name = result[0].upper()
            department_id = result[1]
            
            # Get department name
            cursor.execute("""
                SELECT name FROM [hr].[department] 
                WHERE id = %s AND (is_active IS NULL OR is_active = 1)
            """, [department_id])
            
            dept_result = cursor.fetchone()
            department_name = dept_result[0].upper() if dept_result else ""
        
        # Map berdasarkan section name dan department
        maintenance_section_ids = []
        
        # Engineering sections
        if 'ENGINEERING' in department_name:
            if 'IT' in section_name:
                maintenance_section_ids = [1]  # IT section
            elif 'ELECTRIC' in section_name or 'ELEKTRIK' in section_name:
                maintenance_section_ids = [2]  # Elektrik section
            elif 'MECHANIC' in section_name or 'MEKANIK' in section_name:
                maintenance_section_ids = [3]  # Mekanik section
            elif 'UTILITY' in section_name:
                maintenance_section_ids = [4]  # Utility section
            elif 'CIVIL' in section_name:
                maintenance_section_ids = [5]  # Civil section
        
        # Maintenance sections
        elif 'MAINTENANCE' in department_name:
            maintenance_section_ids = [6]  # General maintenance
        
        logger.debug(f"Mapped SDBM section {sdbm_section_id} ({section_name}) to maintenance sections: {maintenance_section_ids}")
        return maintenance_section_ids
        
    except Exception as e:
        logger.error(f"Error mapping SDBM section {sdbm_section_id}: {e}")
        return []
    
@login_required
def debug_section_mapping(request, sdbm_section_id):
    """
    Debug view untuk test section mapping - SUPERUSER ONLY
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        from wo_maintenance_app.utils import get_maintenance_section_mapping_for_sdbm_section
        
        # Test mapping
        maintenance_sections = get_maintenance_section_mapping_for_sdbm_section(sdbm_section_id)
        
        # Get SDBM section info
        sdbm_info = {}
        try:
            with connections['SDBM'].cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT TOP 1
                        s.name as section_name,
                        d.name as department_name,
                        s.id as section_id
                    FROM [hr].[section] s
                    INNER JOIN [hrbp].[position] p ON p.sectionId = s.id
                    INNER JOIN [hr].[department] d ON p.departmentId = d.id
                    WHERE s.id = %s 
                        AND (s.is_active IS NULL OR s.is_active = 1)
                        AND p.is_active = 1
                        AND (d.is_active IS NULL OR d.is_active = 1)
                    ORDER BY p.id DESC
                """, [sdbm_section_id])
                
                result = cursor.fetchone()
                if result:
                    sdbm_info = {
                        'section_name': result[0],
                        'department_name': result[1],
                        'section_id': result[2]
                    }
        except Exception as e:
            sdbm_info['error'] = str(e)
        
        # Check maintenance sections
        maintenance_info = []
        if maintenance_sections:
            try:
                with connections['DB_Maintenance'].cursor() as cursor:
                    placeholders = ','.join(['%s'] * len(maintenance_sections))
                    cursor.execute(f"""
                        SELECT id_section, seksi 
                        FROM tabel_msection 
                        WHERE id_section IN ({placeholders})
                    """, [float(sid) for sid in maintenance_sections])
                    
                    for row in cursor.fetchall():
                        maintenance_info.append({
                            'id_section': row[0],
                            'section_name': row[1]
                        })
            except Exception as e:
                maintenance_info = [{'error': str(e)}]
        
        # Test pengajuan count
        pengajuan_count = 0
        if maintenance_sections:
            try:
                with connections['DB_Maintenance'].cursor() as cursor:
                    placeholders = ','.join(['%s'] * len(maintenance_sections))
                    float_section_ids = [float(sid) for sid in maintenance_sections]
                    
                    cursor.execute(f"""
                        SELECT COUNT(*) 
                        FROM tabel_pengajuan 
                        WHERE (id_section IN ({placeholders}) OR final_section_id IN ({placeholders}))
                            AND status IN ('A', '1')
                            AND approve IN ('Y', '1')
                    """, float_section_ids + float_section_ids)
                    
                    pengajuan_count = cursor.fetchone()[0] or 0
            except Exception as e:
                pengajuan_count = f"Error: {e}"
        
        debug_result = {
            'sdbm_section_id': sdbm_section_id,
            'sdbm_info': sdbm_info,
            'mapped_maintenance_sections': maintenance_sections,
            'maintenance_section_details': maintenance_info,
            'accessible_pengajuan_count': pengajuan_count,
            'success': len(maintenance_sections) > 0,
            'recommendations': []
        }
        
        # Add recommendations
        if not maintenance_sections:
            debug_result['recommendations'].append('No maintenance sections mapped - check section name patterns')
        elif pengajuan_count == 0:
            debug_result['recommendations'].append('Mapping successful but no pengajuan found - check if there are approved pengajuan in those sections')
        else:
            debug_result['recommendations'].append(f'SUCCESS: {pengajuan_count} pengajuan should be accessible')
        
        return JsonResponse(debug_result, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)
    
@login_required
@reviewer_required_fixed
def review_pengajuan_detail_enhanced(request, nomor_pengajuan):
    """
    ENHANCED: Detail pengajuan untuk review oleh SITI FATIMAH dengan section update
    """
    try:
        logger.info(f"ENHANCED REVIEW: Starting review for {nomor_pengajuan} by {request.user.username}")
        
        # Ambil employee data dengan function yang fixed
        employee_data = get_employee_data_for_request_fixed(request)
        
        if not employee_data:
            logger.error(f"ENHANCED REVIEW: No employee data for {request.user.username}")
            messages.error(request, 'Data employee tidak ditemukan. Silakan login ulang.')
            return redirect('login')
        
        # Import enhanced functions
        from .utils import (
            auto_discover_maintenance_sections,
            assign_pengajuan_after_siti_review_enhanced,
            ensure_enhanced_review_tables_exist,
            get_section_change_history
        )
        
        # Ensure enhanced tables exist
        ensure_enhanced_review_tables_exist()
        
        # Ambil data pengajuan dengan enhanced info
        pengajuan = None
        
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT 
                    tp.history_id,
                    tp.number_wo,
                    tp.tgl_insert,
                    tp.oleh,
                    tp.user_insert,
                    tm.mesin,
                    tms.seksi as section_tujuan,
                    tpek.pekerjaan,
                    tp.deskripsi_perbaikan,
                    tp.status,
                    tp.approve,
                    tl.line as line_name,
                    tp.tgl_his,
                    tp.jam_his,
                    tp.review_status,
                    tp.reviewed_by,
                    tp.review_date,
                    tp.review_notes,
                    tp.final_section_id,
                    final_section.seksi as final_section_name,
                    tp.status_pekerjaan,
                    tp.id_section as current_section_id
                FROM tabel_pengajuan tp
                LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
                LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
                LEFT JOIN tabel_msection tms ON tp.id_section = tms.id_section
                LEFT JOIN tabel_pekerjaan tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
                LEFT JOIN tabel_msection final_section ON tp.final_section_id = final_section.id_section
                WHERE tp.history_id = %s
            """, [nomor_pengajuan])
            
            row = cursor.fetchone()
            
            if not row:
                logger.error(f"ENHANCED REVIEW: Pengajuan {nomor_pengajuan} not found")
                messages.error(request, 'Pengajuan tidak ditemukan.')
                return redirect('wo_maintenance_app:review_pengajuan_list')
            
            pengajuan = {
                'history_id': row[0],
                'number_wo': row[1],
                'tgl_insert': row[2],
                'oleh': row[3],
                'user_insert': row[4],
                'mesin': row[5],
                'section_tujuan': row[6],
                'pekerjaan': row[7],
                'deskripsi_perbaikan': row[8],
                'status': row[9],
                'approve': row[10],
                'line_name': row[11],
                'tgl_his': row[12],
                'jam_his': row[13],
                'review_status': row[14],
                'reviewed_by': row[15],
                'review_date': row[16],
                'review_notes': row[17],
                'final_section_id': row[18],
                'final_section_name': row[19],
                'status_pekerjaan': row[20],
                'current_section_id': row[21]
            }
        
        logger.debug(f"ENHANCED REVIEW: Pengajuan loaded - Current section ID: {pengajuan['current_section_id']}")
        
        # Cek apakah pengajuan sudah di-approve dan belum direview
        if pengajuan['status'] != STATUS_APPROVED or pengajuan['approve'] != APPROVE_YES:
            logger.warning(f"ENHANCED REVIEW: Pengajuan {nomor_pengajuan} not approved")
            messages.warning(request, 'Pengajuan ini belum di-approve oleh atasan.')
            return redirect('wo_maintenance_app:review_pengajuan_list')
        
        # Cek apakah sudah direview
        already_reviewed = pengajuan['review_status'] in ['1', '2']
        
        # Get section change history
        section_change_history = get_section_change_history(nomor_pengajuan) if already_reviewed else []
        
        # ENHANCED: Handle review form submission dengan section update
        if request.method == 'POST' and not already_reviewed:
            logger.info(f"ENHANCED REVIEW: Processing POST request for {nomor_pengajuan}")
            
            # Ensure session is preserved
            request.session.modified = True
            
            review_form = ReviewForm(request.POST)
            
            if review_form.is_valid():
                action = review_form.cleaned_data['action']
                target_section = review_form.cleaned_data['target_section']
                review_notes = review_form.cleaned_data['review_notes']
                priority_level = review_form.cleaned_data['priority_level']
                
                logger.info(f"ENHANCED REVIEW: Form valid - Action: {action}, Target: {target_section}")
                
                try:
                    with connections['DB_Maintenance'].cursor() as cursor:
                        if action == 'process':
                            # Update pengajuan dengan review processing
                            cursor.execute("""
                                UPDATE tabel_pengajuan
                                SET review_status = '1',
                                    reviewed_by = %s,
                                    review_date = GETDATE(),
                                    review_notes = %s
                                WHERE history_id = %s
                            """, [
                                REVIEWER_EMPLOYEE_NUMBER, 
                                review_notes, 
                                nomor_pengajuan
                            ])
                            
                            logger.info(f"ENHANCED REVIEW: Updated pengajuan {nomor_pengajuan} with review processing")
                            
                            # ENHANCED: Section update dengan auto-discovery dan SDBM integration
                            if target_section:
                                logger.info(f"ENHANCED REVIEW: Processing section change to {target_section}")
                                
                                assignment_result = assign_pengajuan_after_siti_review_enhanced(
                                    nomor_pengajuan,
                                    target_section,
                                    REVIEWER_EMPLOYEE_NUMBER,
                                    review_notes
                                )
                                
                                # Enhanced success message dengan section change info
                                if assignment_result['success']:
                                    success_parts = []
                                    
                                    # Base success message
                                    success_parts.append(f'✅ Pengajuan {nomor_pengajuan} berhasil diproses!')
                                    
                                    # Section change info
                                    if assignment_result['section_updated']:
                                        if assignment_result['section_changed']:
                                            original_name = assignment_result['original_section']['name'] if assignment_result['original_section'] else 'Unknown'
                                            new_name = assignment_result['new_section']['display_name'] if assignment_result['new_section'] else 'Unknown'
                                            success_parts.append(f'🎯 Section tujuan berubah dari "{original_name}" ke "{new_name}"')
                                        else:
                                            success_parts.append(f'🎯 Section tujuan dikonfirmasi ke "{assignment_result["new_section"]["display_name"]}"')
                                    
                                    # Assignment info
                                    if assignment_result['assigned_employees']:
                                        assigned_count = len(assignment_result['assigned_employees'])
                                        supervisors_info = [
                                            f"{emp['fullname']} ({emp['level_description']})" 
                                            for emp in assignment_result['assigned_employees'][:3]
                                        ]
                                        
                                        success_parts.append(f'📋 Auto-assigned ke {assigned_count} supervisor:')
                                        success_parts.extend([f'• {info}' for info in supervisors_info])
                                        
                                        if assigned_count > 3:
                                            success_parts.append(f'• dan {assigned_count - 3} supervisor lainnya')
                                    
                                    # Join semua pesan
                                    messages.success(request, '\n'.join(success_parts))
                                    
                                    logger.info(f"ENHANCED REVIEW SUCCESS: {nomor_pengajuan} -> {target_section}, section_changed: {assignment_result['section_changed']}, assignments: {len(assignment_result['assigned_employees'])}")
                                    
                                else:
                                    # Error dalam assignment tapi review tetap berhasil
                                    error_msg = assignment_result.get('error', 'Unknown error')
                                    messages.warning(request,
                                        f'✅ Pengajuan {nomor_pengajuan} berhasil diproses, '
                                        f'tetapi terjadi masalah: {error_msg}'
                                    )
                                    logger.warning(f"ENHANCED REVIEW PARTIAL: {nomor_pengajuan} processed but assignment failed: {error_msg}")
                                
                            else:
                                # No specific target section - standard processing
                                messages.success(request, 
                                    f'✅ Pengajuan {nomor_pengajuan} berhasil diproses! '
                                    f'Akan ditindaklanjuti sesuai prosedur standar.'
                                )
                                logger.info(f"ENHANCED REVIEW: {nomor_pengajuan} processed with standard procedure")
                            
                        elif action == 'reject':
                            # Update pengajuan dengan review rejection
                            cursor.execute("""
                                UPDATE tabel_pengajuan
                                SET review_status = '2',
                                    reviewed_by = %s,
                                    review_date = GETDATE(),
                                    review_notes = %s,
                                    status = '2'
                                WHERE history_id = %s
                            """, [REVIEWER_EMPLOYEE_NUMBER, review_notes, nomor_pengajuan])
                            
                            logger.info(f"ENHANCED REVIEW: Rejected pengajuan {nomor_pengajuan}")
                            messages.success(request, f'❌ Pengajuan {nomor_pengajuan} berhasil ditolak. Alasan: {review_notes}')
                    
                    logger.info(f"ENHANCED REVIEW: Successfully processed review for {nomor_pengajuan}")
                    
                    # Ensure session is saved before redirect
                    request.session.modified = True
                    request.session.save()
                    
                    # Redirect ke enhanced detail view
                    return redirect('wo_maintenance_app:review_pengajuan_detail_enhanced', nomor_pengajuan=nomor_pengajuan)
                    
                except Exception as update_error:
                    logger.error(f"ENHANCED REVIEW: Error processing review for {nomor_pengajuan}: {update_error}")
                    messages.error(request, f'Terjadi kesalahan saat memproses review: {str(update_error)}')
            else:
                # Form validation error
                logger.warning(f"ENHANCED REVIEW: Form validation failed for {nomor_pengajuan}: {review_form.errors}")
                messages.error(request, 'Form review tidak valid. Periksa kembali input Anda.')
        else:
            review_form = ReviewForm()
        
        # Get enhanced available sections dengan auto-discovery
        available_sections = []
        try:
            section_mapping = auto_discover_maintenance_sections()
            
            for key, info in section_mapping.items():
                available_sections.append({
                    'key': key,
                    'name': info['display_name'],
                    'section_id': info['id_section'],
                    'section_name': info['section_name'],
                    'is_current': info['id_section'] == pengajuan['current_section_id'],
                    'matched_keyword': info['matched_keyword']
                })
                
        except Exception as section_error:
            logger.error(f"ENHANCED REVIEW: Error getting sections: {section_error}")
            # Fallback ke basic sections
            available_sections = [
                {'key': 'it', 'name': '💻 IT', 'section_id': 1, 'is_current': False},
                {'key': 'elektrik', 'name': '⚡ Elektrik', 'section_id': 2, 'is_current': False},
                {'key': 'utility', 'name': '🏭 Utility', 'section_id': 4, 'is_current': False},
                {'key': 'mekanik', 'name': '🔧 Mekanik', 'section_id': 3, 'is_current': False}
            ]
        
        # Enhanced context
        context = {
            'pengajuan': pengajuan,
            'review_form': review_form,
            'already_reviewed': already_reviewed,
            'reviewer_name': employee_data.get('fullname', REVIEWER_FULLNAME),
            'available_sections': available_sections,
            'employee_data': employee_data,
            'page_title': f'Enhanced Review Pengajuan {nomor_pengajuan}',
            
            # ENHANCED: Section change info
            'section_change_history': section_change_history,
            'has_section_changes': len(section_change_history) > 0,
            'current_section_info': {
                'id': pengajuan['current_section_id'],
                'name': pengajuan['section_tujuan']
            },
            'final_section_info': {
                'id': pengajuan['final_section_id'],
                'name': pengajuan['final_section_name']
            },
            
            # Enhanced features
            'enhanced_mode': True,
            'section_update_enabled': True,
            'auto_discovery_enabled': True,
            
            # Debug info
            'debug_mode': request.user.is_superuser,
            'section_mapping_debug': auto_discover_maintenance_sections() if request.user.is_superuser else None
        }
        
        logger.info(f"ENHANCED REVIEW: Rendering enhanced template for {nomor_pengajuan}")
        return render(request, 'wo_maintenance_app/review_pengajuan_detail_enhanced.html', context)
        
    except Exception as e:
        logger.error(f"ENHANCED REVIEW: Critical error for {nomor_pengajuan}: {e}")
        import traceback
        logger.error(f"ENHANCED REVIEW: Traceback: {traceback.format_exc()}")
        messages.error(request, 'Terjadi kesalahan saat memuat enhanced detail pengajuan.')
        return redirect('wo_maintenance_app:review_pengajuan_list')

# ===== AJAX ENDPOINTS untuk Enhanced Features =====

@login_required
@reviewer_required_fixed
def ajax_preview_section_change(request):
    """
    AJAX preview untuk section change sebelum submit
    Menampilkan preview perubahan section pengaju
    """
    try:
        history_id = request.GET.get('history_id', '').strip()
        target_section = request.GET.get('target_section', '').strip()
        
        if not history_id or not target_section:
            return JsonResponse({
                'success': False,
                'error': 'history_id and target_section required'
            })
        
        from .utils import auto_discover_maintenance_sections
        
        # Get current section info
        current_section = None
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT tp.id_section, ms.seksi
                FROM tabel_pengajuan tp
                LEFT JOIN tabel_msection ms ON tp.id_section = ms.id_section
                WHERE tp.history_id = %s
            """, [history_id])
            
            row = cursor.fetchone()
            if row:
                current_section = {
                    'id': int(float(row[0])) if row[0] else None,
                    'name': row[1] or 'Unknown',
                    'display_name': row[1] or 'Section Saat Ini'
                }
        
        # Get target section info
        section_mapping = auto_discover_maintenance_sections()
        target_info = section_mapping.get(target_section, {})
        
        # Determine if section will actually change
        will_change = (
            current_section and 
            target_info.get('id_section') and 
            current_section['id'] != target_info.get('id_section')
        )
        
        preview = {
            'history_id': history_id,
            'target_section': target_section,
            'current_section': current_section,
            'target_section_info': {
                'id': target_info.get('id_section'),
                'name': target_info.get('section_name', 'Unknown'),
                'display_name': target_info.get('display_name', target_section.title())
            },
            'will_change': will_change,
            'change_description': None
        }
        
        # Generate change description
        if will_change:
            preview['change_description'] = (
                f"Section pengaju akan berubah dari "
                f'"{current_section["display_name"]}" ke '
                f'"{target_info.get("display_name", target_section.title())}"'
            )
        elif current_section and target_info.get('id_section'):
            if current_section['id'] == target_info.get('id_section'):
                preview['change_description'] = (
                    f'Section pengaju akan tetap di '
                    f'"{target_info.get("display_name", target_section.title())}" '
                    f'(tidak ada perubahan)'
                )
        else:
            preview['change_description'] = "Informasi section tidak lengkap"
        
        return JsonResponse({
            'success': True,
            'preview': preview
        })
        
    except Exception as e:
        logger.error(f"Error in ajax_preview_section_change: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# ENHANCED: AJAX endpoint untuk konfirmasi section change
@login_required
@reviewer_required_fixed
def ajax_confirm_section_change(request):
    """
    AJAX endpoint untuk konfirmasi section change dengan detail info
    """
    try:
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'POST required'})
        
        data = json.loads(request.body)
        history_id = data.get('history_id', '').strip()
        target_section = data.get('target_section', '').strip()
        
        if not history_id or not target_section:
            return JsonResponse({
                'success': False,
                'error': 'history_id and target_section required'
            })
        
        from .utils import (
            auto_discover_maintenance_sections,
            get_sdbm_supervisors_by_section_mapping
        )
        
        # Get current pengajuan info
        pengajuan_info = None
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT tp.history_id, tp.oleh, tp.id_section, ms.seksi
                FROM tabel_pengajuan tp
                LEFT JOIN tabel_msection ms ON tp.id_section = ms.id_section
                WHERE tp.history_id = %s
            """, [history_id])
            
            row = cursor.fetchone()
            if row:
                pengajuan_info = {
                    'history_id': row[0],
                    'pengaju': row[1],
                    'current_section_id': int(float(row[2])) if row[2] else None,
                    'current_section_name': row[3] or 'Unknown'
                }
        
        if not pengajuan_info:
            return JsonResponse({
                'success': False,
                'error': 'Pengajuan tidak ditemukan'
            })
        
        # Get target section info dan supervisors
        section_mapping = auto_discover_maintenance_sections()
        target_info = section_mapping.get(target_section, {})
        supervisors = get_sdbm_supervisors_by_section_mapping(target_section)
        
        # Build confirmation data
        confirmation = {
            'pengajuan': pengajuan_info,
            'section_change': {
                'from': {
                    'id': pengajuan_info['current_section_id'],
                    'name': pengajuan_info['current_section_name']
                },
                'to': {
                    'id': target_info.get('id_section'),
                    'name': target_info.get('display_name', target_section.title())
                },
                'will_change': (
                    pengajuan_info['current_section_id'] != target_info.get('id_section')
                    if pengajuan_info['current_section_id'] and target_info.get('id_section') else True
                )
            },
            'supervisors': [
                {
                    'name': s['fullname'],
                    'title': s['title_name'],
                    'level': s.get('level_description', 'Supervisor')
                } for s in supervisors[:5]  # Limit to first 5
            ],
            'supervisor_count': len(supervisors),
            'confirmation_message': None
        }
        
        # Generate confirmation message
        if confirmation['section_change']['will_change']:
            confirmation['confirmation_message'] = (
                f"Pengajuan dari {pengajuan_info['pengaju']} akan dipindahkan "
                f'dari section "{pengajuan_info["current_section_name"]}" '
                f'ke section "{target_info.get("display_name", target_section.title())}" '
                f'dan di-assign ke {len(supervisors)} supervisor.'
            )
        else:
            confirmation['confirmation_message'] = (
                f"Pengajuan dari {pengajuan_info['pengaju']} akan tetap di "
                f'section "{target_info.get("display_name", target_section.title())}" '
                f'dan di-assign ke {len(supervisors)} supervisor.'
            )
        
        return JsonResponse({
            'success': True,
            'confirmation': confirmation
        })
        
    except Exception as e:
        logger.error(f"Error in ajax_confirm_section_change: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def ajax_get_section_mapping_info(request):
    """
    AJAX endpoint untuk mendapatkan section mapping info
    """
    if not request.user.is_superuser and not is_reviewer_fixed(request):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        from .utils import auto_discover_maintenance_sections, get_target_section_to_maintenance_mapping
        
        # Get auto-discovered mapping
        discovered = auto_discover_maintenance_sections()
        
        # Get default mapping
        default = get_target_section_to_maintenance_mapping()
        
        mapping_info = {
            'timestamp': timezone.now().isoformat(),
            'discovered_mapping': discovered,
            'default_mapping': default,
            'differences': []
        }
        
        # Check for differences
        for target in default.keys():
            default_id = default[target]['maintenance_section_id']
            discovered_id = discovered.get(target, {}).get('id_section')
            
            if default_id != discovered_id:
                mapping_info['differences'].append({
                    'target_section': target,
                    'default_id': default_id,
                    'discovered_id': discovered_id,
                    'status': 'mismatch'
                })
        
        return JsonResponse(mapping_info, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)

# wo_maintenance_app/views.py - FIXED section_based_daftar_laporan dengan type conversion

@login_required
def section_based_daftar_laporan(request):
    """
    FIXED: Enhanced daftar laporan dengan section-based access dan proper type conversion
    """
    try:
        # ===== AMBIL DATA HIERARCHY USER =====
        user_hierarchy = get_employee_hierarchy_data(request.user)
        
        if not user_hierarchy:
            logger.warning(f"User {request.user.username} tidak ditemukan di database SDBM")
            messages.error(request, 'Data karyawan tidak ditemukan. Hubungi administrator.')
            return redirect('wo_maintenance_app:dashboard')
        
        # ===== GET ENHANCED ACCESS INFO =====
        access_info = get_enhanced_pengajuan_access_for_user(user_hierarchy)
        access_info['user_employee_number'] = user_hierarchy.get('employee_number')
        
        logger.info(f"Section Access for {user_hierarchy.get('fullname')}: {access_info['access_type']}")
        
        # ===== FILTER FORM =====
        filter_form = PengajuanFilterForm(request.GET or None)
        search_query = request.GET.get('search', '').strip()
        
        # ===== QUERY DATABASE dengan Fixed Type Conversion =====
        pengajuan_list = []
        total_records = 0
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # ===== BUILD WHERE CONDITIONS dengan Type-safe Parameters =====
                where_conditions = ["tp.history_id IS NOT NULL"]
                query_params = []
                
                # UPDATED: Exclude final processed (status A, approve Y)
                where_conditions.append("NOT (tp.status = %s AND tp.approve = %s)")
                query_params.extend([STATUS_REVIEWED, APPROVE_REVIEWED])
                
                # ===== ACCESS-BASED CONDITIONS dengan Type Conversion =====
                access_type = access_info.get('access_type')
                
                if access_type == 'SITI_FATIMAH_FULL':
                    # SITI FATIMAH - Access ke semua approved pengajuan (status B, approve N)
                    where_conditions.extend([
                        "tp.status = %s",
                        "tp.approve = %s"
                    ])
                    query_params.extend([STATUS_APPROVED, APPROVE_YES])
                    
                elif access_type.startswith('ENGINEERING_') and access_type.endswith('_SUPERVISOR'):
                    # Engineering Supervisor - Section-based access dengan PROPER TYPE CONVERSION
                    section_ids = access_info.get('allowed_section_ids', [])
                    if section_ids:
                        logger.info(f"SECTION ACCESS: User has access to section IDs: {section_ids}")
                        
                        # FIXED: Convert section IDs to strings untuk compatibility
                        section_id_strings = [str(sid) for sid in section_ids]
                        section_placeholders = ','.join(['%s'] * len(section_id_strings))
                        
                        # FIXED: Use proper CAST in SQL untuk type conversion
                        where_conditions.append(f"""(
                            CAST(tp.id_section AS varchar(10)) IN ({section_placeholders}) OR 
                            CAST(tp.final_section_id AS varchar(10)) IN ({section_placeholders})
                        )""")
                        
                        # Add section IDs as strings (twice for both conditions)
                        query_params.extend(section_id_strings)
                        query_params.extend(section_id_strings)
                        
                        logger.info(f"SECTION QUERY: Added {len(section_id_strings)} section conditions with type conversion")
                    else:
                        # Jika tidak ada section, tampilkan kosong
                        where_conditions.append("1 = 0")
                        logger.warning("SECTION ACCESS: No section IDs found, showing empty result")
                
                elif access_type == 'HIERARCHY_NORMAL':
                    # Regular hierarchy access
                    allowed_employee_numbers = access_info.get('allowed_employee_numbers', [])
                    if allowed_employee_numbers and '*' not in allowed_employee_numbers:
                        # Limit untuk menghindari query terlalu panjang
                        if len(allowed_employee_numbers) > 50:
                            allowed_employee_numbers = allowed_employee_numbers[:50]
                        
                        if allowed_employee_numbers:
                            placeholders = ','.join(['%s'] * len(allowed_employee_numbers))
                            where_conditions.append(f"tp.user_insert IN ({placeholders})")
                            query_params.extend(allowed_employee_numbers)
                    else:
                        # Fallback to own pengajuan only
                        where_conditions.append("tp.user_insert = %s")
                        query_params.append(access_info.get('user_employee_number', ''))
                
                else:
                    # Default: own pengajuan only
                    where_conditions.append("tp.user_insert = %s")
                    query_params.append(user_hierarchy.get('employee_number', ''))
                
                # ===== FORM FILTERS =====
                if filter_form.is_valid():
                    tanggal_dari = filter_form.cleaned_data.get('tanggal_dari')
                    if tanggal_dari:
                        where_conditions.append("CAST(tp.tgl_insert AS DATE) >= %s")
                        query_params.append(tanggal_dari)
                    
                    tanggal_sampai = filter_form.cleaned_data.get('tanggal_sampai')
                    if tanggal_sampai:
                        where_conditions.append("CAST(tp.tgl_insert AS DATE) <= %s")
                        query_params.append(tanggal_sampai)
                    
                    status_filter = filter_form.cleaned_data.get('status')
                    if status_filter:
                        where_conditions.append("tp.status = %s")
                        query_params.append(status_filter)
                
                # ===== SEARCH =====
                if search_query:
                    search_conditions = [
                        "tp.history_id LIKE %s",
                        "tp.oleh LIKE %s",
                        "tp.deskripsi_perbaikan LIKE %s",
                        "tp.number_wo LIKE %s"
                    ]
                    where_conditions.append(f"({' OR '.join(search_conditions)})")
                    search_param = f"%{search_query}%"
                    query_params.extend([search_param] * len(search_conditions))
                
                # ===== BUILD WHERE CLAUSE =====
                where_clause = "WHERE " + " AND ".join(where_conditions)
                
                # LOG untuk debugging
                logger.info(f"QUERY DEBUG: Where conditions count: {len(where_conditions)}")
                logger.info(f"QUERY DEBUG: Query params count: {len(query_params)}")
                logger.info(f"QUERY DEBUG: First few params: {query_params[:5]}")
                
                # ===== COUNT QUERY =====
                count_query = f"""
                    SELECT COUNT(DISTINCT tp.history_id)
                    FROM tabel_pengajuan tp
                    LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
                    LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
                    LEFT JOIN tabel_msection tms ON tp.id_section = tms.id_section
                    LEFT JOIN tabel_pekerjaan tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
                    LEFT JOIN tabel_msection final_section ON tp.final_section_id = final_section.id_section
                    {where_clause}
                """
                
                cursor.execute(count_query, query_params)
                total_records = cursor.fetchone()[0] or 0
                
                logger.info(f"COUNT QUERY SUCCESS: Found {total_records} total records")
                
                # ===== PAGINATION =====
                page_size = 20
                page_number = int(request.GET.get('page', 1))
                
                total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
                has_previous = page_number > 1
                has_next = page_number < total_pages
                previous_page_number = page_number - 1 if has_previous else None
                next_page_number = page_number + 1 if has_next else None
                
                # ===== MAIN QUERY =====
                offset = (page_number - 1) * page_size
                
                main_query = f"""
                    SELECT DISTINCT
                        tp.history_id,                    -- 0
                        tp.oleh,                          -- 1
                        ISNULL(tm.mesin, 'N/A'),          -- 2
                        ISNULL(tms.seksi, 'N/A'),         -- 3 (current section)
                        ISNULL(tpek.pekerjaan, 'N/A'),    -- 4
                        tp.deskripsi_perbaikan,           -- 5
                        tp.status,                        -- 6
                        tp.tgl_insert,                    -- 7
                        tp.user_insert,                   -- 8
                        tp.number_wo,                     -- 9
                        ISNULL(tl.line, 'N/A'),           -- 10
                        tp.approve,                       -- 11
                        tp.tgl_his,                       -- 12
                        tp.jam_his,                       -- 13
                        tp.status_pekerjaan,              -- 14
                        ISNULL(tp.review_status, '0'),    -- 15
                        tp.reviewed_by,                   -- 16
                        tp.review_date,                   -- 17
                        ISNULL(final_section.seksi, tms.seksi), -- 18 (final or current section)
                        %s as access_type                 -- 19
                    FROM tabel_pengajuan tp
                    LEFT JOIN (
                        SELECT DISTINCT id_mesin, mesin 
                        FROM tabel_mesin 
                        WHERE mesin IS NOT NULL
                    ) tm ON tp.id_mesin = tm.id_mesin
                    LEFT JOIN (
                        SELECT DISTINCT id_line, line 
                        FROM tabel_line 
                        WHERE line IS NOT NULL
                    ) tl ON tp.id_line = tl.id_line
                    LEFT JOIN (
                        SELECT DISTINCT id_section, seksi 
                        FROM tabel_msection 
                        WHERE seksi IS NOT NULL
                    ) tms ON tp.id_section = tms.id_section
                    LEFT JOIN (
                        SELECT DISTINCT id_pekerjaan, pekerjaan 
                        FROM tabel_pekerjaan 
                        WHERE pekerjaan IS NOT NULL
                    ) tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
                    LEFT JOIN (
                        SELECT DISTINCT id_section, seksi 
                        FROM tabel_msection 
                        WHERE seksi IS NOT NULL
                    ) final_section ON tp.final_section_id = final_section.id_section
                    {where_clause}
                    ORDER BY tp.tgl_insert DESC, tp.history_id DESC
                    OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
                """
                
                # Add access_type parameter dan pagination parameters
                final_params = query_params + [access_info['access_type'], offset, page_size]
                
                logger.info(f"MAIN QUERY DEBUG: Final params count: {len(final_params)}")
                
                cursor.execute(main_query, final_params)
                pengajuan_list = cursor.fetchall()
                
                logger.info(f"MAIN QUERY SUCCESS: Retrieved {len(pengajuan_list)} records for {access_info['access_type']}")
                
        except Exception as db_error:
            logger.error(f"Database error in section_based_daftar_laporan: {db_error}")
            logger.error(f"Query params count: {len(query_params) if 'query_params' in locals() else 'undefined'}")
            logger.error(f"Where conditions: {where_conditions if 'where_conditions' in locals() else 'undefined'}")
            
            # Enhanced error info untuk debugging
            if 'section_ids' in locals():
                logger.error(f"Section IDs being queried: {locals()['section_ids']}")
            
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            messages.error(request, f'Terjadi kesalahan database. Silakan coba lagi atau hubungi administrator.')
            pengajuan_list = []
            total_records = 0
            total_pages = 1
            has_previous = False
            has_next = False
            previous_page_number = None
            next_page_number = None
            page_number = 1
        
        # ===== GET ACCESS STATISTICS dengan Error Handling =====
        access_stats = {'total_accessible': 0, 'by_status': {}}
        try:
            access_stats = get_access_statistics(access_info)
        except Exception as stats_error:
            logger.error(f"Error getting access statistics: {stats_error}")
        
        # ===== ENHANCED CONTEXT =====
        context = {
            'pengajuan_list': pengajuan_list,
            'filter_form': filter_form,
            'search_query': search_query,
            'total_records': total_records,
            'total_pages': total_pages,
            'page_number': page_number,
            'has_previous': has_previous,
            'has_next': has_next,
            'previous_page_number': previous_page_number,
            'next_page_number': next_page_number,
            'can_approve': True,
            'user_hierarchy': user_hierarchy,
            'employee_data': user_hierarchy,
            
            # Enhanced section access info
            'access_info': access_info,
            'access_stats': access_stats,
            'is_siti_fatimah': access_info['access_type'] == 'SITI_FATIMAH_FULL',
            'is_engineering_supervisor': access_info['access_type'].startswith('ENGINEERING_'),
            'section_access_display': access_info.get('access_description', ''),
            
            # Engineering supervisor specific info
            'allowed_section_ids': access_info.get('allowed_section_ids', []),
            'section_keywords': access_info.get('section_keywords', []),
            
            # Page info
            'page_title': 'Section-based Daftar Laporan',
            'enhanced_mode': True,
            'section_based_access': True,
            
            # Status constants untuk template
            'STATUS_PENDING': STATUS_PENDING,       # 0
            'STATUS_APPROVED': STATUS_APPROVED,     # B
            'STATUS_REVIEWED': STATUS_REVIEWED,     # A
            'APPROVE_NO': APPROVE_NO,               # 0
            'APPROVE_YES': APPROVE_YES,             # N
            'APPROVE_REVIEWED': APPROVE_REVIEWED,   # Y
            
            # Debug info untuk superuser
            'debug_info': {
                'access_type': access_info['access_type'],
                'allowed_employee_count': len(access_info.get('allowed_employee_numbers', [])),
                'allowed_section_count': len(access_info.get('allowed_section_ids', [])),
                'user_role': f"{user_hierarchy.get('title_name', 'Unknown')}",
                'department_section': f"{user_hierarchy.get('department_name', '')}-{user_hierarchy.get('section_name', '')}",
                'total_pengajuan_loaded': len(pengajuan_list),
                'excluded_final_processed': True,
                'section_based_mode': True,
                'query_params_count': len(query_params) if 'query_params' in locals() else 0,
                'where_conditions_count': len(where_conditions) if 'where_conditions' in locals() else 0,
                'type_conversion_used': 'CAST to varchar for section compatibility'
            } if request.user.is_superuser else None
        }
        
        return render(request, 'wo_maintenance_app/section_based_daftar_laporan.html', context)
        
    except Exception as e:
        logger.error(f"Critical error in section_based_daftar_laporan: {e}")
        import traceback
        logger.error(f"Critical traceback: {traceback.format_exc()}")
        messages.error(request, 'Terjadi kesalahan sistem. Silakan coba lagi.')
        return redirect('wo_maintenance_app:dashboard')

@login_required
def ajax_get_section_access_info(request):
    """
    AJAX view untuk mendapatkan info section access user
    """
    try:
        user_hierarchy = get_employee_hierarchy_data(request.user)
        
        if not user_hierarchy:
            return JsonResponse({
                'success': False,
                'error': 'User hierarchy data not found'
            })
        
        access_info = get_enhanced_pengajuan_access_for_user(user_hierarchy)
        access_stats = get_access_statistics(access_info)
        
        # Engineering section info
        engineering_access = get_engineering_section_access(user_hierarchy)
        
        response_data = {
            'success': True,
            'user_info': {
                'employee_number': user_hierarchy.get('employee_number'),
                'fullname': user_hierarchy.get('fullname'),
                'title_name': user_hierarchy.get('title_name'),
                'department_name': user_hierarchy.get('department_name'),
                'section_name': user_hierarchy.get('section_name')
            },
            'access_info': {
                'access_type': access_info['access_type'],
                'access_description': access_info['access_description'],
                'allowed_section_count': len(access_info.get('allowed_section_ids', [])),
                'allowed_employee_count': len(access_info.get('allowed_employee_numbers', []))
            },
            'access_stats': access_stats,
            'engineering_access': engineering_access,
            'is_siti_fatimah': access_info['access_type'] == 'SITI_FATIMAH_FULL',
            'is_engineering_supervisor': access_info['access_type'].startswith('ENGINEERING_')
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error in ajax_get_section_access_info: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def debug_section_access(request):
    """
    Debug view untuk testing section access - SUPERUSER ONLY
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        user_hierarchy = get_employee_hierarchy_data(request.user)
        
        debug_info = {
            'timestamp': timezone.now().isoformat(),
            'user_hierarchy': user_hierarchy,
            'access_tests': {}
        }
        
        if user_hierarchy:
            # Test all access functions
            debug_info['access_tests'] = {
                'is_engineering_supervisor': is_engineering_supervisor_or_above(user_hierarchy),
                'engineering_section_access': get_engineering_section_access(user_hierarchy),
                'enhanced_access_info': get_enhanced_pengajuan_access_for_user(user_hierarchy),
                'access_statistics': get_access_statistics(get_enhanced_pengajuan_access_for_user(user_hierarchy))
            }
            
            # Test section ID mapping
            engineering_access = get_engineering_section_access(user_hierarchy)
            if engineering_access:
                keywords = engineering_access['maintenance_section_keywords']
                section_ids = get_maintenance_section_ids_by_keywords(keywords)
                debug_info['access_tests']['section_id_mapping'] = {
                    'keywords': keywords,
                    'found_section_ids': section_ids
                }
        
        return JsonResponse(debug_info, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)
    

# wo_maintenance_app/views.py - ADD this debug view

@login_required
def debug_section_access_view(request):
    """
    Debug view untuk troubleshoot section access system
    SUPERUSER ONLY untuk debugging
    """
    if not request.user.is_superuser:
        messages.error(request, 'Akses ditolak. Hanya untuk debugging.')
        return redirect('wo_maintenance_app:dashboard')
    
    debug_info = {
        'timestamp': timezone.now().isoformat(),
        'user_info': {},
        'access_info': {},
        'query_test': {},
        'section_mapping': {},
        'database_test': {}
    }
    
    try:
        # 1. Test user hierarchy
        user_hierarchy = get_employee_hierarchy_data(request.user)
        debug_info['user_info'] = {
            'found': user_hierarchy is not None,
            'data': user_hierarchy
        }
        
        if user_hierarchy:
            # 2. Test access info
            try:
                access_info = get_enhanced_pengajuan_access_for_user(user_hierarchy)
                debug_info['access_info'] = {
                    'success': True,
                    'data': access_info
                }
                
                # 3. Test query building
                try:
                    where_conditions, query_params = build_enhanced_pengajuan_query_conditions(access_info)
                    debug_info['query_test'] = {
                        'success': True,
                        'where_conditions_count': len(where_conditions),
                        'query_params_count': len(query_params),
                        'where_conditions': where_conditions,
                        'query_params': query_params[:10],  # First 10 params only
                        'params_match': len([c for c in ' '.join(where_conditions) if c == '%']) <= len(query_params)
                    }
                    
                    # 4. Test actual query execution
                    try:
                        with connections['DB_Maintenance'].cursor() as cursor:
                            where_clause = "WHERE " + " AND ".join(where_conditions)
                            test_query = f"""
                                SELECT COUNT(DISTINCT tp.history_id)
                                FROM tabel_pengajuan tp
                                LEFT JOIN tabel_msection tms ON tp.id_section = tms.id_section
                                {where_clause}
                            """
                            
                            cursor.execute(test_query, query_params)
                            count_result = cursor.fetchone()[0]
                            
                            debug_info['database_test'] = {
                                'success': True,
                                'count_result': count_result,
                                'query_executed': True
                            }
                            
                    except Exception as db_error:
                        debug_info['database_test'] = {
                            'success': False,
                            'error': str(db_error),
                            'query_executed': False
                        }
                    
                except Exception as query_error:
                    debug_info['query_test'] = {
                        'success': False,
                        'error': str(query_error)
                    }
                
            except Exception as access_error:
                debug_info['access_info'] = {
                    'success': False,
                    'error': str(access_error)
                }
        
        # 5. Test section mapping
        try:
            debug_info['section_mapping'] = {
                'engineering_sections': get_engineering_section_access(user_hierarchy) if user_hierarchy else None,
                'maintenance_sections': get_maintenance_section_ids_by_keywords(['MEKANIK', 'ELEKTRIK', 'IT', 'UTILITY'])
            }
        except Exception as mapping_error:
            debug_info['section_mapping'] = {
                'error': str(mapping_error)
            }
        
        # 6. Test dengan user lain (sample engineering supervisors)
        try:
            debug_info['sample_users'] = {}
            
            with connections['SDBM'].cursor() as cursor:
                cursor.execute("""
                    SELECT TOP 3
                        e.employee_number,
                        e.fullname,
                        d.name as department_name,
                        s.name as section_name,
                        t.Name as title_name
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
                            UPPER(t.Name) LIKE '%SUPERVISOR%'
                        )
                    ORDER BY s.name
                """)
                
                sample_users = cursor.fetchall()
                for user in sample_users:
                    emp_num = user[0]
                    try:
                        # Create dummy user for testing
                        from django.contrib.auth.models import User
                        dummy_user = User(username=emp_num)
                        test_hierarchy = get_employee_hierarchy_data(dummy_user)
                        
                        if test_hierarchy:
                            test_access = get_enhanced_pengajuan_access_for_user(test_hierarchy)
                            debug_info['sample_users'][emp_num] = {
                                'name': user[1],
                                'section': user[3],
                                'access_type': test_access.get('access_type'),
                                'allowed_sections': len(test_access.get('allowed_section_ids', []))
                            }
                    except Exception as user_error:
                        debug_info['sample_users'][emp_num] = {
                            'error': str(user_error)
                        }
                        
        except Exception as sample_error:
            debug_info['sample_users'] = {
                'error': str(sample_error)
            }
        
    except Exception as e:
        debug_info['critical_error'] = str(e)
        import traceback
        debug_info['traceback'] = traceback.format_exc()
    
    context = {
        'debug_info': debug_info,
        'page_title': 'Debug Section Access System'
    }
    
    return render(request, 'wo_maintenance_app/debug_section_access.html', context)


# SIMPLE fallback view untuk testing
@login_required
def simple_section_test(request):
    """
    Simple test view untuk memastikan basic functionality bekerja
    """
    try:
        user_hierarchy = get_employee_hierarchy_data(request.user)
        
        if not user_hierarchy:
            return JsonResponse({
                'success': False,
                'error': 'User hierarchy not found',
                'user': request.user.username
            })
        
        access_info = get_enhanced_pengajuan_access_for_user(user_hierarchy)
        
        # Simple count query
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE history_id IS NOT NULL")
            total_pengajuan = cursor.fetchone()[0]
        
        return JsonResponse({
            'success': True,
            'user': {
                'username': request.user.username,
                'fullname': user_hierarchy.get('fullname'),
                'department': user_hierarchy.get('department_name'),
                'section': user_hierarchy.get('section_name'),
                'title': user_hierarchy.get('title_name')
            },
            'access': {
                'type': access_info.get('access_type'),
                'description': access_info.get('access_description'),
                'allowed_sections': len(access_info.get('allowed_section_ids', [])),
                'allowed_employees': len(access_info.get('allowed_employee_numbers', []))
            },
            'database': {
                'total_pengajuan': total_pengajuan
            }
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })
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
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import json
import logging
from functools import wraps
from django.http import JsonResponse
from wo_maintenance_app.models import transfer_pengajuan_to_main, create_new_history_id, create_number_wo_with_section, save_checker_to_database, get_checker_data_from_database, transfer_checker_pengajuan_to_main, save_checker_to_pengajuan, save_checker_to_main
from wo_maintenance_app.forms import PengajuanMaintenanceForm, PengajuanFilterForm, ApprovalForm, ReviewForm, ReviewFilterForm, HistoryMaintenanceForm, HistoryFilterForm, update_history_maintenance
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
     is_pengajuan_approved_for_review,
     is_pengajuan_final_processed,  # NEW
    initialize_review_data
)

# Setup logging
logger = logging.getLogger(__name__)

# ===== REVIEW SYSTEM CONSTANTS =====
REVIEWER_EMPLOYEE_NUMBER = '007522'  # SITI FATIMAH
REVIEWER_FULLNAME = 'SITI FATIMAH'


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

# @login_required
# @reviewer_required_fixed
# def review_pengajuan_detail(request, nomor_pengajuan):
#     """
#     ENHANCED: Detail pengajuan untuk review oleh SITI FATIMAH dengan conditional number WO update
#     FIXED: Section mapping untuk 4=M, 5=E, 6=U, 8=I sesuai database
#     - Jika target section TIDAK berubah: number WO tetap sama
#     - Jika target section BERUBAH: number WO otomatis update dengan format section baru
#     """
#     try:
#         logger.info(f"FIXED REVIEW: Starting review for {nomor_pengajuan} by {request.user.username}")
        
#         employee_data = get_employee_data_for_request_fixed(request)
        
#         if not employee_data:
#             logger.error(f"FIXED REVIEW: No employee data for {request.user.username}")
#             messages.error(request, 'Data employee tidak ditemukan. Silakan login ulang.')
#             return redirect('login')
        
#         initialize_review_data()
        
#         # Ambil data pengajuan
#         pengajuan = None
        
#         with connections['DB_Maintenance'].cursor() as cursor:
#             cursor.execute("""
#                 SELECT 
#                     tp.history_id, tp.number_wo, tp.tgl_insert, tp.oleh, tp.user_insert,
#                     tm.mesin, tms.seksi as section_tujuan, tpek.pekerjaan,
#                     tp.deskripsi_perbaikan, tp.status, tp.approve, tl.line as line_name,
#                     tp.tgl_his, tp.jam_his, tp.review_status, tp.reviewed_by,
#                     tp.review_date, tp.review_notes, tp.final_section_id,
#                     final_section.seksi as final_section_name, tp.status_pekerjaan,
#                     tp.id_section as current_section_id, tp.id_line, tp.id_mesin,
#                     tp.id_pekerjaan
#                 FROM tabel_pengajuan tp
#                 LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
#                 LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
#                 LEFT JOIN tabel_msection tms ON tp.id_section = tms.id_section
#                 LEFT JOIN tabel_pekerjaan tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
#                 LEFT JOIN tabel_msection final_section ON tp.final_section_id = final_section.id_section
#                 WHERE tp.history_id = %s
#             """, [nomor_pengajuan])
            
#             row = cursor.fetchone()
            
#             if not row:
#                 logger.error(f"FIXED REVIEW: Pengajuan {nomor_pengajuan} not found")
#                 messages.error(request, 'Pengajuan tidak ditemukan.')
#                 return redirect('wo_maintenance_app:review_pengajuan_list')
            
#             pengajuan = {
#                 'history_id': row[0], 'number_wo': row[1], 'tgl_insert': row[2],
#                 'oleh': row[3], 'user_insert': row[4], 'mesin': row[5],
#                 'section_tujuan': row[6], 'pekerjaan': row[7], 'deskripsi_perbaikan': row[8],
#                 'status': row[9], 'approve': row[10], 'line_name': row[11],
#                 'tgl_his': row[12], 'jam_his': row[13], 'review_status': row[14],
#                 'reviewed_by': row[15], 'review_date': row[16], 'review_notes': row[17],
#                 'final_section_id': row[18], 'final_section_name': row[19],
#                 'status_pekerjaan': row[20], 'current_section_id': row[21],
#                 'id_line': row[22], 'id_mesin': row[23], 'id_pekerjaan': row[24]
#             }
        
#         # Cek apakah pengajuan siap di-review
#         if pengajuan['status'] != STATUS_APPROVED or pengajuan['approve'] != APPROVE_YES:
#             logger.warning(f"FIXED REVIEW: Pengajuan {nomor_pengajuan} not approved")
#             messages.warning(request, 'Pengajuan ini belum di-approve oleh atasan.')
#             return redirect('wo_maintenance_app:review_pengajuan_list')
        
#         already_reviewed = pengajuan['review_status'] in ['1', '2']
        
#         # Handle review form submission dengan ENHANCED NUMBER WO LOGIC
#         if request.method == 'POST' and not already_reviewed:
#             logger.info(f"FIXED REVIEW: Processing POST with conditional number WO for {nomor_pengajuan}")
            
#             request.session.modified = True
            
#             review_form = ReviewForm(request.POST)
            
#             if review_form.is_valid():
#                 action = review_form.cleaned_data['action']
#                 target_section = review_form.cleaned_data.get('target_section', '').strip()
#                 review_notes = review_form.cleaned_data['review_notes']
                
#                 logger.info(f"FIXED REVIEW: Form valid - Action: {action}, Target: {target_section}")
                
#                 try:
#                     with transaction.atomic(using='DB_Maintenance'):
#                         with connections['DB_Maintenance'].cursor() as cursor:
                            
#                             if action == 'process':
#                                 # FIXED: Preserve original section, hanya validate target section
#                                 # JANGAN ubah current_section_id - terima apa adanya dari database
#                                 original_section_id = pengajuan['current_section_id']
#                                 final_section_id = original_section_id  # Default ke original section
#                                 section_changed = False
#                                 section_change_info = ""
                                
#                                 logger.info(f"FIXED REVIEW: Original section from database - ID: {original_section_id}")
                                
#                                 if target_section:
#                                     # FIXED: Mapping section sesuai database aktual (4=M, 5=E, 6=U, 8=I)
#                                     section_mapping = {
#                                         'mekanik': 4,    # Mekanik = 4 
#                                         'elektrik': 5,   # Elektrik = 5
#                                         'utility': 6,    # Utility = 6
#                                         'it': 8          # IT = 8
#                                     }
                                    
#                                     if target_section in section_mapping:
#                                         target_section_id = section_mapping[target_section]
                                        
#                                         # Check if section actually changes
#                                         if target_section_id != original_section_id:
#                                             section_changed = True
#                                             final_section_id = target_section_id
#                                             section_change_info = f"Section berubah dari {pengajuan['section_tujuan']} (ID: {original_section_id}) ke {target_section.title()} (ID: {target_section_id})"
#                                             logger.info(f"FIXED REVIEW: Section changed from {original_section_id} to {target_section_id}")
#                                         else:
#                                             # Target sama dengan current
#                                             final_section_id = target_section_id
#                                             section_change_info = f"Section dikonfirmasi tetap di {target_section.title()} (ID: {target_section_id})"
#                                             logger.info(f"FIXED REVIEW: Section confirmed at {target_section_id}")
#                                     else:
#                                         logger.warning(f"FIXED REVIEW: Unknown target_section {target_section}")
#                                         # Tetap gunakan original section
#                                         final_section_id = original_section_id
#                                         section_change_info = f"Section tetap di {pengajuan['section_tujuan']} (ID: {original_section_id}) - target tidak valid"
#                                 else:
#                                     # TIDAK ADA target section dipilih - GUNAKAN ORIGINAL SECTION
#                                     final_section_id = original_section_id
#                                     section_change_info = f"Section tetap di {pengajuan['section_tujuan']} (ID: {original_section_id})"
#                                     logger.info(f"FIXED REVIEW: No target section specified, keeping original section {original_section_id}")
                                
#                                 # FIXED: Generate number WO berdasarkan final section dengan mapping yang benar
#                                 from wo_maintenance_app.models import create_number_wo_with_section_fixed
                                
#                                 # FIXED: Support untuk section 4, 5, 6, 8 sesuai database
#                                 if final_section_id in [4, 5, 6, 8]:
#                                     new_number_wo = create_number_wo_with_section_fixed(final_section_id)
#                                     logger.info(f"FIXED REVIEW: Generated Number WO: {new_number_wo} for mapped section {final_section_id}")
#                                 else:
#                                     # Section lain, gunakan fallback ke IT (section 8)
#                                     fallback_section = 8  # IT sebagai default
#                                     new_number_wo = create_number_wo_with_section_fixed(fallback_section)
#                                     logger.info(f"FIXED REVIEW: Generated Number WO: {new_number_wo} for unmapped section {final_section_id} (using IT fallback)")
                                
#                                 # VALIDATION: Log section info
#                                 logger.info(f"FIXED REVIEW: Section Summary:")
#                                 logger.info(f"  - Original Section ID: {original_section_id}")
#                                 logger.info(f"  - Final Section ID: {final_section_id}")
#                                 logger.info(f"  - Section Changed: {section_changed}")
#                                 logger.info(f"  - Generated Number WO: {new_number_wo}")
                                
#                                 # FIXED: Update review status dengan conditional section update
#                                 if section_changed:
#                                     # Jika section berubah, update final_section_id
#                                     cursor.execute("""
#                                         UPDATE tabel_pengajuan
#                                         SET review_status = %s,
#                                             reviewed_by = %s,
#                                             review_date = GETDATE(),
#                                             review_notes = %s,
#                                             status = %s,
#                                             approve = %s,
#                                             final_section_id = %s,
#                                             number_wo = %s
#                                         WHERE history_id = %s
#                                     """, [
#                                         '1',                        # review_status = processed
#                                         REVIEWER_EMPLOYEE_NUMBER, 
#                                         review_notes,
#                                         STATUS_REVIEWED,            # A - final processed
#                                         APPROVE_REVIEWED,           # Y - final processed
#                                         float(final_section_id),   # Update section karena berubah
#                                         new_number_wo,
#                                         nomor_pengajuan
#                                     ])
#                                     logger.info(f"FIXED REVIEW: Updated with section change to {final_section_id}")
#                                 else:
#                                     # Jika section TIDAK berubah, TIDAK update final_section_id
#                                     cursor.execute("""
#                                         UPDATE tabel_pengajuan
#                                         SET review_status = %s,
#                                             reviewed_by = %s,
#                                             review_date = GETDATE(),
#                                             review_notes = %s,
#                                             status = %s,
#                                             approve = %s,
#                                             number_wo = %s
#                                         WHERE history_id = %s
#                                     """, [
#                                         '1',                        # review_status = processed
#                                         REVIEWER_EMPLOYEE_NUMBER, 
#                                         review_notes,
#                                         STATUS_REVIEWED,            # A - final processed
#                                         APPROVE_REVIEWED,           # Y - final processed
#                                         new_number_wo,              # Update number WO aja
#                                         nomor_pengajuan
#                                     ])
#                                     logger.info(f"FIXED REVIEW: Updated number WO only, section unchanged")
                                
#                                 update_count = cursor.rowcount
#                                 logger.info(f"FIXED REVIEW: Updated {update_count} row(s) in tabel_pengajuan")
                                
#                                 # FIXED: Transfer ke tabel_main dengan section ASLI yang benar
#                                 logger.info(f"FIXED REVIEW: Starting auto transfer to tabel_main for {nomor_pengajuan}")
                                
#                                 # Check apakah data sudah ada di tabel_main
#                                 truncated_history_id = nomor_pengajuan[:11]
#                                 cursor.execute("""
#                                     SELECT COUNT(*) FROM tabel_main WHERE history_id = %s
#                                 """, [truncated_history_id])
#                                 exists_in_main = cursor.fetchone()[0] > 0
                                
#                                 transfer_success = False
                                
#                                 if not exists_in_main:
#                                     # FIXED: Gunakan section yang BENAR untuk transfer
#                                     if section_changed:
#                                         # Section berubah, gunakan final_section_id yang baru
#                                         transfer_section_id = final_section_id
#                                         logger.info(f"FIXED REVIEW: Transfer with CHANGED section {transfer_section_id}")
#                                     else:
#                                         # Section TIDAK berubah, gunakan ORIGINAL section dari database
#                                         transfer_section_id = original_section_id
#                                         logger.info(f"FIXED REVIEW: Transfer with ORIGINAL section {transfer_section_id}")
                                    
#                                     # Insert data ke tabel_main dengan section ASLI
#                                     truncated_number_wo = new_number_wo[:15]
#                                     user_insert_truncated = pengajuan['user_insert'][:50] if pengajuan['user_insert'] else None
#                                     oleh_truncated = pengajuan['oleh'][:500] if pengajuan['oleh'] else '-'
                                    
#                                     logger.info(f"FIXED REVIEW: Inserting to tabel_main - Section: {transfer_section_id}, Number WO: {truncated_number_wo}")
                                    
#                                     insert_sql = """
#                                         INSERT INTO tabel_main (
#                                             history_id, tgl_his, jam_his, id_line, id_mesin, 
#                                             id_section, id_pekerjaan, number_wo, deskripsi_perbaikan,
#                                             pic_produksi, pic_maintenance, status, user_insert, 
#                                             tgl_insert, oleh, status_pekerjaan
#                                         ) VALUES (
#                                             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
#                                         )
#                                     """
                                    
#                                     insert_params = [
#                                         truncated_history_id,
#                                         pengajuan['tgl_his'],
#                                         pengajuan['jam_his'],
#                                         float(pengajuan['id_line']) if pengajuan['id_line'] else None,
#                                         float(pengajuan['id_mesin']) if pengajuan['id_mesin'] else None,
#                                         float(transfer_section_id),             # CORRECT: Section asli atau yang berubah
#                                         float(pengajuan['id_pekerjaan']) if pengajuan['id_pekerjaan'] else None,
#                                         truncated_number_wo,                    # Number WO format baru
#                                         pengajuan['deskripsi_perbaikan'],
#                                         oleh_truncated,
#                                         '-',
#                                         '0',
#                                         user_insert_truncated,
#                                         pengajuan['tgl_insert'],
#                                         oleh_truncated,
#                                         '0'
#                                     ]
                                    
#                                     cursor.execute(insert_sql, insert_params)
#                                     insert_count = cursor.rowcount
                                    
#                                     logger.info(f"FIXED REVIEW: Inserted {insert_count} row(s) to tabel_main with section {transfer_section_id}")
#                                     transfer_success = True
                                    
#                                 else:
#                                     logger.warning(f"FIXED REVIEW: Data {nomor_pengajuan} already exists in tabel_main")
#                                     transfer_success = True
                                
#                                 # ENHANCED success message dengan number WO format baru
#                                 success_parts = []
#                                 success_parts.append(f'Pengajuan {nomor_pengajuan} berhasil diproses dan diselesaikan!')
                                
#                                 # Number WO info - SELALU format baru dengan section code yang benar
#                                 section_code_map = {4: 'M', 5: 'E', 6: 'U', 8: 'I'}
#                                 current_section_code = section_code_map.get(final_section_id, 'X')
#                                 success_parts.append(f'Number WO: {new_number_wo} (format section {current_section_code})')
                                
#                                 success_parts.append(f'Status: Final Processed (A/Y)')
                                
#                                 if transfer_success:
#                                     success_parts.append(f'Data berhasil masuk ke History Maintenance')
                                
#                                 # Section info
#                                 success_parts.append(section_change_info)
                                
#                                 messages.success(request, '\n'.join(success_parts))
                                
#                                 logger.info(f"FIXED REVIEW SUCCESS SUMMARY:")
#                                 logger.info(f"  - Pengajuan: {nomor_pengajuan}")
#                                 logger.info(f"  - Section Changed: {section_changed}")
#                                 logger.info(f"  - Final Section ID: {final_section_id}")
#                                 logger.info(f"  - Number WO (NEW FORMAT): {new_number_wo}")
#                                 logger.info(f"  - Transfer Success: {transfer_success}")
                                
#                             elif action == 'reject':
#                                 # Update pengajuan dengan review rejection
#                                 cursor.execute("""
#                                     UPDATE tabel_pengajuan
#                                     SET review_status = %s,
#                                         reviewed_by = %s,
#                                         review_date = GETDATE(),
#                                         review_notes = %s,
#                                         status = %s
#                                     WHERE history_id = %s
#                                 """, ['2', REVIEWER_EMPLOYEE_NUMBER, review_notes, STATUS_REJECTED, nomor_pengajuan])
                                
#                                 logger.info(f"FIXED REVIEW: Rejected pengajuan {nomor_pengajuan}")
#                                 messages.success(request, f'Pengajuan {nomor_pengajuan} berhasil ditolak. Alasan: {review_notes}')
                    
#                     logger.info(f"FIXED REVIEW: Transaction completed successfully for {nomor_pengajuan}")
                    
#                     request.session.modified = True
#                     request.session.save()
                    
#                     return redirect('wo_maintenance_app:review_pengajuan_detail', nomor_pengajuan=nomor_pengajuan)
                    
#                 except Exception as update_error:
#                     logger.error(f"FIXED REVIEW: Error processing review for {nomor_pengajuan}: {update_error}")
#                     import traceback
#                     logger.error(f"FIXED REVIEW: Traceback: {traceback.format_exc()}")
#                     messages.error(request, f'Terjadi kesalahan saat memproses review: {str(update_error)}')
#             else:
#                 logger.warning(f"FIXED REVIEW: Form validation failed for {nomor_pengajuan}: {review_form.errors}")
#                 messages.error(request, 'Form review tidak valid. Periksa kembali input Anda.')
#         else:
#             review_form = ReviewForm()
        
#         # FIXED: Available sections dengan mapping yang benar sesuai database
#         available_sections = [
#             {'key': 'mekanik', 'name': '🔧 Mekanik', 'section_id': 4, 'format_code': 'M', 'example': '25-M-08-0001'},
#             {'key': 'elektrik', 'name': '⚡ Elektrik', 'section_id': 5, 'format_code': 'E', 'example': '25-E-08-0001'},
#             {'key': 'utility', 'name': '🏭 Utility', 'section_id': 6, 'format_code': 'U', 'example': '25-U-08-0001'},
#             {'key': 'it', 'name': '💻 IT', 'section_id': 8, 'format_code': 'I', 'example': '25-I-08-0001'}
#         ]
        
#         context = {
#             'pengajuan': pengajuan,
#             'review_form': review_form,
#             'already_reviewed': already_reviewed,
#             'reviewer_name': employee_data.get('fullname', REVIEWER_FULLNAME),
#             'available_sections': available_sections,
#             'employee_data': employee_data,
#             'page_title': f'FIXED Review dengan Format Number WO Sesuai Database {nomor_pengajuan}',
            
#             # Enhanced context dengan number WO info yang benar
#             'enhanced_mode': True,
#             'always_new_format': True,  # SELALU format baru
#             'current_number_wo': pengajuan['number_wo'],
#             'current_section_info': {
#                 'id': pengajuan['current_section_id'],
#                 'name': pengajuan['section_tujuan']
#             },
#             'format_info': {
#                 'description': 'Number WO akan selalu menggunakan format baru: YY-S-MM-NNNN',
#                 'based_on_section': 'Berdasarkan section tujuan (4=M, 5=E, 6=U, 8=I)',
#                 'section_mapping': '4=Mekanik(M), 5=Elektrik(E), 6=Utility(U), 8=IT(I)'
#             },
            
#             # Status constants untuk template
#             'STATUS_APPROVED': STATUS_APPROVED,
#             'STATUS_REVIEWED': STATUS_REVIEWED,
#             'APPROVE_YES': APPROVE_YES,
#             'APPROVE_REVIEWED': APPROVE_REVIEWED
#         }
        
#         logger.info(f"FIXED REVIEW: Rendering template dengan section mapping 4=M, 5=E, 6=U, 8=I untuk {nomor_pengajuan}")
#         return render(request, 'wo_maintenance_app/review_pengajuan_detail.html', context)
        
#     except Exception as e:
#         logger.error(f"FIXED REVIEW: Critical error for {nomor_pengajuan}: {e}")
#         import traceback
#         logger.error(f"FIXED REVIEW: Traceback: {traceback.format_exc()}")
#         messages.error(request, 'Terjadi kesalahan saat memuat detail review.')
#         return redirect('wo_maintenance_app:review_pengajuan_list')

# wo_maintenance_app/views.py - UPDATE review_pengajuan_detail dengan Priority Level

# @login_required
# @reviewer_required_fixed
# def review_pengajuan_detail(request, nomor_pengajuan):
#     """
#     ENHANCED: Detail pengajuan untuk review oleh SITI FATIMAH dengan priority level support
#     FIXED: Section mapping untuk 4=M, 5=E, 6=U, 8=I sesuai database + Priority Level
#     """
#     try:
#         logger.info(f"ENHANCED REVIEW: Starting review for {nomor_pengajuan} by {request.user.username}")
        
#         employee_data = get_employee_data_for_request_fixed(request)
        
#         if not employee_data:
#             logger.error(f"ENHANCED REVIEW: No employee data for {request.user.username}")
#             messages.error(request, 'Data employee tidak ditemukan. Silakan login ulang.')
#             return redirect('login')
        
#         initialize_review_data()
        
#         # Ambil data pengajuan
#         pengajuan = None
        
#         with connections['DB_Maintenance'].cursor() as cursor:
#             cursor.execute("""
#                 SELECT 
#                     tp.history_id, tp.number_wo, tp.tgl_insert, tp.oleh, tp.user_insert,
#                     tm.mesin, tms.seksi as section_tujuan, tpek.pekerjaan,
#                     tp.deskripsi_perbaikan, tp.status, tp.approve, tl.line as line_name,
#                     tp.tgl_his, tp.jam_his, tp.review_status, tp.reviewed_by,
#                     tp.review_date, tp.review_notes, tp.final_section_id,
#                     final_section.seksi as final_section_name, tp.status_pekerjaan,
#                     tp.id_section as current_section_id, tp.id_line, tp.id_mesin,
#                     tp.id_pekerjaan
#                 FROM tabel_pengajuan tp
#                 LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
#                 LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
#                 LEFT JOIN tabel_msection tms ON tp.id_section = tms.id_section
#                 LEFT JOIN tabel_pekerjaan tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
#                 LEFT JOIN tabel_msection final_section ON tp.final_section_id = final_section.id_section
#                 WHERE tp.history_id = %s
#             """, [nomor_pengajuan])
            
#             row = cursor.fetchone()
            
#             if not row:
#                 logger.error(f"ENHANCED REVIEW: Pengajuan {nomor_pengajuan} not found")
#                 messages.error(request, 'Pengajuan tidak ditemukan.')
#                 return redirect('wo_maintenance_app:review_pengajuan_list')
            
#             pengajuan = {
#                 'history_id': row[0], 'number_wo': row[1], 'tgl_insert': row[2],
#                 'oleh': row[3], 'user_insert': row[4], 'mesin': row[5],
#                 'section_tujuan': row[6], 'pekerjaan': row[7], 'deskripsi_perbaikan': row[8],
#                 'status': row[9], 'approve': row[10], 'line_name': row[11],
#                 'tgl_his': row[12], 'jam_his': row[13], 'review_status': row[14],
#                 'reviewed_by': row[15], 'review_date': row[16], 'review_notes': row[17],
#                 'final_section_id': row[18], 'final_section_name': row[19],
#                 'status_pekerjaan': row[20], 'current_section_id': row[21],
#                 'id_line': row[22], 'id_mesin': row[23], 'id_pekerjaan': row[24]
#             }
        
#         # Cek apakah pengajuan siap di-review
#         if pengajuan['status'] != STATUS_APPROVED or pengajuan['approve'] != APPROVE_YES:
#             logger.warning(f"ENHANCED REVIEW: Pengajuan {nomor_pengajuan} not approved")
#             messages.warning(request, 'Pengajuan ini belum di-approve oleh atasan.')
#             return redirect('wo_maintenance_app:review_pengajuan_list')
        
#         already_reviewed = pengajuan['review_status'] in ['1', '2']
        
#         # Handle review form submission dengan ENHANCED NUMBER WO LOGIC + PRIORITY LEVEL
#         if request.method == 'POST' and not already_reviewed:
#             logger.info(f"ENHANCED REVIEW: Processing POST with priority level for {nomor_pengajuan}")
            
#             request.session.modified = True
            
#             review_form = ReviewForm(request.POST)
            
#             if review_form.is_valid():
#                 action = review_form.cleaned_data['action']
#                 target_section = review_form.cleaned_data.get('target_section', '').strip()
#                 priority_level = review_form.cleaned_data.get('priority_level', '').strip()  # NEW: Priority level
#                 review_notes = review_form.cleaned_data['review_notes']
                
#                 logger.info(f"ENHANCED REVIEW: Form valid - Action: {action}, Target: {target_section}, Priority: {priority_level}")
                
#                 try:
#                     with transaction.atomic(using='DB_Maintenance'):
#                         with connections['DB_Maintenance'].cursor() as cursor:
                            
#                             if action == 'process':
#                                 # FIXED: Preserve original section, hanya validate target section
#                                 original_section_id = pengajuan['current_section_id']
#                                 final_section_id = original_section_id  # Default ke original section
#                                 section_changed = False
#                                 section_change_info = ""
                                
#                                 logger.info(f"ENHANCED REVIEW: Original section from database - ID: {original_section_id}")
                                
#                                 if target_section:
#                                     # FIXED: Mapping section sesuai database aktual (4=M, 5=E, 6=U, 8=I)
#                                     section_mapping = {
#                                         'mekanik': 4,    # Mekanik = 4 
#                                         'elektrik': 5,   # Elektrik = 5
#                                         'utility': 6,    # Utility = 6
#                                         'it': 8          # IT = 8
#                                     }
                                    
#                                     if target_section in section_mapping:
#                                         target_section_id = section_mapping[target_section]
                                        
#                                         # Check if section actually changes
#                                         if target_section_id != original_section_id:
#                                             section_changed = True
#                                             final_section_id = target_section_id
#                                             section_change_info = f"Section berubah dari {pengajuan['section_tujuan']} (ID: {original_section_id}) ke {target_section.title()} (ID: {target_section_id})"
#                                             logger.info(f"ENHANCED REVIEW: Section changed from {original_section_id} to {target_section_id}")
#                                         else:
#                                             # Target sama dengan current
#                                             final_section_id = target_section_id
#                                             section_change_info = f"Section dikonfirmasi tetap di {target_section.title()} (ID: {target_section_id})"
#                                             logger.info(f"ENHANCED REVIEW: Section confirmed at {target_section_id}")
#                                     else:
#                                         logger.warning(f"ENHANCED REVIEW: Unknown target_section {target_section}")
#                                         final_section_id = original_section_id
#                                         section_change_info = f"Section tetap di {pengajuan['section_tujuan']} (ID: {original_section_id}) - target tidak valid"
#                                 else:
#                                     final_section_id = original_section_id
#                                     section_change_info = f"Section tetap di {pengajuan['section_tujuan']} (ID: {original_section_id})"
#                                     logger.info(f"ENHANCED REVIEW: No target section specified, keeping original section {original_section_id}")
                                
#                                 # FIXED: Generate number WO berdasarkan final section dengan mapping yang benar
#                                 from wo_maintenance_app.models import create_number_wo_with_section_fixed
                                
#                                 # FIXED: Support untuk section 4, 5, 6, 8 sesuai database
#                                 if final_section_id in [4, 5, 6, 8]:
#                                     new_number_wo = create_number_wo_with_section_fixed(final_section_id)
#                                     logger.info(f"ENHANCED REVIEW: Generated Number WO: {new_number_wo} for mapped section {final_section_id}")
#                                 else:
#                                     # Section lain, gunakan fallback ke IT (section 8)
#                                     fallback_section = 8  # IT sebagai default
#                                     new_number_wo = create_number_wo_with_section_fixed(fallback_section)
#                                     logger.info(f"ENHANCED REVIEW: Generated Number WO: {new_number_wo} for unmapped section {final_section_id} (using IT fallback)")
                                
#                                 # VALIDATION: Log section info
#                                 logger.info(f"ENHANCED REVIEW: Section Summary:")
#                                 logger.info(f"  - Original Section ID: {original_section_id}")
#                                 logger.info(f"  - Final Section ID: {final_section_id}")
#                                 logger.info(f"  - Section Changed: {section_changed}")
#                                 logger.info(f"  - Generated Number WO: {new_number_wo}")
#                                 logger.info(f"  - Priority Level: {priority_level}")
                                
#                                 # ENHANCED: Update review status dengan conditional section update + priority
#                                 if section_changed:
#                                     # Jika section berubah, update final_section_id
#                                     cursor.execute("""
#                                         UPDATE tabel_pengajuan
#                                         SET review_status = %s,
#                                             reviewed_by = %s,
#                                             review_date = GETDATE(),
#                                             review_notes = %s,
#                                             status = %s,
#                                             approve = %s,
#                                             final_section_id = %s,
#                                             number_wo = %s
#                                         WHERE history_id = %s
#                                     """, [
#                                         '1',                        # review_status = processed
#                                         REVIEWER_EMPLOYEE_NUMBER, 
#                                         review_notes,
#                                         STATUS_REVIEWED,            # A - final processed
#                                         APPROVE_REVIEWED,           # Y - final processed
#                                         float(final_section_id),   # Update section karena berubah
#                                         new_number_wo,
#                                         nomor_pengajuan
#                                     ])
#                                     logger.info(f"ENHANCED REVIEW: Updated with section change to {final_section_id}")
#                                 else:
#                                     # Jika section TIDAK berubah, TIDAK update final_section_id
#                                     cursor.execute("""
#                                         UPDATE tabel_pengajuan
#                                         SET review_status = %s,
#                                             reviewed_by = %s,
#                                             review_date = GETDATE(),
#                                             review_notes = %s,
#                                             status = %s,
#                                             approve = %s,
#                                             number_wo = %s
#                                         WHERE history_id = %s
#                                     """, [
#                                         '1',                        # review_status = processed
#                                         REVIEWER_EMPLOYEE_NUMBER, 
#                                         review_notes,
#                                         STATUS_REVIEWED,            # A - final processed
#                                         APPROVE_REVIEWED,           # Y - final processed
#                                         new_number_wo,              # Update number WO aja
#                                         nomor_pengajuan
#                                     ])
#                                     logger.info(f"ENHANCED REVIEW: Updated number WO only, section unchanged")
                                
#                                 update_count = cursor.rowcount
#                                 logger.info(f"ENHANCED REVIEW: Updated {update_count} row(s) in tabel_pengajuan")
                                
#                                 # ENHANCED: Transfer ke tabel_main dengan priority level
#                                 logger.info(f"ENHANCED REVIEW: Starting auto transfer to tabel_main for {nomor_pengajuan} with priority {priority_level}")
                                
#                                 # Check apakah data sudah ada di tabel_main
#                                 truncated_history_id = nomor_pengajuan[:11]
#                                 cursor.execute("""
#                                     SELECT COUNT(*) FROM tabel_main WHERE history_id = %s
#                                 """, [truncated_history_id])
#                                 exists_in_main = cursor.fetchone()[0] > 0
                                
#                                 transfer_success = False
                                
#                                 if not exists_in_main:
#                                     # ENHANCED: Gunakan section yang BENAR untuk transfer + priority level
#                                     if section_changed:
#                                         transfer_section_id = final_section_id
#                                         logger.info(f"ENHANCED REVIEW: Transfer with CHANGED section {transfer_section_id}")
#                                     else:
#                                         transfer_section_id = original_section_id
#                                         logger.info(f"ENHANCED REVIEW: Transfer with ORIGINAL section {transfer_section_id}")
                                    
#                                     # Insert data ke tabel_main dengan section ASLI + PriMa field
#                                     truncated_number_wo = new_number_wo[:15]
#                                     user_insert_truncated = pengajuan['user_insert'][:50] if pengajuan['user_insert'] else None
#                                     oleh_truncated = pengajuan['oleh'][:500] if pengajuan['oleh'] else '-'
                                    
#                                     # ENHANCED: Prepare PriMa value dengan validation
#                                     prima_value = priority_level if priority_level in ['BI', 'AI', 'AOL', 'AOI', 'BOL', 'BOI'] else None
                                    
#                                     logger.info(f"ENHANCED REVIEW: Inserting to tabel_main - Section: {transfer_section_id}, Number WO: {truncated_number_wo}, PriMa: {prima_value}")
                                    
#                                     insert_sql = """
#                                         INSERT INTO tabel_main (
#                                             history_id, tgl_his, jam_his, id_line, id_mesin, 
#                                             id_section, id_pekerjaan, number_wo, deskripsi_perbaikan,
#                                             pic_produksi, pic_maintenance, status, user_insert, 
#                                             tgl_insert, oleh, status_pekerjaan, PriMa
#                                         ) VALUES (
#                                             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
#                                         )
#                                     """
                                    
#                                     insert_params = [
#                                         truncated_history_id,
#                                         pengajuan['tgl_his'],
#                                         pengajuan['jam_his'],
#                                         float(pengajuan['id_line']) if pengajuan['id_line'] else None,
#                                         float(pengajuan['id_mesin']) if pengajuan['id_mesin'] else None,
#                                         float(transfer_section_id),             # CORRECT: Section asli atau yang berubah
#                                         float(pengajuan['id_pekerjaan']) if pengajuan['id_pekerjaan'] else None,
#                                         truncated_number_wo,                    # Number WO format baru
#                                         pengajuan['deskripsi_perbaikan'],
#                                         oleh_truncated,
#                                         '-',
#                                         'A',                                    # Status umum 'A'
#                                         user_insert_truncated,
#                                         pengajuan['tgl_insert'],
#                                         oleh_truncated,
#                                         'O',                                    # Status pekerjaan 'O'
#                                         prima_value                             # NEW: PriMa priority level
#                                     ]
                                    
#                                     cursor.execute(insert_sql, insert_params)
#                                     insert_count = cursor.rowcount
                                    
#                                     logger.info(f"ENHANCED REVIEW: Inserted {insert_count} row(s) to tabel_main with section {transfer_section_id} and priority {prima_value}")
#                                     transfer_success = True
                                    
#                                 else:
#                                     logger.warning(f"ENHANCED REVIEW: Data {nomor_pengajuan} already exists in tabel_main")
#                                     transfer_success = True
                                
#                                 # ENHANCED success message dengan number WO format baru + priority info
#                                 success_parts = []
#                                 success_parts.append(f'Pengajuan {nomor_pengajuan} berhasil diproses dan diselesaikan!')
                                
#                                 # Number WO info
#                                 section_code_map = {4: 'M', 5: 'E', 6: 'U', 8: 'I'}
#                                 current_section_code = section_code_map.get(final_section_id, 'X')
#                                 success_parts.append(f'Number WO: {new_number_wo} (format section {current_section_code})')
                                
#                                 # Priority info
#                                 if priority_level:
#                                     success_parts.append(f'Prioritas Pekerjaan: {priority_level}')
                                
#                                 success_parts.append(f'Status: Final Processed (A/Y)')
                                
#                                 if transfer_success:
#                                     success_parts.append(f'Data berhasil masuk ke History Maintenance')
                                
#                                 # Section info
#                                 success_parts.append(section_change_info)
                                
#                                 messages.success(request, '\n'.join(success_parts))
                                
#                                 logger.info(f"ENHANCED REVIEW SUCCESS SUMMARY:")
#                                 logger.info(f"  - Pengajuan: {nomor_pengajuan}")
#                                 logger.info(f"  - Section Changed: {section_changed}")
#                                 logger.info(f"  - Final Section ID: {final_section_id}")
#                                 logger.info(f"  - Number WO (NEW FORMAT): {new_number_wo}")
#                                 logger.info(f"  - Priority Level: {priority_level}")
#                                 logger.info(f"  - Transfer Success: {transfer_success}")
                                
#                             elif action == 'reject':
#                                 # Update pengajuan dengan review rejection
#                                 cursor.execute("""
#                                     UPDATE tabel_pengajuan
#                                     SET review_status = %s,
#                                         reviewed_by = %s,
#                                         review_date = GETDATE(),
#                                         review_notes = %s,
#                                         status = %s
#                                     WHERE history_id = %s
#                                 """, ['2', REVIEWER_EMPLOYEE_NUMBER, review_notes, STATUS_REJECTED, nomor_pengajuan])
                                
#                                 logger.info(f"ENHANCED REVIEW: Rejected pengajuan {nomor_pengajuan}")
#                                 messages.success(request, f'Pengajuan {nomor_pengajuan} berhasil ditolak. Alasan: {review_notes}')
                    
#                     logger.info(f"ENHANCED REVIEW: Transaction completed successfully for {nomor_pengajuan}")
                    
#                     request.session.modified = True
#                     request.session.save()
                    
#                     return redirect('wo_maintenance_app:review_pengajuan_detail', nomor_pengajuan=nomor_pengajuan)
                    
#                 except Exception as update_error:
#                     logger.error(f"ENHANCED REVIEW: Error processing review for {nomor_pengajuan}: {update_error}")
#                     import traceback
#                     logger.error(f"ENHANCED REVIEW: Traceback: {traceback.format_exc()}")
#                     messages.error(request, f'Terjadi kesalahan saat memproses review: {str(update_error)}')
#             else:
#                 logger.warning(f"ENHANCED REVIEW: Form validation failed for {nomor_pengajuan}: {review_form.errors}")
#                 messages.error(request, 'Form review tidak valid. Periksa kembali input Anda.')
#         else:
#             review_form = ReviewForm()
        
#         # FIXED: Available sections dengan mapping yang benar sesuai database
#         available_sections = [
#             {'key': 'mekanik', 'name': '🔧 Mekanik', 'section_id': 4, 'format_code': 'M', 'example': '25-M-08-0001'},
#             {'key': 'elektrik', 'name': '⚡ Elektrik', 'section_id': 5, 'format_code': 'E', 'example': '25-E-08-0001'},
#             {'key': 'utility', 'name': '🏭 Utility', 'section_id': 6, 'format_code': 'U', 'example': '25-U-08-0001'},
#             {'key': 'it', 'name': '💻 IT', 'section_id': 8, 'format_code': 'I', 'example': '25-I-08-0001'}
#         ]
        
#         # ENHANCED: Priority choices info
#         priority_choices = [
#             {'value': 'BI', 'label': 'BI - Basic Important', 'description': 'Prioritas basic yang penting'},
#             {'value': 'AI', 'label': 'AI - Advanced Important', 'description': 'Prioritas advanced yang penting'},
#             {'value': 'AOL', 'label': 'AOL - Advanced Online', 'description': 'Prioritas advanced online'},
#             {'value': 'AOI', 'label': 'AOI - Advanced Offline Important', 'description': 'Prioritas advanced offline penting'},
#             {'value': 'BOL', 'label': 'BOL - Basic Online', 'description': 'Prioritas basic online'},
#             {'value': 'BOI', 'label': 'BOI - Basic Offline Important', 'description': 'Prioritas basic offline penting'}
#         ]
        
#         context = {
#             'pengajuan': pengajuan,
#             'review_form': review_form,
#             'already_reviewed': already_reviewed,
#             'reviewer_name': employee_data.get('fullname', REVIEWER_FULLNAME),
#             'available_sections': available_sections,
#             'priority_choices': priority_choices,  # NEW: Priority choices for template
#             'employee_data': employee_data,
#             'page_title': f'ENHANCED Review dengan Priority Level {nomor_pengajuan}',
            
#             # Enhanced context dengan number WO info yang benar + priority
#             'enhanced_mode': True,
#             'priority_level_enabled': True,  # NEW: Flag for priority level feature
#             'always_new_format': True,
#             'current_number_wo': pengajuan['number_wo'],
#             'current_section_info': {
#                 'id': pengajuan['current_section_id'],
#                 'name': pengajuan['section_tujuan']
#             },
#             'format_info': {
#                 'description': 'Number WO akan selalu menggunakan format baru: YY-S-MM-NNNN',
#                 'based_on_section': 'Berdasarkan section tujuan (4=M, 5=E, 6=U, 8=I)',
#                 'section_mapping': '4=Mekanik(M), 5=Elektrik(E), 6=Utility(U), 8=IT(I)',
#                 'priority_info': 'Priority Level akan disimpan ke field PriMa di tabel_main'  # NEW
#             },
            
#             # Status constants untuk template
#             'STATUS_APPROVED': STATUS_APPROVED,
#             'STATUS_REVIEWED': STATUS_REVIEWED,
#             'APPROVE_YES': APPROVE_YES,
#             'APPROVE_REVIEWED': APPROVE_REVIEWED
#         }
        
#         logger.info(f"ENHANCED REVIEW: Rendering template dengan priority level support untuk {nomor_pengajuan}")
#         return render(request, 'wo_maintenance_app/review_pengajuan_detail.html', context)
        
#     except Exception as e:
#         logger.error(f"ENHANCED REVIEW: Critical error for {nomor_pengajuan}: {e}")
#         import traceback
#         logger.error(f"ENHANCED REVIEW: Traceback: {traceback.format_exc()}")
#         messages.error(request, 'Terjadi kesalahan saat memuat detail review.')
#         return redirect('wo_maintenance_app:review_pengajuan_list')

# @login_required
# @reviewer_required_fixed
# def review_pengajuan_detail(request, nomor_pengajuan):
#     """
#     ENHANCED: Detail pengajuan untuk review oleh SITI FATIMAH dengan priority level support
#     FIXED: Section mapping untuk 4=M, 5=E, 6=U, 8=I sesuai database + Priority Level
#     """
#     try:
#         logger.info(f"ENHANCED REVIEW: Starting review for {nomor_pengajuan} by {request.user.username}")
        
#         employee_data = get_employee_data_for_request_fixed(request)
        
#         if not employee_data:
#             logger.error(f"ENHANCED REVIEW: No employee data for {request.user.username}")
#             messages.error(request, 'Data employee tidak ditemukan. Silakan login ulang.')
#             return redirect('login')
        
#         initialize_review_data()
        
#         # Ambil data pengajuan
#         pengajuan = None
        
#         with connections['DB_Maintenance'].cursor() as cursor:
#             cursor.execute("""
#                 SELECT 
#                     tp.history_id, tp.number_wo, tp.tgl_insert, tp.oleh, tp.user_insert,
#                     tm.mesin, tms.seksi as section_tujuan, tpek.pekerjaan,
#                     tp.deskripsi_perbaikan, tp.status, tp.approve, tl.line as line_name,
#                     tp.tgl_his, tp.jam_his, tp.review_status, tp.reviewed_by,
#                     tp.review_date, tp.review_notes, tp.final_section_id,
#                     final_section.seksi as final_section_name, tp.status_pekerjaan,
#                     tp.id_section as current_section_id, tp.id_line, tp.id_mesin,
#                     tp.id_pekerjaan
#                 FROM tabel_pengajuan tp
#                 LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
#                 LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
#                 LEFT JOIN tabel_msection tms ON tp.id_section = tms.id_section
#                 LEFT JOIN tabel_pekerjaan tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
#                 LEFT JOIN tabel_msection final_section ON tp.final_section_id = final_section.id_section
#                 WHERE tp.history_id = %s
#             """, [nomor_pengajuan])
            
#             row = cursor.fetchone()
            
#             if not row:
#                 logger.error(f"ENHANCED REVIEW: Pengajuan {nomor_pengajuan} not found")
#                 messages.error(request, 'Pengajuan tidak ditemukan.')
#                 return redirect('wo_maintenance_app:review_pengajuan_list')
            
#             pengajuan = {
#                 'history_id': row[0], 'number_wo': row[1], 'tgl_insert': row[2],
#                 'oleh': row[3], 'user_insert': row[4], 'mesin': row[5],
#                 'section_tujuan': row[6], 'pekerjaan': row[7], 'deskripsi_perbaikan': row[8],
#                 'status': row[9], 'approve': row[10], 'line_name': row[11],
#                 'tgl_his': row[12], 'jam_his': row[13], 'review_status': row[14],
#                 'reviewed_by': row[15], 'review_date': row[16], 'review_notes': row[17],
#                 'final_section_id': row[18], 'final_section_name': row[19],
#                 'status_pekerjaan': row[20], 'current_section_id': row[21],
#                 'id_line': row[22], 'id_mesin': row[23], 'id_pekerjaan': row[24]
#             }
        
#         # Cek apakah pengajuan siap di-review
#         if pengajuan['status'] != STATUS_APPROVED or pengajuan['approve'] != APPROVE_YES:
#             logger.warning(f"ENHANCED REVIEW: Pengajuan {nomor_pengajuan} not approved")
#             messages.warning(request, 'Pengajuan ini belum di-approve oleh atasan.')
#             return redirect('wo_maintenance_app:review_pengajuan_list')
        
#         already_reviewed = pengajuan['review_status'] in ['1', '2']
        
#         # Handle review form submission dengan ENHANCED NUMBER WO LOGIC + PRIORITY LEVEL
#         if request.method == 'POST' and not already_reviewed:
#             logger.info(f"ENHANCED REVIEW: Processing POST with priority level for {nomor_pengajuan}")
            
#             request.session.modified = True
            
#             review_form = ReviewForm(request.POST)
            
#             if review_form.is_valid():
#                 action = review_form.cleaned_data['action']
#                 target_section = review_form.cleaned_data.get('target_section', '').strip()
#                 priority_level = review_form.cleaned_data.get('priority_level', '').strip()  # NEW: Priority level
#                 review_notes = review_form.cleaned_data['review_notes']
                
#                 logger.info(f"ENHANCED REVIEW: Form valid - Action: {action}, Target: {target_section}, Priority: {priority_level}")
                
#                 try:
#                     with transaction.atomic(using='DB_Maintenance'):
#                         with connections['DB_Maintenance'].cursor() as cursor:
                            
#                             if action == 'process':
#                                 # FIXED: Preserve original section, hanya validate target section
#                                 original_section_id = pengajuan['current_section_id']
#                                 final_section_id = original_section_id  # Default ke original section
#                                 section_changed = False
#                                 section_change_info = ""
                                
#                                 logger.info(f"ENHANCED REVIEW: Original section from database - ID: {original_section_id}")
                                
#                                 if target_section:
#                                     # FIXED: Mapping section sesuai database aktual (4=M, 5=E, 6=U, 8=I)
#                                     section_mapping = {
#                                         'mekanik': 4,    # Mekanik = 4 
#                                         'elektrik': 5,   # Elektrik = 5
#                                         'utility': 6,    # Utility = 6
#                                         'it': 8          # IT = 8
#                                     }
                                    
#                                     if target_section in section_mapping:
#                                         target_section_id = section_mapping[target_section]
                                        
#                                         # Check if section actually changes
#                                         if target_section_id != original_section_id:
#                                             section_changed = True
#                                             final_section_id = target_section_id
#                                             section_change_info = f"Section berubah dari {pengajuan['section_tujuan']} (ID: {original_section_id}) ke {target_section.title()} (ID: {target_section_id})"
#                                             logger.info(f"ENHANCED REVIEW: Section changed from {original_section_id} to {target_section_id}")
#                                         else:
#                                             # Target sama dengan current
#                                             final_section_id = target_section_id
#                                             section_change_info = f"Section dikonfirmasi tetap di {target_section.title()} (ID: {target_section_id})"
#                                             logger.info(f"ENHANCED REVIEW: Section confirmed at {target_section_id}")
#                                     else:
#                                         logger.warning(f"ENHANCED REVIEW: Unknown target_section {target_section}")
#                                         final_section_id = original_section_id
#                                         section_change_info = f"Section tetap di {pengajuan['section_tujuan']} (ID: {original_section_id}) - target tidak valid"
#                                 else:
#                                     final_section_id = original_section_id
#                                     section_change_info = f"Section tetap di {pengajuan['section_tujuan']} (ID: {original_section_id})"
#                                     logger.info(f"ENHANCED REVIEW: No target section specified, keeping original section {original_section_id}")
                                
#                                 # FIXED: Generate number WO berdasarkan final section dengan mapping yang benar
#                                 from wo_maintenance_app.models import create_number_wo_with_section_fixed
                                
#                                 # FIXED: Support untuk section 4, 5, 6, 8 sesuai database
#                                 if final_section_id in [4, 5, 6, 8]:
#                                     new_number_wo = create_number_wo_with_section_fixed(final_section_id)
#                                     logger.info(f"ENHANCED REVIEW: Generated Number WO: {new_number_wo} for mapped section {final_section_id}")
#                                 else:
#                                     # Section lain, gunakan fallback ke IT (section 8)
#                                     fallback_section = 8  # IT sebagai default
#                                     new_number_wo = create_number_wo_with_section_fixed(fallback_section)
#                                     logger.info(f"ENHANCED REVIEW: Generated Number WO: {new_number_wo} for unmapped section {final_section_id} (using IT fallback)")
                                
#                                 # VALIDATION: Log section info
#                                 logger.info(f"ENHANCED REVIEW: Section Summary:")
#                                 logger.info(f"  - Original Section ID: {original_section_id}")
#                                 logger.info(f"  - Final Section ID: {final_section_id}")
#                                 logger.info(f"  - Section Changed: {section_changed}")
#                                 logger.info(f"  - Generated Number WO: {new_number_wo}")
#                                 logger.info(f"  - Priority Level: {priority_level}")
                                
#                                 # ENHANCED: Update review status dengan conditional section update + priority
#                                 if section_changed:
#                                     # Jika section berubah, update final_section_id
#                                     cursor.execute("""
#                                         UPDATE tabel_pengajuan
#                                         SET review_status = %s,
#                                             reviewed_by = %s,
#                                             review_date = GETDATE(),
#                                             review_notes = %s,
#                                             status = %s,
#                                             approve = %s,
#                                             final_section_id = %s,
#                                             number_wo = %s
#                                         WHERE history_id = %s
#                                     """, [
#                                         '1',                        # review_status = processed
#                                         REVIEWER_EMPLOYEE_NUMBER, 
#                                         review_notes,
#                                         STATUS_REVIEWED,            # A - final processed
#                                         APPROVE_REVIEWED,           # Y - final processed
#                                         float(final_section_id),   # Update section karena berubah
#                                         new_number_wo,
#                                         nomor_pengajuan
#                                     ])
#                                     logger.info(f"ENHANCED REVIEW: Updated with section change to {final_section_id}")
#                                 else:
#                                     # Jika section TIDAK berubah, TIDAK update final_section_id
#                                     cursor.execute("""
#                                         UPDATE tabel_pengajuan
#                                         SET review_status = %s,
#                                             reviewed_by = %s,
#                                             review_date = GETDATE(),
#                                             review_notes = %s,
#                                             status = %s,
#                                             approve = %s,
#                                             number_wo = %s
#                                         WHERE history_id = %s
#                                     """, [
#                                         '1',                        # review_status = processed
#                                         REVIEWER_EMPLOYEE_NUMBER, 
#                                         review_notes,
#                                         STATUS_REVIEWED,            # A - final processed
#                                         APPROVE_REVIEWED,           # Y - final processed
#                                         new_number_wo,              # Update number WO aja
#                                         nomor_pengajuan
#                                     ])
#                                     logger.info(f"ENHANCED REVIEW: Updated number WO only, section unchanged")
                                
#                                 update_count = cursor.rowcount
#                                 logger.info(f"ENHANCED REVIEW: Updated {update_count} row(s) in tabel_pengajuan")
                                
#                                 # ENHANCED: Transfer ke tabel_main dengan priority level
#                                 logger.info(f"ENHANCED REVIEW: Starting auto transfer to tabel_main for {nomor_pengajuan} with priority {priority_level}")
                                
#                                 # Check apakah data sudah ada di tabel_main
#                                 truncated_history_id = nomor_pengajuan[:11]
#                                 cursor.execute("""
#                                     SELECT COUNT(*) FROM tabel_main WHERE history_id = %s
#                                 """, [truncated_history_id])
#                                 exists_in_main = cursor.fetchone()[0] > 0
                                
#                                 transfer_success = False
                                
#                                 if not exists_in_main:
#                                     # ENHANCED: Gunakan section yang BENAR untuk transfer + priority level
#                                     if section_changed:
#                                         transfer_section_id = final_section_id
#                                         logger.info(f"ENHANCED REVIEW: Transfer with CHANGED section {transfer_section_id}")
#                                     else:
#                                         transfer_section_id = original_section_id
#                                         logger.info(f"ENHANCED REVIEW: Transfer with ORIGINAL section {transfer_section_id}")
                                    
#                                     # Insert data ke tabel_main dengan section ASLI + PriMa field
#                                     truncated_number_wo = new_number_wo[:15]
#                                     user_insert_truncated = pengajuan['user_insert'][:50] if pengajuan['user_insert'] else None
#                                     oleh_truncated = pengajuan['oleh'][:500] if pengajuan['oleh'] else '-'
                                    
#                                     # ENHANCED: Prepare PriMa value dengan validation
#                                     prima_value = priority_level if priority_level in ['BI', 'AI', 'AOL', 'AOI', 'BOL', 'BOI'] else None
                                    
#                                     logger.info(f"ENHANCED REVIEW: Inserting to tabel_main - Section: {transfer_section_id}, Number WO: {truncated_number_wo}, PriMa: {prima_value}")
                                    
#                                     insert_sql = """
#                                         INSERT INTO tabel_main (
#                                             history_id, tgl_his, jam_his, id_line, id_mesin, 
#                                             id_section, id_pekerjaan, number_wo, deskripsi_perbaikan,
#                                             pic_produksi, pic_maintenance, status, user_insert, 
#                                             tgl_insert, oleh, status_pekerjaan, PriMa
#                                         ) VALUES (
#                                             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
#                                         )
#                                     """
                                    
#                                     insert_params = [
#                                         truncated_history_id,
#                                         pengajuan['tgl_his'],
#                                         pengajuan['jam_his'],
#                                         float(pengajuan['id_line']) if pengajuan['id_line'] else None,
#                                         float(pengajuan['id_mesin']) if pengajuan['id_mesin'] else None,
#                                         float(transfer_section_id),             # CORRECT: Section asli atau yang berubah
#                                         float(pengajuan['id_pekerjaan']) if pengajuan['id_pekerjaan'] else None,
#                                         truncated_number_wo,                    # Number WO format baru
#                                         pengajuan['deskripsi_perbaikan'],
#                                         oleh_truncated,
#                                         '-',
#                                         'A',                                    # Status umum 'A'
#                                         user_insert_truncated,
#                                         pengajuan['tgl_insert'],
#                                         oleh_truncated,
#                                         'O',                                    # Status pekerjaan 'O'
#                                         prima_value                             # NEW: PriMa priority level
#                                     ]
                                    
#                                     cursor.execute(insert_sql, insert_params)
#                                     insert_count = cursor.rowcount
                                    
#                                     logger.info(f"ENHANCED REVIEW: Inserted {insert_count} row(s) to tabel_main with section {transfer_section_id} and priority {prima_value}")
#                                     transfer_success = True
                                    
#                                 else:
#                                     logger.warning(f"ENHANCED REVIEW: Data {nomor_pengajuan} already exists in tabel_main")
#                                     transfer_success = True
                                
#                                 # ENHANCED success message dengan number WO format baru + priority info
#                                 success_parts = []
#                                 success_parts.append(f'Pengajuan {nomor_pengajuan} berhasil diproses dan diselesaikan!')
                                
#                                 # Number WO info
#                                 section_code_map = {4: 'M', 5: 'E', 6: 'U', 8: 'I'}
#                                 current_section_code = section_code_map.get(final_section_id, 'X')
#                                 success_parts.append(f'Number WO: {new_number_wo} (format section {current_section_code})')
                                
#                                 # Priority info
#                                 if priority_level:
#                                     success_parts.append(f'Prioritas Pekerjaan: {priority_level}')
                                
#                                 success_parts.append(f'Status: Final Processed (A/Y)')
                                
#                                 if transfer_success:
#                                     success_parts.append(f'Data berhasil masuk ke History Maintenance')
                                
#                                 # Section info
#                                 success_parts.append(section_change_info)
                                
#                                 messages.success(request, '\n'.join(success_parts))
                                
#                                 logger.info(f"ENHANCED REVIEW SUCCESS SUMMARY:")
#                                 logger.info(f"  - Pengajuan: {nomor_pengajuan}")
#                                 logger.info(f"  - Section Changed: {section_changed}")
#                                 logger.info(f"  - Final Section ID: {final_section_id}")
#                                 logger.info(f"  - Number WO (NEW FORMAT): {new_number_wo}")
#                                 logger.info(f"  - Priority Level: {priority_level}")
#                                 logger.info(f"  - Transfer Success: {transfer_success}")
                                
#                             elif action == 'reject':
#                                 # Update pengajuan dengan review rejection
#                                 cursor.execute("""
#                                     UPDATE tabel_pengajuan
#                                     SET review_status = %s,
#                                         reviewed_by = %s,
#                                         review_date = GETDATE(),
#                                         review_notes = %s,
#                                         status = %s
#                                     WHERE history_id = %s
#                                 """, ['2', REVIEWER_EMPLOYEE_NUMBER, review_notes, STATUS_REJECTED, nomor_pengajuan])
                                
#                                 logger.info(f"ENHANCED REVIEW: Rejected pengajuan {nomor_pengajuan}")
#                                 messages.success(request, f'Pengajuan {nomor_pengajuan} berhasil ditolak. Alasan: {review_notes}')
                    
#                     logger.info(f"ENHANCED REVIEW: Transaction completed successfully for {nomor_pengajuan}")
                    
#                     request.session.modified = True
#                     request.session.save()
                    
#                     return redirect('wo_maintenance_app:review_pengajuan_detail', nomor_pengajuan=nomor_pengajuan)
                    
#                 except Exception as update_error:
#                     logger.error(f"ENHANCED REVIEW: Error processing review for {nomor_pengajuan}: {update_error}")
#                     import traceback
#                     logger.error(f"ENHANCED REVIEW: Traceback: {traceback.format_exc()}")
#                     messages.error(request, f'Terjadi kesalahan saat memproses review: {str(update_error)}')
#             else:
#                 logger.warning(f"ENHANCED REVIEW: Form validation failed for {nomor_pengajuan}: {review_form.errors}")
#                 messages.error(request, 'Form review tidak valid. Periksa kembali input Anda.')
#         else:
#             review_form = ReviewForm()
        
#         # FIXED: Available sections dengan mapping yang benar sesuai database
#         available_sections = [
#             {'key': 'mekanik', 'name': '🔧 Mekanik', 'section_id': 4, 'format_code': 'M', 'example': '25-M-08-0001'},
#             {'key': 'elektrik', 'name': '⚡ Elektrik', 'section_id': 5, 'format_code': 'E', 'example': '25-E-08-0001'},
#             {'key': 'utility', 'name': '🏭 Utility', 'section_id': 6, 'format_code': 'U', 'example': '25-U-08-0001'},
#             {'key': 'it', 'name': '💻 IT', 'section_id': 8, 'format_code': 'I', 'example': '25-I-08-0001'}
#         ]
        
#         # ENHANCED: Priority choices info
#         priority_choices = [
#             {'value': 'BI', 'label': 'BI - Basic Important', 'description': 'Prioritas basic yang penting'},
#             {'value': 'AI', 'label': 'AI - Advanced Important', 'description': 'Prioritas advanced yang penting'},
#             {'value': 'AOL', 'label': 'AOL - Advanced Online', 'description': 'Prioritas advanced online'},
#             {'value': 'AOI', 'label': 'AOI - Advanced Offline Important', 'description': 'Prioritas advanced offline penting'},
#             {'value': 'BOL', 'label': 'BOL - Basic Online', 'description': 'Prioritas basic online'},
#             {'value': 'BOI', 'label': 'BOI - Basic Offline Important', 'description': 'Prioritas basic offline penting'}
#         ]
        
#         context = {
#             'pengajuan': pengajuan,
#             'review_form': review_form,
#             'already_reviewed': already_reviewed,
#             'reviewer_name': employee_data.get('fullname', REVIEWER_FULLNAME),
#             'available_sections': available_sections,
#             'priority_choices': priority_choices,  # NEW: Priority choices for template
#             'employee_data': employee_data,
#             'page_title': f'ENHANCED Review dengan Priority Level {nomor_pengajuan}',
            
#             # Enhanced context dengan number WO info yang benar + priority
#             'enhanced_mode': True,
#             'priority_level_enabled': True,  # NEW: Flag for priority level feature
#             'always_new_format': True,
#             'current_number_wo': pengajuan['number_wo'],
#             'current_section_info': {
#                 'id': pengajuan['current_section_id'],
#                 'name': pengajuan['section_tujuan']
#             },
#             'format_info': {
#                 'description': 'Number WO akan selalu menggunakan format baru: YY-S-MM-NNNN',
#                 'based_on_section': 'Berdasarkan section tujuan (4=M, 5=E, 6=U, 8=I)',
#                 'section_mapping': '4=Mekanik(M), 5=Elektrik(E), 6=Utility(U), 8=IT(I)',
#                 'priority_info': 'Priority Level akan disimpan ke field PriMa di tabel_main'  # NEW
#             },
            
#             # Status constants untuk template
#             'STATUS_APPROVED': STATUS_APPROVED,
#             'STATUS_REVIEWED': STATUS_REVIEWED,
#             'APPROVE_YES': APPROVE_YES,
#             'APPROVE_REVIEWED': APPROVE_REVIEWED
#         }
        
#         logger.info(f"ENHANCED REVIEW: Rendering template dengan priority level support untuk {nomor_pengajuan}")
#         return render(request, 'wo_maintenance_app/review_pengajuan_detail.html', context)
        
#     except Exception as e:
#         logger.error(f"ENHANCED REVIEW: Critical error for {nomor_pengajuan}: {e}")
#         import traceback
#         logger.error(f"ENHANCED REVIEW: Traceback: {traceback.format_exc()}")
#         messages.error(request, 'Terjadi kesalahan saat memuat detail review.')
#         return redirect('wo_maintenance_app:review_pengajuan_list')

@login_required
@reviewer_required_fixed
def review_pengajuan_detail(request, nomor_pengajuan):
    """
    ENHANCED: Detail pengajuan untuk review oleh SITI FATIMAH 
    dengan AUTO TRANSFER CHECKER dari pengajuan ke diproses
    """
    try:
        logger.info(f"ENHANCED REVIEW dengan CHECKER TRANSFER: Starting review for {nomor_pengajuan} by {request.user.username}")
        
        employee_data = get_employee_data_for_request_fixed(request)
        
        if not employee_data:
            logger.error(f"ENHANCED REVIEW: No employee data for {request.user.username}")
            messages.error(request, 'Data employee ga ketemu bro. Silakan login ulang.')
            return redirect('login')
        
        initialize_review_data()
        # Ambil data pengajuan
        pengajuan = None
        
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT 
                    tp.history_id, tp.number_wo, tp.tgl_insert, tp.oleh, tp.user_insert,
                    tm.mesin, tms.seksi as section_tujuan, tpek.pekerjaan,
                    tp.deskripsi_perbaikan, tp.status, tp.approve, tl.line as line_name,
                    tp.tgl_his, tp.jam_his, tp.review_status, tp.reviewed_by,
                    tp.review_date, tp.review_notes, tp.final_section_id,
                    final_section.seksi as final_section_name, tp.status_pekerjaan,
                    tp.id_section as current_section_id, tp.id_line, tp.id_mesin,
                    tp.id_pekerjaan,
                    tp.checker_name, tp.checker_time, tp.checker_status  -- NEW: Checker info
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
                messages.error(request, 'Pengajuan ga ketemu bro.')
                return redirect('wo_maintenance_app:review_pengajuan_list')
            
            pengajuan = {
                'history_id': row[0], 'number_wo': row[1], 'tgl_insert': row[2],
                'oleh': row[3], 'user_insert': row[4], 'mesin': row[5],
                'section_tujuan': row[6], 'pekerjaan': row[7], 'deskripsi_perbaikan': row[8],
                'status': row[9], 'approve': row[10], 'line_name': row[11],
                'tgl_his': row[12], 'jam_his': row[13], 'review_status': row[14],
                'reviewed_by': row[15], 'review_date': row[16], 'review_notes': row[17],
                'final_section_id': row[18], 'final_section_name': row[19],
                'status_pekerjaan': row[20], 'current_section_id': row[21],
                'id_line': row[22], 'id_mesin': row[23], 'id_pekerjaan': row[24],
                # NEW: Checker data
                'checker_name': row[25], 'checker_time': row[26], 'checker_status': row[27]
            }
        
        # Cek apakah pengajuan siap di-review
        if pengajuan['status'] != STATUS_APPROVED or pengajuan['approve'] != APPROVE_YES:
            logger.warning(f"ENHANCED REVIEW: Pengajuan {nomor_pengajuan} belum di-approve")
            messages.warning(request, 'Pengajuan ini belum di-approve sama atasan dulu bro.')
            return redirect('wo_maintenance_app:review_pengajuan_list')
        
        already_reviewed = pengajuan['review_status'] in ['1', '2']
        
        # NEW: Checker info untuk display
        has_checker_in_pengajuan = bool(pengajuan['checker_status'] == '1' and pengajuan['checker_name'])
        
        # Handle review form submission dengan ENHANCED CHECKER TRANSFER
        if request.method == 'POST' and not already_reviewed:
            logger.info(f"ENHANCED REVIEW dengan CHECKER TRANSFER: Processing POST for {nomor_pengajuan}")
            
            review_form = ReviewForm(request.POST)
            
            if review_form.is_valid():
                action = review_form.cleaned_data['action']
                target_section = review_form.cleaned_data.get('target_section', '').strip()
                priority_level = review_form.cleaned_data.get('priority_level', '').strip()
                review_notes = review_form.cleaned_data['review_notes']
                
                logger.info(f"ENHANCED REVIEW: Form valid - Action: {action}, Target: {target_section}, Priority: {priority_level}")
                logger.info(f"CHECKER INFO: Has checker in pengajuan = {has_checker_in_pengajuan}")
                
                try:
                    with transaction.atomic(using='DB_Maintenance'):
                        with connections['DB_Maintenance'].cursor() as cursor:
                            
                            if action == 'process':
                                # Section mapping logic (same as before)
                                original_section_id = pengajuan['current_section_id']
                                final_section_id = original_section_id
                                section_changed = False
                                
                                if target_section:
                                    section_mapping = {
                                        'mekanik': 4, 'elektrik': 5, 'utility': 6, 'it': 8
                                    }
                                    
                                    if target_section in section_mapping:
                                        target_section_id = section_mapping[target_section]
                                        if target_section_id != original_section_id:
                                            section_changed = True
                                            final_section_id = target_section_id
                                
                                # Generate number WO
                                from wo_maintenance_app.models import create_number_wo_with_section_fixed
                                if final_section_id in [4, 5, 6, 8]:
                                    new_number_wo = create_number_wo_with_section_fixed(final_section_id)
                                else:
                                    new_number_wo = create_number_wo_with_section_fixed(8)  # IT fallback
                                
                                logger.info(f"ENHANCED REVIEW: Generated Number WO: {new_number_wo}")
                                
                                # Update review status di tabel_pengajuan
                                if section_changed:
                                    cursor.execute("""
                                        UPDATE tabel_pengajuan
                                        SET review_status = %s,
                                            reviewed_by = %s,
                                            review_date = GETDATE(),
                                            review_notes = %s,
                                            status = %s,
                                            approve = %s,
                                            final_section_id = %s,
                                            number_wo = %s
                                        WHERE history_id = %s
                                    """, [
                                        '1', REVIEWER_EMPLOYEE_NUMBER, review_notes,
                                        STATUS_REVIEWED, APPROVE_REVIEWED,
                                        float(final_section_id), new_number_wo, nomor_pengajuan
                                    ])
                                else:
                                    cursor.execute("""
                                        UPDATE tabel_pengajuan
                                        SET review_status = %s,
                                            reviewed_by = %s,
                                            review_date = GETDATE(),
                                            review_notes = %s,
                                            status = %s,
                                            approve = %s,
                                            number_wo = %s
                                        WHERE history_id = %s
                                    """, [
                                        '1', REVIEWER_EMPLOYEE_NUMBER, review_notes,
                                        STATUS_REVIEWED, APPROVE_REVIEWED,
                                        new_number_wo, nomor_pengajuan
                                    ])
                                
                                # ENHANCED: Transfer ke tabel_main dengan CHECKER AUTO TRANSFER
                                logger.info(f"ENHANCED REVIEW: Starting auto transfer to tabel_main dengan CHECKER TRANSFER")
                                
                                truncated_history_id = nomor_pengajuan[:11]
                                cursor.execute("""
                                    SELECT COUNT(*) FROM tabel_main WHERE history_id = %s
                                """, [truncated_history_id])
                                exists_in_main = cursor.fetchone()[0] > 0
                                
                                transfer_success = False
                                checker_transfer_result = {'transferred': False, 'message': ''}
                                
                                if not exists_in_main:
                                    # Insert data ke tabel_main
                                    transfer_section_id = final_section_id if section_changed else original_section_id
                                    truncated_number_wo = new_number_wo[:15]
                                    user_insert_truncated = pengajuan['user_insert'][:50] if pengajuan['user_insert'] else None
                                    oleh_truncated = pengajuan['oleh'][:500] if pengajuan['oleh'] else '-'
                                    prima_value = priority_level if priority_level in ['BI', 'AI', 'AOL', 'AOI', 'BOL', 'BOI'] else None
                                    
                                    logger.info(f"ENHANCED REVIEW: Inserting to tabel_main - Section: {transfer_section_id}, PriMa: {prima_value}")
                                    
                                    cursor.execute("""
                                        INSERT INTO tabel_main (
                                            history_id, tgl_his, jam_his, id_line, id_mesin, 
                                            id_section, id_pekerjaan, number_wo, deskripsi_perbaikan,
                                            pic_produksi, pic_maintenance, status, user_insert, 
                                            tgl_insert, oleh, status_pekerjaan, PriMa
                                        ) VALUES (
                                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                                        )
                                    """, [
                                        truncated_history_id, pengajuan['tgl_his'], pengajuan['jam_his'],
                                        float(pengajuan['id_line']) if pengajuan['id_line'] else None,
                                        float(pengajuan['id_mesin']) if pengajuan['id_mesin'] else None,
                                        float(transfer_section_id),
                                        float(pengajuan['id_pekerjaan']) if pengajuan['id_pekerjaan'] else None,
                                        truncated_number_wo, pengajuan['deskripsi_perbaikan'],
                                        oleh_truncated, '-', 'A', user_insert_truncated,
                                        pengajuan['tgl_insert'], oleh_truncated, 'O', prima_value
                                    ])
                                    
                                    transfer_success = True
                                    
                                    # ENHANCED: AUTO TRANSFER CHECKER dari tabel_pengajuan ke tabel_main
                                    if has_checker_in_pengajuan:
                                        logger.info(f"ENHANCED CHECKER TRANSFER: Found checker in pengajuan: {pengajuan['checker_name']}")
                                        checker_transfer_result = transfer_checker_on_review_process(
                                            nomor_pengajuan, 
                                            REVIEWER_EMPLOYEE_NUMBER
                                        )
                                        logger.info(f"ENHANCED CHECKER TRANSFER: Result = {checker_transfer_result}")
                                    else:
                                        logger.info(f"ENHANCED CHECKER TRANSFER: No checker found in pengajuan")
                                        checker_transfer_result = {'transferred': False, 'message': 'Tidak ada checker untuk di-transfer'}
                                else:
                                    logger.warning(f"ENHANCED REVIEW: Data {nomor_pengajuan} already exists in tabel_main")
                                    transfer_success = True
                                    
                                    # Cek apakah perlu transfer checker untuk data yang sudah ada
                                    if has_checker_in_pengajuan:
                                        checker_transfer_result = transfer_checker_on_review_process(
                                            nomor_pengajuan, 
                                            REVIEWER_EMPLOYEE_NUMBER
                                        )
                                
                                # ENHANCED success message dengan checker transfer info
                                success_parts = []
                                success_parts.append(f'Pengajuan {nomor_pengajuan} berhasil diproses!')
                                
                                section_code_map = {4: 'M', 5: 'E', 6: 'U', 8: 'I'}
                                current_section_code = section_code_map.get(final_section_id, 'X')
                                success_parts.append(f'Number WO: {new_number_wo} (section {current_section_code})')
                                
                                if priority_level:
                                    success_parts.append(f'Prioritas: {priority_level}')
                                
                                success_parts.append(f'Status: Final Processed (A/Y)')
                                
                                if transfer_success:
                                    success_parts.append(f'Data berhasil masuk ke History Maintenance')
                                
                                # NEW: Checker transfer result
                                if checker_transfer_result['transferred']:
                                    success_parts.append(f'✅ Checker berhasil di-transfer ke tabel_main: {pengajuan["checker_name"]}')
                                elif has_checker_in_pengajuan and not checker_transfer_result['transferred']:
                                    success_parts.append(f'⚠️ Checker transfer gagal: {checker_transfer_result["message"]}')
                                else:
                                    success_parts.append(f'ℹ️ Tidak ada checker untuk di-transfer')
                                
                                messages.success(request, '\n'.join(success_parts))
                                
                                logger.info(f"ENHANCED REVIEW SUCCESS dengan CHECKER TRANSFER:")
                                logger.info(f"  - Pengajuan: {nomor_pengajuan}")
                                logger.info(f"  - Number WO: {new_number_wo}")
                                logger.info(f"  - Priority: {priority_level}")
                                logger.info(f"  - Transfer Success: {transfer_success}")
                                logger.info(f"  - Checker Transfer: {checker_transfer_result}")
                                
                            elif action == 'reject':
                                # Update pengajuan dengan review rejection
                                cursor.execute("""
                                    UPDATE tabel_pengajuan
                                    SET review_status = %s,
                                        reviewed_by = %s,
                                        review_date = GETDATE(),
                                        review_notes = %s,
                                        status = %s
                                    WHERE history_id = %s
                                """, ['2', REVIEWER_EMPLOYEE_NUMBER, review_notes, STATUS_REJECTED, nomor_pengajuan])
                                
                                logger.info(f"ENHANCED REVIEW: Rejected pengajuan {nomor_pengajuan}")
                                messages.success(request, f'Pengajuan {nomor_pengajuan} berhasil ditolak. Alasan: {review_notes}')
                    
                    logger.info(f"ENHANCED REVIEW dengan CHECKER TRANSFER: Transaction completed for {nomor_pengajuan}")
                    return redirect('wo_maintenance_app:review_pengajuan_detail', nomor_pengajuan=nomor_pengajuan)
                    
                except Exception as update_error:
                    logger.error(f"ENHANCED REVIEW: Error processing review with checker transfer: {update_error}")
                    messages.error(request, f'Terjadi kesalahan saat memproses review: {str(update_error)}')
            else:
                logger.warning(f"ENHANCED REVIEW: Form validation failed: {review_form.errors}")
                messages.error(request, 'Form review ga valid bro. Cek lagi input-nya.')
        else:
            review_form = ReviewForm()
        
        # Available sections
        available_sections = [
            {'key': 'mekanik', 'name': '🔧 Mekanik', 'section_id': 4, 'format_code': 'M'},
            {'key': 'elektrik', 'name': '⚡ Elektrik', 'section_id': 5, 'format_code': 'E'},
            {'key': 'utility', 'name': '🏭 Utility', 'section_id': 6, 'format_code': 'U'},
            {'key': 'it', 'name': '💻 IT', 'section_id': 8, 'format_code': 'I'}
        ]
        
        priority_choices = [
            {'value': 'BI', 'label': 'BI - Basic Important'},
            {'value': 'AI', 'label': 'AI - Advanced Important'},
            {'value': 'AOL', 'label': 'AOL - Advanced Online'},
            {'value': 'AOI', 'label': 'AOI - Advanced Offline Important'},
            {'value': 'BOL', 'label': 'BOL - Basic Online'},
            {'value': 'BOI', 'label': 'BOI - Basic Offline Important'}
        ]
        
        context = {
            'pengajuan': pengajuan,
            'review_form': review_form,
            'already_reviewed': already_reviewed,
            'reviewer_name': employee_data.get('fullname', REVIEWER_FULLNAME),
            'available_sections': available_sections,
            'priority_choices': priority_choices,
            'employee_data': employee_data,
            
            # NEW: Checker context
            'has_checker_in_pengajuan': has_checker_in_pengajuan,
            'checker_info': {
                'name': pengajuan.get('checker_name', ''),
                'time': pengajuan.get('checker_time', ''),
                'status': pengajuan.get('checker_status', '0')
            } if has_checker_in_pengajuan else None,
            
            'page_title': f'ENHANCED Review dengan Auto Checker Transfer - {nomor_pengajuan}',
            'enhanced_mode': True,
            'priority_level_enabled': True,
            'checker_transfer_enabled': True,  # NEW: Flag for checker transfer
            'always_new_format': True,
            'current_number_wo': pengajuan['number_wo'],
        }
        
        logger.info(f"ENHANCED REVIEW: Rendering template dengan checker transfer support untuk {nomor_pengajuan}")
        return render(request, 'wo_maintenance_app/review_pengajuan_detail.html', context)
        
    except Exception as e:
        logger.error(f"ENHANCED REVIEW: Critical error untuk {nomor_pengajuan}: {e}")
        messages.error(request, 'Terjadi kesalahan saat memuat detail review bro.')
        return redirect('wo_maintenance_app:review_pengajuan_list')

# Export functions
__all__ = [
    'monitoring_informasi_system',
    'ajax_monitoring_refresh',
    'save_checker_to_database',
    'get_all_checkers_from_database', 
    'clear_checker_from_database',
    'review_pengajuan_detail'
]

@login_required
def debug_transfer_status_fixed(request, nomor_pengajuan):
    """
    Debug function untuk check status transfer - SUPERUSER ONLY (NO MARS ERROR)
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        debug_info = {
            'timestamp': timezone.now().isoformat(),
            'history_id': nomor_pengajuan,
            'checks': {}
        }
        
        # FIXED: Gunakan single cursor tanpa nested operations
        with connections['DB_Maintenance'].cursor() as cursor:
            # Check di tabel_pengajuan
            cursor.execute("""
                SELECT history_id, status, approve, review_status, reviewed_by, review_date
                FROM tabel_pengajuan 
                WHERE history_id = %s
            """, [nomor_pengajuan])
            
            pengajuan_row = cursor.fetchone()
            if pengajuan_row:
                debug_info['checks']['tabel_pengajuan'] = {
                    'found': True,
                    'history_id': pengajuan_row[0],
                    'status': pengajuan_row[1],
                    'approve': pengajuan_row[2],
                    'review_status': pengajuan_row[3],
                    'reviewed_by': pengajuan_row[4],
                    'review_date': pengajuan_row[5].isoformat() if pengajuan_row[5] else None,
                    'is_final_processed': pengajuan_row[1] == 'A' and pengajuan_row[2] == 'Y',
                    'is_reviewed': pengajuan_row[3] in ['1', '2']
                }
            else:
                debug_info['checks']['tabel_pengajuan'] = {
                    'found': False,
                    'error': 'Pengajuan tidak ditemukan'
                }
        
        # FIXED: Separate cursor untuk tabel_main check
        with connections['DB_Maintenance'].cursor() as cursor:
            # Check di tabel_main
            cursor.execute("""
                SELECT history_id, status, status_pekerjaan, pic_produksi, pic_maintenance, tgl_insert
                FROM tabel_main 
                WHERE history_id = %s
            """, [nomor_pengajuan])
            
            main_row = cursor.fetchone()
            if main_row:
                debug_info['checks']['tabel_main'] = {
                    'found': True,
                    'history_id': main_row[0],
                    'status': main_row[1],
                    'status_pekerjaan': main_row[2],
                    'pic_produksi': main_row[3],
                    'pic_maintenance': main_row[4],
                    'tgl_insert': main_row[5].isoformat() if main_row[5] else None
                }
            else:
                debug_info['checks']['tabel_main'] = {
                    'found': False,
                    'error': 'Data tidak ditemukan di tabel_main'
                }
        
        # Analysis
        if debug_info['checks']['tabel_pengajuan']['found']:
            pengajuan_data = debug_info['checks']['tabel_pengajuan']
            
            if pengajuan_data['is_final_processed'] and not debug_info['checks']['tabel_main']['found']:
                debug_info['analysis'] = 'ERROR: Pengajuan sudah final processed tapi belum masuk tabel_main'
                debug_info['recommendation'] = 'Jalankan manual transfer atau debug fungsi auto transfer'
            elif pengajuan_data['is_final_processed'] and debug_info['checks']['tabel_main']['found']:
                debug_info['analysis'] = 'SUCCESS: Pengajuan sudah final processed dan data ada di tabel_main'
                debug_info['recommendation'] = 'Data sudah berhasil ter-transfer'
            elif not pengajuan_data['is_final_processed']:
                debug_info['analysis'] = 'PENDING: Pengajuan belum final processed'
                debug_info['recommendation'] = 'Review pengajuan dengan SITI FATIMAH untuk transfer ke tabel_main'
            else:
                debug_info['analysis'] = 'UNKNOWN: Status tidak dapat ditentukan'
        
        return JsonResponse(debug_info, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


# ===== MANUAL TRANSFER FUNCTION untuk Recovery (FIXED) =====

@login_required
def manual_transfer_to_main_fixed(request, nomor_pengajuan):
    """
    Manual transfer function untuk recovery - SUPERUSER ONLY (NO MARS ERROR)
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        # FIXED: Gunakan Django atomic transaction
        with transaction.atomic(using='DB_Maintenance'):
            with connections['DB_Maintenance'].cursor() as cursor:
                # Get data from tabel_pengajuan
                cursor.execute("""
                    SELECT 
                        tp.history_id, tp.tgl_his, tp.jam_his, tp.id_line, tp.id_mesin,
                        tp.id_section, tp.id_pekerjaan, tp.number_wo, tp.deskripsi_perbaikan,
                        tp.user_insert, tp.tgl_insert, tp.oleh, tp.status, tp.approve, tp.review_status
                    FROM tabel_pengajuan tp
                    WHERE tp.history_id = %s
                """, [nomor_pengajuan])
                
                pengajuan_row = cursor.fetchone()
                
                if not pengajuan_row:
                    return JsonResponse({
                        'success': False,
                        'error': f'Pengajuan {nomor_pengajuan} tidak ditemukan'
                    })
                
                # Check if already final processed
                if pengajuan_row[12] != 'A' or pengajuan_row[13] != 'Y':
                    return JsonResponse({
                        'success': False,
                        'error': f'Pengajuan {nomor_pengajuan} belum final processed (status: {pengajuan_row[12]}/{pengajuan_row[13]})'
                    })
                
                # Check if already exists in tabel_main
                cursor.execute("SELECT COUNT(*) FROM tabel_main WHERE history_id = %s", [nomor_pengajuan])
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({
                        'success': False,
                        'error': f'Data {nomor_pengajuan} sudah ada di tabel_main'
                    })
                
                # Manual insert to tabel_main (dalam atomic transaction)
                cursor.execute("""
                    INSERT INTO tabel_main (
                        history_id, tgl_his, jam_his, id_line, id_mesin, 
                        id_section, id_pekerjaan, number_wo, deskripsi_perbaikan,
                        pic_produksi, pic_maintenance, status, user_insert, 
                        tgl_insert, oleh, status_pekerjaan
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, [
                    pengajuan_row[0],   # history_id
                    pengajuan_row[1],   # tgl_his
                    pengajuan_row[2],   # jam_his
                    pengajuan_row[3],   # id_line
                    pengajuan_row[4],   # id_mesin
                    pengajuan_row[5],   # id_section
                    pengajuan_row[6],   # id_pekerjaan
                    pengajuan_row[7],   # number_wo
                    pengajuan_row[8],   # deskripsi_perbaikan
                    pengajuan_row[11] or '-',  # pic_produksi (oleh)
                    '-',                # pic_maintenance
                    '0',                # status (default Open)
                    pengajuan_row[9],   # user_insert
                    pengajuan_row[10],  # tgl_insert
                    pengajuan_row[11],  # oleh
                    '0'                 # status_pekerjaan (default Open)
                ])
                
                # Django akan auto-commit atomic transaction di sini
                
                logger.info(f"MANUAL TRANSFER FIXED: Successfully transferred {nomor_pengajuan} to tabel_main")
                
                return JsonResponse({
                    'success': True,
                    'message': f'Manual transfer {nomor_pengajuan} berhasil tanpa MARS error!'
                })
        
    except Exception as e:
        logger.error(f"MANUAL TRANSFER FIXED: Error for {nomor_pengajuan}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# Export functions
__all__ = [
    'review_pengajuan_detail',  # FIXED version tanpa MARS error
    'debug_transfer_status_fixed',
    'manual_transfer_to_main_fixed'
]

def transfer_pengajuan_to_tabel_main(pengajuan_data, reviewer_employee_number):
    """
    Helper function untuk transfer data dari tabel_pengajuan ke tabel_main
    
    Args:
        pengajuan_data: Dictionary data pengajuan
        reviewer_employee_number: Employee number yang melakukan review
    
    Returns:
        bool: Success status
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Check apakah data sudah ada
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_main WHERE history_id = %s
            """, [pengajuan_data['history_id']])
            
            if cursor.fetchone()[0] > 0:
                logger.warning(f"Data {pengajuan_data['history_id']} already exists in tabel_main")
                return True  # Consider as success
            
            # Insert data ke tabel_main
            cursor.execute("""
                INSERT INTO tabel_main (
                    history_id, tgl_his, jam_his, id_line, id_mesin, 
                    id_section, id_pekerjaan, number_wo, deskripsi_perbaikan,
                    pic_produksi, pic_maintenance, status, user_insert, 
                    tgl_insert, oleh, status_pekerjaan
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, [
                pengajuan_data['history_id'],
                pengajuan_data.get('tgl_his'),
                pengajuan_data.get('jam_his'),
                pengajuan_data.get('id_line'),
                pengajuan_data.get('id_mesin'),
                pengajuan_data.get('current_section_id'),
                pengajuan_data.get('id_pekerjaan'),
                pengajuan_data.get('number_wo'),
                pengajuan_data.get('deskripsi_perbaikan'),
                pengajuan_data.get('oleh', '-'),  # pic_produksi default ke pengaju
                '-',  # pic_maintenance default kosong
                '0',  # status default Open
                pengajuan_data.get('user_insert'),
                pengajuan_data.get('tgl_insert'),
                pengajuan_data.get('oleh'),
                '0'   # status_pekerjaan default Open
            ])
            
            logger.info(f"Successfully transferred {pengajuan_data['history_id']} to tabel_main")
            return True
            
    except Exception as e:
        logger.error(f"Error transferring {pengajuan_data.get('history_id', 'unknown')} to tabel_main: {e}")
        return False

@login_required
@reviewer_required_fixed
def ajax_check_transfer_status(request, nomor_pengajuan):
    """
    AJAX endpoint untuk check apakah pengajuan sudah di-transfer ke tabel_main
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Check di tabel_main
            cursor.execute("""
                SELECT COUNT(*), status, status_pekerjaan 
                FROM tabel_main 
                WHERE history_id = %s
                GROUP BY status, status_pekerjaan
            """, [nomor_pengajuan])
            
            result = cursor.fetchone()
            
            if result and result[0] > 0:
                return JsonResponse({
                    'success': True,
                    'transferred': True,
                    'status': result[1],
                    'status_pekerjaan': result[2],
                    'history_url': f"/wo-maintenance/history/{nomor_pengajuan}/",
                    'message': f'Data sudah ada di History Maintenance'
                })
            else:
                return JsonResponse({
                    'success': True,
                    'transferred': False,
                    'message': f'Data belum masuk ke History Maintenance'
                })
        
    except Exception as e:
        logger.error(f"Error checking transfer status for {nomor_pengajuan}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# Export fungsi tambahan
__all__ = [
    'transfer_pengajuan_to_tabel_main',
    'ajax_check_transfer_status'
]    
# wo_maintenance_app/views.py - FIXED enhanced_daftar_laporan
# User yang mengajukan tetap bisa melihat pengajuan mereka sendiri

@login_required
def enhanced_daftar_laporan(request):
    """
    Enhanced view untuk menampilkan daftar pengajuan dengan SDBM integration
    FIXED: User pembuat pengajuan tetap bisa melihat pengajuan mereka sendiri meskipun sudah final processed
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
        
        # ===== QUERY DATABASE dengan FIXED LOGIC =====
        pengajuan_list = []
        total_records = 0
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # ===== FIXED BASE CONDITIONS: Conditional exclude final processed =====
                base_conditions = ["tp.history_id IS NOT NULL"]
                query_params = []
                
                if is_siti_fatimah and view_mode == 'approved':
                    # SITI FATIMAH - Only pengajuan siap review (status B, approve N)
                    base_conditions.extend([
                        "tp.status = %s",
                        "tp.approve = %s"
                    ])
                    query_params.extend([STATUS_APPROVED, APPROVE_YES])  # B, N
                    logger.info("SITI FATIMAH mode: querying pengajuan ready for review (status=B, approve=N)")
                    
                elif is_siti_fatimah:
                    # ENHANCED: SITI FATIMAH normal mode - show pengajuan ready for review, exclude final processed
                    base_conditions.extend([
                        "tp.status = %s",
                        "tp.approve = %s"
                    ])
                    query_params.extend([STATUS_APPROVED, APPROVE_YES])  # B, N
                    logger.info("SITI FATIMAH mode: accessing pengajuan ready for review")
                    
                else:
                    # FIXED: Mode normal untuk user lain - hierarchy filter dengan conditional exclude
                    allowed_employee_numbers = get_subordinate_employee_numbers(user_hierarchy)
                    
                    if not allowed_employee_numbers:
                        allowed_employee_numbers = [user_hierarchy.get('employee_number')]
                    
                    # Simplified access control
                    if allowed_employee_numbers:
                        placeholders = ','.join(['%s'] * len(allowed_employee_numbers))
                        base_conditions.append(f"tp.user_insert IN ({placeholders})")
                        query_params.extend(allowed_employee_numbers)
                    
                    # FIXED: Conditional exclude final processed
                    # User pembuat pengajuan tetap bisa melihat pengajuan mereka sendiri
                    # Hanya exclude final processed yang bukan milik user atau bukan yang user approve
                    current_user_employee_number = user_hierarchy.get('employee_number')
                    
                    if current_user_employee_number:
                        # FIXED LOGIC: Exclude final processed KECUALI:
                        # 1. User adalah pembuat pengajuan (user_insert = current_user)
                        # 2. User pernah approve pengajuan tersebut (ada di approval log)
                        base_conditions.append(f"""
                            NOT (
                                tp.status = %s AND tp.approve = %s 
                                AND tp.user_insert != %s
                                AND NOT EXISTS (
                                    SELECT 1 FROM tabel_approval_log tal 
                                    WHERE tal.history_id = tp.history_id 
                                        AND tal.approver_user = %s
                                )
                            )
                        """)
                        query_params.extend([
                            STATUS_REVIEWED, APPROVE_REVIEWED,  # A, Y
                            current_user_employee_number,      # user_insert != current_user
                            current_user_employee_number       # approver_user = current_user
                        ])
                        
                        logger.info(f"Applied conditional exclude logic for user {current_user_employee_number}")
                
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
                        -- Enhanced status flags
                        CASE 
                            WHEN tp.status = %s AND tp.approve = %s THEN 1 
                            ELSE 0 
                        END as is_approved_for_review,   -- 20 (status B, approve N)
                        CASE 
                            WHEN tp.status = %s AND tp.approve = %s AND (tp.review_status IS NULL OR tp.review_status = '0') THEN 1 
                            ELSE 0 
                        END as needs_review,             -- 21
                        -- FIXED: Ownership flag
                        CASE 
                            WHEN tp.user_insert = %s THEN 1 
                            ELSE 0 
                        END as is_own_pengajuan          -- 22
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
                
                # FIXED: Add parameters untuk status checks dan ownership
                final_params = [
                    STATUS_APPROVED, APPROVE_YES,                    # is_approved_for_review check
                    STATUS_APPROVED, APPROVE_YES,                    # needs_review check  
                    user_hierarchy.get('employee_number')           # ownership check
                ] + query_params + [offset, page_size]
                
                cursor.execute(main_query, final_params)
                
                pengajuan_list = cursor.fetchall()
                
                logger.info(f"FIXED query executed successfully - Found {total_records} records for view_mode: {view_mode}")
                
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
            
            # Enhanced: Review info untuk SITI FATIMAH
            'show_review_buttons': is_siti_fatimah,
            'reviewer_employee_number': REVIEWER_EMPLOYEE_NUMBER,
            
            # Status constants untuk template
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
                'fixed_user_visibility': 'Yes - Users can see their own final processed pengajuan'  # NEW
            } if request.user.is_superuser else None
        }
        
        return render(request, 'wo_maintenance_app/enhanced_daftar_laporan.html', context)
        
    except Exception as e:
        logger.error(f"Critical error in enhanced daftar_laporan: {e}")
        import traceback
        logger.error(f"Critical traceback: {traceback.format_exc()}")
        messages.error(request, 'Terjadi kesalahan sistem. Silakan coba lagi.')
        return redirect('wo_maintenance_app:dashboard')

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

@login_required
def input_laporan(request):
    """
    FIXED: View untuk input pengajuan maintenance dengan format History ID baru: 25-08-0001
    """
    
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
                    # FIXED: Generate history_id dengan format baru 25-08-0001
                    from wo_maintenance_app.models import create_new_history_id
                    history_id = create_new_history_id()
                    
                    # Generate temporary number_wo (akan diupdate saat review)
                    today = datetime.now()
                    temp_number_wo = f"TEMP-{today.strftime('%y%m%d%H%M%S')}"[:15]
                    
                    # Get next id_pengajuan
                    cursor.execute("SELECT ISNULL(MAX(id_pengajuan), 0) + 1 FROM tabel_pengajuan")
                    next_id_pengajuan = cursor.fetchone()[0]
                    
                    # Convert dan validate data
                    line_id_int = int(validated_data['line_section'])
                    mesin_id_int = int(validated_data['nama_mesin'])
                    section_id_int = int(validated_data['section_tujuan'])
                    pekerjaan_id_int = int(validated_data['jenis_pekerjaan'])
                    
                    # Get actual line_id float
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
                    
                    # Insert dengan format history_id baru
                    cursor.execute("""
                        INSERT INTO tabel_pengajuan 
                        (history_id, tgl_his, jam_his, id_line, id_mesin, number_wo, 
                         deskripsi_perbaikan, status, user_insert, tgl_insert, oleh, 
                         approve, id_section, id_pekerjaan, id_pengajuan, idpengajuan)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        history_id,                     # Format baru: 25-08-0001
                        today,
                        today.strftime('%H:%M:%S'),
                        actual_line_id,
                        float(mesin_id_int),
                        temp_number_wo,                 # Temporary, akan diupdate saat review
                        deskripsi,
                        STATUS_PENDING,                 # '0' - pending
                        user_insert,
                        today,
                        oleh,
                        APPROVE_NO,                     # '0' - not approved
                        float(section_id_int),
                        float(pekerjaan_id_int),
                        next_id_pengajuan,
                        float(next_id_pengajuan)
                    ])
                
                logger.info(f"SUCCESS: Pengajuan {history_id} berhasil disimpan dengan format baru")
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


# wo_maintenance_app/views.py - FIXED detail_laporan dengan proper approval logging

@login_required
def detail_laporan(request, nomor_pengajuan):
    """
    View untuk menampilkan detail pengajuan dengan sistem approval hierarchy
    FIXED: Proper approval logging untuk user visibility
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
        
        # Check status pending dengan nilai yang benar
        if pengaju_hierarchy and pengajuan['status'] == STATUS_PENDING:  # Status pending = '0'
            can_approve = can_user_approve(user_hierarchy, pengaju_hierarchy)
        
        # ===== GET APPROVAL HISTORY =====
        from .utils import get_approval_log_for_pengajuan
        approval_logs = get_approval_log_for_pengajuan(nomor_pengajuan)
        
         # ===== HANDLE APPROVAL FORM =====
        approval_form = ApprovalForm()
        
        if request.method == 'POST' and can_approve:
            approval_form = ApprovalForm(request.POST)
            
            if approval_form.is_valid():
                action = approval_form.cleaned_data['action']
                keterangan = approval_form.cleaned_data['keterangan']
                
                try:
                    with connections['DB_Maintenance'].cursor() as cursor:
                        # Approval logic dengan status baru
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
                        
                        # FIXED: Log approval action dengan function baru
                        try:
                            from .utils import log_approval_action
                            log_approval_action(nomor_pengajuan, user_hierarchy, action, keterangan)
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
            'approval_logs': approval_logs,  # FIXED: Add approval logs
            
            # Status constants untuk template
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

# @login_required
# def history_pengajuan_list(request):
#     """
#     Halaman history pengajuan maintenance - data dari tabel_main
#     FIXED: Konsistensi status antara display dan actions
#     """
#     try:
#         # Ambil data hierarchy user
#         user_hierarchy = get_employee_hierarchy_data(request.user)
        
#         if not user_hierarchy:
#             messages.error(request, 'Data karyawan tidak ditemukan. Hubungi administrator.')
#             return redirect('wo_maintenance_app:dashboard')
        
#         # Filter form
#         filter_form = HistoryFilterForm(request.GET or None)
#         search_query = request.GET.get('search', '').strip()
        
#         # Query database tabel_main
#         history_list = []
#         total_records = 0
        
#         try:
#             with connections['DB_Maintenance'].cursor() as cursor:
#                 # Base WHERE conditions
#                 where_conditions = ["tm.history_id IS NOT NULL"]
#                 query_params = []
                
#                 # Apply filters dari form
#                 if filter_form.is_valid():
#                     tanggal_dari = filter_form.cleaned_data.get('tanggal_dari')
#                     if tanggal_dari:
#                         where_conditions.append("CAST(tm.tgl_insert AS DATE) >= %s")
#                         query_params.append(tanggal_dari)
                    
#                     tanggal_sampai = filter_form.cleaned_data.get('tanggal_sampai')
#                     if tanggal_sampai:
#                         where_conditions.append("CAST(tm.tgl_insert AS DATE) <= %s")
#                         query_params.append(tanggal_sampai)
                    
#                     status_filter = filter_form.cleaned_data.get('status')
#                     if status_filter:
#                         # Normalize filter status (support both O/C and 0/1)
#                         if status_filter in ['O', 'o', '0']:
#                             where_conditions.append("(tm.status = 'O' OR tm.status = '0')")
#                         elif status_filter in ['C', 'c', '1']:
#                             where_conditions.append("(tm.status = 'C' OR tm.status = '1')")
                    
#                     status_pekerjaan_filter = filter_form.cleaned_data.get('status_pekerjaan')
#                     if status_pekerjaan_filter:
#                         # Normalize filter status pekerjaan
#                         if status_pekerjaan_filter in ['O', 'o', '0']:
#                             where_conditions.append("(tm.status_pekerjaan = 'O' OR tm.status_pekerjaan = '0')")
#                         elif status_pekerjaan_filter in ['C', 'c', '1']:
#                             where_conditions.append("(tm.status_pekerjaan = 'C' OR tm.status_pekerjaan = '1')")
                    
#                     history_id_filter = filter_form.cleaned_data.get('history_id')
#                     if history_id_filter:
#                         where_conditions.append("tm.history_id LIKE %s")
#                         query_params.append(f"%{history_id_filter}%")
                    
#                     pengaju_filter = filter_form.cleaned_data.get('pengaju')
#                     if pengaju_filter:
#                         where_conditions.append("tm.oleh LIKE %s")
#                         query_params.append(f"%{pengaju_filter}%")
                    
#                     pic_produksi_filter = filter_form.cleaned_data.get('pic_produksi')
#                     if pic_produksi_filter:
#                         where_conditions.append("tm.pic_produksi LIKE %s")
#                         query_params.append(f"%{pic_produksi_filter}%")
                    
#                     pic_maintenance_filter = filter_form.cleaned_data.get('pic_maintenance')
#                     if pic_maintenance_filter:
#                         where_conditions.append("tm.pic_maintenance LIKE %s")
#                         query_params.append(f"%{pic_maintenance_filter}%")
                    
#                     section_filter = filter_form.cleaned_data.get('section_filter')
#                     if section_filter:
#                         where_conditions.append("tm.id_section = %s")
#                         query_params.append(float(section_filter))
                
#                 # General search
#                 if search_query:
#                     search_conditions = [
#                         "tm.history_id LIKE %s",
#                         "tm.oleh LIKE %s",
#                         "tm.deskripsi_perbaikan LIKE %s",
#                         "tm.pic_produksi LIKE %s",
#                         "tm.pic_maintenance LIKE %s"
#                     ]
#                     where_conditions.append(f"({' OR '.join(search_conditions)})")
#                     search_param = f"%{search_query}%"
#                     query_params.extend([search_param] * len(search_conditions))
                
#                 # Build WHERE clause
#                 where_clause = ""
#                 if where_conditions:
#                     where_clause = "WHERE " + " AND ".join(where_conditions)
                
#                 # Count total records
#                 count_query = f"""
#                     SELECT COUNT(DISTINCT tm.history_id)
#                     FROM tabel_main tm
#                     LEFT JOIN tabel_mesin tmes ON tm.id_mesin = tmes.id_mesin
#                     LEFT JOIN tabel_line tl ON tm.id_line = tl.id_line
#                     LEFT JOIN tabel_msection tms ON tm.id_section = tms.id_section
#                     {where_clause}
#                 """
                
#                 cursor.execute(count_query, query_params)
#                 total_records = cursor.fetchone()[0] or 0
                
#                 # Pagination
#                 page_size = 20
#                 page_number = int(request.GET.get('page', 1))
#                 offset = (page_number - 1) * page_size
                
#                 total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
#                 has_previous = page_number > 1
#                 has_next = page_number < total_pages
#                 previous_page_number = page_number - 1 if has_previous else None
#                 next_page_number = page_number + 1 if has_next else None
                
#                 # Main query - FIXED dengan normalisasi status
#                 main_query = f"""
#                     SELECT DISTINCT
#                         tm.history_id,                    -- 0
#                         tm.oleh,                          -- 1 (pengaju)
#                         ISNULL(tmes.mesin, 'N/A'),        -- 2 (mesin)
#                         ISNULL(tms.seksi, 'N/A'),         -- 3 (section)
#                         tm.deskripsi_perbaikan,           -- 4 (deskripsi)
#                         -- FIXED: Normalize status values
#                         CASE 
#                             WHEN tm.status IN ('O', 'o') THEN 'O'
#                             WHEN tm.status IN ('C', 'c', '1') THEN 'C'
#                             WHEN tm.status = '0' THEN 'O'
#                             ELSE 'O'
#                         END as status_normalized,         -- 5 (status normalized)
#                         CASE 
#                             WHEN tm.status_pekerjaan IN ('O', 'o') THEN 'O'
#                             WHEN tm.status_pekerjaan IN ('C', 'c', '1') THEN 'C'
#                             WHEN tm.status_pekerjaan = '0' THEN 'O'
#                             ELSE 'O'
#                         END as status_pekerjaan_normalized, -- 6 (status pekerjaan normalized)
#                         tm.pic_produksi,                  -- 7 (pic produksi)
#                         tm.pic_maintenance,               -- 8 (pic maintenance)
#                         tm.tgl_insert,                    -- 9 (tanggal insert)
#                         ISNULL(tl.line, 'N/A'),           -- 10 (line)
#                         tm.penyebab,                      -- 11 (penyebab)
#                         tm.akar_masalah,                  -- 12 (akar masalah)
#                         tm.tindakan_perbaikan,            -- 13 (tindakan perbaikan)
#                         tm.tindakan_pencegahan,           -- 14 (tindakan pencegahan)
#                         tm.tgl_selesai,                   -- 15 (tanggal selesai)
#                         tm.number_wo,                     -- 16 (number WO)
#                         tm.tgl_edit,                      -- 17 (tanggal edit)
#                         tm.usert_edit                     -- 18 (user edit)
#                     FROM tabel_main tm
#                     LEFT JOIN tabel_mesin tmes ON tm.id_mesin = tmes.id_mesin
#                     LEFT JOIN tabel_line tl ON tm.id_line = tl.id_line
#                     LEFT JOIN tabel_msection tms ON tm.id_section = tms.id_section
#                     {where_clause}
#                     ORDER BY tm.tgl_insert DESC, tm.history_id DESC
#                     OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
#                 """
                
#                 final_params = query_params + [offset, page_size]
#                 cursor.execute(main_query, final_params)
                
#                 history_list = cursor.fetchall()
                
#                 logger.info(f"History query executed - Found {total_records} records")
                
#         except Exception as db_error:
#             logger.error(f"Database error in history_pengajuan_list: {db_error}")
#             messages.error(request, f'Terjadi kesalahan database: {str(db_error)}')
#             history_list = []
#             total_records = 0
#             total_pages = 1
#             has_previous = False
#             has_next = False
#             previous_page_number = None
#             next_page_number = None
#             page_number = 1
        
#         # Statistics dengan normalisasi status
#         stats = {}
#         try:
#             with connections['DB_Maintenance'].cursor() as cursor:
#                 # Total history
#                 cursor.execute("SELECT COUNT(*) FROM tabel_main WHERE history_id IS NOT NULL")
#                 stats['total_history'] = cursor.fetchone()[0] or 0
                
#                 # Open vs close dengan normalisasi
#                 cursor.execute("""
#                     SELECT COUNT(*) FROM tabel_main 
#                     WHERE (status IN ('O', 'o', '0')) AND history_id IS NOT NULL
#                 """)
#                 stats['open_count'] = cursor.fetchone()[0] or 0
                
#                 cursor.execute("""
#                     SELECT COUNT(*) FROM tabel_main 
#                     WHERE (status IN ('C', 'c', '1')) AND history_id IS NOT NULL
#                 """)
#                 stats['close_count'] = cursor.fetchone()[0] or 0
                
#                 # Today's updates
#                 today = timezone.now().date()
#                 cursor.execute("""
#                     SELECT COUNT(*) FROM tabel_main 
#                     WHERE CAST(tgl_edit AS DATE) = %s AND history_id IS NOT NULL
#                 """, [today])
#                 stats['today_updates'] = cursor.fetchone()[0] or 0
                
#         except Exception as stats_error:
#             logger.error(f"Error getting history stats: {stats_error}")
#             stats = {
#                 'total_history': 0,
#                 'open_count': 0,
#                 'close_count': 0,
#                 'today_updates': 0
#             }
        
#         context = {
#             'history_list': history_list,
#             'filter_form': filter_form,
#             'search_query': search_query,
#             'total_records': total_records,
#             'total_pages': total_pages,
#             'page_number': page_number,
#             'has_previous': has_previous,
#             'has_next': has_next,
#             'previous_page_number': previous_page_number,
#             'next_page_number': next_page_number,
#             'user_hierarchy': user_hierarchy,
#             'employee_data': user_hierarchy,
#             'stats': stats,
#             'page_title': 'History Pengajuan Maintenance'
#         }
        
#         return render(request, 'wo_maintenance_app/history_pengajuan_list.html', context)
        
#     except Exception as e:
#         logger.error(f"Critical error in history_pengajuan_list: {e}")
#         messages.error(request, 'Terjadi kesalahan sistem. Silakan coba lagi.')
#         return redirect('wo_maintenance_app:dashboard')

@login_required
def history_pengajuan_list(request):
    """
    Halaman history pengajuan maintenance - data dari tabel_main
    UPDATED: Hapus Status Umum filter, hanya gunakan Status Pekerjaan
    """
    try:
        # Ambil data hierarchy user
        user_hierarchy = get_employee_hierarchy_data(request.user)
        
        if not user_hierarchy:
            messages.error(request, 'Data karyawan tidak ditemukan. Hubungi administrator.')
            return redirect('wo_maintenance_app:dashboard')
        
        # Filter form
        filter_form = HistoryFilterForm(request.GET or None)
        search_query = request.GET.get('search', '').strip()
        
        # Query database tabel_main
        history_list = []
        total_records = 0
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Base WHERE conditions
                where_conditions = ["tm.history_id IS NOT NULL"]
                query_params = []
                
                # Apply filters dari form
                if filter_form.is_valid():
                    tanggal_dari = filter_form.cleaned_data.get('tanggal_dari')
                    if tanggal_dari:
                        where_conditions.append("CAST(tm.tgl_insert AS DATE) >= %s")
                        query_params.append(tanggal_dari)
                    
                    tanggal_sampai = filter_form.cleaned_data.get('tanggal_sampai')
                    if tanggal_sampai:
                        where_conditions.append("CAST(tm.tgl_insert AS DATE) <= %s")
                        query_params.append(tanggal_sampai)
                    
                    # UPDATED: Hanya filter status_pekerjaan, status umum dihapus
                    status_pekerjaan_filter = filter_form.cleaned_data.get('status_pekerjaan')
                    if status_pekerjaan_filter:
                        # Normalize filter status pekerjaan
                        if status_pekerjaan_filter in ['O', 'o', '0']:
                            where_conditions.append("(tm.status_pekerjaan = 'O' OR tm.status_pekerjaan = '0')")
                        elif status_pekerjaan_filter in ['C', 'c', '1']:
                            where_conditions.append("(tm.status_pekerjaan = 'C' OR tm.status_pekerjaan = '1')")
                    
                    history_id_filter = filter_form.cleaned_data.get('history_id')
                    if history_id_filter:
                        where_conditions.append("tm.history_id LIKE %s")
                        query_params.append(f"%{history_id_filter}%")
                    
                    pengaju_filter = filter_form.cleaned_data.get('pengaju')
                    if pengaju_filter:
                        where_conditions.append("tm.oleh LIKE %s")
                        query_params.append(f"%{pengaju_filter}%")
                    
                    pic_produksi_filter = filter_form.cleaned_data.get('pic_produksi')
                    if pic_produksi_filter:
                        where_conditions.append("tm.pic_produksi LIKE %s")
                        query_params.append(f"%{pic_produksi_filter}%")
                    
                    pic_maintenance_filter = filter_form.cleaned_data.get('pic_maintenance')
                    if pic_maintenance_filter:
                        where_conditions.append("tm.pic_maintenance LIKE %s")
                        query_params.append(f"%{pic_maintenance_filter}%")
                    
                    section_filter = filter_form.cleaned_data.get('section_filter')
                    if section_filter:
                        where_conditions.append("tm.id_section = %s")
                        query_params.append(float(section_filter))
                
                # General search
                if search_query:
                    search_conditions = [
                        "tm.history_id LIKE %s",
                        "tm.oleh LIKE %s",
                        "tm.deskripsi_perbaikan LIKE %s",
                        "tm.pic_produksi LIKE %s",
                        "tm.pic_maintenance LIKE %s"
                    ]
                    where_conditions.append(f"({' OR '.join(search_conditions)})")
                    search_param = f"%{search_query}%"
                    query_params.extend([search_param] * len(search_conditions))
                
                # Build WHERE clause
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                
                # Count total records
                count_query = f"""
                    SELECT COUNT(DISTINCT tm.history_id)
                    FROM tabel_main tm
                    LEFT JOIN tabel_mesin tmes ON tm.id_mesin = tmes.id_mesin
                    LEFT JOIN tabel_line tl ON tm.id_line = tl.id_line
                    LEFT JOIN tabel_msection tms ON tm.id_section = tms.id_section
                    {where_clause}
                """
                
                cursor.execute(count_query, query_params)
                total_records = cursor.fetchone()[0] or 0
                
                # Pagination
                page_size = 20
                page_number = int(request.GET.get('page', 1))
                offset = (page_number - 1) * page_size
                
                total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
                has_previous = page_number > 1
                has_next = page_number < total_pages
                previous_page_number = page_number - 1 if has_previous else None
                next_page_number = page_number + 1 if has_next else None
                
                # UPDATED: Main query - hapus status umum, hanya tampilkan status pekerjaan
                main_query = f"""
                    SELECT DISTINCT
                        tm.history_id,                    -- 0
                        tm.oleh,                          -- 1 (pengaju)
                        ISNULL(tmes.mesin, 'N/A'),        -- 2 (mesin)
                        ISNULL(tms.seksi, 'N/A'),         -- 3 (section)
                        tm.deskripsi_perbaikan,           -- 4 (deskripsi)
                        -- UPDATED: Hanya status_pekerjaan yang ditampilkan, status umum dihapus
                        CASE 
                            WHEN tm.status_pekerjaan IN ('O', 'o') THEN 'O'
                            WHEN tm.status_pekerjaan IN ('C', 'c', '1') THEN 'C'
                            WHEN tm.status_pekerjaan = '0' THEN 'O'
                            ELSE 'O'
                        END as status_pekerjaan_normalized, -- 5 (hanya status pekerjaan)
                        tm.pic_produksi,                  -- 6 (pic produksi)
                        tm.pic_maintenance,               -- 7 (pic maintenance)
                        tm.tgl_insert,                    -- 8 (tanggal insert)
                        ISNULL(tl.line, 'N/A'),           -- 9 (line)
                        tm.penyebab,                      -- 10 (penyebab)
                        tm.akar_masalah,                  -- 11 (akar masalah)
                        tm.tindakan_perbaikan,            -- 12 (tindakan perbaikan)
                        tm.tindakan_pencegahan,           -- 13 (tindakan pencegahan)
                        tm.tgl_selesai,                   -- 14 (tanggal selesai)
                        tm.number_wo,                     -- 15 (number WO)
                        tm.tgl_edit,                      -- 16 (tanggal edit)
                        tm.usert_edit                     -- 17 (user edit)
                    FROM tabel_main tm
                    LEFT JOIN tabel_mesin tmes ON tm.id_mesin = tmes.id_mesin
                    LEFT JOIN tabel_line tl ON tm.id_line = tl.id_line
                    LEFT JOIN tabel_msection tms ON tm.id_section = tms.id_section
                    {where_clause}
                    ORDER BY tm.tgl_insert DESC, tm.history_id DESC
                    OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
                """
                
                final_params = query_params + [offset, page_size]
                cursor.execute(main_query, final_params)
                
                history_list = cursor.fetchall()
                
                logger.info(f"History query executed - Found {total_records} records")
                
        except Exception as db_error:
            logger.error(f"Database error in history_pengajuan_list: {db_error}")
            messages.error(request, f'Terjadi kesalahan database: {str(db_error)}')
            history_list = []
            total_records = 0
            total_pages = 1
            has_previous = False
            has_next = False
            previous_page_number = None
            next_page_number = None
            page_number = 1
        
        # UPDATED: Statistics hanya berdasarkan status_pekerjaan
        stats = {}
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Total history
                cursor.execute("SELECT COUNT(*) FROM tabel_main WHERE history_id IS NOT NULL")
                stats['total_history'] = cursor.fetchone()[0] or 0
                
                # UPDATED: Open vs close berdasarkan status_pekerjaan saja
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_main 
                    WHERE (status_pekerjaan IN ('O', 'o', '0')) AND history_id IS NOT NULL
                """)
                stats['pekerjaan_open_count'] = cursor.fetchone()[0] or 0
                
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_main 
                    WHERE (status_pekerjaan IN ('C', 'c', '1')) AND history_id IS NOT NULL
                """)
                stats['pekerjaan_close_count'] = cursor.fetchone()[0] or 0
                
                # Today's updates
                today = timezone.now().date()
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_main 
                    WHERE CAST(tgl_edit AS DATE) = %s AND history_id IS NOT NULL
                """, [today])
                stats['today_updates'] = cursor.fetchone()[0] or 0
                
        except Exception as stats_error:
            logger.error(f"Error getting history stats: {stats_error}")
            stats = {
                'total_history': 0,
                'pekerjaan_open_count': 0,
                'pekerjaan_close_count': 0,
                'today_updates': 0
            }
        
        context = {
            'history_list': history_list,
            'filter_form': filter_form,
            'search_query': search_query,
            'total_records': total_records,
            'total_pages': total_pages,
            'page_number': page_number,
            'has_previous': has_previous,
            'has_next': has_next,
            'previous_page_number': previous_page_number,
            'next_page_number': next_page_number,
            'user_hierarchy': user_hierarchy,
            'employee_data': user_hierarchy,
            'stats': stats,
            'page_title': 'History Pengajuan Maintenance'
        }
        
        return render(request, 'wo_maintenance_app/history_pengajuan_list.html', context)
        
    except Exception as e:
        logger.error(f"Critical error in history_pengajuan_list: {e}")
        messages.error(request, 'Terjadi kesalahan sistem. Silakan coba lagi.')
        return redirect('wo_maintenance_app:dashboard')


# @login_required
# def history_pengajuan_detail(request, nomor_pengajuan):
#     """
#     Detail dan edit history pengajuan maintenance
#     User bisa edit data analisis masalah, tindakan, PIC, status, dll
#     """
#     try:
#         # Ambil data hierarchy user
#         user_hierarchy = get_employee_hierarchy_data(request.user)
        
#         if not user_hierarchy:
#             messages.error(request, 'Data karyawan tidak ditemukan. Hubungi administrator.')
#             return redirect('wo_maintenance_app:history_pengajuan_list')
        
#         # Ambil data history dari tabel_main
#         history_data = None
        
#         try:
#             with connections['DB_Maintenance'].cursor() as cursor:
#                 cursor.execute("""
#                     SELECT 
#                         tm.history_id, tm.oleh, tm.number_wo, tm.tgl_insert,
#                         tm.deskripsi_perbaikan, tm.penyebab, tm.akar_masalah,
#                         tm.tindakan_perbaikan, tm.tindakan_pencegahan,
#                         tm.status, tm.status_pekerjaan, tm.pic_produksi, tm.pic_maintenance,
#                         tm.tgl_wp_dari, tm.tgl_wp_sampai, tm.tgl_lt_dari, tm.tgl_lt_sampai,
#                         tm.tgl_dt_dari, tm.tgl_dt_sampai, tm.alasan_dt,
#                         tm.tgl_estimasidt, tm.tgl_selesai, tm.alasan_delay, tm.masalah,
#                         tmes.mesin, tl.line, tms.seksi, tpek.pekerjaan,
#                         tm.user_insert, tm.usert_edit, tm.tgl_edit
#                     FROM tabel_main tm
#                     LEFT JOIN tabel_mesin tmes ON tm.id_mesin = tmes.id_mesin
#                     LEFT JOIN tabel_line tl ON tm.id_line = tl.id_line
#                     LEFT JOIN tabel_msection tms ON tm.id_section = tms.id_section
#                     LEFT JOIN tabel_pekerjaan tpek ON tm.id_pekerjaan = tpek.id_pekerjaan
#                     WHERE tm.history_id = %s
#                 """, [nomor_pengajuan])
                
#                 row = cursor.fetchone()
                
#                 if not row:
#                     messages.error(request, 'Data history tidak ditemukan.')
#                     return redirect('wo_maintenance_app:history_pengajuan_list')
                
#                 # Map data ke dictionary
#                 history_data = {
#                     'history_id': row[0], 'oleh': row[1], 'number_wo': row[2], 'tgl_insert': row[3],
#                     'deskripsi_perbaikan': row[4], 'penyebab': row[5], 'akar_masalah': row[6],
#                     'tindakan_perbaikan': row[7], 'tindakan_pencegahan': row[8],
#                     'status': row[9], 'status_pekerjaan': row[10], 'pic_produksi': row[11], 
#                     'pic_maintenance': row[12], 'tgl_wp_dari': row[13], 'tgl_wp_sampai': row[14],
#                     'tgl_lt_dari': row[15], 'tgl_lt_sampai': row[16], 'tgl_dt_dari': row[17], 
#                     'tgl_dt_sampai': row[18], 'alasan_dt': row[19], 'tgl_estimasidt': row[20],
#                     'tgl_selesai': row[21], 'alasan_delay': row[22], 'masalah': row[23],
#                     'mesin': row[24], 'line': row[25], 'section': row[26], 'pekerjaan': row[27],
#                     'user_insert': row[28], 'usert_edit': row[29], 'tgl_edit': row[30]
#                 }
                
#         except Exception as db_error:
#             logger.error(f"Database error in history_pengajuan_detail: {db_error}")
#             messages.error(request, 'Terjadi kesalahan saat mengambil data history.')
#             return redirect('wo_maintenance_app:history_pengajuan_list')
        
#         # Handle form submission
#         if request.method == 'POST':
#             form = HistoryMaintenanceForm(request.POST, history_data=history_data)
            
#             if form.is_valid():
#                 # Update data history
#                 result = update_history_maintenance(
#                     nomor_pengajuan, 
#                     form.cleaned_data, 
#                     request.user
#                 )
                
#                 if result['success']:
#                     messages.success(request, result['message'])
#                     return redirect('wo_maintenance_app:history_pengajuan_detail', nomor_pengajuan=nomor_pengajuan)
#                 else:
#                     messages.error(request, result['message'])
#             else:
#                 messages.error(request, 'Form tidak valid. Periksa kembali input Anda.')
#         else:
#             form = HistoryMaintenanceForm(history_data=history_data)
        
#         context = {
#             'history_data': history_data,
#             'form': form,
#             'user_hierarchy': user_hierarchy,
#             'employee_data': user_hierarchy,
#             'page_title': f'Detail History {nomor_pengajuan}',
#             'can_edit': True  # Semua user bisa edit history
#         }
        
#         return render(request, 'wo_maintenance_app/history_pengajuan_detail.html', context)
        
#     except Exception as e:
#         logger.error(f"Critical error in history_pengajuan_detail: {e}")
#         messages.error(request, 'Terjadi kesalahan sistem. Silakan coba lagi.')
#         return redirect('wo_maintenance_app:history_pengajuan_list')

@login_required
def history_pengajuan_detail(request, nomor_pengajuan):
    """
    Detail dan edit history pengajuan maintenance
    UPDATED: Hapus Status Umum, hanya tampilkan dan edit Status Pekerjaan
    """
    try:
        # Ambil data hierarchy user
        user_hierarchy = get_employee_hierarchy_data(request.user)
        
        if not user_hierarchy:
            messages.error(request, 'Data karyawan tidak ditemukan. Hubungi administrator.')
            return redirect('wo_maintenance_app:history_pengajuan_list')
        
        # Ambil data history dari tabel_main
        history_data = None
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        tm.history_id, tm.oleh, tm.number_wo, tm.tgl_insert,
                        tm.deskripsi_perbaikan, tm.penyebab, tm.akar_masalah,
                        tm.tindakan_perbaikan, tm.tindakan_pencegahan,
                        tm.status_pekerjaan, tm.pic_produksi, tm.pic_maintenance,
                        tm.tgl_wp_dari, tm.tgl_wp_sampai, tm.tgl_lt_dari, tm.tgl_lt_sampai,
                        tm.tgl_dt_dari, tm.tgl_dt_sampai, tm.alasan_dt,
                        tm.tgl_estimasidt, tm.tgl_selesai, tm.alasan_delay, tm.masalah,
                        tmes.mesin, tl.line, tms.seksi, tpek.pekerjaan,
                        tm.user_insert, tm.usert_edit, tm.tgl_edit
                    FROM tabel_main tm
                    LEFT JOIN tabel_mesin tmes ON tm.id_mesin = tmes.id_mesin
                    LEFT JOIN tabel_line tl ON tm.id_line = tl.id_line
                    LEFT JOIN tabel_msection tms ON tm.id_section = tms.id_section
                    LEFT JOIN tabel_pekerjaan tpek ON tm.id_pekerjaan = tpek.id_pekerjaan
                    WHERE tm.history_id = %s
                """, [nomor_pengajuan])
                
                row = cursor.fetchone()
                
                if not row:
                    messages.error(request, 'Data history tidak ditemukan.')
                    return redirect('wo_maintenance_app:history_pengajuan_list')
                
                # UPDATED: Map data ke dictionary - hapus status umum
                history_data = {
                    'history_id': row[0], 'oleh': row[1], 'number_wo': row[2], 'tgl_insert': row[3],
                    'deskripsi_perbaikan': row[4], 'penyebab': row[5], 'akar_masalah': row[6],
                    'tindakan_perbaikan': row[7], 'tindakan_pencegahan': row[8],
                    'status_pekerjaan': row[9], 'pic_produksi': row[10], 'pic_maintenance': row[11], 
                    'tgl_wp_dari': row[12], 'tgl_wp_sampai': row[13],
                    'tgl_lt_dari': row[14], 'tgl_lt_sampai': row[15], 'tgl_dt_dari': row[16], 
                    'tgl_dt_sampai': row[17], 'alasan_dt': row[18], 'tgl_estimasidt': row[19],
                    'tgl_selesai': row[20], 'alasan_delay': row[21], 'masalah': row[22],
                    'mesin': row[23], 'line': row[24], 'section': row[25], 'pekerjaan': row[26],
                    'user_insert': row[27], 'usert_edit': row[28], 'tgl_edit': row[29]
                }
                
        except Exception as db_error:
            logger.error(f"Database error in history_pengajuan_detail: {db_error}")
            messages.error(request, 'Terjadi kesalahan saat mengambil data history.')
            return redirect('wo_maintenance_app:history_pengajuan_list')
        
        # Handle form submission
        if request.method == 'POST':
            form = HistoryMaintenanceForm(request.POST, history_data=history_data)
            
            if form.is_valid():
                # UPDATED: Update data history dengan auto-set status umum
                result = update_history_maintenance(
                    nomor_pengajuan, 
                    form.cleaned_data, 
                    request.user
                )
                
                if result['success']:
                    messages.success(request, result['message'])
                    return redirect('wo_maintenance_app:history_pengajuan_detail', nomor_pengajuan=nomor_pengajuan)
                else:
                    messages.error(request, result['message'])
            else:
                messages.error(request, 'Form tidak valid. Periksa kembali input Anda.')
        else:
            form = HistoryMaintenanceForm(history_data=history_data)
        
        context = {
            'history_data': history_data,
            'form': form,
            'user_hierarchy': user_hierarchy,
            'employee_data': user_hierarchy,
            'page_title': f'Detail History {nomor_pengajuan}',
            'can_edit': True,
            'status_umum_hidden': True  # UPDATED: Flag untuk template bahwa status umum disembunyikan
        }
        
        return render(request, 'wo_maintenance_app/history_pengajuan_detail.html', context)
        
    except Exception as e:
        logger.error(f"Critical error in history_pengajuan_detail: {e}")
        messages.error(request, 'Terjadi kesalahan sistem. Silakan coba lagi.')
        return redirect('wo_maintenance_app:history_pengajuan_list')

# ===== ENHANCED REVIEW SYSTEM dengan Auto Transfer ke Tabel Main =====

def enhanced_review_pengajuan_detail_with_transfer(request, nomor_pengajuan):
    """
    ENHANCED: Review pengajuan dengan auto transfer ke tabel_main
    Update fungsi review SITI FATIMAH biar data langsung masuk ke tabel_main
    """
    try:
        # Original review logic
        logger.info(f"ENHANCED REVIEW WITH TRANSFER: Starting review for {nomor_pengajuan} by {request.user.username}")
        
        employee_data = get_employee_data_for_request_fixed(request)
        
        if not employee_data:
            logger.error(f"ENHANCED REVIEW: No employee data for {request.user.username}")
            messages.error(request, 'Data employee tidak ditemukan. Silakan login ulang.')
            return redirect('login')
        
        # Ambil data pengajuan
        pengajuan = None
        
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT 
                    tp.history_id, tp.number_wo, tp.tgl_insert, tp.oleh, tp.user_insert,
                    tm.mesin, tms.seksi as section_tujuan, tpek.pekerjaan,
                    tp.deskripsi_perbaikan, tp.status, tp.approve, tl.line as line_name,
                    tp.tgl_his, tp.jam_his, tp.review_status, tp.reviewed_by,
                    tp.review_date, tp.review_notes, tp.final_section_id,
                    final_section.seksi as final_section_name, tp.status_pekerjaan,
                    tp.id_section as current_section_id, tp.id_line, tp.id_mesin,
                    tp.id_pekerjaan
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
                'history_id': row[0], 'number_wo': row[1], 'tgl_insert': row[2],
                'oleh': row[3], 'user_insert': row[4], 'mesin': row[5],
                'section_tujuan': row[6], 'pekerjaan': row[7], 'deskripsi_perbaikan': row[8],
                'status': row[9], 'approve': row[10], 'line_name': row[11],
                'tgl_his': row[12], 'jam_his': row[13], 'review_status': row[14],
                'reviewed_by': row[15], 'review_date': row[16], 'review_notes': row[17],
                'final_section_id': row[18], 'final_section_name': row[19],
                'status_pekerjaan': row[20], 'current_section_id': row[21],
                'id_line': row[22], 'id_mesin': row[23], 'id_pekerjaan': row[24]
            }
        
        # Cek apakah pengajuan siap di-review
        if pengajuan['status'] != STATUS_APPROVED or pengajuan['approve'] != APPROVE_YES:
            logger.warning(f"ENHANCED REVIEW: Pengajuan {nomor_pengajuan} not approved")
            messages.warning(request, 'Pengajuan ini belum di-approve oleh atasan.')
            return redirect('wo_maintenance_app:review_pengajuan_list')
        
        already_reviewed = pengajuan['review_status'] in ['1', '2']
        
        # Handle review form submission dengan auto transfer
        if request.method == 'POST' and not already_reviewed:
            logger.info(f"ENHANCED REVIEW: Processing POST with auto transfer for {nomor_pengajuan}")
            
            request.session.modified = True
            
            review_form = ReviewForm(request.POST)
            
            if review_form.is_valid():
                action = review_form.cleaned_data['action']
                target_section = review_form.cleaned_data.get('target_section', '')
                review_notes = review_form.cleaned_data['review_notes']
                
                logger.info(f"ENHANCED REVIEW: Form valid - Action: {action}, Target: {target_section}")
                
                try:
                    with connections['DB_Maintenance'].cursor() as cursor:
                        if action == 'process':
                            # Step 1: Update review status
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
                            
                            logger.info(f"ENHANCED REVIEW: Updated pengajuan {nomor_pengajuan} - final status A/Y")
                            
                            # Step 2: AUTO TRANSFER ke tabel_main
                            transfer_success = transfer_pengajuan_to_main(pengajuan, REVIEWER_EMPLOYEE_NUMBER)
                            
                            if transfer_success:
                                logger.info(f"ENHANCED REVIEW: Successfully transferred {nomor_pengajuan} to tabel_main")
                                
                                success_message = (
                                    f'Pengajuan {nomor_pengajuan} berhasil diproses dan diselesaikan! '
                                    f'Data sudah otomatis masuk ke History Maintenance untuk pengelolaan lebih lanjut.'
                                )
                                
                                if target_section:
                                    success_message += f' Section tujuan: {target_section}.'
                                
                                messages.success(request, success_message)
                                
                            else:
                                logger.error(f"ENHANCED REVIEW: Failed to transfer {nomor_pengajuan} to tabel_main")
                                messages.warning(request, 
                                    f'Pengajuan {nomor_pengajuan} berhasil diproses, '
                                    f'tetapi transfer ke History gagal. Silakan hubungi administrator.'
                                )
                            
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
                            
                            logger.info(f"ENHANCED REVIEW: Rejected pengajuan {nomor_pengajuan}")
                            messages.success(request, f'Pengajuan {nomor_pengajuan} berhasil ditolak. Alasan: {review_notes}')
                    
                    request.session.modified = True
                    request.session.save()
                    
                    return redirect('wo_maintenance_app:review_pengajuan_detail', nomor_pengajuan=nomor_pengajuan)
                    
                except Exception as update_error:
                    logger.error(f"ENHANCED REVIEW: Error processing review for {nomor_pengajuan}: {update_error}")
                    messages.error(request, f'Terjadi kesalahan saat memproses review: {str(update_error)}')
            else:
                logger.warning(f"ENHANCED REVIEW: Form validation failed for {nomor_pengajuan}: {review_form.errors}")
                messages.error(request, 'Form review tidak valid. Periksa kembali input Anda.')
        else:
            review_form = ReviewForm()
        
        # Basic available sections
        available_sections = [
            {'key': 'it', 'name': 'IT', 'section_id': 1},
            {'key': 'elektrik', 'name': 'Elektrik', 'section_id': 2},
            {'key': 'utility', 'name': 'Utility', 'section_id': 4},
            {'key': 'mekanik', 'name': 'Mekanik', 'section_id': 3}
        ]
        
        context = {
            'pengajuan': pengajuan,
            'review_form': review_form,
            'already_reviewed': already_reviewed,
            'reviewer_name': employee_data.get('fullname', REVIEWER_FULLNAME),
            'available_sections': available_sections,
            'employee_data': employee_data,
            'page_title': f'Enhanced Review dengan Auto Transfer {nomor_pengajuan}',
            'enhanced_mode': True,
            'auto_transfer_enabled': True
        }
        
        logger.info(f"ENHANCED REVIEW: Rendering enhanced template with auto transfer for {nomor_pengajuan}")
        return render(request, 'wo_maintenance_app/review_pengajuan_detail_enhanced.html', context)
        
    except Exception as e:
        logger.error(f"ENHANCED REVIEW: Critical error for {nomor_pengajuan}: {e}")
        import traceback
        logger.error(f"ENHANCED REVIEW: Traceback: {traceback.format_exc()}")
        messages.error(request, 'Terjadi kesalahan saat memuat enhanced review dengan auto transfer.')
        return redirect('wo_maintenance_app:review_pengajuan_list')
    
# @login_required
# def ajax_get_history_stats(request):
#     """
#     AJAX endpoint untuk mendapatkan statistik history
#     """
#     try:
#         stats = {}
        
#         with connections['DB_Maintenance'].cursor() as cursor:
#             # Basic stats
#             cursor.execute("SELECT COUNT(*) FROM tabel_main WHERE history_id IS NOT NULL")
#             stats['total'] = cursor.fetchone()[0] or 0
            
#             cursor.execute("SELECT COUNT(*) FROM tabel_main WHERE status = '0'")
#             stats['open'] = cursor.fetchone()[0] or 0
            
#             cursor.execute("SELECT COUNT(*) FROM tabel_main WHERE status = '1'")
#             stats['close'] = cursor.fetchone()[0] or 0
            
#             # Monthly stats
#             cursor.execute("""
#                 SELECT COUNT(*) FROM tabel_main 
#                 WHERE MONTH(tgl_insert) = MONTH(GETDATE()) 
#                 AND YEAR(tgl_insert) = YEAR(GETDATE())
#             """)
#             stats['this_month'] = cursor.fetchone()[0] or 0
            
#             # Today's edits
#             cursor.execute("""
#                 SELECT COUNT(*) FROM tabel_main 
#                 WHERE CAST(tgl_edit AS DATE) = CAST(GETDATE() AS DATE)
#             """)
#             stats['today_edits'] = cursor.fetchone()[0] or 0
        
#         return JsonResponse({
#             'success': True,
#             'stats': stats
#         })
        
#     except Exception as e:
#         logger.error(f"Error getting history stats: {e}")
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         })

# Update ajax_get_history_stats function:
# @login_required
# def ajax_get_history_stats(request):
#     """
#     AJAX endpoint untuk mendapatkan statistik history - UPDATED untuk O/C
#     """
#     try:
#         stats = {}
        
#         with connections['DB_Maintenance'].cursor() as cursor:
#             # Basic stats
#             cursor.execute("SELECT COUNT(*) FROM tabel_main WHERE history_id IS NOT NULL")
#             stats['total'] = cursor.fetchone()[0] or 0
            
#             # UPDATED: Status counts dengan O/C (dan backward compatibility)
#             cursor.execute("""
#                 SELECT COUNT(*) FROM tabel_main 
#                 WHERE status IN ('O', '0')
#             """)
#             stats['open'] = cursor.fetchone()[0] or 0
            
#             cursor.execute("""
#                 SELECT COUNT(*) FROM tabel_main 
#                 WHERE status IN ('C', '1')
#             """)
#             stats['close'] = cursor.fetchone()[0] or 0
            
#             # Monthly stats
#             cursor.execute("""
#                 SELECT COUNT(*) FROM tabel_main 
#                 WHERE MONTH(tgl_insert) = MONTH(GETDATE()) 
#                 AND YEAR(tgl_insert) = YEAR(GETDATE())
#             """)
#             stats['this_month'] = cursor.fetchone()[0] or 0
            
#             # Today's edits
#             cursor.execute("""
#                 SELECT COUNT(*) FROM tabel_main 
#                 WHERE CAST(tgl_edit AS DATE) = CAST(GETDATE() AS DATE)
#             """)
#             stats['today_edits'] = cursor.fetchone()[0] or 0
        
#         return JsonResponse({
#             'success': True,
#             'stats': stats
#         })
        
#     except Exception as e:
#         logger.error(f"Error getting history stats: {e}")
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         })

@login_required
def ajax_get_history_stats(request):
    """
    AJAX endpoint untuk mendapatkan statistik history - UPDATED: Hanya status pekerjaan
    """
    try:
        stats = {}
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Basic stats
            cursor.execute("SELECT COUNT(*) FROM tabel_main WHERE history_id IS NOT NULL")
            stats['total'] = cursor.fetchone()[0] or 0
            
            # UPDATED: Status counts hanya berdasarkan status_pekerjaan
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_main 
                WHERE status_pekerjaan IN ('O', '0')
            """)
            stats['pekerjaan_open'] = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_main 
                WHERE status_pekerjaan IN ('C', '1')
            """)
            stats['pekerjaan_close'] = cursor.fetchone()[0] or 0
            
            # Monthly stats
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_main 
                WHERE MONTH(tgl_insert) = MONTH(GETDATE()) 
                AND YEAR(tgl_insert) = YEAR(GETDATE())
            """)
            stats['this_month'] = cursor.fetchone()[0] or 0
            
            # Today's edits
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_main 
                WHERE CAST(tgl_edit AS DATE) = CAST(GETDATE() AS DATE)
            """)
            stats['today_edits'] = cursor.fetchone()[0] or 0
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting history stats: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# @login_required
# def ajax_quick_update_status(request):
#     """
#     AJAX endpoint untuk quick update status history
#     """
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'POST required'})
    
#     try:
#         data = json.loads(request.body)
#         history_id = data.get('history_id', '').strip()
#         new_status = data.get('status', '').strip()
        
#         if not history_id or new_status not in ['0', '1']:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Invalid parameters'
#             })
        
#         with connections['DB_Maintenance'].cursor() as cursor:
#             cursor.execute("""
#                 UPDATE tabel_main 
#                 SET status = %s, usert_edit = %s, tgl_edit = GETDATE()
#                 WHERE history_id = %s
#             """, [new_status, request.user.username, history_id])
            
#             if cursor.rowcount > 0:
#                 status_text = 'Close' if new_status == '1' else 'Open'
#                 return JsonResponse({
#                     'success': True,
#                     'message': f'Status history {history_id} berhasil diubah ke {status_text}'
#                 })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'History tidak ditemukan'
#                 })
        
#     except Exception as e:
#         logger.error(f"Error quick update status: {e}")
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         })

# @login_required
# def ajax_quick_update_status(request):
#     """
#     AJAX endpoint untuk quick update status history - FIXED untuk konsistensi
#     """
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'POST required'})
    
#     try:
#         data = json.loads(request.body)
#         history_id = data.get('history_id', '').strip()
#         new_status = data.get('status', '').strip()
#         field_type = data.get('field_type', 'status')  # 'status' atau 'status_pekerjaan'
        
#         # FIXED: Normalize status value
#         normalized_status = normalize_status_value(new_status)
        
#         if not history_id:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'History ID required'
#             })
        
#         # Determine field to update
#         if field_type == 'status_pekerjaan':
#             update_field = 'status_pekerjaan'
#         else:
#             update_field = 'status'
        
#         with connections['DB_Maintenance'].cursor() as cursor:
#             cursor.execute(f"""
#                 UPDATE tabel_main 
#                 SET {update_field} = %s, usert_edit = %s, tgl_edit = GETDATE()
#                 WHERE history_id = %s
#             """, [normalized_status, request.user.username, history_id])
            
#             if cursor.rowcount > 0:
#                 status_text = get_status_display_text(normalized_status)
#                 opposite_status = get_opposite_status(normalized_status)
                
#                 return JsonResponse({
#                     'success': True,
#                     'message': f'Status history {history_id} berhasil diubah ke {status_text}',
#                     'new_status': normalized_status,
#                     'status_display': status_text,
#                     'opposite_status': opposite_status,
#                     'field_type': field_type
#                 })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'History tidak ditemukan'
#                 })
        
#     except Exception as e:
#         logger.error(f"Error quick update status: {e}")
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         })

@login_required
def ajax_quick_update_status(request):
    """
    AJAX endpoint untuk quick update status history - UPDATED: Hanya status pekerjaan
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        history_id = data.get('history_id', '').strip()
        new_status = data.get('status', '').strip()
        
        # UPDATED: Hanya handle status_pekerjaan, bukan status umum
        # Status umum otomatis tetap 'A'
        
        # Normalize status value untuk status_pekerjaan
        normalized_status = normalize_status_value(new_status)
        
        if not history_id:
            return JsonResponse({
                'success': False,
                'error': 'History ID required'
            })
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # UPDATED: Hanya update status_pekerjaan, status umum tetap 'A'
            cursor.execute("""
                UPDATE tabel_main 
                SET status_pekerjaan = %s, 
                    status = 'A',
                    usert_edit = %s, 
                    tgl_edit = GETDATE()
                WHERE history_id = %s
            """, [normalized_status, request.user.username, history_id])
            
            if cursor.rowcount > 0:
                status_text = get_status_display_text(normalized_status)
                opposite_status = get_opposite_status(normalized_status)
                
                return JsonResponse({
                    'success': True,
                    'message': f'Status pekerjaan history {history_id} berhasil diubah ke {status_text}',
                    'new_status': normalized_status,
                    'status_display': status_text,
                    'opposite_status': opposite_status,
                    'field_type': 'status_pekerjaan'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'History tidak ditemukan'
                })
        
    except Exception as e:
        logger.error(f"Error quick update status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# Export tambahan untuk history
__all__ = [
    'history_pengajuan_list',
    'history_pengajuan_detail', 
    'enhanced_review_pengajuan_detail_with_transfer',
    'ajax_get_history_stats',
    'ajax_quick_update_status'
]

@login_required
def test_id_generation(request):
    """
    Test view untuk testing ID generation functions - SUPERUSER ONLY
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        from wo_maintenance_app.models import (
            create_new_history_id, 
            create_number_wo_with_section,
            get_section_code_mapping,
            get_section_display_name
        )
        
        test_results = {
            'timestamp': timezone.now().isoformat(),
            'tests': {}
        }
        
        # Test 1: History ID Generation
        history_ids = []
        for i in range(5):
            new_id = create_new_history_id()
            history_ids.append(new_id)
        
        test_results['tests']['history_id_generation'] = {
            'function': 'create_new_history_id()',
            'expected_format': 'YY-MM-NNNN (25-08-0001)',
            'generated_samples': history_ids,
            'pattern_check': all('-' in hid and len(hid.split('-')) == 3 for hid in history_ids)
        }
        
        # Test 2: Number WO Generation untuk semua section
        section_mapping = get_section_code_mapping()
        number_wo_tests = {}
        
        for section_id, section_code in section_mapping.items():
            section_name = get_section_display_name(section_code)
            number_wo = create_number_wo_with_section(section_id)
            
            number_wo_tests[f'section_{section_id}'] = {
                'section_id': section_id,
                'section_code': section_code,
                'section_name': section_name,
                'generated_number_wo': number_wo,
                'expected_format': f'YY-{section_code}-MM-NNNN',
                'pattern_check': section_code in number_wo
            }
        
        test_results['tests']['number_wo_generation'] = number_wo_tests
        
        # Test 3: Section Code Mapping
        test_results['tests']['section_mapping'] = {
            'mapping': section_mapping,
            'reverse_mapping': {code: get_section_display_name(code) for code in section_mapping.values()},
            'total_sections': len(section_mapping)
        }
        
        # Test 4: Database Compatibility Check
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Test insert dengan format baru (tanpa commit)
                test_history_id = create_new_history_id()
                test_number_wo = create_number_wo_with_section(2)  # Elektrik
                
                # Check field lengths
                cursor.execute("SELECT TOP 1 history_id, number_wo FROM tabel_pengajuan")
                sample_row = cursor.fetchone()
                
                test_results['tests']['database_compatibility'] = {
                    'test_history_id': test_history_id,
                    'test_number_wo': test_number_wo,
                    'history_id_length': len(test_history_id),
                    'number_wo_length': len(test_number_wo),
                    'max_history_id_db': 15,  # varchar(15) di tabel_pengajuan
                    'max_number_wo_db': 15,   # varchar(15) di tabel_pengajuan
                    'history_id_fits': len(test_history_id) <= 15,
                    'number_wo_fits': len(test_number_wo) <= 15,
                    'sample_existing_data': sample_row if sample_row else None
                }
        
        except Exception as db_error:
            test_results['tests']['database_compatibility'] = {
                'error': str(db_error),
                'status': 'failed'
            }
        
        # Test 5: Format Validation
        import re
        
        history_pattern = r'^\d{2}-\d{2}-\d{4}$'  # 25-08-0001
        number_wo_pattern = r'^\d{2}-[A-Z]-\d{2}-\d{4}$'  # 25-E-08-0001
        
        test_results['tests']['format_validation'] = {
            'history_id_pattern': history_pattern,
            'number_wo_pattern': number_wo_pattern,
            'history_id_samples_valid': [
                {
                    'id': hid,
                    'valid': bool(re.match(history_pattern, hid))
                } for hid in history_ids
            ],
            'number_wo_samples_valid': [
                {
                    'section': section_name,
                    'number_wo': number_wo,
                    'valid': bool(re.match(number_wo_pattern, number_wo))
                } for section_name, data in number_wo_tests.items() 
                for number_wo in [data['generated_number_wo']]
            ]
        }
        
        # Summary
        all_tests_passed = all([
            test_results['tests']['history_id_generation']['pattern_check'],
            all(data['pattern_check'] for data in number_wo_tests.values()),
            test_results['tests']['database_compatibility'].get('history_id_fits', False),
            test_results['tests']['database_compatibility'].get('number_wo_fits', False)
        ])
        
        test_results['summary'] = {
            'all_tests_passed': all_tests_passed,
            'total_tests': 5,
            'recommendations': []
        }
        
        if not all_tests_passed:
            test_results['summary']['recommendations'].append('Some tests failed - check individual test results')
        else:
            test_results['summary']['recommendations'].append('All tests passed - format ID baru ready untuk production')
        
        return JsonResponse(test_results, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@login_required 
def migrate_existing_ids(request):
    """
    Migration view untuk update existing data ke format ID baru - SUPERUSER ONLY
    WARNING: This will modify existing data
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Safety check
    if request.method != 'POST':
        return JsonResponse({
            'error': 'POST required',
            'warning': 'This operation will modify existing data. Use POST to confirm.',
            'instruction': 'Send POST request with "confirm=true" to proceed'
        })
    
    confirm = request.POST.get('confirm', '').lower() == 'true'
    if not confirm:
        return JsonResponse({
            'error': 'Confirmation required',
            'warning': 'This operation will modify existing data',
            'instruction': 'Send POST with confirm=true to proceed'
        })
    
    try:
        migration_results = {
            'timestamp': timezone.now().isoformat(),
            'migration_steps': [],
            'errors': [],
            'summary': {}
        }
        
        from wo_maintenance_app.models import create_number_wo_with_section
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Step 1: Backup existing data info
            cursor.execute("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN number_wo LIKE 'WO%' THEN 1 END) as old_format_count,
                       COUNT(CASE WHEN number_wo LIKE '__-_-__-____' THEN 1 END) as new_format_count
                FROM tabel_pengajuan 
                WHERE history_id IS NOT NULL
            """)
            
            backup_info = cursor.fetchone()
            migration_results['migration_steps'].append({
                'step': 'backup_analysis',
                'total_records': backup_info[0],
                'old_format_count': backup_info[1], 
                'new_format_count': backup_info[2],
                'status': 'completed'
            })
            
            # Step 2: Update Number WO untuk pengajuan yang sudah di-review (status A/Y)
            cursor.execute("""
                SELECT history_id, id_section, final_section_id, number_wo, status, approve
                FROM tabel_pengajuan 
                WHERE status = 'A' AND approve = 'Y'
                    AND (number_wo LIKE 'WO%' OR number_wo LIKE 'TEMP%')
                ORDER BY tgl_insert DESC
            """)
            
            reviewed_pengajuan = cursor.fetchall()
            updated_reviewed = 0
            
            for row in reviewed_pengajuan:
                history_id, id_section, final_section_id, old_number_wo, status, approve = row
                
                # Use final_section_id if available, otherwise id_section
                target_section_id = final_section_id if final_section_id else id_section
                
                if target_section_id:
                    try:
                        new_number_wo = create_number_wo_with_section(int(target_section_id))
                        
                        cursor.execute("""
                            UPDATE tabel_pengajuan 
                            SET number_wo = %s 
                            WHERE history_id = %s
                        """, [new_number_wo, history_id])
                        
                        # Also update tabel_main if exists
                        cursor.execute("""
                            UPDATE tabel_main 
                            SET number_wo = %s 
                            WHERE history_id = %s
                        """, [new_number_wo[:15], history_id[:11]])
                        
                        updated_reviewed += 1
                        
                    except Exception as update_error:
                        migration_results['errors'].append({
                            'history_id': history_id,
                            'error': str(update_error),
                            'step': 'update_reviewed_number_wo'
                        })
            
            migration_results['migration_steps'].append({
                'step': 'update_reviewed_number_wo',
                'processed': len(reviewed_pengajuan),
                'updated': updated_reviewed,
                'status': 'completed'
            })
            
            # Step 3: Clean up temporary Number WO untuk pending pengajuan
            cursor.execute("""
                UPDATE tabel_pengajuan 
                SET number_wo = CONCAT('TEMP-', FORMAT(tgl_insert, 'yyMMddHHmmss'))
                WHERE (status != 'A' OR approve != 'Y') 
                    AND (number_wo LIKE 'WO%' OR number_wo IS NULL)
            """)
            
            temp_updated = cursor.rowcount
            migration_results['migration_steps'].append({
                'step': 'clean_temp_number_wo',
                'updated': temp_updated,
                'status': 'completed'
            })
            
            # Step 4: Validate migration results
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN number_wo LIKE '__-_-__-____' THEN 1 END) as new_format,
                    COUNT(CASE WHEN number_wo LIKE 'TEMP-%' THEN 1 END) as temp_format,
                    COUNT(CASE WHEN number_wo LIKE 'WO%' THEN 1 END) as old_format_remaining
                FROM tabel_pengajuan 
                WHERE history_id IS NOT NULL
            """)
            
            validation_info = cursor.fetchone()
            migration_results['migration_steps'].append({
                'step': 'validation',
                'total_records': validation_info[0],
                'new_format_count': validation_info[1],
                'temp_format_count': validation_info[2], 
                'old_format_remaining': validation_info[3],
                'status': 'completed'
            })
        
        # Summary
        migration_results['summary'] = {
            'total_errors': len(migration_results['errors']),
            'migration_successful': len(migration_results['errors']) == 0,
            'reviewed_pengajuan_updated': updated_reviewed,
            'temp_number_wo_cleaned': temp_updated,
            'recommendation': (
                'Migration completed successfully' if len(migration_results['errors']) == 0 
                else f'Migration completed with {len(migration_results["errors"])} errors'
            )
        }
        
        return JsonResponse(migration_results, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@login_required
def validate_id_formats(request):
    """
    Validate existing ID formats di database - untuk monitoring
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        validation_results = {
            'timestamp': timezone.now().isoformat(),
            'validation_checks': {}
        }
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Check 1: History ID formats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN history_id LIKE 'WO%' THEN 1 END) as old_wo_format,
                    COUNT(CASE WHEN history_id LIKE '__-__-____' THEN 1 END) as new_dash_format,
                    COUNT(CASE WHEN LEN(history_id) > 15 THEN 1 END) as too_long
                FROM tabel_pengajuan 
                WHERE history_id IS NOT NULL
            """)
            
            history_check = cursor.fetchone()
            validation_results['validation_checks']['history_id_formats'] = {
                'total_records': history_check[0],
                'old_wo_format': history_check[1],
                'new_dash_format': history_check[2], 
                'too_long_for_db': history_check[3],
                'migration_needed': history_check[1] > 0
            }
            
            # Check 2: Number WO formats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN number_wo LIKE 'WO%' THEN 1 END) as old_wo_format,
                    COUNT(CASE WHEN number_wo LIKE '__-_-__-____' THEN 1 END) as new_section_format,
                    COUNT(CASE WHEN number_wo LIKE 'TEMP-%' THEN 1 END) as temp_format,
                    COUNT(CASE WHEN LEN(number_wo) > 15 THEN 1 END) as too_long
                FROM tabel_pengajuan 
                WHERE number_wo IS NOT NULL
            """)
            
            number_wo_check = cursor.fetchone()
            validation_results['validation_checks']['number_wo_formats'] = {
                'total_records': number_wo_check[0],
                'old_wo_format': number_wo_check[1],
                'new_section_format': number_wo_check[2],
                'temp_format': number_wo_check[3],
                'too_long_for_db': number_wo_check[4],
                'migration_needed': number_wo_check[1] > 0
            }
            
            # Check 3: Sample data untuk format validation
            cursor.execute("""
                SELECT TOP 10 history_id, number_wo, status, approve, tgl_insert
                FROM tabel_pengajuan 
                WHERE history_id IS NOT NULL
                ORDER BY tgl_insert DESC
            """)
            
            samples = []
            for row in cursor.fetchall():
                samples.append({
                    'history_id': row[0],
                    'number_wo': row[1],
                    'status': row[2],
                    'approve': row[3],
                    'tgl_insert': row[4].isoformat() if row[4] else None
                })
            
            validation_results['validation_checks']['sample_data'] = samples
            
            # Check 4: Potential issues
            issues = []
            
            if history_check[1] > 0:
                issues.append(f'{history_check[1]} history_id masih pake format lama (WO...)')
            
            if number_wo_check[1] > 0:  
                issues.append(f'{number_wo_check[1]} number_wo masih pake format lama (WO...)')
                
            if history_check[3] > 0:
                issues.append(f'{history_check[3]} history_id terlalu panjang untuk database')
                
            if number_wo_check[4] > 0:
                issues.append(f'{number_wo_check[4]} number_wo terlalu panjang untuk database')
            
            validation_results['issues'] = issues
            validation_results['issues_count'] = len(issues)
            validation_results['needs_migration'] = len(issues) > 0
        
        return JsonResponse(validation_results, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)

# wo_maintenance_app/views.py - ADD debug function untuk check database section mapping

@login_required
def debug_database_section_mapping(request):
    """
    Debug function untuk check actual section mapping di database - SUPERUSER ONLY
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        debug_info = {
            'timestamp': timezone.now().isoformat(),
            'database_sections': {},
            'form_mapping': {},
            'template_mapping': {},
            'consistency_check': {}
        }
        
        # 1. Check actual database sections
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT id_section, seksi, keterangan, status
                FROM tabel_msection 
                ORDER BY id_section
            """)
            
            db_sections = []
            for row in cursor.fetchall():
                section_id = int(float(row[0]))
                section_name = row[1] or 'N/A'
                keterangan = row[2] or 'N/A'
                status = row[3] or 'Active'
                
                db_sections.append({
                    'id': section_id,
                    'name': section_name,
                    'keterangan': keterangan,
                    'status': status
                })
            
            debug_info['database_sections'] = {
                'total_sections': len(db_sections),
                'sections': db_sections
            }
        
        # 2. Form mapping dari forms.py
        from wo_maintenance_app.forms import ReviewForm
        form = ReviewForm()
        form_choices = form.fields['target_section'].choices
        
        debug_info['form_mapping'] = {
            'choices': list(form_choices),
            'total_choices': len(form_choices)
        }
        
        # 3. Template mapping (hardcoded dari template)
        template_mapping = {
            'it': 1,
            'elektrik': 2,
            'mekanik': 3,
            'utility': 4,
            'civil': 5
        }
        debug_info['template_mapping'] = template_mapping
        
        # 4. Views mapping (dari views.py)
        views_mapping = {
            'it': {'id': 1, 'name': 'IT', 'code': 'I'},
            'elektrik': {'id': 2, 'name': 'Elektrik', 'code': 'E'},
            'mekanik': {'id': 3, 'name': 'Mekanik', 'code': 'M'},
            'utility': {'id': 4, 'name': 'Utility', 'code': 'U'},
            'civil': {'id': 5, 'name': 'Civil', 'code': 'C'}
        }
        debug_info['views_mapping'] = views_mapping
        
        # 5. Consistency check
        issues = []
        
        # Check each mapping
        for key, template_id in template_mapping.items():
            views_id = views_mapping.get(key, {}).get('id')
            views_name = views_mapping.get(key, {}).get('name')
            
            # Find corresponding database section
            db_section = next((s for s in db_sections if s['id'] == template_id), None)
            
            check_result = {
                'key': key,
                'template_id': template_id,
                'views_id': views_id,
                'views_name': views_name,
                'db_section': db_section,
                'consistent': True,
                'issues': []
            }
            
            # Check consistency
            if template_id != views_id:
                check_result['consistent'] = False
                check_result['issues'].append(f'Template ID ({template_id}) != Views ID ({views_id})')
            
            if not db_section:
                check_result['consistent'] = False
                check_result['issues'].append(f'Database section ID {template_id} not found')
            else:
                db_name = db_section['name'].upper()
                expected_name = views_name.upper() if views_name else key.upper()
                
                # Check if names match (flexible check)
                if expected_name not in db_name and db_name not in expected_name:
                    # Special cases
                    if key == 'utility' and ('UTILITY' in db_name or 'UTIL' in db_name):
                        pass  # OK
                    elif key == 'elektrik' and ('ELEKTRIK' in db_name or 'ELECTRIC' in db_name):
                        pass  # OK
                    elif key == 'mekanik' and ('MEKANIK' in db_name or 'MECHANIC' in db_name):
                        pass  # OK
                    else:
                        check_result['consistent'] = False
                        check_result['issues'].append(f'Database name "{db_name}" does not match expected "{expected_name}"')
            
            debug_info['consistency_check'][key] = check_result
            
            if not check_result['consistent']:
                issues.extend(check_result['issues'])
        
        # 6. Root cause analysis
        debug_info['root_cause_analysis'] = {
            'total_issues': len(issues),
            'issues': issues,
            'likely_cause': 'Database section names or IDs do not match expected mapping',
            'solution': 'Fix mapping to match actual database content'
        }
        
        # 7. Recommendations
        recommendations = []
        
        if issues:
            recommendations.append('UPDATE mapping in views.py to match actual database content')
            recommendations.append('UPDATE template data-section-id to match database')
            recommendations.append('Consider creating migration to fix database section names')
        else:
            recommendations.append('All mappings are consistent')
        
        debug_info['recommendations'] = recommendations
        
        return JsonResponse(debug_info, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)
    

   # AJAX endpoint untuk preview number WO change
@login_required
@reviewer_required_fixed  
def ajax_preview_number_wo_change(request):
    """
    AJAX endpoint untuk preview perubahan number WO
    """
    try:
        history_id = request.GET.get('history_id', '').strip()
        target_section = request.GET.get('target_section', '').strip()
        
        if not history_id or not target_section:
            return JsonResponse({
                'success': False,
                'error': 'history_id and target_section required'
            })
        
        # Get current pengajuan data
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT id_section, number_wo, seksi
                FROM tabel_pengajuan tp
                LEFT JOIN tabel_msection ms ON tp.id_section = ms.id_section
                WHERE tp.history_id = %s
            """, [history_id])
            
            row = cursor.fetchone()
            if not row:
                return JsonResponse({
                    'success': False,
                    'error': 'Pengajuan tidak ditemukan'
                })
            
            current_section_id = int(float(row[0])) if row[0] else None
            current_number_wo = row[1] or 'Unknown'
            current_section_name = row[2] or 'Unknown'
        
        # Generate preview
        preview = preview_number_wo_change(current_section_id, target_section, current_number_wo)
        
        # Enhanced response
        response_data = {
            'success': True,
            'history_id': history_id,
            'target_section': target_section,
            'current_section': {
                'id': current_section_id,
                'name': current_section_name
            },
            'preview': preview,
            'recommendation': (
                'Number WO akan diperbarui dengan format section baru' if preview['will_change'] 
                else 'Number WO akan tetap sama'
            )
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in ajax_preview_number_wo_change: {e}")
        
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# Debug endpoint untuk test number WO generation
@login_required
def debug_number_wo_generation(request):
    """
    Debug endpoint untuk test number WO generation - SUPERUSER ONLY
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        from wo_maintenance_app.models import create_number_wo_with_section, get_section_code_mapping
        
        debug_info = {
            'timestamp': timezone.now().isoformat(),
            'test_results': {}
        }
        
        # Test generation untuk semua section
        section_mapping = get_section_code_mapping()
        
        for section_id, section_code in section_mapping.items():
            try:
                test_number_wo = create_number_wo_with_section(section_id)
                validation = validate_number_wo_format(test_number_wo)
                
                debug_info['test_results'][f'section_{section_id}'] = {
                    'section_id': section_id,
                    'section_code': section_code,
                    'generated_number_wo': test_number_wo,
                    'validation': validation,
                    'success': validation['is_new_format']
                }
                
            except Exception as e:
                debug_info['test_results'][f'section_{section_id}'] = {
                    'section_id': section_id,
                    'section_code': section_code,
                    'error': str(e),
                    'success': False
                }
        
        # Test preview function
        debug_info['preview_tests'] = {}
        
        test_cases = [
            {'current_section': 1, 'target': 'elektrik', 'current_wo': '25-I-08-0001'},
            {'current_section': 2, 'target': 'elektrik', 'current_wo': '25-E-08-0001'},
            {'current_section': 1, 'target': 'mekanik', 'current_wo': 'WO250801001'}
        ]
        
        for i, case in enumerate(test_cases):
            preview = preview_number_wo_change(
                case['current_section'], 
                case['target'], 
                case['current_wo']
            )
            debug_info['preview_tests'][f'case_{i+1}'] = {
                'test_case': case,
                'preview_result': preview
            }
        
        return JsonResponse(debug_info, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


# Export functions
__all__ = [
    'get_section_code_for_target',
    'preview_number_wo_change', 
    'validate_number_wo_format',
    'ajax_preview_number_wo_change',
    'debug_number_wo_generation'
]

# Update function untuk update history maintenance:
def update_history_maintenance(history_id, form_data, user):
    """
    Update data history maintenance - UPDATED untuk support O/C
    
    Args:
        history_id: ID history yang akan diupdate
        form_data: Data dari form
        user: User yang melakukan update
    
    Returns:
        dict: Result dengan success status dan message
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Validasi status values (O/C dengan backward compatibility)
            status = form_data.get('status', 'O')
            status_pekerjaan = form_data.get('status_pekerjaan', 'O')
            
            # Ensure valid values
            if status not in ['O', 'C']:
                status = 'O'  # Default ke Open
            if status_pekerjaan not in ['O', 'C']:
                status_pekerjaan = 'O'  # Default ke Open
            
            # Build update query dengan semua fields
            update_fields = []
            update_params = []
            
            # Text fields
            text_fields = [
                'penyebab', 'akar_masalah', 'tindakan_perbaikan', 
                'tindakan_pencegahan', 'pic_produksi', 'pic_maintenance',
                'alasan_dt', 'alasan_delay', 'masalah'
            ]
            
            for field in text_fields:
                if field in form_data:
                    value = form_data[field]
                    if value:  # Only update if not empty
                        update_fields.append(f"{field} = %s")
                        update_params.append(value)
            
            # Datetime fields
            datetime_fields = [
                'tgl_wp_dari', 'tgl_wp_sampai', 'tgl_lt_dari', 'tgl_lt_sampai',
                'tgl_dt_dari', 'tgl_dt_sampai', 'tgl_estimasidt', 'tgl_selesai'
            ]
            
            for field in datetime_fields:
                if field in form_data and form_data[field]:
                    update_fields.append(f"{field} = %s")
                    update_params.append(form_data[field])
            
            # Status fields - UPDATED untuk O/C
            update_fields.extend([
                "status = %s",
                "status_pekerjaan = %s",
                "usert_edit = %s",
                "tgl_edit = GETDATE()"
            ])
            update_params.extend([
                status,
                status_pekerjaan,
                user.username
            ])
            
            # Build final query
            update_query = f"""
                UPDATE tabel_main 
                SET {', '.join(update_fields)}
                WHERE history_id = %s
            """
            update_params.append(history_id)
            
            # Execute update
            cursor.execute(update_query, update_params)
            
            if cursor.rowcount > 0:
                logger.info(f"Successfully updated history {history_id} by {user.username}")
                return {
                    'success': True,
                    'message': f'Data history {history_id} berhasil diperbarui!'
                }
            else:
                return {
                    'success': False,
                    'message': f'History {history_id} tidak ditemukan atau tidak ada perubahan.'
                }
            
    except Exception as e:
        logger.error(f"Error updating history {history_id}: {e}")
        return {
            'success': False,
            'message': f'Terjadi kesalahan saat mengupdate data: {str(e)}'
        }

def normalize_status_value(status_value):
    """
    Normalize status value untuk konsistensi O/C
    """
    if status_value in ['O', 'o', '0']:
        return 'O'  # Open
    elif status_value in ['C', 'c', '1']:
        return 'C'  # Close
    else:
        return 'O'  # Default ke Open

def get_status_display_text(status_value):
    """
    Get display text untuk status
    """
    normalized = normalize_status_value(status_value)
    return 'Open' if normalized == 'O' else 'Close'

def get_opposite_status(status_value):
    """
    Get opposite status untuk toggle button
    """
    normalized = normalize_status_value(status_value)
    return 'C' if normalized == 'O' else 'O'

def get_status_button_class(status_value):
    """
    Get CSS class untuk status button
    """
    normalized = normalize_status_value(status_value)
    return 'btn-success' if normalized == 'O' else 'btn-secondary'

def get_status_button_text(status_value):
    """
    Get text untuk status button (opposite action)
    """
    normalized = normalize_status_value(status_value)
    return 'Set to Close' if normalized == 'O' else 'Set to Open'

# Export functions
__all__ = [
    'history_pengajuan_list',
    'history_pengajuan_detail', 
    'ajax_get_history_stats',
    'ajax_quick_update_status',
    'normalize_status_value',
    'get_status_display_text',
    'get_opposite_status'
]

def load_checkers_from_database_enhanced():
    """
    Enhanced version: Load checker data dengan include langsung di monitoring query
    Biar nama checker langsung kepanggil pas query monitoring data
    """
    checker_data = {}
    
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            logger.info("Loading enhanced checker data from tabel_pengajuan...")
            
            # Load checker data dari tabel_pengajuan dengan status '1' (sudah dicek)
            cursor.execute("""
                SELECT 
                    history_id, 
                    checker_name, 
                    checker_time, 
                    checker_device_id, 
                    checker_status,
                    checker_notes
                FROM tabel_pengajuan 
                WHERE checker_status = '1' 
                  AND checker_name IS NOT NULL 
                  AND checker_name != ''
                  AND history_id IS NOT NULL
                  AND history_id != ''
                ORDER BY checker_time DESC
            """)
            
            pengajuan_rows = cursor.fetchall()
            logger.info(f"Found {len(pengajuan_rows)} checked pengajuan items")
            
            for row in pengajuan_rows:
                history_id, checker_name, checker_time, device_id, status, notes = row
                if history_id:
                    checker_data[f"row-{history_id}"] = {
                        'user': checker_name,
                        'time': checker_time.isoformat() if checker_time else None,
                        'device_id': device_id,
                        'status': status,
                        'notes': notes,
                        'status_type': 'pengajuan',
                        'source_table': 'tabel_pengajuan',
                        'last_updated': checker_time.isoformat() if checker_time else None,
                        'display_time': checker_time.strftime('%d/%m %H:%M') if checker_time else None
                    }
                    logger.debug(f"Loaded checker: {history_id} -> {checker_name}")
            
            # Load checker dari tabel_main juga (untuk diproses)
            cursor.execute("""
                SELECT 
                    history_id, 
                    checker_name, 
                    checker_time, 
                    checker_device_id, 
                    checker_status,
                    checker_transferred_from,
                    checker_notes
                FROM tabel_main 
                WHERE checker_status = '1' 
                  AND checker_name IS NOT NULL 
                  AND checker_name != ''
                  AND history_id IS NOT NULL
                  AND history_id != ''
                ORDER BY checker_time DESC
            """)
            
            main_rows = cursor.fetchall()
            logger.info(f"Found {len(main_rows)} checked main items")
            
            for row in main_rows:
                history_id, checker_name, checker_time, device_id, status, transferred_from, notes = row
                if history_id:
                    # Use transferred_from untuk mapping kalo ada
                    mapping_id = transferred_from if transferred_from else history_id
                    
                    checker_data[f"row-{mapping_id}"] = {
                        'user': checker_name,
                        'time': checker_time.isoformat() if checker_time else None,
                        'device_id': device_id,
                        'status': status,
                        'notes': notes,
                        'status_type': 'diproses',
                        'source_table': 'tabel_main',
                        'short_history_id': history_id,
                        'transferred_from': transferred_from,
                        'last_updated': checker_time.isoformat() if checker_time else None,
                        'display_time': checker_time.strftime('%d/%m %H:%M') if checker_time else None
                    }
                    logger.debug(f"Loaded main checker: {mapping_id} -> {checker_name}")
            
            logger.info(f"Total enhanced checker data loaded: {len(checker_data)}")
            return checker_data
            
    except Exception as e:
        logger.error(f"Error loading enhanced checkers: {e}")
        return {}

def load_checkers_from_database_mapping_fix():
    """
    MAPPING FIX: Load checker data dengan multiple mapping keys
    """
    checker_data = {}
    
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Get checker data dari tabel_pengajuan
            cursor.execute("""
                SELECT 
                    history_id, checker_name, checker_time, checker_device_id, 
                    checker_status, checker_notes
                FROM tabel_pengajuan 
                WHERE checker_status = '1' 
                  AND checker_name IS NOT NULL 
                  AND checker_name != ''
                  AND history_id IS NOT NULL
                  AND history_id != ''
            """)
            
            pengajuan_rows = cursor.fetchall()
            logger.info(f"MAPPING FIX: Found {len(pengajuan_rows)} checked items in tabel_pengajuan")
            
            for row in pengajuan_rows:
                history_id, checker_name, checker_time, device_id, status, notes = row
                if history_id:
                    checker_info = {
                        'user': checker_name,
                        'time': checker_time.isoformat() if checker_time else None,
                        'device_id': device_id,
                        'status': status,
                        'notes': notes,
                        'status_type': 'pengajuan',
                        'source_table': 'tabel_pengajuan',
                        'last_updated': checker_time.isoformat() if checker_time else None
                    }
                    
                    # MAPPING FIX: Buat multiple keys untuk handle berbagai format
                    # Key 1: Format asli
                    checker_data[f"row-{history_id}"] = checker_info
                    
                    # Key 2: Format dengan pattern "XXXXX -- YYYY" jika ada yang match
                    # Coba detect apakah ada format gabungan di monitoring data
                    logger.info(f"MAPPING FIX: Adding checker key for pengajuan: row-{history_id}")
            
            # Get checker data dari tabel_main
            cursor.execute("""
                SELECT 
                    history_id, checker_name, checker_time, checker_device_id, 
                    checker_status, checker_transferred_from, checker_notes
                FROM tabel_main 
                WHERE checker_status = '1' 
                  AND checker_name IS NOT NULL 
                  AND checker_name != ''
                  AND history_id IS NOT NULL
                  AND history_id != ''
            """)
            
            main_rows = cursor.fetchall()
            logger.info(f"MAPPING FIX: Found {len(main_rows)} checked items in tabel_main")
            
            for row in main_rows:
                history_id, checker_name, checker_time, device_id, status, transferred_from, notes = row
                if history_id:
                    checker_info = {
                        'user': checker_name,
                        'time': checker_time.isoformat() if checker_time else None,
                        'device_id': device_id,
                        'status': status,
                        'notes': notes,
                        'status_type': 'diproses',
                        'source_table': 'tabel_main',
                        'short_history_id': history_id,
                        'transferred_from': transferred_from,
                        'last_updated': checker_time.isoformat() if checker_time else None
                    }
                    
                    # Use transferred_from for mapping if available
                    mapping_id = transferred_from if transferred_from else history_id
                    checker_data[f"row-{mapping_id}"] = checker_info
                    
                    logger.info(f"MAPPING FIX: Adding checker key for main: row-{mapping_id}")
            
            logger.info(f"MAPPING FIX: Total checker data loaded: {len(checker_data)}")
            logger.info(f"MAPPING FIX: Checker keys: {list(checker_data.keys())[:5]}")
            
            return checker_data
            
    except Exception as e:
        logger.error(f"MAPPING FIX: Error loading checkers from database: {e}")
        return {}
# Enhanced AJAX refresh juga
@login_required
def ajax_monitoring_refresh_enhanced(request):
    """
    Enhanced AJAX refresh dengan direct checker query
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    monitoring_data = []
    
    try:
        # Load enhanced checker data
        existing_checkers = load_checkers_from_database_enhanced()
        
        with connections['DB_Maintenance'].cursor() as cursor:
            today = timezone.now().date()
            
            # SAME ENHANCED QUERY as monitoring view
            cursor.execute(f"""
                SELECT 
                    a.history_id,
                    MAX(a.tgl_his) as tgl_his,
                    MAX(a.jam_his) as jam_his,
                    a.id_line,
                    a.id_mesin,
                    MAX(a.deskripsi_perbaikan) as deskripsi_perbaikan,
                    MAX(a.number_wo) as number_wo,
                    MAX(b.line) as line,
                    MAX(c.mesin) as mesin,
                    MAX(a.status_pekerjaan) as status_pekerjaan,
                    MAX(a.status) as status,
                    MAX(c.nomer) as nomer,
                    MAX(d.seksi) as seksi,
                    MAX(a.prima) as prima,
                    MAX(a.approve) as approve,
                    MAX(a.oleh) as oleh,
                    -- ENHANCED: Include checker data
                    MAX(a.checker_name) as checker_name,
                    MAX(a.checker_time) as checker_time,
                    MAX(a.checker_status) as checker_status
                FROM (
                    SELECT 
                        tp.history_id, tp.tgl_his, tp.jam_his, tp.id_line, tp.id_mesin,
                        tp.deskripsi_perbaikan, tp.number_wo, tp.status_pekerjaan,
                        tp.status, tp.id_section, NULL as prima, tp.approve, tp.oleh,
                        tp.checker_name, tp.checker_time, tp.checker_status
                    FROM tabel_pengajuan tp
                    WHERE tp.status_pekerjaan != 'C'
                      AND tp.history_id IS NOT NULL 
                      AND tp.history_id != ''
                    
                    UNION ALL
                    
                    SELECT 
                        tm.history_id, tm.tgl_his, tm.jam_his, tm.id_line, tm.id_mesin,
                        tm.deskripsi_perbaikan, tm.number_wo, tm.status_pekerjaan,
                        tm.status, tm.id_section, tm.PriMa as prima, NULL as approve, tm.oleh,
                        tm.checker_name, tm.checker_time, tm.checker_status
                    FROM tabel_main tm
                    WHERE tm.status_pekerjaan != 'C'
                      AND tm.history_id IS NOT NULL 
                      AND tm.history_id != ''
                ) a
                LEFT JOIN tabel_line b ON b.id_line = a.id_line
                LEFT JOIN tabel_mesin c ON c.id_mesin = a.id_mesin
                LEFT JOIN tabel_msection d ON d.id_section = a.id_section
                WHERE convert(datetime,a.tgl_his,120) BETWEEN 
                    dateadd(day, -1, convert(datetime,'{today}' + ' 19:30:00.000',120)) AND 
                    dateadd(day, 1, convert(datetime,'{today}' + ' 06:59:59.000',120))
                GROUP BY a.history_id, a.id_line, a.id_mesin
                ORDER BY MAX(a.tgl_his) DESC
            """)
            
            results = cursor.fetchall()
            
            # Process sama seperti view utama
            for row in results:
                history_id = row[0]
                tgl_his = row[1]
                jam_his = row[2]
                id_line = row[3] 
                id_mesin = row[4]
                deskripsi_perbaikan = row[5]
                number_wo = row[6] if row[6] else ''
                line_name = row[7]
                mesin_name = row[8]
                status_pekerjaan = row[9] if row[9] else ''
                status = row[10] if row[10] else ''
                nomer = row[11]
                seksi = row[12]
                prima = row[13]
                approve = row[14] if len(row) > 14 else None
                oleh = row[15] if len(row) > 15 else ''
                db_checker_name = row[16] if len(row) > 16 else None
                db_checker_time = row[17] if len(row) > 17 else None
                db_checker_status = row[18] if len(row) > 18 else None
                
                if status_pekerjaan == 'C':
                    continue
                
                # Status determination
                if (not number_wo or number_wo.strip() == '' or number_wo.startswith('TEMP-') or (status != 'A' and approve != 'Y')):
                    status_display = 'pengajuan'
                elif (status == 'A' and approve == 'Y' and status_pekerjaan == 'O'):
                    status_display = 'diproses'
                else:
                    status_display = 'diproses'
                
                # Enhanced checker mapping
                checker_key = f"row-{history_id}"
                checker_info = existing_checkers.get(checker_key, {})
                
                final_checker_name = db_checker_name if db_checker_name else checker_info.get('user', '')
                final_checker_time = db_checker_time if db_checker_time else None
                final_checker_status = db_checker_status if db_checker_status else checker_info.get('status', '0')
                has_checker = (final_checker_status == '1' and final_checker_name and final_checker_name.strip() != '')
                
                waktu_display = ''
                if tgl_his:
                    waktu_display = tgl_his.strftime('%d/%m/%Y') + ' - ' + tgl_his.strftime('%H:%M:%S') + ' WIB'
                
                mesin_display = f"{mesin_name or ''} {nomer or ''}".strip() or '-'
                
                monitoring_data.append({
                    'prioritas': prima or '-',
                    'waktu_pengajuan': waktu_display,
                    'no_pengajuan': history_id,
                    'nomor_wo': number_wo or '-',
                    'line_name': line_name or '-',
                    'mesin_name': mesin_display,
                    'deskripsi': deskripsi_perbaikan or '-',
                    'section_name': seksi or '-',
                    'status': status_display,
                    'oleh': oleh or '-',
                    
                    # Enhanced checker integration
                    'has_checker': has_checker,
                    'checker_name': final_checker_name,
                    'checker_time': final_checker_time.isoformat() if final_checker_time else '',
                    'checker_display_time': final_checker_time.strftime('%d/%m %H:%M') if final_checker_time else '',
                    'checker_source_table': checker_info.get('source_table', 'tabel_pengajuan'),
                    'checker_status_type': status_display
                })
        
        stats = {
            'total_pengajuan': len([x for x in monitoring_data if x['status'] == 'pengajuan']),
            'total_diproses': len([x for x in monitoring_data if x['status'] == 'diproses']),
            'total_all': len(monitoring_data),
            'total_checked': len([x for x in monitoring_data if x['has_checker']]),
            'last_update': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        # Debug logging
        checked_items = [item for item in monitoring_data if item['has_checker']]
        logger.info(f"Enhanced Ajax: Found {len(checked_items)} items with checkers")
        
        return JsonResponse({
            'success': True,
            'data': monitoring_data,
            'stats': stats,
            'checker_data': existing_checkers,
            'enhanced_mode': True,
            'sync_timestamp': timezone.now().timestamp()
        })
        
    except Exception as e:
        logger.error(f"Enhanced Ajax error: {e}")
        return JsonResponse({
            'success': True,
            'data': [],
            'stats': {
                'total_pengajuan': 0, 'total_diproses': 0,
                'total_all': 0, 'total_checked': 0,
                'last_update': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
            },
            'checker_data': {},
            'message': 'No data available',
            'enhanced_mode': True
        })
    
@login_required   
def monitoring_informasi_system(request):
    """
    MAPPING FIX: View monitoring dengan consistent checker mapping
    """
    
    employee_data = request.session.get('employee_data', {})
    monitoring_data = []
    
    try:
        # Load checker data dengan mapping fix
        existing_checkers = load_checkers_from_database_mapping_fix()
        logger.info(f"MAPPING FIX Monitoring: Loaded {len(existing_checkers)} existing checkers")
        
        with connections['DB_Maintenance'].cursor() as cursor:
            today = timezone.now().date()
            
            # Query monitoring data (sama dengan view utama)
            try:
                cursor.execute("SELECT COUNT(*) FROM View_Monitor2 WHERE 1=0")
                use_view_monitor = True
            except:
                use_view_monitor = False
                logger.warning("View_Monitor not found, using manual UNION query")
            
            if use_view_monitor:
                cursor.execute(f"""
                    SELECT 
                        a.history_id,
                        MAX(a.tgl_his) as tgl_his,
                        MAX(a.jam_his) as jam_his,
                        a.id_line,
                        a.id_mesin,
                        MAX(a.deskripsi_perbaikan) as deskripsi_perbaikan,
                        MAX(a.number_wo) as number_wo,
                        MAX(b.line) as line,
                        MAX(c.mesin) as mesin,
                        MAX(a.status_pekerjaan) as status_pekerjaan,
                        MAX(a.status) as status,
                        MAX(a.user_insert) as user_insert,
                        MAX(a.tgl_insert) as tgl_insert,
                        MAX(a.oleh) as oleh,
                        MAX(c.nomer) as nomer,
                        MAX(d.seksi) as seksi,
                        MAX(a.prima) as prima,
                        MAX(a.approve) as approve,
                        MAX(a.checker_name) as checker_name,   -- ✅ tambahkan
                        MAX(a.checker_time) as checker_time    -- ✅ tambahkan
                    FROM View_Monitor2 a 
                    JOIN tabel_line b ON b.id_line = a.id_line
                    JOIN tabel_mesin c ON c.id_mesin = a.id_mesin
                    JOIN tabel_msection d ON d.id_section = a.id_section
                    WHERE a.status_pekerjaan != 'C' 
                      AND a.history_id IS NOT NULL 
                      AND a.history_id != ''
                      AND convert(datetime,a.tgl_his,120) BETWEEN 
                          dateadd(day, -1, convert(datetime,'{today}' + ' 19:30:00.000',120)) AND 
                          dateadd(day, 1, convert(datetime,'{today}' + ' 06:59:59.000',120))
                    GROUP BY a.history_id, a.id_line, a.id_mesin
                    ORDER BY
                        CASE
                            WHEN MAX(a.number_wo) = '' OR MAX(a.number_wo) IS NULL THEN 0
                            ELSE 1
                        END, 
                        MAX(a.tgl_his) DESC
                """)
            else:
                # Manual UNION query
                cursor.execute(f"""
                    SELECT 
                        a.history_id,
                        MAX(a.tgl_his) as tgl_his,
                        MAX(a.jam_his) as jam_his,
                        a.id_line,
                        a.id_mesin,
                        MAX(a.deskripsi_perbaikan) as deskripsi_perbaikan,
                        MAX(a.number_wo) as number_wo,
                        MAX(b.line) as line,
                        MAX(c.mesin) as mesin,
                        MAX(a.status_pekerjaan) as status_pekerjaan,
                        MAX(a.status) as status,
                        MAX(a.user_insert) as user_insert,
                        MAX(a.tgl_insert) as tgl_insert,
                        MAX(a.oleh) as oleh,
                        MAX(c.nomer) as nomer,
                        MAX(d.seksi) as seksi,
                        MAX(a.prima) as prima,
                        MAX(a.approve) as approve,
                        MAX(a.checker_name) as checker_name,
                        MAX(a.checker_time) as checker_time
                    FROM (
                        SELECT 
                            tp.history_id,
                            tp.tgl_his,
                            tp.jam_his,
                            tp.id_line,
                            tp.id_mesin,
                            tp.deskripsi_perbaikan,
                            tp.number_wo,
                            tp.status_pekerjaan,
                            tp.status,
                            tp.id_section,
                            NULL as prima,
                            tp.tgl_insert,
                            tp.user_insert,
                            tp.oleh,
                            tp.approve,
                            tp.checker_name,
                            tp.checker_time
                        FROM tabel_pengajuan tp
                        WHERE tp.status_pekerjaan != 'C'
                          AND tp.history_id IS NOT NULL 
                          AND tp.history_id != ''
                        
                        UNION ALL
                        
                        SELECT 
                            tm.history_id,
                            tm.tgl_his,
                            tm.jam_his,
                            tm.id_line,
                            tm.id_mesin,
                            tm.deskripsi_perbaikan,
                            tm.number_wo,
                            tm.status_pekerjaan,
                            tm.status,
                            tm.id_section,
                            tm.PriMa as prima,
                            tm.tgl_insert,
                            NULL as user_insert,
                            tm.oleh,
                            NULL as approve,
                               tm.checker_name,
                            tm.checker_time
                        FROM tabel_main tm
                        WHERE tm.status_pekerjaan != 'C'
                          AND tm.history_id IS NOT NULL 
                          AND tm.history_id != ''
                    ) a
                    LEFT JOIN tabel_line b ON b.id_line = a.id_line
                    LEFT JOIN tabel_mesin c ON c.id_mesin = a.id_mesin
                    LEFT JOIN tabel_msection d ON d.id_section = a.id_section
                    WHERE convert(datetime,a.tgl_his,120) BETWEEN 
                        dateadd(day, -1, convert(datetime,'{today}' + ' 19:30:00.000',120)) AND 
                        dateadd(day, 1, convert(datetime,'{today}' + ' 06:59:59.000',120))
                    GROUP BY a.history_id, a.id_line, a.id_mesin
                    ORDER BY
                        CASE
                            WHEN MAX(a.number_wo) = '' OR MAX(a.number_wo) IS NULL THEN 0
                            ELSE 1
                        END, 
                        MAX(a.tgl_his) DESC
                """)
            
            results = cursor.fetchall()
            
            # MAPPING FIX: Process data dengan improved checker mapping
            for row in results:
                history_id = row[0]  # history_id asli dari database
                tgl_his = row[1]
                jam_his = row[2]
                id_line = row[3] 
                id_mesin = row[4]
                deskripsi_perbaikan = row[5]
                number_wo = row[6] if row[6] else ''
                line_name = row[7]
                mesin_name = row[8]
                status_pekerjaan = row[9] if row[9] else ''
                status = row[10] if row[10] else ''
                user_insert = row[11]
                tgl_insert = row[12]
                oleh = row[13]
                nomer = row[14]
                seksi = row[15]
                prima = row[16]
                approve = row[17] if len(row) > 17 else None
                checker_name = row[18] if len(row) > 18 else ''
                checker_time = row[19] if len(row) > 19 else None


                
                # Skip jika completed
                if status_pekerjaan == 'C':
                    continue
                
                # Determine status display
                if (not number_wo or 
                    number_wo.strip() == '' or 
                    number_wo.startswith('TEMP-') or
                    (status != 'A' and approve != 'Y')):
                    status_display = 'pengajuan'
                    status_color = '#DC143C'
                elif (status == 'A' and 
                      approve == 'Y' and 
                      status_pekerjaan == 'O'):
                    status_display = 'diproses'
                    status_color = '#7FFF00'
                else:
                    status_display = 'diproses'
                    status_color = '#7FFF00'
                
                # MAPPING FIX: Check database checker dengan exact history_id
                checker_key = f"row-{history_id}"
                # has_checker = checker_key in existing_checkers
                checker_info = existing_checkers.get(checker_key, {})

                final_checker_name = checker_name or checker_info.get('user', '')
                final_checker_time = checker_time or checker_info.get('time', '')
                has_checker = bool(final_checker_name and str(final_checker_name).strip() != '')

                logger.debug(
                f"Row {history_id} -> checker_name={checker_name}, "
                f"checker_time={checker_time}, "
                f"final_name={final_checker_name}, "
                f"has_checker={has_checker}"
    )

                
                # logger.debug(f"MAPPING FIX: Checking history_id '{history_id}' -> key '{checker_key}' -> found: {has_checker}")
                # if has_checker:
                #     logger.info(f"MAPPING FIX: Found checker for {history_id}: {checker_info.get('user', 'Unknown')}")
                
                # Format waktu
                waktu_display = ''
                if tgl_his:
                    waktu_display = tgl_his.strftime('%d/%m/%Y') + ' - ' + tgl_his.strftime('%H:%M:%S') + ' WIB'
                
                # Gabung mesin + nomer
                mesin_display = f"{mesin_name or ''} {nomer or ''}".strip() or '-'
                
                # MAPPING FIX: Use clean history_id for both no_pengajuan and row mapping  
                monitoring_data.append({
                    'history_id': history_id,  # history_id asli
                    'prioritas': prima or '-',
                    'waktu_pengajuan': waktu_display,
                    'no_pengajuan': history_id,  # MAPPING FIX: Use clean history_id
                    'nomor_wo': number_wo or '-',
                    'line_name': line_name or '-',
                    'mesin_name': mesin_display,
                    'deskripsi': deskripsi_perbaikan or '-',
                    'section_name': seksi or '-',
                    'status': status_display,
                    'status_color': status_color,
                    'tgl_insert': tgl_insert,
                    
                    # Database checker info
                    'has_checker': has_checker,
                    'checker_name': final_checker_name,
                    'checker_time': (
                        final_checker_time.strftime('%Y-%m-%d %H:%M:%S') 
                        if isinstance(final_checker_time, datetime) else final_checker_time
                    ),
                    'checker_source_table': checker_info.get('source_table', 'View_Monitor2' if checker_name else ''),
                    'checker_status_type': checker_info.get('status_type', status_display)
                })
                
    except Exception as e:
        logger.error(f"MAPPING FIX: Error loading standalone monitoring data: {e}")
        monitoring_data = []
    
    # Debug logging untuk checker mapping
    checked_items = [item for item in monitoring_data if item['has_checker']]
    logger.info(f"MAPPING FIX: Found {len(checked_items)} items with checkers")
    for item in checked_items:
        logger.info(f"MAPPING FIX: Item {item['no_pengajuan']} checked by {item['checker_name']}")
    
    # Statistik
    stats = {
        'total_pengajuan': len([x for x in monitoring_data if x['status'] == 'pengajuan']),
        'total_diproses': len([x for x in monitoring_data if x['status'] == 'diproses']),
        'total_all': len(monitoring_data),
        'total_checked': len([x for x in monitoring_data if x['has_checker']]),
        'use_marquee': len(monitoring_data) > 30
    }
    
    context = {
        'monitoring_data': monitoring_data,
        'stats': stats,
        'employee_data': employee_data,
        'page_title': 'MONITORING INFORMASI SYSTEM - Fullscreen Mode',
        'current_time': timezone.now(),
        'standalone_mode': True,
        'database_mode': True
    }
    
    return render(request, 'wo_maintenance_app/monitoring_informasi_system.html', context)


@login_required
def ajax_monitoring_refresh_database(request):
    """
    MAPPING FIX: Ajax refresh dengan consistent mapping
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    monitoring_data = []
    
    try:
        # Load checker data dengan mapping fix
        existing_checkers = load_checkers_from_database_mapping_fix()
        
        with connections['DB_Maintenance'].cursor() as cursor:
            today = timezone.now().date()
            
            # SAME QUERY as monitoring view
            try:
                cursor.execute("SELECT COUNT(*) FROM View_Monitor2 WHERE 1=0")
                use_view_monitor = True
            except:
                use_view_monitor = False
            
            if use_view_monitor:
                cursor.execute(f"""
                    SELECT 
                        a.history_id,
                        MAX(a.tgl_his) as tgl_his,
                        MAX(a.jam_his) as jam_his,
                        a.id_line,
                        a.id_mesin,
                        MAX(a.deskripsi_perbaikan) as deskripsi_perbaikan,
                        MAX(a.number_wo) as number_wo,
                        MAX(b.line) as line,
                        MAX(c.mesin) as mesin,
                        MAX(a.status_pekerjaan) as status_pekerjaan,
                        MAX(a.status) as status,
                        MAX(c.nomer) as nomer,
                        MAX(d.seksi) as seksi,
                        MAX(a.prima) as prima,
                        MAX(a.approve) as approve,
                        MAX(a.oleh) as oleh,
                               MAX(a.checker_name) as checker_name,   -- ✅ tambahkan
                        MAX(a.checker_time) as checker_time    -- ✅ tambahkan
                    FROM View_Monitor2 a 
                    JOIN tabel_line b ON b.id_line = a.id_line
                    JOIN tabel_mesin c ON c.id_mesin = a.id_mesin
                    JOIN tabel_msection d ON d.id_section = a.id_section
                    WHERE a.status_pekerjaan != 'C' 
                      AND a.history_id IS NOT NULL 
                      AND a.history_id != ''
                      AND convert(datetime,a.tgl_his,120) BETWEEN 
                          dateadd(day, -1, convert(datetime,'{today}' + ' 19:30:00.000',120)) AND 
                          dateadd(day, 1, convert(datetime,'{today}' + ' 06:59:59.000',120))
                    GROUP BY a.history_id, a.id_line, a.id_mesin
                    ORDER BY MAX(a.tgl_his) DESC
                """)
            else:
                cursor.execute(f"""
                    SELECT 
                        a.history_id,
                        MAX(a.tgl_his) as tgl_his,
                        MAX(a.jam_his) as jam_his,
                        a.id_line,
                        a.id_mesin,
                        MAX(a.deskripsi_perbaikan) as deskripsi_perbaikan,
                        MAX(a.number_wo) as number_wo,
                        MAX(b.line) as line,
                        MAX(c.mesin) as mesin,
                        MAX(a.status_pekerjaan) as status_pekerjaan,
                        MAX(a.status) as status,
                        MAX(c.nomer) as nomer,
                        MAX(d.seksi) as seksi,
                        MAX(a.prima) as prima,
                        MAX(a.approve) as approve,
                        MAX(a.oleh) as oleh,
                               MAX(a.checker_name) as checker_name,   -- ✅ tambahkan
                        MAX(a.checker_time) as checker_time    -- ✅ tambahkan
                    FROM (
                        SELECT 
                            tp.history_id, tp.tgl_his, tp.jam_his, tp.id_line, tp.id_mesin,
                            tp.deskripsi_perbaikan, tp.number_wo, tp.status_pekerjaan,
                            tp.status, tp.id_section, NULL as prima, tp.approve, tp.oleh
                        FROM tabel_pengajuan tp
                        WHERE tp.status_pekerjaan != 'C'
                          AND tp.history_id IS NOT NULL 
                          AND tp.history_id != ''
                        
                        UNION ALL
                        
                        SELECT 
                            tm.history_id, tm.tgl_his, tm.jam_his, tm.id_line, tm.id_mesin,
                            tm.deskripsi_perbaikan, tm.number_wo, tm.status_pekerjaan,
                            tm.status, tm.id_section, tm.PriMa as prima, NULL as approve, tm.oleh
                        FROM tabel_main tm
                        WHERE tm.status_pekerjaan != 'C'
                          AND tm.history_id IS NOT NULL 
                          AND tm.history_id != ''
                    ) a
                    LEFT JOIN tabel_line b ON b.id_line = a.id_line
                    LEFT JOIN tabel_mesin c ON c.id_mesin = a.id_mesin
                    LEFT JOIN tabel_msection d ON d.id_section = a.id_section
                    WHERE convert(datetime,a.tgl_his,120) BETWEEN 
                        dateadd(day, -1, convert(datetime,'{today}' + ' 19:30:00.000',120)) AND 
                        dateadd(day, 1, convert(datetime,'{today}' + ' 06:59:59.000',120))
                    GROUP BY a.history_id, a.id_line, a.id_mesin
                    ORDER BY MAX(a.tgl_his) DESC
                """)
            
            results = cursor.fetchall()
            
            # Process dengan clean history_id
            for row in results:
                history_id = row[0]  # history_id asli
                tgl_his = row[1]
                jam_his = row[2]
                id_line = row[3] 
                id_mesin = row[4]
                deskripsi_perbaikan = row[5]
                number_wo = row[6] if row[6] else ''
                line_name = row[7]
                mesin_name = row[8]
                status_pekerjaan = row[9] if row[9] else ''
                status = row[10] if row[10] else ''
                nomer = row[11]
                seksi = row[12]
                prima = row[13]
                approve = row[14] if len(row) > 14 else None
                oleh = row[15] if len(row) > 15 else ''
                checker_name = row[16] if len(row) > 16 else ''
                checker_time = row[17] if len(row) > 17 else None
                
                if status_pekerjaan == 'C':
                    continue
                
                # Status determination
                if (not number_wo or number_wo.strip() == '' or number_wo.startswith('TEMP-') or (status != 'A' and approve != 'Y')):
                    status_display = 'pengajuan'
                elif (status == 'A' and approve == 'Y' and status_pekerjaan == 'O'):
                    status_display = 'diproses'
                else:
                    status_display = 'diproses'
                
                # MAPPING FIX: Checker mapping dengan exact history_id
                checker_key = f"row-{history_id}"
                # has_checker = checker_key in existing_checkers
                checker_info = existing_checkers.get(checker_key, {})

                final_checker_name = checker_name or checker_info.get('user', '')
                final_checker_time = checker_time or checker_info.get('time', '')
                has_checker = bool(final_checker_name and str(final_checker_name).strip() != '')

                logger.debug(
                    f"Row {history_id} -> checker_name={checker_name}, "
                    f"checker_time={checker_time}, "
                    f"final_name={final_checker_name}, "
                    f"has_checker={has_checker}"
                )
                
                waktu_display = ''
                if tgl_his:
                    waktu_display = tgl_his.strftime('%d/%m/%Y') + ' - ' + tgl_his.strftime('%H:%M:%S') + ' WIB'

                
                mesin_display = f"{mesin_name or ''} {nomer or ''}".strip() or '-'
                
                # MAPPING FIX: Clean no_pengajuan = history_id asli
                monitoring_data.append({
                    'prioritas': prima or '-',
                    'waktu_pengajuan': waktu_display,
                    'no_pengajuan': history_id,  # MAPPING FIX: Clean history_id
                    'nomor_wo': number_wo or '-',
                    'line_name': line_name or '-',
                    'mesin_name': mesin_display,
                    'deskripsi': deskripsi_perbaikan or '-',
                    'section_name': seksi or '-',
                    'status': status_display,
                    'oleh': oleh or '-',
                    
                    # Database checker integration
                    'has_checker': has_checker,
                    'checker_name': final_checker_name,
                    'checker_time': (
                        final_checker_time.strftime('%Y-%m-%d %H:%M:%S') 
                        if isinstance(final_checker_time, datetime) else final_checker_time
                    ),
                    'checker_source_table': checker_info.get('source_table', 'View_Monitor2' if checker_name else ''),
                    'checker_status_type': checker_info.get('status_type', status_display)
                            })
        
        stats = {
            'total_pengajuan': len([x for x in monitoring_data if x['status'] == 'pengajuan']),
            'total_diproses': len([x for x in monitoring_data if x['status'] == 'diproses']),
            'total_all': len(monitoring_data),
            'total_checked': len([x for x in monitoring_data if x['has_checker']]),
            'last_update': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        # Debug logging
        checked_items = [item for item in monitoring_data if item['has_checker']]
        logger.info(f"MAPPING FIX Ajax: Found {len(checked_items)} items with checkers")
        
        return JsonResponse({
            'success': True,
            'data': monitoring_data,
            'stats': stats,
            'checker_data': existing_checkers,
            'standalone_mode': True,
            'sync_timestamp': timezone.now().timestamp()
        })
        
    except Exception as e:
        logger.error(f"MAPPING FIX Ajax: Error refreshing monitoring data: {e}")
        return JsonResponse({
            'success': True,
            'data': [],
            'stats': {
                'total_pengajuan': 0, 'total_diproses': 0,
                'total_all': 0, 'total_checked': 0,
                'last_update': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
            },
            'checker_data': {},
            'message': 'No data available',
            'standalone_mode': True
        })

logger = logging.getLogger(__name__)

    
# Export functions
__all__ = [
    'save_checker_to_database_api',
    'get_all_checkers_from_database_api', 
    'save_checker_to_pengajuan_table',
    'save_checker_to_main_table',
    'load_checkers_from_database',
    'transfer_checker_on_review_process',
    'monitoring_informasi_system_database'
]

@login_required
@require_http_methods(["POST"])
def save_checker_api(request):
    """
    API untuk save checker ke database - UPDATED: Langsung ke Database
    """
    try:
        data = json.loads(request.body)
        history_id = data.get('history_id', '').strip()
        checker_name = data.get('checker_name', '').strip()
        status_type = data.get('status_type', 'pengajuan').strip()  # 'pengajuan' atau 'diproses'
        device_id = data.get('device_id', None)
        
        logger.info(f"Save checker API called - History: {history_id}, Name: {checker_name}, Type: {status_type}")
        
        # Validasi input
        if not all([history_id, checker_name]):
            return JsonResponse({
                'success': False,
                'error': 'History ID dan nama checker wajib diisi bro!'
            })
        
        # Validasi nama
        if checker_name.lower() in ['test', 'testing', '']:
            return JsonResponse({
                'success': False,
                'error': 'Jangan pake nama testing dong, pake nama asli!'
            })
        
        # Validasi status type
        if status_type not in ['pengajuan', 'diproses']:
            return JsonResponse({
                'success': False,
                'error': 'Status type harus pengajuan atau diproses!'
            })
        
        # Check apakah sudah ada checker untuk history_id ini
        with connections['DB_Maintenance'].cursor() as cursor:
            if status_type == 'pengajuan':
                cursor.execute("""
                    SELECT checker_name, checker_status 
                    FROM tabel_pengajuan 
                    WHERE history_id = %s
                """, [history_id])
            else:  # diproses
                short_history_id = history_id[:11] if len(history_id) > 11 else history_id
                cursor.execute("""
                    SELECT checker_name, checker_status 
                    FROM tabel_main 
                    WHERE history_id = %s
                """, [short_history_id])
            
            existing_data = cursor.fetchone()
            
            if existing_data and existing_data[1] == '1' and existing_data[0]:
                return JsonResponse({
                    'success': False,
                    'error': f'Item ini udah dicek sama: {existing_data[0]}'
                })
        
        # Save ke database
        result = save_checker_to_database(
            history_id=history_id,
            checker_name=checker_name,
            device_id=device_id,
            status_type=status_type
        )
        
        if result['success']:
            logger.info(f"Checker saved successfully: {history_id} by {checker_name}")
            return JsonResponse({
                'success': True,
                'message': f'Checker berhasil disimpan: {checker_name}',
                'history_id': history_id,
                'checker_name': checker_name,
                'status_type': status_type,
                'rows_affected': result.get('rows_affected', 0)
            })
        else:
            logger.error(f"Failed to save checker: {result['message']}")
            return JsonResponse({
                'success': False,
                'error': result['message']
            })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Format data tidak valid bro!'
        })
    except Exception as e:
        logger.error(f"Error in save_checker_api: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Terjadi kesalahan server: {str(e)}'
        })


@login_required
@require_http_methods(["GET"])
def get_checker_data_api(request):
    """
    API untuk ambil data checker dari database
    """
    try:
        # Load checker data dari database
        checker_data = get_checker_data_from_database()
        
        logger.info(f"Loaded {len(checker_data)} checker records from database")
        
        return JsonResponse({
            'success': True,
            'checker_data': checker_data,
            'total_checkers': len(checker_data),
            'last_update': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
            'source': 'database'
        })
        
    except Exception as e:
        logger.error(f"Error in get_checker_data_api: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Gagal mengambil data checker: {str(e)}',
            'checker_data': {}
        })


def load_checkers_from_database_fixed():
    """
    Load checker data dengan exact history_id mapping
    """
    checker_data = {}
    
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Get checker data dari tabel_pengajuan
            cursor.execute("""
                SELECT 
                    history_id, 
                    checker_name, 
                    checker_time, 
                    checker_device_id, 
                    checker_status,
                    checker_notes
                FROM tabel_pengajuan 
                WHERE checker_status = '1' 
                  AND checker_name IS NOT NULL 
                  AND checker_name != ''
                  AND history_id IS NOT NULL
                  AND history_id != ''
            """)
            
            pengajuan_rows = cursor.fetchall()
            logger.info(f"Found {len(pengajuan_rows)} checked items in tabel_pengajuan")
            
            for row in pengajuan_rows:
                history_id, checker_name, checker_time, device_id, status, notes = row
                if history_id:
                    checker_data[f"row-{history_id}"] = {
                        'user': checker_name,
                        'time': checker_time.isoformat() if checker_time else None,
                        'device_id': device_id,
                        'status': status,
                        'notes': notes,
                        'status_type': 'pengajuan',
                        'source_table': 'tabel_pengajuan',
                        'last_updated': checker_time.isoformat() if checker_time else None
                    }
            
            # Get checker data dari tabel_main
            cursor.execute("""
                SELECT 
                    history_id, 
                    checker_name, 
                    checker_time, 
                    checker_device_id, 
                    checker_status,
                    checker_transferred_from,
                    checker_notes
                FROM tabel_main 
                WHERE checker_status = '1' 
                  AND checker_name IS NOT NULL 
                  AND checker_name != ''
                  AND history_id IS NOT NULL
                  AND history_id != ''
            """)
            
            main_rows = cursor.fetchall()
            logger.info(f"Found {len(main_rows)} checked items in tabel_main")
            
            for row in main_rows:
                history_id, checker_name, checker_time, device_id, status, transferred_from, notes = row
                if history_id:
                    # Use transferred_from for mapping if available
                    mapping_id = transferred_from if transferred_from else history_id
                    
                    checker_data[f"row-{mapping_id}"] = {
                        'user': checker_name,
                        'time': checker_time.isoformat() if checker_time else None,
                        'device_id': device_id,
                        'status': status,
                        'notes': notes,
                        'status_type': 'diproses',
                        'source_table': 'tabel_main',
                        'short_history_id': history_id,
                        'transferred_from': transferred_from,
                        'last_updated': checker_time.isoformat() if checker_time else None
                    }
            
            logger.info(f"Total checker data loaded: {len(checker_data)}")
            return checker_data
            
    except Exception as e:
        logger.error(f"Error loading checkers from database: {e}")
        return {}

# AJAX refresh dengan database integration
@login_required
def ajax_monitoring_refresh(request):
    """
    AJAX endpoint untuk refresh monitoring dengan original query structure
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    monitoring_data = []
    
    try:
        # Load checker data dari database
        existing_checkers = load_checkers_from_database_fixed()
        
        with connections['DB_Maintenance'].cursor() as cursor:
            today = timezone.now().date()
            
            # SAME ORIGINAL QUERY as monitoring_informasi_system
            cursor.execute(f"""
                SELECT 
                    a.history_id,
                    MAX(a.tgl_his) as tgl_his,
                    a.id_line,
                    a.id_mesin,
                    MAX(a.deskripsi_perbaikan) as deskripsi_perbaikan,
                    MAX(a.number_wo) as number_wo,
                    MAX(b.line) as line,
                    MAX(c.mesin) as mesin,
                    MAX(a.status_pekerjaan) as status_pekerjaan,
                    MAX(a.status) as status,
                    MAX(c.nomer) as nomer,
                    MAX(d.seksi) as seksi,
                    MAX(a.prima) as prima,
                    MAX(a.approve) as approve,
                    MAX(a.oleh) as oleh
                FROM (
                    SELECT 
                        tp.history_id, tp.tgl_his, tp.id_line, tp.id_mesin,
                        tp.deskripsi_perbaikan, tp.number_wo, tp.status_pekerjaan,
                        tp.status, tp.id_section, NULL as prima, tp.approve, tp.oleh
                    FROM tabel_pengajuan tp
                    WHERE tp.status_pekerjaan != 'C' 
                      AND tp.history_id IS NOT NULL 
                      AND tp.history_id != ''
                    
                    UNION ALL
                    
                    SELECT 
                        tm.history_id, tm.tgl_his, tm.id_line, tm.id_mesin,
                        tm.deskripsi_perbaikan, tm.number_wo, tm.status_pekerjaan,
                        tm.status, tm.id_section, tm.PriMa as prima, NULL as approve, tm.oleh
                    FROM tabel_main tm
                    WHERE tm.status_pekerjaan != 'C' 
                      AND tm.history_id IS NOT NULL 
                      AND tm.history_id != ''
                ) a
                LEFT JOIN tabel_line b ON b.id_line = a.id_line
                LEFT JOIN tabel_mesin c ON c.id_mesin = a.id_mesin
                LEFT JOIN tabel_msection d ON d.id_section = a.id_section
                WHERE convert(datetime,a.tgl_his,120) BETWEEN 
                    dateadd(day, -1, convert(datetime,'{today}' + ' 19:30:00.000',120)) AND 
                    dateadd(day, 1, convert(datetime,'{today}' + ' 06:59:59.000',120))
                GROUP BY a.history_id, a.id_line, a.id_mesin
                ORDER BY MAX(a.tgl_his) DESC
            """)
            
            results = cursor.fetchall()
            logger.info(f"Ajax refresh found {len(results)} monitoring records")
            
            # Process data dengan logic yang sama
            for row in results:
                history_id, tgl_his, id_line, id_mesin, deskripsi, number_wo, line_name, mesin_name, status_pekerjaan, status, nomer, seksi, prima, approve, oleh = row
                
                if status_pekerjaan == 'C':
                    continue
                
                # Status determination - sama dengan original
                if (not number_wo or number_wo.strip() == '' or (status != 'A' and approve != 'Y')):
                    status_display = 'pengajuan'
                else:
                    status_display = 'diproses'
                
                # Checker mapping
                checker_key = f"row-{history_id}"
                has_checker = checker_key in existing_checkers
                checker_info = existing_checkers.get(checker_key, {})
                
                waktu_display = tgl_his.strftime('%d/%m/%Y - %H:%M:%S WIB') if tgl_his else '-'
                mesin_display = f"{mesin_name or ''} {nomer or ''}".strip() or '-'
                
                # Truncate long descriptions
                deskripsi_display = deskripsi or '-'
                if len(deskripsi_display) > 50:
                    deskripsi_display = deskripsi_display[:50] + '...'
                
                monitoring_data.append({
                    'prioritas': prima or '-',
                    'waktu_pengajuan': waktu_display,
                    'no_pengajuan': history_id,
                    'nomor_wo': number_wo or '-',
                    'line_name': line_name or '-',
                    'mesin_name': mesin_display,
                    'deskripsi': deskripsi_display,
                    'section_name': seksi or '-',
                    'status': status_display,
                    'oleh': oleh or '-',
                    
                    # Database checker integration
                    'has_checker': has_checker,
                    'checker_name': checker_info.get('user', ''),
                    'checker_time': checker_info.get('time', ''),
                    'checker_source_table': checker_info.get('source_table', ''),
                    'checker_status_type': checker_info.get('status_type', status_display)
                })
        
        stats = {
            'total_pengajuan': len([x for x in monitoring_data if x['status'] == 'pengajuan']),
            'total_diproses': len([x for x in monitoring_data if x['status'] == 'diproses']),
            'total_all': len(monitoring_data),
            'total_checked': len([x for x in monitoring_data if x['has_checker']]),
            'last_update': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        return JsonResponse({
            'success': True,
            'data': monitoring_data,
            'stats': stats,
            'checker_data': existing_checkers,
            'standalone_mode': True,
            'sync_timestamp': timezone.now().timestamp()
        })
        
    except Exception as e:
        logger.error(f"Error refreshing monitoring data: {e}")
        return JsonResponse({
            'success': True,
            'data': [],
            'stats': {
                'total_pengajuan': 0, 'total_diproses': 0,
                'total_all': 0, 'total_checked': 0,
                'last_update': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
            },
            'checker_data': {},
            'message': 'No data available',
            'standalone_mode': True
        })

@login_required
def keep_session_alive(request):
    """
    Endpoint untuk menjaga session tetap aktif
    """
    return JsonResponse({
        'success': True,
        'message': 'Session refreshed',
        'time': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
    })


# Export functions
__all__ = [
    'monitoring_informasi_system',
    'ajax_monitoring_refresh',
    'keep_session_alive',
    'save_checker_api',
    'get_checker_data_api'
]

# ============== SESSION-BASED CHECKER MANAGEMENT FUNCTIONS ==============

@login_required
@require_http_methods(["POST"])
def session_save_checker(request):
    """
    API untuk save checker data ke session - Tanpa Database Model
    """
    try:
        data = json.loads(request.body)
        row_id = data.get('row_id', '').strip()
        checker_name = data.get('checker_name', '').strip()
        
        # Validasi input
        if not all([row_id, checker_name]):
            return JsonResponse({
                'success': False,
                'error': 'Data tidak lengkap'
            })
        
        # Validasi nama
        if checker_name.lower() in ['test', 'testing', '']:
            return JsonResponse({
                'success': False,
                'error': 'Jangan pake nama testing, pake nama asli!'
            })
        
        # Initialize session checker data jika belum ada
        if 'checker_data' not in request.session:
            request.session['checker_data'] = {}
        
        # Cek apakah sudah ada data
        if row_id in request.session['checker_data']:
            existing_checker = request.session['checker_data'][row_id]
            return JsonResponse({
                'success': False,
                'error': f'Item ini udah dicek sama: {existing_checker["user"]}'
            })
        
        # Simpan data checker ke session
        request.session['checker_data'][row_id] = {
            'user': checker_name,
            'time': timezone.now().isoformat(),
            'input_source': 'manual_user_input',
            'last_updated': timezone.now().isoformat(),
            'browser_info': request.META.get('HTTP_USER_AGENT', '')[:200],
            'additional_data': data.get('additional_data', {})
        }
        
        request.session.modified = True
        
        logger.info(f"Session checker saved: {row_id} - {checker_name}")
        
        return JsonResponse({
            'success': True,
            'message': f'Data checker berhasil disimpan: {checker_name}',
            'row_id': row_id,
            'checker_name': checker_name
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Format data tidak valid'
        })
    except Exception as e:
        logger.error(f"Error save session checker: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Terjadi kesalahan server'
        })


@login_required
@require_http_methods(["GET"])
def session_get_checkers(request):
    """
    API untuk get semua checker data dari session
    """
    try:
        checker_data = request.session.get('checker_data', {})
        
        # Clean up old data (lebih dari 24 jam)
        current_time = timezone.now()
        cleaned_data = {}
        
        for row_id, data in checker_data.items():
            try:
                data_time = datetime.fromisoformat(data.get('time', ''))
                if (current_time - data_time.replace(tzinfo=timezone.get_current_timezone())).total_seconds() < 86400:  # 24 hours
                    cleaned_data[row_id] = data
            except (ValueError, TypeError):
                # Skip invalid time data
                continue
        
        # Update session jika ada perubahan
        if len(cleaned_data) != len(checker_data):
            request.session['checker_data'] = cleaned_data
            request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'checker_data': cleaned_data,
            'total_checkers': len(cleaned_data),
            'last_update': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
        })
        
    except Exception as e:
        logger.error(f"Error get session checkers: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Gagal mengambil data',
            'checker_data': {}
        })


@login_required
@require_http_methods(["POST"])
def session_clear_checker(request):
    """
    API untuk clear specific checker data dari session
    """
    try:
        data = json.loads(request.body)
        row_id = data.get('row_id', '').strip()
        
        if not row_id:
            return JsonResponse({
                'success': False,
                'error': 'Row ID diperlukan'
            })
        
        checker_data = request.session.get('checker_data', {})
        
        if row_id in checker_data:
            removed_checker = checker_data.pop(row_id)
            request.session['checker_data'] = checker_data
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': f'Checker data dihapus: {removed_checker.get("user", "Unknown")}',
                'removed_row_id': row_id
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Data checker tidak ditemukan'
            })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Format data tidak valid'
        })
    except Exception as e:
        logger.error(f"Error clear session checker: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Terjadi kesalahan server'
        })


# Export functions
__all__ = [
    'monitoring_informasi_system',
    'ajax_monitoring_refresh',
    'keep_session_alive',
    'session_save_checker',
    'session_get_checkers', 
    'session_clear_checker'
]

# =============== DATABASE CHECKER API FUNCTIONS ===============

@login_required
@require_http_methods(["POST"])
def save_checker_to_database_api(request):
    """
    FINAL FIX: API untuk save checker dengan improved error handling
    """
    try:
        data = json.loads(request.body)
        history_id = data.get('history_id', '').strip()
        checker_name = data.get('checker_name', '').strip()
        status_type = data.get('status_type', 'pengajuan').strip()
        device_id = data.get('device_id', request.META.get('HTTP_USER_AGENT', '')[:50])
        checker_notes = data.get('checker_notes', '')
        
        logger.info(f"FINAL FIX: Save checker API - ID: '{history_id}', Name: '{checker_name}', Type: '{status_type}'")
        
        # Validasi input
        if not all([history_id, checker_name]):
            return JsonResponse({
                'success': False,
                'error': 'History ID dan nama checker wajib diisi!'
            })
        
        if checker_name.lower() in ['test', 'testing', '']:
            return JsonResponse({
                'success': False,
                'error': 'Jangan pake nama testing, pake nama asli!'
            })
        
        if status_type not in ['pengajuan', 'diproses']:
            return JsonResponse({
                'success': False,
                'error': 'Status type harus "pengajuan" atau "diproses"!'
            })
        
        # Save based on status type with final fix
        if status_type == 'pengajuan':
            result = save_checker_to_pengajuan_table_final_fix(history_id, checker_name, device_id, checker_notes)
        else:
            result = save_checker_to_main_table_fixed(history_id, checker_name, device_id, checker_notes)
        
        if result['success']:
            logger.info(f"FINAL FIX: Checker saved: {history_id} by {checker_name} to {result['table']}")
            return JsonResponse({
                'success': True,
                'message': result['message'],
                'history_id': history_id,
                'checker_name': checker_name,
                'status_type': status_type,
                'table_saved': result['table'],
                'rows_affected': result.get('rows_affected', 0)
            })
        else:
            logger.error(f"FINAL FIX: Failed to save checker: {result['message']}")
            return JsonResponse({
                'success': False,
                'error': result['message']
            })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Format data tidak valid!'
        })
    except Exception as e:
        logger.error(f"FINAL FIX: Error in save_checker_to_database_api: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Terjadi kesalahan server: {str(e)}'
        })

# FINAL FIX: Improved checker save function dengan better parsing
def save_checker_to_pengajuan_table_final_fix(history_id, checker_name, device_id=None, checker_notes=None):
    """
    FINAL FIX: Save checker ke tabel_pengajuan dengan improved history_id parsing
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            logger.info(f"FINAL FIX: Saving checker for history_id: '{history_id}'")
            
            # STEP 1: Parse history_id dengan prioritas yang benar
            search_ids = []
            
            if ' -- ' in history_id:
                # Format "20864 -- 25-08-0435" -> ambil bagian kedua "25-08-0435"
                parts = history_id.split(' -- ')
                if len(parts) == 2:
                    search_ids.append(parts[1].strip())  # "25-08-0435" 
                    search_ids.append(parts[0].strip())  # "20864" sebagai fallback
                search_ids.append(history_id)  # Original sebagai fallback
            else:
                search_ids.append(history_id)  # Direct search
            
            logger.info(f"FINAL FIX: Search IDs to try: {search_ids}")
            
            # STEP 2: Coba setiap search ID sampai ketemu
            result = None
            found_history_id = None
            
            for search_id in search_ids:
                logger.info(f"FINAL FIX: Trying search with: '{search_id}'")
                
                cursor.execute("""
                    SELECT history_id, status, approve, checker_name, checker_status,
                           tgl_his, oleh, deskripsi_perbaikan
                    FROM tabel_pengajuan 
                    WHERE history_id = %s
                """, [search_id])
                
                result = cursor.fetchone()
                if result:
                    found_history_id = search_id
                    logger.info(f"FINAL FIX: Found match with: '{found_history_id}'")
                    break
            
            if not result:
                # STEP 3: Show debug info
                cursor.execute("""
                    SELECT TOP 10 history_id, tgl_his, oleh 
                    FROM tabel_pengajuan 
                    WHERE tgl_his >= DATEADD(day, -2, GETDATE())
                    ORDER BY tgl_his DESC
                """)
                
                recent_data = cursor.fetchall()
                available_ids = [row[0] for row in recent_data if row[0]]
                
                logger.error(f"FINAL FIX: No match found for any of: {search_ids}")
                logger.error(f"FINAL FIX: Available recent IDs: {available_ids}")
                
                return {
                    'success': False,
                    'message': f'Pengajuan dengan history_id "{history_id}" tidak ditemukan. Available: {available_ids[:3]}',
                    'table': 'tabel_pengajuan'
                }
            
            # STEP 4: Process found data
            history_id_found, status, approve, existing_checker, checker_status, tgl_his, oleh, deskripsi = result
            logger.info(f"FINAL FIX: Processing pengajuan: {history_id_found}")
            
            # Cek apakah sudah ada checker
            if checker_status == '1' and existing_checker and existing_checker.strip():
                return {
                    'success': False,
                    'message': f'Item ini sudah dicek oleh: {existing_checker}',
                    'table': 'tabel_pengajuan'
                }
            
            # STEP 5: Save checker - ALLOW ALL STATUS PENGAJUAN
            cursor.execute("""
                UPDATE tabel_pengajuan 
                SET checker_name = %s, 
                    checker_time = GETDATE(),
                    checker_device_id = %s,
                    checker_status = '1',
                    checker_notes = %s
                WHERE history_id = %s
            """, [checker_name.strip(), device_id, checker_notes, history_id_found])
            
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                logger.info(f"FINAL FIX: Checker saved successfully: {history_id_found} by {checker_name}")
                return {
                    'success': True,
                    'message': f'Berhasil dicek oleh: {checker_name}',
                    'table': 'tabel_pengajuan',
                    'rows_affected': rows_affected,
                    'actual_history_id': history_id_found
                }
            else:
                return {
                    'success': False,
                    'message': 'Gagal menyimpan data checker ke tabel_pengajuan',
                    'table': 'tabel_pengajuan'
                }
                
    except Exception as e:
        logger.error(f"FINAL FIX: Error save_checker_to_pengajuan_table: {e}")
        return {
            'success': False,
            'message': f'Error database: {str(e)}',
            'table': 'tabel_pengajuan'
        }

    
def save_checker_to_main_table_fixed(history_id, checker_name, device_id=None, checker_notes=None):
    """
    Save checker ke tabel_main (keep existing - sudah benar)
    """
    try:
        truncated_history_id = history_id[:11]
        
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT history_id, status_pekerjaan, checker_name, checker_status
                FROM tabel_main 
                WHERE history_id = %s
            """, [truncated_history_id])
            
            result = cursor.fetchone()
            if not result:
                return {
                    'success': False,
                    'message': f'Data history {history_id} tidak ditemukan di tabel_main',
                    'table': 'tabel_main'
                }
            
            found_history_id, status_pekerjaan, existing_checker, checker_status = result
            
            if checker_status == '1' and existing_checker and existing_checker.strip():
                return {
                    'success': False,
                    'message': f'Item ini sudah dicek oleh: {existing_checker}',
                    'table': 'tabel_main'
                }
            
            if status_pekerjaan == 'C':
                return {
                    'success': False,
                    'message': 'Pekerjaan sudah selesai, tidak bisa dicek lagi',
                    'table': 'tabel_main'
                }
            
            cursor.execute("""
                UPDATE tabel_main 
                SET checker_name = %s, 
                    checker_time = GETDATE(),
                    checker_device_id = %s,
                    checker_status = '1',
                    checker_notes = %s
                WHERE history_id = %s
            """, [checker_name.strip(), device_id, checker_notes, truncated_history_id])
            
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                return {
                    'success': True,
                    'message': f'Berhasil dicek oleh: {checker_name}',
                    'table': 'tabel_main',
                    'rows_affected': rows_affected
                }
            else:
                return {
                    'success': False,
                    'message': 'Gagal menyimpan data checker ke tabel_main',
                    'table': 'tabel_main'
                }
                
    except Exception as e:
        logger.error(f"Error save_checker_to_main_table: {e}")
        return {
            'success': False,
            'message': f'Error database: {str(e)}',
            'table': 'tabel_main'
        }
    
@login_required
@require_http_methods(["GET"])
def get_all_checkers_from_database_api(request):
    """
    API untuk get semua data checker dari database
    """
    try:
        checker_data = load_checkers_from_database_fixed()
        
        return JsonResponse({
            'success': True,
            'checker_data': checker_data,
            'total_checkers': len(checker_data),
            'last_update': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
            'source': 'database_direct'
        })
        
    except Exception as e:
        logger.error(f"Error in get_all_checkers_from_database_api: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Gagal mengambil data checker: {str(e)}',
            'checker_data': {}
        })


def transfer_checker_on_review_process(original_history_id, reviewed_by):
    """
    Transfer checker data dari tabel_pengajuan ke tabel_main saat review process
    Dipanggil otomatis saat SITI FATIMAH review pengajuan dari pengajuan ke diproses
    
    Args:
        original_history_id: History ID di tabel_pengajuan 
        reviewed_by: Employee number reviewer (007522)
    
    Returns:
        dict: Result dengan transfer info
    """
    logger.info(f"Starting checker transfer: {original_history_id} reviewed by {reviewed_by}")
    
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Get checker data dari tabel_pengajuan
            cursor.execute("""
                SELECT checker_name, checker_time, checker_device_id, checker_notes
                FROM tabel_pengajuan 
                WHERE history_id = %s 
                  AND checker_status = '1'
                  AND checker_name IS NOT NULL
            """, [original_history_id])
            
            checker_data = cursor.fetchone()
            
            if not checker_data:
                logger.info(f"No checker data found for {original_history_id} in tabel_pengajuan")
                return {
                    'success': True, 
                    'message': 'Tidak ada checker data untuk di-transfer',
                    'transferred': False
                }
            
            checker_name, checker_time, device_id, notes = checker_data
            logger.info(f"Found checker data: {checker_name} at {checker_time}")
            
            # Target history_id untuk tabel_main (max 11 chars)
            target_history_id = original_history_id[:11]
            
            # Update tabel_main dengan checker data yang di-transfer
            cursor.execute("""
                UPDATE tabel_main 
                SET checker_name = %s,
                    checker_time = %s,
                    checker_device_id = %s,
                    checker_status = '1',
                    checker_transferred_from = %s,
                    checker_notes = %s
                WHERE history_id = %s
            """, [checker_name, checker_time, device_id, original_history_id, notes, target_history_id])
            
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                logger.info(f"✅ Checker transferred: {original_history_id} -> {target_history_id} ({checker_name})")
                return {
                    'success': True,
                    'message': f'Checker {checker_name} berhasil di-transfer ke tabel_main',
                    'transferred': True,
                    'checker_name': checker_name,
                    'target_history_id': target_history_id,
                    'rows_affected': rows_affected
                }
            else:
                logger.warning(f"❌ Failed to transfer checker to {target_history_id}")
                return {
                    'success': False,
                    'message': f'Gagal transfer checker ke tabel_main (history_id: {target_history_id})',
                    'transferred': False
                }
                
    except Exception as e:
        logger.error(f"Error transferring checker data: {e}")
        return {
            'success': False,
            'message': f'Error transfer: {str(e)}',
            'transferred': False
        }
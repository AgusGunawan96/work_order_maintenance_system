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
import json
import logging
from functools import wraps
from django.http import JsonResponse


from wo_maintenance_app.forms import PengajuanMaintenanceForm, PengajuanFilterForm, ApprovalForm
from wo_maintenance_app.utils import (
    get_employee_hierarchy_data, 
    can_user_approve, 
    get_subordinate_employee_numbers,
    get_employee_by_number,
    assign_pengajuan_to_section_supervisors,
    get_assigned_pengajuan_for_user,
    get_target_section_supervisors
)

# Setup logging
logger = logging.getLogger(__name__)

# ===== REVIEW SYSTEM CONSTANTS =====
REVIEWER_EMPLOYEE_NUMBER = '007522'  # SITI FATIMAH
REVIEWER_FULLNAME = 'SITI FATIMAH'

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
@reviewer_required
def review_dashboard(request):
    """
    Dashboard review untuk SITI FATIMAH - UPDATED dengan SDBM integration
    """
    try:
        # Ambil employee data dari session atau SDBM
        employee_data = get_employee_data_for_request(request)
        
        if not employee_data:
            messages.error(request, 'Data employee tidak ditemukan. Silakan login ulang.')
            return redirect('login')
        
        # Filter untuk review
        filter_form = ReviewFilterForm(request.GET or None)
        search_query = request.GET.get('search', '').strip()
        
        # Statistik review
        with connections['DB_Maintenance'].cursor() as cursor:
            # Total pengajuan pending review
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_pengajuan 
                WHERE status = '1' AND approve = '1' 
                    AND (review_status IS NULL OR review_status = '0')
            """)
            pending_review_count = cursor.fetchone()[0] or 0
            
            # Total sudah direview hari ini
            today = timezone.now().date()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_pengajuan 
                WHERE reviewed_by = %s 
                    AND CAST(review_date AS DATE) = %s
            """, [REVIEWER_EMPLOYEE_NUMBER, today])
            reviewed_today_count = cursor.fetchone()[0] or 0
            
            # Total sudah direview minggu ini
            week_start = today - timedelta(days=today.weekday())
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_pengajuan 
                WHERE reviewed_by = %s 
                    AND CAST(review_date AS DATE) BETWEEN %s AND %s
            """, [REVIEWER_EMPLOYEE_NUMBER, week_start, today])
            reviewed_week_count = cursor.fetchone()[0] or 0
            
            # Review by status
            cursor.execute("""
                SELECT review_status, COUNT(*) 
                FROM tabel_pengajuan 
                WHERE reviewed_by = %s
                GROUP BY review_status
            """, [REVIEWER_EMPLOYEE_NUMBER])
            review_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        context = {
            'pending_review_count': pending_review_count,
            'reviewed_today_count': reviewed_today_count,
            'reviewed_week_count': reviewed_week_count,
            'review_stats': review_stats,
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
@reviewer_required
def review_pengajuan_list(request):
    """
    Halaman daftar pengajuan yang perlu direview oleh SITI FATIMAH
    UPDATED: dengan SDBM integration dan auto-initialize
    """
    try:
        # Ambil employee data
        employee_data = get_employee_data_for_request(request)
        
        # Auto-initialize review data jika perlu
        initialize_review_data()
        
        # Filter dan search
        filter_form = ReviewFilterForm(request.GET or None)
        search_query = request.GET.get('search', '').strip()
        
        # Query pengajuan yang perlu direview
        pengajuan_list = []
        total_records = 0
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Base WHERE conditions
            where_conditions = [
                "tp.status = '1'",  # Approved
                "tp.approve = '1'", # Approved  
                "(tp.review_status IS NULL OR tp.review_status = '0')"  # Pending review
            ]
            query_params = []
            
            # Apply filters
            if filter_form.is_valid():
                # Filter tanggal
                tanggal_dari = filter_form.cleaned_data.get('tanggal_dari')
                tanggal_sampai = filter_form.cleaned_data.get('tanggal_sampai')
                
                if tanggal_dari:
                    where_conditions.append("CAST(tp.tgl_insert AS DATE) >= %s")
                    query_params.append(tanggal_dari)
                
                if tanggal_sampai:
                    where_conditions.append("CAST(tp.tgl_insert AS DATE) <= %s")
                    query_params.append(tanggal_sampai)
                
                # Filter section
                section_filter = filter_form.cleaned_data.get('section_filter')
                if section_filter:
                    where_conditions.append("tp.id_section = %s")
                    query_params.append(float(section_filter))
            
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
                LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
                LEFT JOIN tabel_msection tms ON tp.id_section = tms.id_section
                LEFT JOIN tabel_pekerjaan tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
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
                    tp.review_date,          -- 14
                    tp.final_section_id      -- 15
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
            
            logger.info(f"Found {total_records} pengajuan for review by {employee_data.get('fullname', REVIEWER_FULLNAME)}")
        
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
            'reviewer_name': employee_data.get('fullname', REVIEWER_FULLNAME),
            'employee_data': employee_data,
            'page_title': 'Daftar Pengajuan untuk Review'
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
    Auto-initialize pengajuan approved untuk review
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
            
            # Initialize approved pengajuan untuk review
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
        logger.error(f"Error initializing review data: {e}")
        return False

@login_required
@reviewer_required
def review_pengajuan_detail(request, nomor_pengajuan):
    """
    Detail pengajuan untuk review oleh SITI FATIMAH
    """
    try:
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
                    final_section.seksi as final_section_name
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
                'final_section_name': row[19]
            }
        
        # Cek apakah pengajuan sudah di-approve dan belum direview
        if pengajuan['status'] != '1' or pengajuan['approve'] != '1':
            messages.warning(request, 'Pengajuan ini belum di-approve oleh atasan.')
            return redirect('wo_maintenance_app:review_pengajuan_list')
        
        # Cek apakah sudah direview
        already_reviewed = pengajuan['review_status'] in ['1', '2']
        
        # Handle review form submission
        if request.method == 'POST' and not already_reviewed:
            review_form = ReviewForm(request.POST)
            
            if review_form.is_valid():
                action = review_form.cleaned_data['action']
                final_section = review_form.cleaned_data['final_section']
                review_notes = review_form.cleaned_data['review_notes']
                
                try:
                    with connections['DB_Maintenance'].cursor() as cursor:
                        if action == 'approve':
                            # Update pengajuan dengan review approval
                            cursor.execute("""
                                UPDATE tabel_pengajuan
                                SET review_status = '1',
                                    reviewed_by = %s,
                                    review_date = GETDATE(),
                                    review_notes = %s,
                                    final_section_id = %s
                                WHERE history_id = %s
                            """, [REVIEWER_EMPLOYEE_NUMBER, review_notes, float(final_section), nomor_pengajuan])
                            
                            # Log review action
                            try:
                                cursor.execute("""
                                    INSERT INTO tabel_review_log 
                                    (history_id, reviewer_employee, action, final_section_id, review_notes, review_date)
                                    VALUES (%s, %s, %s, %s, %s, GETDATE())
                                """, [nomor_pengajuan, REVIEWER_EMPLOYEE_NUMBER, 'approve', float(final_section), review_notes])
                            except Exception as log_error:
                                logger.warning(f"Failed to log review action: {log_error}")
                            
                            # Auto-assign ke supervisors di final section
                            try:
                                from .utils import assign_pengajuan_to_section_supervisors
                                assigned_employees = assign_pengajuan_to_section_supervisors(
                                    nomor_pengajuan, 
                                    int(final_section), 
                                    REVIEWER_EMPLOYEE_NUMBER
                                )
                                
                                if assigned_employees:
                                    messages.info(request, f'Pengajuan telah di-assign ke {len(assigned_employees)} supervisor di section tujuan.')
                            except Exception as assign_error:
                                logger.error(f"Failed to auto-assign after review: {assign_error}")
                            
                            messages.success(request, f'Pengajuan {nomor_pengajuan} berhasil di-approve dan didistribusikan ke section tujuan.')
                            
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
                            
                            # Log review action
                            try:
                                cursor.execute("""
                                    INSERT INTO tabel_review_log 
                                    (history_id, reviewer_employee, action, review_notes, review_date)
                                    VALUES (%s, %s, %s, %s, GETDATE())
                                """, [nomor_pengajuan, REVIEWER_EMPLOYEE_NUMBER, 'reject', review_notes])
                            except Exception as log_error:
                                logger.warning(f"Failed to log review action: {log_error}")
                            
                            messages.success(request, f'Pengajuan {nomor_pengajuan} berhasil ditolak.')
                    
                    logger.info(f"Review {action} for {nomor_pengajuan} by {REVIEWER_FULLNAME}")
                    return redirect('wo_maintenance_app:review_pengajuan_detail', nomor_pengajuan=nomor_pengajuan)
                    
                except Exception as update_error:
                    logger.error(f"Error processing review for {nomor_pengajuan}: {update_error}")
                    messages.error(request, 'Terjadi kesalahan saat memproses review.')
        else:
            review_form = ReviewForm()
        
        context = {
            'pengajuan': pengajuan,
            'review_form': review_form,
            'already_reviewed': already_reviewed,
            'reviewer_name': REVIEWER_FULLNAME,
            'page_title': f'Review Pengajuan {nomor_pengajuan}'
        }
        
        return render(request, 'wo_maintenance_app/review_pengajuan_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error in review pengajuan detail: {e}")
        messages.error(request, 'Terjadi kesalahan saat memuat detail pengajuan.')
        return redirect('wo_maintenance_app:review_pengajuan_list')


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
    
    # Ambil data employee dari session (dari SDBM authentication)
    employee_data = request.session.get('employee_data', {})
    
    try:
        # Statistik pengajuan dari database DB_Maintenance
        with connections['DB_Maintenance'].cursor() as cursor:
            # Total pengajuan
            cursor.execute("SELECT COUNT(*) FROM tabel_pengajuan WHERE history_id IS NOT NULL")
            total_pengajuan = cursor.fetchone()[0] or 0
            
            # Pengajuan berdasarkan status
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM tabel_pengajuan 
                WHERE history_id IS NOT NULL
                GROUP BY status
            """)
            status_data = cursor.fetchall()
            
            # Pengajuan hari ini
            today = timezone.now().date()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_pengajuan 
                WHERE CAST(tgl_insert AS DATE) = %s
                    AND history_id IS NOT NULL
            """, [today])
            pengajuan_today = cursor.fetchone()[0] or 0
            
            # Pengajuan minggu ini
            week_start = today - timedelta(days=today.weekday())
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_pengajuan 
                WHERE CAST(tgl_insert AS DATE) BETWEEN %s AND %s
                    AND history_id IS NOT NULL
            """, [week_start, today])
            pengajuan_this_week = cursor.fetchone()[0] or 0
            
            # Pengajuan terbaru (5 terakhir) dengan join tabel mesin dan line
            cursor.execute("""
                SELECT TOP 5 
                    tp.history_id, tm.mesin, tp.oleh, 
                    tp.status, tp.tgl_insert, tl.line
                FROM tabel_pengajuan tp
                LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
                LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
                WHERE tp.history_id IS NOT NULL
                ORDER BY tp.tgl_insert DESC
            """)
            recent_pengajuan = cursor.fetchall()
            
    except Exception as e:
        print(f"Error loading dashboard data: {e}")
        total_pengajuan = 0
        status_data = []
        pengajuan_today = 0
        pengajuan_this_week = 0
        recent_pengajuan = []
    
    # Proses data status
    status_counts = {}
    for status, count in status_data:
        status_counts[str(status) if status else '0'] = count
    
    context = {
        'employee_data': employee_data,
        'total_pengajuan': total_pengajuan,
        'pengajuan_pending': status_counts.get('0', 0),
        'pengajuan_approved': status_counts.get('1', 0),
        'pengajuan_completed': status_counts.get('4', 0),
        'pengajuan_today': pengajuan_today,
        'pengajuan_this_week': pengajuan_this_week,
        'recent_pengajuan': recent_pengajuan,
        'page_title': 'Dashboard WO Maintenance'
    }
    
    return render(request, 'wo_maintenance_app/dashboard.html', context)


# ===== INPUT LAPORAN =====

# FIXED input_laporan - Bagian untuk mengganti di wo_maintenance_app/views.py

@login_required
def input_laporan(request):
    """View untuk input pengajuan maintenance baru - FIXED VERSION"""
    
    # Ambil data employee dari session (dari SDBM authentication)
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
        
        logger.debug(f"Form POST data: {request.POST}")
        
        if form.is_valid():
            try:
                logger.debug(f"Form cleaned data: {form.cleaned_data}")
                
                # FIXED: Ambil data yang sudah divalidasi dari form
                validated_data = form.cleaned_data
                
                with connections['DB_Maintenance'].cursor() as cursor:
                    # Generate history_id
                    today = datetime.now()
                    prefix = f"WO{today.strftime('%Y%m%d')}"
                    
                    # Cari nomor terakhir
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
                    
                    # Generate number_wo (dibatasi 15 karakter)
                    number_wo = f"WO{today.strftime('%y%m%d%H%M%S')}"
                    if len(number_wo) > 15:
                        number_wo = number_wo[:15]
                    
                    # Get next id_pengajuan
                    cursor.execute("SELECT ISNULL(MAX(id_pengajuan), 0) + 1 FROM tabel_pengajuan")
                    next_id_pengajuan = cursor.fetchone()[0]
                    
                    # FIXED: Konversi data dengan konsisten
                    line_id_int = int(validated_data['line_section'])
                    mesin_id_int = int(validated_data['nama_mesin'])  # Sudah divalidasi di form
                    section_id_int = int(validated_data['section_tujuan'])
                    pekerjaan_id_int = int(validated_data['jenis_pekerjaan'])
                    
                    # Dapatkan id_line float yang asli dari tabel_line
                    cursor.execute("""
                        SELECT id_line FROM tabel_line 
                        WHERE CAST(id_line AS int) = %s AND status = 'A'
                    """, [line_id_int])
                    
                    line_result = cursor.fetchone()
                    if not line_result:
                        raise ValueError(f"Line ID {line_id_int} tidak ditemukan")
                    
                    actual_line_id = line_result[0]  # Float value asli
                    
                    # Double check validasi mesin (sudah divalidasi di form, tapi safety check)
                    cursor.execute("""
                        SELECT tm.id_mesin 
                        FROM tabel_mesin tm
                        INNER JOIN tabel_line tl ON CAST(tl.id_line AS varchar(10)) = tm.id_line
                        WHERE tm.id_mesin = %s 
                            AND CAST(tl.id_line AS int) = %s
                            AND tm.mesin IS NOT NULL 
                            AND (tm.status IS NULL OR tm.status != '0')
                            AND tl.status = 'A'
                    """, [mesin_id_int, line_id_int])
                    
                    mesin_validation = cursor.fetchone()
                    if not mesin_validation:
                        raise ValueError(f"Validasi final gagal: Mesin {mesin_id_int} tidak valid untuk line {line_id_int}")
                    
                    # Batasi panjang data sesuai struktur database
                    user_insert = str(request.user.username)[:50]
                    oleh = str(employee_data.get('fullname', request.user.username))[:500]
                    deskripsi = str(validated_data['deskripsi_pekerjaan'])[:2000]  # Limit description
                    
                    logger.info(f"SAVE: Inserting pengajuan {history_id}")
                    logger.debug(f"SAVE: line_id={actual_line_id}, mesin_id={mesin_id_int}")
                    
                    # Insert data pengajuan dengan data yang sudah divalidasi
                    cursor.execute("""
                        INSERT INTO tabel_pengajuan 
                        (history_id, tgl_his, jam_his, id_line, id_mesin, number_wo, 
                         deskripsi_perbaikan, status, user_insert, tgl_insert, oleh, 
                         approve, id_section, id_pekerjaan, id_pengajuan, idpengajuan)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        history_id,
                        today,  # tgl_his
                        today.strftime('%H:%M:%S'),  # jam_his
                        actual_line_id,  # id_line (float value asli)
                        float(mesin_id_int),  # id_mesin
                        number_wo,  # number_wo
                        deskripsi,  # deskripsi_perbaikan
                        '0',  # status (pending)
                        user_insert,  # user_insert
                        today,  # tgl_insert
                        oleh,  # oleh
                        '0',  # approve (not approved)
                        float(section_id_int),  # id_section
                        float(pekerjaan_id_int),  # id_pekerjaan
                        next_id_pengajuan,  # id_pengajuan
                        float(next_id_pengajuan)  # idpengajuan
                    ])
                
                logger.info(f"SUCCESS: Pengajuan {history_id} berhasil disimpan")
                messages.success(
                    request, 
                    f'Pengajuan berhasil dibuat dengan ID: {history_id}'
                )
                return redirect('wo_maintenance_app:daftar_laporan')
                
            except Exception as e:
                logger.error(f"ERROR saving pengajuan: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                messages.error(request, f'Terjadi kesalahan saat menyimpan data: {str(e)}')
        else:
            # Form tidak valid - log error dengan detail
            logger.error(f"DEBUG INPUT: Form validation errors: {form.errors}")
            logger.debug(f"DEBUG INPUT: Form data: {request.POST}")
            
            # Cek error spesifik untuk mesin
            if 'nama_mesin' in form.errors:
                mesin_id = request.POST.get('nama_mesin', '')
                line_id = request.POST.get('line_section', '')
                logger.error(f"MESIN ERROR: Mesin ID {mesin_id} tidak valid untuk Line ID {line_id}")
                
                # Coba cek di database untuk debugging
                try:
                    with connections['DB_Maintenance'].cursor() as cursor:
                        cursor.execute("""
                            SELECT COUNT(*) 
                            FROM tabel_mesin tm
                            INNER JOIN tabel_line tl ON CAST(tl.id_line AS varchar(10)) = tm.id_line
                            WHERE tm.id_mesin = %s AND CAST(tl.id_line AS int) = %s
                        """, [int(mesin_id), int(line_id)])
                        count = cursor.fetchone()[0]
                        logger.error(f"MESIN DEBUG: Found {count} matching records for mesin {mesin_id} in line {line_id}")
                except Exception as debug_e:
                    logger.error(f"MESIN DEBUG ERROR: {debug_e}")
            
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
    
@login_required
def daftar_laporan(request):
    """
    View untuk menampilkan daftar pengajuan maintenance dengan sistem hierarchy filter
    FIXED: menggunakan tabel_pengajuan yang benar
    """
    try:
        # ===== AMBIL DATA HIERARCHY USER =====
        user_hierarchy = get_employee_hierarchy_data(request.user)
        
        if not user_hierarchy:
            logger.warning(f"User {request.user.username} tidak ditemukan di database SDBM")
            messages.error(request, 'Data karyawan tidak ditemukan. Hubungi administrator.')
            return redirect('wo_maintenance_app:dashboard')
        
        logger.info(f"User {user_hierarchy.get('fullname')} accessing daftar laporan with hierarchy filter")
        
        # ===== TENTUKAN EMPLOYEE NUMBERS YANG DAPAT DILIHAT =====
        allowed_employee_numbers = get_subordinate_employee_numbers(user_hierarchy)
        
        if not allowed_employee_numbers:
            logger.warning(f"No subordinates found for user {user_hierarchy.get('fullname')}")
            allowed_employee_numbers = [user_hierarchy.get('employee_number')]
        
        # ===== TAMBAHKAN PENGAJUAN YANG DI-ASSIGN KE USER =====
        assigned_history_ids = get_assigned_pengajuan_for_user(user_hierarchy.get('employee_number'))
        
        logger.debug(f"User {user_hierarchy.get('fullname')} can view pengajuan from: {allowed_employee_numbers}")
        logger.debug(f"User {user_hierarchy.get('fullname')} has assigned pengajuan: {assigned_history_ids}")
        
        # ===== FILTER FORM =====
        filter_form = PengajuanFilterForm(request.GET or None)
        
        # ===== PENCARIAN =====
        search_query = request.GET.get('search', '').strip()
        
        # ===== QUERY DATABASE MAINTENANCE - FIXED: menggunakan tabel_pengajuan =====
        pengajuan_list = []
        total_records = 0
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Base WHERE clause dengan hierarchy filter + assignment filter
                where_conditions = []
                query_params = []
                
                # Filter berdasarkan employee numbers yang diizinkan ATAU pengajuan yang di-assign
                filter_conditions = []
                
                # Kondisi 1: Pengajuan dari bawahan
                if allowed_employee_numbers:
                    placeholders = ','.join(['%s'] * len(allowed_employee_numbers))
                    filter_conditions.append(f"tp.user_insert IN ({placeholders})")
                    query_params.extend(allowed_employee_numbers)
                
                # Kondisi 2: Pengajuan yang di-assign ke user (untuk supervisor di section tujuan)
                if assigned_history_ids:
                    assigned_placeholders = ','.join(['%s'] * len(assigned_history_ids))
                    filter_conditions.append(f"tp.history_id IN ({assigned_placeholders})")
                    query_params.extend(assigned_history_ids)
                
                # Gabungkan kondisi dengan OR
                if filter_conditions:
                    where_conditions.append(f"({' OR '.join(filter_conditions)})")
                else:
                    # Jika tidak ada kondisi, tampilkan kosong
                    where_conditions.append("1 = 0")
                
                # ===== FILTER BERDASARKAN FORM =====
                if filter_form.is_valid():
                    # Filter tanggal
                    tanggal_dari = filter_form.cleaned_data.get('tanggal_dari')
                    tanggal_sampai = filter_form.cleaned_data.get('tanggal_sampai')
                    
                    if tanggal_dari:
                        where_conditions.append("CAST(tp.tgl_insert AS DATE) >= %s")
                        query_params.append(tanggal_dari)
                    
                    if tanggal_sampai:
                        where_conditions.append("CAST(tp.tgl_insert AS DATE) <= %s")
                        query_params.append(tanggal_sampai)
                    
                    # Filter status
                    status_filter = filter_form.cleaned_data.get('status')
                    if status_filter:
                        where_conditions.append("tp.status = %s")
                        query_params.append(status_filter)
                    
                    # Filter nama mesin
                    nama_mesin_filter = filter_form.cleaned_data.get('nama_mesin')
                    if nama_mesin_filter:
                        where_conditions.append("tmes.mesin LIKE %s")
                        query_params.append(f"%{nama_mesin_filter}%")
                    
                    # Filter pengaju
                    pengaju_filter = filter_form.cleaned_data.get('pengaju')
                    if pengaju_filter:
                        where_conditions.append("tp.oleh LIKE %s")
                        query_params.append(f"%{pengaju_filter}%")
                    
                    # Filter history ID
                    history_id_filter = filter_form.cleaned_data.get('history_id')
                    if history_id_filter:
                        where_conditions.append("tp.history_id LIKE %s")
                        query_params.append(f"%{history_id_filter}%")
                
                # ===== PENCARIAN GLOBAL =====
                if search_query:
                    search_conditions = [
                        "tp.history_id LIKE %s",
                        "tp.oleh LIKE %s", 
                        "tmes.mesin LIKE %s",
                        "tp.deskripsi_perbaikan LIKE %s",
                        "tp.number_wo LIKE %s"
                    ]
                    where_conditions.append(f"({' OR '.join(search_conditions)})")
                    search_param = f"%{search_query}%"
                    query_params.extend([search_param] * len(search_conditions))
                
                # ===== BUILD FINAL WHERE CLAUSE =====
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                
                # ===== COUNT TOTAL RECORDS =====
                # Simplified count query untuk assignment
                count_queries = []
                count_params = []
                
                # Count pengajuan dari bawahan
                if allowed_employee_numbers:
                    placeholders = ','.join(['%s'] * len(allowed_employee_numbers))
                    count_queries.append(f"""
                        SELECT COUNT(DISTINCT tp.history_id)
                        FROM [DB_Maintenance].[dbo].[tabel_pengajuan] tp
                        LEFT JOIN [DB_Maintenance].[dbo].[tabel_mesin] tmes ON tp.id_mesin = tmes.id_mesin
                        LEFT JOIN [DB_Maintenance].[dbo].[tabel_line] tl ON tp.id_line = tl.id_line
                        LEFT JOIN [DB_Maintenance].[dbo].[tabel_msection] tms ON tp.id_section = tms.id_section
                        LEFT JOIN [DB_Maintenance].[dbo].[tabel_pekerjaan] tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
                        WHERE tp.user_insert IN ({placeholders})
                    """)
                    count_params.extend(allowed_employee_numbers)
                
                # Count pengajuan yang di-assign
                if assigned_history_ids:
                    assigned_placeholders = ','.join(['%s'] * len(assigned_history_ids))
                    count_queries.append(f"""
                        SELECT COUNT(DISTINCT tp.history_id)
                        FROM [DB_Maintenance].[dbo].[tabel_pengajuan] tp
                        WHERE tp.history_id IN ({assigned_placeholders})
                    """)
                    count_params.extend(assigned_history_ids)
                
                total_records = 0
                for i, count_query in enumerate(count_queries):
                    start_idx = sum(len(allowed_employee_numbers) if j == 0 else len(assigned_history_ids) for j in range(i))
                    end_idx = start_idx + (len(allowed_employee_numbers) if i == 0 else len(assigned_history_ids))
                    params = count_params[start_idx:end_idx] if i < len(count_queries) else []
                    
                    cursor.execute(count_query, params)
                    count_result = cursor.fetchone()
                    if count_result:
                        total_records += count_result[0]
                
                # ===== PAGINATION =====
                page_size = 20
                page_number = int(request.GET.get('page', 1))
                offset = (page_number - 1) * page_size
                
                total_pages = (total_records + page_size - 1) // page_size
                has_previous = page_number > 1
                has_next = page_number < total_pages
                previous_page_number = page_number - 1 if has_previous else None
                next_page_number = page_number + 1 if has_next else None
                
                # ===== MAIN QUERY - SIMPLIFIED untuk menghindari kompleksitas =====
                # Query untuk pengajuan dari bawahan
                subordinate_query = ""
                subordinate_params = []
                
                if allowed_employee_numbers:
                    placeholders = ','.join(['%s'] * len(allowed_employee_numbers))
                    subordinate_query = f"""
                        SELECT DISTINCT
                            tp.history_id,              -- 0
                            tp.oleh,                    -- 1 (pengaju)
                            tmes.mesin,                 -- 2 (nama mesin)
                            tms.seksi,                  -- 3 (section tujuan)
                            tpek.pekerjaan,             -- 4 (jenis pekerjaan)
                            tp.deskripsi_perbaikan,     -- 5 (deskripsi)
                            tp.status,                  -- 6
                            tp.tgl_insert,              -- 7
                            tp.user_insert,             -- 8
                            tp.number_wo,               -- 9
                            tl.line,                    -- 10 (line name)
                            tp.approve,                 -- 11
                            tp.tgl_his,                 -- 12
                            tp.jam_his,                 -- 13
                            tp.status_pekerjaan,        -- 14
                            'SUBORDINATE' as access_type -- 15
                        FROM [DB_Maintenance].[dbo].[tabel_pengajuan] tp
                        LEFT JOIN [DB_Maintenance].[dbo].[tabel_mesin] tmes ON tp.id_mesin = tmes.id_mesin
                        LEFT JOIN [DB_Maintenance].[dbo].[tabel_line] tl ON tp.id_line = tl.id_line
                        LEFT JOIN [DB_Maintenance].[dbo].[tabel_msection] tms ON tp.id_section = tms.id_section
                        LEFT JOIN [DB_Maintenance].[dbo].[tabel_pekerjaan] tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
                        WHERE tp.user_insert IN ({placeholders})
                    """
                    subordinate_params = allowed_employee_numbers
                
                # Query untuk pengajuan yang di-assign
                assigned_query = ""
                assigned_params = []
                
                if assigned_history_ids:
                    assigned_placeholders = ','.join(['%s'] * len(assigned_history_ids))
                    assigned_query = f"""
                        SELECT DISTINCT
                            tp.history_id,              -- 0
                            tp.oleh,                    -- 1 (pengaju)
                            tmes.mesin,                 -- 2 (nama mesin)
                            tms.seksi,                  -- 3 (section tujuan)
                            tpek.pekerjaan,             -- 4 (jenis pekerjaan)
                            tp.deskripsi_perbaikan,     -- 5 (deskripsi)
                            tp.status,                  -- 6
                            tp.tgl_insert,              -- 7
                            tp.user_insert,             -- 8
                            tp.number_wo,               -- 9
                            tl.line,                    -- 10 (line name)
                            tp.approve,                 -- 11
                            tp.tgl_his,                 -- 12
                            tp.jam_his,                 -- 13
                            tp.status_pekerjaan,        -- 14
                            'ASSIGNED' as access_type   -- 15
                        FROM [DB_Maintenance].[dbo].[tabel_pengajuan] tp
                        LEFT JOIN [DB_Maintenance].[dbo].[tabel_mesin] tmes ON tp.id_mesin = tmes.id_mesin
                        LEFT JOIN [DB_Maintenance].[dbo].[tabel_line] tl ON tp.id_line = tl.id_line
                        LEFT JOIN [DB_Maintenance].[dbo].[tabel_msection] tms ON tp.id_section = tms.id_section
                        LEFT JOIN [DB_Maintenance].[dbo].[tabel_pekerjaan] tpek ON tp.id_pekerjaan = tpek.id_pekerjaan
                        WHERE tp.history_id IN ({assigned_placeholders})
                    """
                    assigned_params = assigned_history_ids
                
                # Gabungkan query dengan UNION
                union_queries = []
                union_params = []
                
                if subordinate_query:
                    union_queries.append(subordinate_query)
                    union_params.extend(subordinate_params)
                
                if assigned_query:
                    union_queries.append(assigned_query)
                    union_params.extend(assigned_params)
                
                if not union_queries:
                    # Tidak ada pengajuan yang dapat dilihat
                    pengajuan_list = []
                else:
                    main_query = f"""
                        SELECT * FROM (
                            {' UNION '.join(union_queries)}
                        ) combined_results
                        ORDER BY 
                            CASE WHEN access_type = 'ASSIGNED' THEN 1 ELSE 2 END,
                            tgl_insert DESC, 
                            history_id DESC
                        OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
                    """
                    
                    final_params = union_params + [offset, page_size]
                    
                    cursor.execute(main_query, final_params)
                    pengajuan_list = cursor.fetchall()
                
                logger.info(f"Found {total_records} pengajuan for user {user_hierarchy.get('fullname')} with hierarchy filter")
                
        except Exception as db_error:
            logger.error(f"Database error in daftar_laporan: {db_error}")
            messages.error(request, f'Terjadi kesalahan database: {str(db_error)}')
            pengajuan_list = []
            total_records = 0
            total_pages = 0
            has_previous = False
            has_next = False
            previous_page_number = None
            next_page_number = None
            page_number = 1
        
        # ===== CEK APPROVAL CAPABILITY =====
        # User dapat approve jika memiliki role supervisor/manager
        user_title = str(user_hierarchy.get('title_name', '')).upper()
        can_approve = (
            user_hierarchy.get('is_supervisor', False) or
            user_hierarchy.get('is_manager', False) or
            user_hierarchy.get('is_general_manager', False) or
            user_hierarchy.get('is_bod', False) or
            'SUPERVISOR' in user_title or
            'MANAGER' in user_title or
            'SPV' in user_title or
            'MGR' in user_title
        )
        
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
            'can_approve': can_approve,
            'user_hierarchy': user_hierarchy,
            'employee_data': user_hierarchy,  # Untuk compatibility dengan template
            
            # Hierarchy info untuk debugging (hanya untuk superuser)
            'debug_info': {
                'allowed_employee_count': len(allowed_employee_numbers),
                'assigned_pengajuan_count': len(assigned_history_ids),
                'user_role': f"{user_hierarchy.get('title_name', 'Unknown')} ({user_hierarchy.get('department_name', 'No Dept')})",
                'can_approve': can_approve,
                'table_used': 'tabel_pengajuan'  # Debug info
            } if request.user.is_superuser else None
        }
        
        return render(request, 'wo_maintenance_app/daftar_laporan.html', context)
        
    except Exception as e:
        logger.error(f"Critical error in daftar_laporan: {e}")
        messages.error(request, 'Terjadi kesalahan sistem. Silakan coba lagi atau hubungi administrator.')
        return redirect('wo_maintenance_app:dashboard')


# ===== DETAIL LAPORAN =====

@login_required
def detail_laporan(request, nomor_pengajuan):
    """
    View untuk menampilkan detail pengajuan dengan sistem approval hierarchy
    FIXED: menggunakan tabel_pengajuan yang benar
    """
    try:
        # ===== AMBIL DATA HIERARCHY USER =====
        user_hierarchy = get_employee_hierarchy_data(request.user)
        
        if not user_hierarchy:
            messages.error(request, 'Data karyawan tidak ditemukan. Hubungi administrator.')
            return redirect('wo_maintenance_app:daftar_laporan')
        
        # ===== AMBIL DATA PENGAJUAN - FIXED: menggunakan tabel_pengajuan =====
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
        
        # ===== CEK APAKAH USER DAPAT MELIHAT PENGAJUAN INI =====
        allowed_employee_numbers = get_subordinate_employee_numbers(user_hierarchy)
        assigned_history_ids = get_assigned_pengajuan_for_user(user_hierarchy.get('employee_number'))
        
        # User dapat melihat jika pengajuan dari bawahan ATAU di-assign ke user
        can_view = (
            pengajuan['user_insert'] in allowed_employee_numbers or 
            pengajuan['history_id'] in assigned_history_ids
        )
        
        if not can_view:
            logger.warning(f"User {user_hierarchy.get('fullname')} tried to access unauthorized pengajuan {nomor_pengajuan}")
            messages.error(request, 'Anda tidak memiliki akses ke pengajuan ini.')
            return redirect('wo_maintenance_app:daftar_laporan')
        
        # ===== CEK APPROVAL CAPABILITY =====
        # Ambil data hierarchy pembuat pengajuan
        pengaju_hierarchy = get_employee_by_number(pengajuan['user_insert'])
        can_approve = False
        
        if pengaju_hierarchy and pengajuan['status'] == '0':  # Status pending
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
                        # Update status dan approval pada tabel_pengajuan
                        new_status = action  # '1' untuk approve, '2' untuk reject
                        
                        cursor.execute("""
                            UPDATE [DB_Maintenance].[dbo].[tabel_pengajuan]
                            SET status = %s, approve = %s
                            WHERE history_id = %s
                        """, [new_status, new_status, nomor_pengajuan])
                        
                        # ===== NEW: REVIEW SYSTEM INTEGRATION =====
                        if action == '1':  # Jika di-approve
                            # STEP 1: Set status untuk review oleh SITI FATIMAH
                            cursor.execute("""
                                UPDATE [DB_Maintenance].[dbo].[tabel_pengajuan]
                                SET review_status = '0'
                                WHERE history_id = %s
                            """, [nomor_pengajuan])
                            
                            logger.info(f"Pengajuan {nomor_pengajuan} approved by {user_hierarchy.get('fullname')} - sent to review queue")
                            
                            # STEP 2: Ensure review tables exist
                            from wo_maintenance_app.views import ensure_review_tables_exist
                            ensure_review_tables_exist()
                            
                            messages.success(request, 
                                f'Pengajuan {nomor_pengajuan} berhasil di-approve! '
                                f'Pengajuan akan direview oleh {REVIEWER_FULLNAME} untuk distribusi ke section yang tepat.'
                            )
                            
                            # STEP 3: Optional - Assignment ke assistant supervisor+ di section tujuan 
                            # (Akan dilakukan setelah review oleh Siti Fatimah)
                            # Kode assignment yang lama di-comment karena akan dilakukan di review stage
                            """
                            # Dapatkan section tujuan dari pengajuan
                            cursor.execute(""
                                SELECT id_section 
                                FROM [DB_Maintenance].[dbo].[tabel_pengajuan]
                                WHERE history_id = %s
                            "", [nomor_pengajuan])
                            
                            section_result = cursor.fetchone()
                            if section_result and section_result[0]:
                                section_tujuan_id = int(float(section_result[0]))
                                
                                # Assignment otomatis ke assistant supervisor+ di section tujuan
                                assigned_employees = assign_pengajuan_to_section_supervisors(
                                    nomor_pengajuan, 
                                    section_tujuan_id, 
                                    user_hierarchy.get('employee_number')
                                )
                                
                                if assigned_employees:
                                    logger.info(f"Auto-assigned pengajuan {nomor_pengajuan} to {len(assigned_employees)} assistant supervisors+ in section {section_tujuan_id}")
                                    messages.info(request, f'Pengajuan telah di-assign ke {len(assigned_employees)} assistant supervisor+ di section tujuan.')
                                else:
                                    logger.warning(f"No assistant supervisors+ found for auto-assignment in section {section_tujuan_id}")
                            """
                        else:
                            # Rejection - langsung final, tidak perlu review
                            logger.info(f"Pengajuan {nomor_pengajuan} rejected by {user_hierarchy.get('fullname')}")
                            messages.success(request, f'Pengajuan {nomor_pengajuan} berhasil ditolak.')
                        
                        # Log approval action (existing code)
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
        
        # ===== CEK ASSIGNMENT INFO =====
        is_assigned_to_user = pengajuan['history_id'] in assigned_history_ids
        assignment_info = None
        
        if is_assigned_to_user:
            try:
                with connections['DB_Maintenance'].cursor() as cursor:
                    cursor.execute("""
                        SELECT assigned_by_employee, assignment_date, notes
                        FROM [DB_Maintenance].[dbo].[tabel_pengajuan_assignment]
                        WHERE history_id = %s AND assigned_to_employee = %s AND is_active = 1
                    """, [pengajuan['history_id'], user_hierarchy.get('employee_number')])
                    
                    assignment_row = cursor.fetchone()
                    if assignment_row:
                        assignment_info = {
                            'assigned_by': assignment_row[0],
                            'assignment_date': assignment_row[1],
                            'notes': assignment_row[2]
                        }
            except Exception as e:
                logger.error(f"Error getting assignment info: {e}")
        
        # ===== CONTEXT =====
        context = {
            'pengajuan': pengajuan,
            'can_approve': can_approve,
            'approval_form': approval_form,
            'user_hierarchy': user_hierarchy,
            'employee_data': user_hierarchy,  # Untuk compatibility dengan template
            'pengaju_hierarchy': pengaju_hierarchy,
            'is_assigned_to_user': is_assigned_to_user,
            'assignment_info': assignment_info
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
        from .utils import ensure_assignment_tables_exist
        
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
        from .utils import assign_pengajuan_to_section_supervisors, get_target_section_supervisors
        
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
        from .utils import get_target_section_supervisors
        
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
    """AJAX view untuk mendapatkan mesin berdasarkan line - FIXED VERSION"""
    
    line_id = str(request.GET.get('line_id', '')).strip()
    
    logger.debug(f"AJAX: Getting mesin for line_id: '{line_id}'")
    
    if not line_id:
        return JsonResponse({
            'success': False,
            'mesins': [],
            'message': 'Line ID tidak ditemukan'
        })
    
    try:
        # Validasi line_id adalah integer
        try:
            line_id_int = int(line_id)
        except ValueError:
            return JsonResponse({
                'success': False,
                'mesins': [],
                'message': f'Line ID tidak valid: {line_id}'
            })
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # STEP 1: Validasi line exists
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
            
            # STEP 2: Get mesin dengan method yang konsisten
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
            
            # STEP 3: Build response dengan validasi
            mesin_list = []
            seen_ids = set()  # Prevent duplicates
            
            for mesin in mesins:
                try:
                    id_mesin = int(float(mesin[0]))  # Consistent ID conversion
                    mesin_name = str(mesin[1] or '').strip()
                    mesin_nomer = str(mesin[2] or '').strip()
                    
                    # Skip jika ID sudah ada atau nama kosong
                    if id_mesin in seen_ids or not mesin_name:
                        continue
                    
                    display_name = mesin_name
                    if mesin_nomer:
                        display_name += f" ({mesin_nomer})"
                    
                    mesin_list.append({
                        'id': str(id_mesin),  # String untuk konsistensi dengan form
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
                'message': f'Ditemukan {len(mesin_list)} mesin untuk {line_name}',
                'debug': {
                    'line_id': line_id,
                    'line_id_int': line_id_int,
                    'raw_count': len(mesins),
                    'filtered_count': len(mesin_list)
                }
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
    UPDATED: Check reviewer dengan SDBM
    """
    if not is_reviewer(request.user):
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    try:
        # Auto-initialize jika perlu
        initialize_review_data()
        
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tabel_pengajuan 
                WHERE status = '1' AND approve = '1' 
                    AND (review_status IS NULL OR review_status = '0')
            """)
            count = cursor.fetchone()[0] or 0
            
            employee_data = get_employee_data_for_request(request)
            reviewer_name = employee_data.get('fullname', REVIEWER_FULLNAME) if employee_data else REVIEWER_FULLNAME
            
            return JsonResponse({
                'success': True,
                'count': count,
                'reviewer': reviewer_name
            })
            
    except Exception as e:
        logger.error(f"Error getting pending review count: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def force_review_initialization(request):
    """
    Force initialize review system untuk SITI FATIMAH
    """
    if not is_reviewer(request.user):
        return JsonResponse({'error': 'Unauthorized - Only SITI FATIMAH can access this'}, status=403)
    
    try:
        success = initialize_review_data()
        
        if success:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Get count of ready pengajuan
                cursor.execute("""
                    SELECT COUNT(*) FROM tabel_pengajuan 
                    WHERE status = '1' AND approve = '1' 
                        AND review_status = '0'
                """)
                ready_count = cursor.fetchone()[0]
                
                return JsonResponse({
                    'success': True,
                    'ready_for_review_count': ready_count,
                    'message': f'Successfully initialized review system. {ready_count} pengajuan ready for review.'
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


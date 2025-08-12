from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.urls import path, reverse_lazy

# LIBRARY FOR IMPORT DATA
from django.http import JsonResponse, HttpResponse
from csv import reader
from django.db import connections

from django.contrib.auth.models import User, Group
from master_app.models import UserProfileInfo, UserKeluargaInfo, Province, Regency, District, Village,Department, Division
from it_app.models import IPAddress, Hardware, ListLocation
from qc_app.models import rirMaterial, rirVendor
from hrd_app.models import medicalApprovalList, medicalRemain

from accounting_app.models import coaCode
from production_app.models import masterTagVL, masterTagLowModulus
from django.contrib.auth.decorators import user_passes_test
import csv
# Create your views here.
from django.contrib.auth.hashers import check_password
from datetime import datetime
import json

# ==== TAMBAHAN UNTUK SDBM AUTHENTICATION ====
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django import forms

import logging

logger = logging.getLogger(__name__)

class SDBMLoginForm(forms.Form):
    """
    Form login khusus untuk SDBM authentication
    """
    employee_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nomor Karyawan',
            'required': True,
        }),
        label='Nomor Karyawan'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': True,
        }),
        label='Password'
    )

def convert_datetime_to_string(obj):
    """
    Helper function untuk mengkonversi datetime objects ke string
    """
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif hasattr(obj, 'strftime'):  # untuk date objects
        return obj.strftime('%Y-%m-%d')
    return obj

def sdbm_login_view(request):
    """
    FIXED: View untuk login menggunakan SDBM database
    Handle datetime serialization issue dengan triple safety check
    """
    if request.method == 'POST':
        form = SDBMLoginForm(request.POST)
        
        if form.is_valid():
            employee_number = form.cleaned_data['employee_number']
            password = form.cleaned_data['password']
            
            logger.info(f"LOGIN ATTEMPT: {employee_number}")
            
            # Authenticate menggunakan custom backend
            user = authenticate(
                request=request,
                username=employee_number, 
                password=password
            )
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Selamat datang, {user.first_name}!')
                
                # FIXED: Triple safety untuk session storage
                try:
                    # STEP 1: Cek apakah sudah ada di session dari authentication backend
                    existing_data = request.session.get('employee_data')
                    
                    if not existing_data:
                        # STEP 2: Ambil fresh data jika belum ada
                        logger.info(f"LOGIN: Getting fresh employee data for {employee_number}")
                        employee_data = get_employee_data_for_session(employee_number)
                        
                        if employee_data:
                            # STEP 3: Final conversion dan validation
                            try:
                                # Test JSON serialization sebelum simpan
                                json_test = json.dumps(employee_data)
                                
                                # Jika berhasil, simpan ke session
                                request.session['employee_data'] = employee_data
                                logger.info(f"LOGIN SUCCESS: Employee data saved to session for {employee_number}")
                                
                            except (TypeError, ValueError) as json_error:
                                logger.error(f"LOGIN JSON TEST FAILED: {json_error}")
                                
                                # Last resort: create minimal safe data
                                safe_data = {
                                    'employee_number': employee_number,
                                    'fullname': user.get_full_name() or user.username,
                                    'nickname': user.first_name or user.username,
                                    'department_name': 'Unknown Department',
                                    'section_name': 'Unknown Section',
                                    'title_name': 'Unknown Title',
                                    'display_name': user.first_name or user.username,
                                    'has_approval_role': False,
                                    'is_manager': False,
                                    'is_supervisor': False,
                                    'is_general_manager': False,
                                    'is_bod': False,
                                    'login_method': 'fallback_safe_data'
                                }
                                
                                # Test dan simpan safe data
                                json.dumps(safe_data)  # Test
                                request.session['employee_data'] = safe_data
                                logger.warning(f"LOGIN: Used safe fallback data for {employee_number}")
                    else:
                        logger.info(f"LOGIN: Using existing session data for {employee_number}")
                
                except Exception as session_error:
                    logger.error(f"LOGIN SESSION ERROR: {session_error}")
                    # Login tetap berlanjut meski session save gagal
                    messages.warning(request, 'Login berhasil, tapi ada masalah dengan penyimpanan data. Fungsi mungkin terbatas.')
                
                # Redirect ke halaman yang diminta atau dashboard
                next_url = request.GET.get('next', '/')
                logger.info(f"LOGIN REDIRECT: {employee_number} -> {next_url}")
                return redirect(next_url)
            else:
                logger.warning(f"LOGIN FAILED: Invalid credentials for {employee_number}")
                messages.error(request, 'Nomor karyawan atau password salah!')
        else:
            logger.warning(f"LOGIN FORM ERROR: {form.errors}")
            messages.error(request, 'Form tidak valid!')
    else:
        form = SDBMLoginForm()
    
    context = {
        'form': form,
        'title': 'Login SDBM System'
    }
    
    return render(request, 'registration/login.html', context)

def get_employee_data_for_session(employee_number):
    """
    FIXED: Helper function untuk mengambil data employee dari SDBM untuk session
    Memastikan semua datetime objects dikonversi ke string
    """
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
                    t.is_bod,
                    
                    -- AVOID datetime fields yang menyebabkan masalah
                    -- e.created_date,  -- REMOVE untuk hindari datetime issues
                    
                    p.created_date  -- Ambil dari position table sebagai test
                    
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
            """, [employee_number])
            
            row = cursor.fetchone()
            
            if row:
                # FIXED: Konversi datetime field immediately ke string
                position_created_date = None
                if row[22]:  # position created_date
                    try:
                        position_created_date = row[22].strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        position_created_date = str(row[22]) if row[22] else None
                
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
                    'division_id': row[11],
                    'department_name': row[12],
                    'section_name': row[13],
                    'subsection_name': row[14],
                    'title_name': row[15],
                    'is_manager': row[16],
                    'is_supervisor': row[17],
                    'is_general_manager': row[18],
                    'is_bod': row[19],
                    
                    # FIXED: Convert datetime field to string immediately  
                    'position_created_date': position_created_date,
                    
                    # Computed fields
                    'display_name': row[2] if row[2] else row[1],
                    'has_approval_role': (
                        row[16] or row[17] or row[18] or row[19] or
                        'SUPERVISOR' in str(row[15] or '').upper() or
                        'MANAGER' in str(row[15] or '').upper() or
                        'SPV' in str(row[15] or '').upper() or
                        'MGR' in str(row[15] or '').upper()
                    ),
                    
                    # FIXED: Set safe default values - avoid datetime fields
                    'email': None,
                    'telph_number': None,
                    'join_date': None,  # String, bukan datetime
                    'employee_status': row[4],
                    'created_date': None  # Remove untuk safety
                }
                
                # FINAL SAFETY CHECK: convert any remaining datetime objects
                employee_data = convert_data_for_session(employee_data)
                
                return employee_data
                
    except Exception as e:
        logger.error(f"Error fetching employee data for session: {e}")
        
    return None

def convert_data_for_session(data):
    """
    FIXED: Konversi data agar aman untuk disimpan ke session (JSON serializable)
    """
    if isinstance(data, dict):
        return {key: convert_data_for_session(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_data_for_session(item) for item in data]
    elif isinstance(data, datetime):
        return data.strftime('%Y-%m-%d %H:%M:%S')
    elif hasattr(data, 'strftime'):  # untuk date objects
        return data.strftime('%Y-%m-%d')
    elif data is None:
        return None
    else:
        return data

def sdbm_api_check_user(request, employee_number, password):
    """
    FIXED: API untuk check user dari sistem eksternal - safe JSON response
    """
    user = authenticate(
        request=request,
        username=employee_number, 
        password=password
    )
    
    if user is not None:
        # FIXED: Ambil employee data yang aman untuk JSON response
        try:
            employee_data = get_employee_data_for_session(employee_number)
            serializable_data = convert_data_for_session(employee_data) if employee_data else {}
            
            # Test JSON serialization
            json.dumps(serializable_data)
            
            return JsonResponse({
                'status': 'success',
                'valid': True,
                'employee_data': serializable_data
            })
        except Exception as e:
            logger.error(f"API JSON ERROR: {e}")
            return JsonResponse({
                'status': 'success',
                'valid': True,
                'employee_data': {
                    'employee_number': employee_number,
                    'login_status': 'valid_but_data_error'
                }
            })
    else:
        return JsonResponse({
            'status': 'failed',
            'valid': False,
            'message': 'Invalid credentials'
        })


def get_employee_info(request, employee_number):
    """
    FIXED: API untuk mendapatkan informasi karyawan dari SDBM
    Handle datetime serialization dengan safety check
    """
    try:
        employee_data = get_employee_data_for_session(employee_number)
        
        if employee_data:
            # Konversi ke format yang aman untuk JSON
            serializable_data = convert_data_for_session(employee_data)
            
            # Test JSON serialization
            json.dumps(serializable_data)
            
            return JsonResponse({
                'status': 'success',
                'employee': serializable_data
            })
        else:
            return JsonResponse({
                'status': 'failed',
                'message': 'Employee not found'
            })
            
    except Exception as e:
        logger.error(f"Error in get_employee_info: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })


# def employee_context(request):
#     """
#     Context processor untuk menambahkan data employee ke semua template
#     """
#     if request.user.is_authenticated:
#         employee_data = request.session.get('employee_data', {})
#         return {
#             'employee_data': employee_data
#         }
#     return {}

# FIXED employee_context - Bagian untuk mengganti di master_app/views.py

# FIXED employee_context - Bagian untuk mengganti di master_app/views.py
def employee_context(request):
    """
    FIXED: Context processor untuk menyediakan data employee dari SDBM ke semua template
    Handle datetime serialization dan gunakan data dari session dengan safety check
    """
    
    # Default context
    context = {
        'employee_data': None,
        'sdbm_status': 'not_authenticated'
    }
    
    # Hanya proses jika user authenticated
    if not request.user.is_authenticated:
        return context
    
    try:
        # FIXED: Coba ambil dari session dulu untuk efisiensi
        employee_data = request.session.get('employee_data')
        
        if employee_data:
            # SAFETY CHECK: pastikan data masih JSON serializable
            try:
                json.dumps(employee_data)
                context.update({
                    'employee_data': employee_data,
                    'sdbm_status': 'connected'
                })
                return context
            except Exception as json_error:
                logger.error(f"CONTEXT JSON ERROR: {json_error}")
                # Clear bad session data
                del request.session['employee_data']
        
        # Jika tidak ada di session atau ada error, query database
        employee_data = get_employee_data_for_session(request.user.username)
        
        if employee_data:
            # Konversi untuk session storage
            serializable_data = convert_data_for_session(employee_data)
            
            # Test JSON serialization
            json.dumps(serializable_data)
            
            # Simpan ke session untuk penggunaan berikutnya
            request.session['employee_data'] = serializable_data
            
            context.update({
                'employee_data': serializable_data,
                'sdbm_status': 'connected'
            })
            
            logger.debug(f"Employee context loaded for {employee_data['fullname']} ({employee_data['employee_number']})")
            
        else:
            logger.warning(f"Employee data not found in SDBM for user: {request.user.username}")
            # Fallback safe data
            fallback_data = {
                'fullname': request.user.get_full_name() or request.user.username,
                'nickname': request.user.first_name or request.user.username,
                'employee_number': request.user.username,
                'department_name': 'Unknown Department',
                'section_name': 'Unknown Section',
                'title_name': 'Unknown Title',
                'display_name': request.user.first_name or request.user.username,
                'has_approval_role': False,
                'is_manager': False,
                'is_supervisor': False,
                'is_general_manager': False,
                'is_bod': False,
                'email': None,
                'telph_number': None,
                'join_date': None,
                'employee_status': 'active',
                'context_source': 'fallback'
            }
            
            context.update({
                'employee_data': fallback_data,
                'sdbm_status': 'no_data'
            })
                
    except Exception as e:
        logger.error(f"Error loading employee context for user {request.user.username}: {e}")
        
        # Emergency fallback context dengan data minimal
        emergency_data = {
            'fullname': request.user.get_full_name() or request.user.username,
            'nickname': request.user.first_name or request.user.username,
            'employee_number': request.user.username,
            'department_name': 'System Error',
            'section_name': 'System Error',
            'title_name': 'System Error',
            'display_name': request.user.first_name or request.user.username,
            'has_approval_role': False,
            'is_manager': False,
            'is_supervisor': False,
            'is_general_manager': False,
            'is_bod': False,
            'email': None,
            'telph_number': None,
            'join_date': None,
            'employee_status': 'error',
            'context_source': 'emergency_fallback'
        }
        
        context.update({
            'employee_data': emergency_data,
            'sdbm_status': 'error'
        })
    
    return context

# ===== FUNGSI HELPER UNTUK CEK APPROVAL ROLE =====

def user_has_approval_role(user):
    """
    Fungsi helper untuk mengecek apakah user memiliki role approval
    """
    if not user or not user.is_authenticated:
        return False
    
    try:
        from wo_maintenance_app.utils import get_employee_hierarchy_data
        
        employee_data = get_employee_hierarchy_data(user)
        if employee_data:
            user_title = str(employee_data.get('title_name', '')).upper()
            
            return (
                employee_data.get('is_manager', False) or
                employee_data.get('is_supervisor', False) or
                employee_data.get('is_general_manager', False) or
                employee_data.get('is_bod', False) or
                'SUPERVISOR' in user_title or
                'MANAGER' in user_title or
                'SPV' in user_title or
                'MGR' in user_title
            )
    except Exception as e:
        logger.error(f"Error checking approval role for {user.username}: {e}")
    
    return False


def get_user_department_section(user):
    """
    Fungsi helper untuk mendapatkan department dan section user
    """
    if not user or not user.is_authenticated:
        return None, None
    
    try:
        from wo_maintenance_app.utils import get_employee_hierarchy_data
        
        employee_data = get_employee_hierarchy_data(user)
        if employee_data:
            return employee_data.get('department_name'), employee_data.get('section_name')
    except Exception as e:
        logger.error(f"Error getting department/section for {user.username}: {e}")
    
    return None, None

@login_required
def dashboard_view(request):
    """
    Dashboard utama yang menampilkan informasi employee dari SDBM
    """
    employee_data = request.session.get('employee_data', {})
    
    context = {
        'employee_data': employee_data,
        'page_title': 'Dashboard',
    }
    
    return render(request, 'master_app/dashboard.html', context)

@login_required
def employee_profile_view(request):
    """
    Halaman profil employee dari SDBM
    """
    employee_data = request.session.get('employee_data', {})
    
    context = {
        'employee_data': employee_data,
        'page_title': 'Profil Karyawan',
    }
    
    return render(request, 'master_app/employee_profile.html', context)

# ==== KODE EXISTING YANG DIPERBARUI ====

@login_required
def userIndex(request):
    users = User.objects.all()  # Query all user objects

    # Gunakan database alias yang benar berdasarkan konfigurasi
    try:
        database_alias = 'seiwa_int_app_db'  # Replace with the alias of the desired database
        connection = connections[database_alias]
        
        # Execute a SQL query to fetch multiple fields from sys_user
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT IDUser, UserName, Department, Division, SubSection
                FROM sys_user
            """)
            seiwa_users_data = cursor.fetchall()
    except:
        # Fallback jika database seiwa_int_app_db tidak tersedia
        seiwa_users_data = []

    # Create a list of dictionaries with field names as keys
    seiwa_users = [{'IDUser': row[0], 'UserName': row[1], 'Department': row[2], 'Division': row[3], 'SubSection': row[4]} for row in seiwa_users_data]

    # Compare seiwa_users with users' usernames to find new users
    new_users = [user for user in seiwa_users if user['IDUser'] not in users.values_list('username', flat=True)]

    # Ambil data employee dari SDBM juga
    sdbm_employees = []
    try:
        connection = connections['SDBM']
        cursor = connection.cursor()
        
        query = """
            SELECT 
                e.employee_number, 
                e.fullname, 
                e.nickname,
                d.name as department_name,
                s.name as section_name,
                ss.name as subsection_name,
                t.Name as title_name
            FROM hrbp.employees e
            LEFT JOIN hrbp.position p ON e.id = p.employeeId
            LEFT JOIN hr.department d ON p.departmentId = d.id
            LEFT JOIN hr.section s ON p.sectionId = s.id
            LEFT JOIN hr.subsection ss ON p.subsectionId = ss.id
            LEFT JOIN hr.title t ON p.titleId = t.id
            WHERE e.is_active = 1
            ORDER BY e.employee_number
        """
        
        cursor.execute(query)
        sdbm_data = cursor.fetchall()
        
        sdbm_employees = [{
            'employee_number': row[0],
            'fullname': row[1],
            'nickname': row[2],
            'department_name': row[3],
            'section_name': row[4],
            'subsection_name': row[5],
            'title_name': row[6],
        } for row in sdbm_data]
        
    except Exception as e:
        print(f"Error fetching SDBM employees: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()

    context = {
        'seiwa_users': seiwa_users,
        'users': users,
        'new_users': new_users,
        'sdbm_employees': sdbm_employees,
    }

    return render(request, 'master_app/user.html', context)

@login_required 
def userSynchronize(request):
    users = User.objects.all()  # Query all user objects

    try:
        database_alias = 'seiwa_int_app_db'  # Replace with the alias of the desired database
        connection = connections[database_alias]
        
        # Execute a SQL query to fetch multiple fields from sys_user
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT IDUser, UserName, Department, Division, SubSection
                FROM sys_user
            """)
            seiwa_users_data = cursor.fetchall()

        # Create a list of dictionaries with field names as keys
        seiwa_users = [{'IDUser': row[0], 'UserName': row[1], 'Department': row[2], 'Division': row[3], 'SubSection': row[4]} for row in seiwa_users_data]

        # Compare seiwa_users with users' usernames to find new users
        new_users = [user for user in seiwa_users if user['IDUser'] not in users.values_list('username', flat=True)]

        # Create new auth_user records and set passwords for them
        for new_user in new_users:
            # Define a password for the new user

            # Create a new User record
            user = User.objects.create_user(
                username=new_user['IDUser'],
                password=new_user['IDUser'],
                first_name=new_user['UserName'],
                email='',  # You can set an email if needed
            )
            department_user = ''
            department_user = Department.objects.filter(department_name__contains=new_user['Department']).first()
            division_user = ''
            division_user = Division.objects.filter(division_name__contains = new_user['Division']).first()
            if not division_user or division_user == '' :
                division_user = None
            if not department_user or department_user == '' : 
                department_user = None
    except Exception as e:
        print(f"Error in userSynchronize: {e}")
        messages.error(request, f"Error synchronizing users: {e}")
    
    return redirect('master_app:userIndex')

@login_required
def index(request):
    """
    Index view yang sudah diperbarui dengan dashboard routing yang lebih baik
    """
    # Ambil data employee dari session jika ada
    employee_data = request.session.get('employee_data', {})
    
    # Check user groups - kode existing tetap dipertahankan
    try:
        master_app = Group.objects.get(name="master_app").user_set.all()
        accounting_app = Group.objects.get(name="accounting_app").user_set.all()
        costcontrol_app = Group.objects.get(name="costcontrol_app").user_set.all()
        engineering_app = Group.objects.get(name="engineering_app").user_set.all()
        ga_app = Group.objects.get(name="ga_app").user_set.all()
        hrd_app = Group.objects.get(name="hrd_app").user_set.all()
        ie_app = Group.objects.get(name="ie_app").user_set.all()
        it_app = Group.objects.get(name="it_app").user_set.all()
        ppc_app = Group.objects.get(name="ppc_app").user_set.all()
        qc_app = Group.objects.get(name="qc_app").user_set.all()
        sales_app = Group.objects.get(name="sales_app").user_set.all()
        warehouse_app = Group.objects.get(name="warehouse_app").user_set.all()

        # Logika routing berdasarkan group - tetap seperti kode asli
        if request.user in it_app:
            return render(request,'it_app/dashboard.html', {'employee_data': employee_data})
        elif request.user in master_app:
            return render(request, 'master_app/dashboard.html', {'employee_data': employee_data})
        elif request.user in accounting_app:
            return render(request, 'accounting_app/dashboard.html', {'employee_data': employee_data})
        elif request.user in costcontrol_app:
            return render(request, 'costcontrol_app/dashboard.html', {'employee_data': employee_data})
        elif request.user in engineering_app:
            return render(request, 'engineering_app/dashboard.html', {'employee_data': employee_data})
        elif request.user in ga_app:
            return render(request, 'ga_app/dashboard.html', {'employee_data': employee_data})
        elif request.user in hrd_app:
            return render(request, 'hrd_app/dashboard.html', {'employee_data': employee_data})
        elif request.user in ie_app:
            return render(request, 'ie_app/dashboard.html', {'employee_data': employee_data})
        elif request.user in ppc_app:
            return render(request, 'ppc_app/dashboard.html', {'employee_data': employee_data})
        elif request.user in qc_app:
            return render(request,'qc_app/dashboard.html', {'employee_data': employee_data})
        elif request.user in sales_app:
            return render(request, 'sales_app/dashboard.html', {'employee_data': employee_data})
        elif request.user in warehouse_app:
            return render(request, 'warehouse_app/dashboard.html', {'employee_data': employee_data})
        else:
            return render (request, 'master_app/dashboard.html', {'employee_data': employee_data})
    
    except Group.DoesNotExist:
        # Jika group tidak ada, redirect ke dashboard master
        return render(request, 'master_app/dashboard.html', {'employee_data': employee_data})

# VISUALBASIC START - Diperbarui untuk mendukung SDBM
def pocvl_check_user(request, Username, Password):
    """
    Check user untuk Visual Basic - sekarang mendukung SDBM
    """
    # Coba authenticate dengan SDBM dulu
    user = authenticate(request=request, username=Username, password=Password)
    
    if user is not None:
        return HttpResponse('True')
    else:
        # Fallback ke Django User model
        try:
            user = User.objects.filter(username=Username).first()
            if user and check_password(Password, user.password):
                return HttpResponse('True')
        except:
            pass
        return HttpResponse('False')
    
def getFullName(request, Username):
    """
    Get full name - prioritas dari SDBM, fallback ke Django User
    """
    # Coba ambil dari SDBM dulu
    try:
        connection = connections['SDBM']
        cursor = connection.cursor()
        
        query = """
            SELECT e.fullname, e.nickname
            FROM hrbp.employees e
            WHERE e.is_active = 1 AND e.employee_number = %s
        """
        
        cursor.execute(query, [Username])
        employee_data = cursor.fetchone()
        
        if employee_data:
            fullname, nickname = employee_data
            return HttpResponse(fullname or nickname or Username)
            
    except Exception as e:
        print(f"Error getting fullname from SDBM: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
    
    # Fallback ke Django User
    try:
        user = User.objects.filter(username__contains=Username).first()
        if user:
            fullname = user.first_name + ' ' + user.last_name
            return HttpResponse(fullname)
    except:
        pass
    
    return HttpResponse(Username)

# INI UNTUK GATEPASS SYSTEM - Diperbarui untuk mendukung SDBM
def gatepass_check_user(request, Username, Password):
    """
    Check user untuk gatepass system - sekarang mendukung SDBM
    """
    # Coba authenticate dengan SDBM dulu
    user = authenticate(request=request, username=Username, password=Password)
    
    if user is not None:
        return HttpResponse('True')
    else:
        # Fallback ke Django User model
        try:
            user = User.objects.filter(username=Username).first()
            if user and check_password(Password, user.password):
                return HttpResponse('True')
        except:
            pass
        return HttpResponse('False')
    
def getSecurityName(request, Username):
    """
    Get security name - prioritas dari SDBM, fallback ke Django User
    """
    return getFullName(request, Username)  # Gunakan fungsi yang sama

# VISUALBASIC END

# ==== SEMUA KODE CREATE, UPDATE, DAN FUNCTION LAINNYA TETAP SAMA ====
# Saya akan menyalin semua fungsi yang sudah ada tanpa perubahan

# CREATE START
@login_required
def CreateUserdata(request):
    with open('templates/csv/list_user.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for id,first_name, last_name, username,  password, date_joined, *__ in csvf:
            user = User(id=id, username=username, first_name=first_name, last_name = last_name, is_staff = True, date_joined = date_joined ,is_active = True )
            d = datetime.strptime(user.date_joined, "%m/%d/%Y")
            user.date_joined = d.strftime("%Y-%m-%d-%H:%M:%S")
            user.set_password(password)
            data.append(user)
        User.objects.bulk_create(data)
    return JsonResponse('user csv is now working', safe=False)

@login_required
def CreateUserInfoData(request):
    with open('templates/csv/list_user_info.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for user_id, department_id, division_id, section_id, position, is_supervisor, is_manager, is_bod, *__ in csvf:
            user = UserProfileInfo(user_id=user_id, department_id=department_id, division_id = division_id, section_id = section_id
            ,  position = position, is_supervisor = is_supervisor, is_manager = is_manager, is_bod = is_bod
             )
            data.append(user)
        UserProfileInfo.objects.bulk_create(data)
    return JsonResponse('user Info csv is now working', safe=False)

@login_required
def place_value(number): 
    return ("{:,}".format(number)) 

# LANJUTAN
@login_required
def CreateIPAddressRegistered(request):
    with open('templates/csv/list_registered_ip.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for hardware_id, ip, name, *__ in csvf:
            IPAddressRegistered = IPAddress(hardware_id = hardware_id,ip = ip, name = name, is_used  = True)
            data.append(IPAddressRegistered)
        IPAddress.objects.bulk_create(data)
    return JsonResponse('IP Address Registered csv is now working', safe=False)

@login_required
def CreateIPAddressUnRegistered(request):
    with open('templates/csv/list_unregistered_ip.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for ip, *__ in csvf:
            IPAddressUNRegistered = IPAddress(ip = ip, is_used  = False)
            data.append(IPAddressUNRegistered)
        IPAddress.objects.bulk_create(data)
    return JsonResponse('IP Address Un Registered csv is now working', safe=False)

@login_required
def CreateMaterial(request):
    with open('templates/csv/material.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for name,classification_id,condition,location, classification_status, *__ in csvf:
            material = rirMaterial(name = name, classification_id = classification_id, condition = condition, location = location, classification_status = classification_status )
            data.append(material)
        rirMaterial.objects.bulk_create(data)
    return JsonResponse('Material csv is now working', safe=False)

@login_required 
def CreateVendor(request):
    with open('templates/csv/vendor.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for vendor_company, *__ in csvf:
            vendor = rirVendor(vendor_company = vendor_company)
            data.append(vendor)
        rirVendor.objects.bulk_create(data)
    return JsonResponse('Vendor csv is now working', safe=False)

@login_required
def CreateApprovalMedical(request):
    with open('templates/csv/ApprovalMedical.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for user_id, is_foreman, is_supervisor, is_manager, is_hr, *__ in csvf:
            ApprovalMedical = medicalApprovalList(user_id = user_id, is_foreman = is_foreman, is_supervisor = is_supervisor, is_manager = is_manager, is_hr = is_hr)
            data.append(ApprovalMedical)
        medicalApprovalList.objects.bulk_create(data)
    return JsonResponse('ApprovalMedical csv is now working', safe=False)

@login_required
def CreateInfoKeluarga(request):
    with open('templates/csv/userkeluargainfo.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for user_id, tanggal_lahir, gender, hubungan,nama_lengkap, *__ in csvf:
            user_table_id = User.objects.filter(username = user_id).first()
            InfoKeluarga = UserKeluargaInfo(user_id = user_table_id.id, tanggal_lahir = tanggal_lahir, gender = gender, hubungan = hubungan, nama_lengkap = nama_lengkap)
            data.append(InfoKeluarga)
        UserKeluargaInfo.objects.bulk_create(data)
    return JsonResponse('userkeluargainfo csv is now working', safe=False)

@login_required
def CreateCoaCode(request):
    with open('templates/csv/coacode.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for account_code, cost_centre, description, status, structure_code,  *__ in csvf:
            coacode = coaCode(account_code = account_code, cost_centre = cost_centre, description = description, status = status, structure_code = structure_code, )
            data.append(coacode)
        coaCode.objects.bulk_create(data)
    return JsonResponse('coacode csv is now working', safe=False)

@login_required
def CreateLocation(request):
    with open('templates/csv/list_location.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for location_name,   *__ in csvf:
            coacode = ListLocation(location_name = location_name,)
            data.append(coacode)
        ListLocation.objects.bulk_create(data)
    return JsonResponse('Location csv is now working', safe=False)

@login_required
def CreateRemain(request):
    with open('templates/csv/list_remain.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for user_id, marital_status, limit, used, remain,    *__ in csvf:
            user_table_id = User.objects.filter(username = user_id).first()
            medical_remain = medicalRemain(user = user_table_id, marital_status = marital_status, limit = limit, used = used, remain = remain,)
            data.append(medical_remain)
        medicalRemain.objects.bulk_create(data)
    return JsonResponse('Remain csv is now working', safe=False)

@login_required
def CreateProvince(request):
    with open('templates/csv/list_province.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for id, province_name,   *__ in csvf:
            province = Province(id = id, province_name = province_name,)
            data.append(province)
        Province.objects.bulk_create(data)
    return JsonResponse('Province csv is now working', safe=False)

@login_required
def CreateRegency(request):
    with open('templates/csv/list_regency.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for id, province_id, regency_name,   *__ in csvf:
            regency = Regency(id = id, province_id = province_id, regency_name = regency_name,)
            data.append(regency)
        Regency.objects.bulk_create(data)
    return JsonResponse('Regency csv is now working', safe=False)

@login_required
def CreateDistrict(request):
    with open('templates/csv/list_district.csv', 'r', encoding="utf-8") as csv_file:
        csvf = reader(csv_file)
        data = []
        for id, regency_id ,district_name,   *__ in csvf:
            district = District(id = id, regency_id = regency_id, district_name = district_name,)
            data.append(district) 
        District.objects.bulk_create(data)
    return JsonResponse('District csv is now working', safe=False)

@login_required
def CreateVillage(request):
    with open('templates/csv/list_village.csv', 'r', encoding="utf-8") as csv_file:
        csvf = reader(csv_file)
        data = []
        for id, district_id, village_name,   *__ in csvf:
            village = Village(id = id, district_id = district_id, village_name = village_name,)
            data.append(village)
        Village.objects.bulk_create(data)
    return JsonResponse('Village csv is now working', safe=False)

@login_required
def CreateMasterTagVL(request):
    with open('templates/csv/list_mastertag.csv', 'r', encoding="utf-8") as csv_file:
        csvf = reader(csv_file)
        data = []
        for item_no, item_desc, spec,poc,poc_lower,poc_upper,vib,run_out,tipe_pulley,pulley_diameter,weight_kg,weight_n,top_width,top_width_plus,top_width_minus,thickness,thickness_plus,thickness_minus,tipe_belt,   *__ in csvf:
            master_tag = masterTagVL(item_no = item_no, item_desc = item_desc, spec = spec, poc = poc, poc_lower = poc_lower,poc_upper = poc_upper,vib = vib,run_out = run_out, tipe_pulley = tipe_pulley,pulley_diameter = pulley_diameter,weight_kg = weight_kg,weight_n = weight_n,top_width = top_width,top_width_plus = top_width_plus,top_width_minus = top_width_minus,thickness = thickness,thickness_plus = thickness_plus,thickness_minus = thickness_minus,tipe_belt = tipe_belt)
            data.append(master_tag)
        masterTagVL.objects.bulk_create(data)
    return JsonResponse('Master Tag VL CSV is now Working', safe=False)
# CREATE END

# ==== SEMUA FUNGSI UPDATE DAN LAINNYA TETAP SAMA ====
# Saya akan melanjutkan dengan semua fungsi existing tanpa perubahan

# UPDATE START
@login_required
def UpdateRemain(request):
    # Read CSV File
    with open('hrd_app/templates/csv/updateremain.csv') as f:
        reader = csv.reader(f)
        data = list(reader)
    # Retrieve objects from database and update fields
        updates = []
    # Return the response object
        for username_row,marital_status_row,limit_row,used_row,remain_row , *__ in data:
            user = UserProfileInfo.objects.filter(user__username__contains=username_row).first()
            if user:
                medical = medicalRemain.objects.filter(user = user.id ).first()
                if medical:
                    id_value= medical.id 
                    marital_status_value = marital_status_row
                    limit_value =limit_row
                    used_value = used_row
                    remain_value = remain_row
                    updates.append(medicalRemain(id = id_value, marital_status = marital_status_value, limit = limit_value, used = used_value, remain = remain_value))
        medicalRemain.objects.bulk_update(updates, ['marital_status','limit','used','remain'])
    return JsonResponse('updateremain csv is  now working', safe=False)

@login_required
def UpdateUpdateUserProfileInfoGenderStatus(request):
    # Read CSV file
    with open('templates/csv/updateuserprofileinfogenderandstatus.csv') as f:
        reader = csv.reader(f)
        data = list(reader)
    # Retrieve objects from database and update fields
    updates = []
    # Return the response object
    for username_row,contract_row,is_permanent_row,gender_row in data:
        user = UserProfileInfo.objects.filter(user__username=username_row).first()
        if user:
            id_value = user.id
            is_contract_value   = contract_row
            is_permanent_value  = is_permanent_row
            gender_value    = gender_row
            updates.append(UserProfileInfo(id=id_value, is_contract   = is_contract_value, is_permanent  = is_permanent_value, gender = gender_value))

    UserProfileInfo.objects.bulk_update(updates, ['is_contract', 'is_permanent', 'gender'])
    return JsonResponse('updateuserprofileinfogenderandstatus csv is now working', safe=False)

@login_required
def UpdateUserProfileInfoTanggalLahir(request):
    # Read CSV File
    with open('templates/csv/userprofileinfoupdatetanggallahir.csv') as f:
        reader = csv.reader(f)
        data = list(reader)
    # Retrieve objects from database and update fields
    updates = []
    # Return the response object
    for username_row, tanggal_lahir in data:
            user = UserProfileInfo.objects.filter(user__username=username_row).first()
            if user:
                id_value = user.id
                tanggal_lahir_value = tanggal_lahir
                updates.append(UserProfileInfo(id=id_value, tanggal_lahir=tanggal_lahir_value))
    # return HttpResponse(updates, content_type="application/json")
    UserProfileInfo.objects.bulk_update(updates, ['tanggal_lahir',])
    return JsonResponse('userprofileinfoupdatetanggallahir csv is now working', safe=False)

def UpdateMasterLowModulus(request):
    # check if a file was uploaded
    if 'file' not in request.FILES:
        return None, None
    
    file = request.FILES['file']
    
    csv_data = []
    try:
        for line in file:
            csv_data.append(line.decode('utf-8'))
    except UnicodeDecodeError:
        return None, None
    
    reader = csv.reader(csv_data)
    data = list(reader)

    updates = []
    creates = []
    for item_no_row,item_desc_row,spec_row,poc_row,tension_row,tension_plus_row,tension_minus_row,ride_out_row,ride_out_plus_row,ride_out_minus_row,tipe_pulley_row,pulley_diameter_row,top_width_row,top_width_plus_row,top_width_minus_row,thickness_row,thickness_plus_row,thickness_minus_row,cpl100mm_row, cpl1round_row,high_speed_row,low_speed_row,rpm_row,is_doc_row, *__ in data:
        item = masterTagLowModulus.objects.filter(item_no=item_no_row).first()
        if item:
            if(
            item.item_desc      != item_desc_row or
            item.spec           != spec_row or
            item.poc            != poc_row or
            item.tension        != tension_row or
            item.tension_plus   != tension_plus_row or
            item.tension_minus  != tension_minus_row or
            item.ride_out       != ride_out_row or
            item.ride_out_plus  != ride_out_plus_row or
            item.ride_out_minus != ride_out_minus_row or
            item.tipe_pulley    != tipe_pulley_row or
            item.pulley_diameter!= pulley_diameter_row or
            item.top_width      != top_width_row or
            item.top_width_plus != top_width_plus_row or
            item.top_width_minus!= top_width_minus_row or
            item.thickness      != thickness_row or
            item.thickness_plus != thickness_plus_row or
            item.thickness_minus!= thickness_minus_row or
            item.cpl100mm       != cpl100mm_row or
            item.cpl1round      != cpl1round_row or
            item.high_speed     != high_speed_row or
            item.low_speed      != low_speed_row or
            item.rpm            != rpm_row or
            item.is_doc         != is_doc_row 
            ):
                item.item_desc  = item_desc_row
                item.spec   = spec_row
                item.poc    = poc_row
                item.tension    = tension_row
                item.tension_plus   = tension_plus_row
                item.tension_minus  = tension_minus_row
                item.ride_out   = ride_out_row
                item.ride_out_plus  = ride_out_plus_row
                item.ride_out_minus = ride_out_minus_row
                item.tipe_pulley    = tipe_pulley_row
                item.pulley_diameter    = pulley_diameter_row
                item.top_width  = top_width_row
                item.top_width_plus = top_width_plus_row
                item.top_width_minus    = top_width_minus_row
                item.thickness  = thickness_row
                item.thickness_plus = thickness_plus_row
                item.thickness_minus    = thickness_minus_row
                item.cpl100mm   = cpl100mm_row
                item.cpl1round  = cpl1round_row
                item.high_speed = high_speed_row
                item.low_speed = low_speed_row
                item.rpm = rpm_row
                item.is_doc = is_doc_row
                updates.append(item)
        else:
            item_exists_in_creates = any(item.item_no == item_no_row for item in creates)
            if not item_exists_in_creates:
                creates.append(masterTagLowModulus(
                    item_no     = item_no_row,
                    item_desc       = item_desc_row,
                    spec        = spec_row,
                    poc     = poc_row,
                    tension     = tension_row,
                    tension_plus        = tension_plus_row,
                    tension_minus       = tension_minus_row,
                    ride_out        = ride_out_row,
                    ride_out_plus       = ride_out_plus_row,
                    ride_out_minus      = ride_out_minus_row,
                    tipe_pulley     = tipe_pulley_row,
                    pulley_diameter     = pulley_diameter_row,
                    top_width       = top_width_row,
                    top_width_plus      = top_width_plus_row,
                    top_width_minus     = top_width_minus_row,
                    thickness       = thickness_row,
                    thickness_plus      = thickness_plus_row,
                    thickness_minus     = thickness_minus_row,
                    cpl100mm        = cpl100mm_row,
                    cpl1round       = cpl1round_row,
                    high_speed       = high_speed_row,
                    low_speed       = low_speed_row,
                    rpm       = rpm_row,
                    is_doc       = is_doc_row
                ))
    if updates:
        masterTagLowModulus.objects.bulk_update(updates, ['item_no','item_desc','spec','poc','tension','tension_plus','tension_minus','ride_out','ride_out_plus','ride_out_minus','tipe_pulley','pulley_diameter','top_width','top_width_plus','top_width_minus','thickness','thickness_plus','thickness_minus','cpl100mm','cpl1round','high_speed','low_speed','rpm', 'is_doc'])
    if creates:
        masterTagLowModulus.objects.bulk_create(creates)
    return updates, creates

def UpdateMasterVL(request):
    # Check if a file was uploaded
    if 'file' not in request.FILES:
        return None, None

    # Get the uploaded file
    file = request.FILES['file']

    # Read CSV File
    csv_data = []
    try:
        for line in file:
            csv_data.append(line.decode('utf-8'))  # Decode bytes to string
    except UnicodeDecodeError:
        return None, None

    # Parse CSV data
    reader = csv.reader(csv_data)
    data = list(reader)

    updates = []  # For updating existing records
    creates = []  # For creating new records

    for item_no_row, item_desc_row, spec_row, poc_row, poc_lower_row, poc_upper_row, vib_row, run_out_row, tipe_pulley_row, pulley_diameter_row, weight_kg_row, weight_n_row, top_width_row, top_width_plus_row, top_width_minus_row, thickness_row, thickness_plus_row, thickness_minus_row, tipe_belt_row, *__ in data:
        item = masterTagVL.objects.filter(item_no=item_no_row).first()
        if tipe_belt_row == 'FALSE':
            tipe_belt_row = 'False'
        elif tipe_belt_row == 'TRUE':
            tipe_belt_row = 'True'
        else:
            tipe_belt_row = 'False'

        if item:
            # If the record exists, check if any field has changed
            if (
                item.item_desc != item_desc_row or
                item.spec != spec_row or
                item.poc != poc_row or
                item.poc_lower != poc_lower_row or
                item.poc_upper != poc_upper_row or
                item.vib != vib_row or
                item.run_out != run_out_row or
                item.tipe_pulley != tipe_pulley_row or
                item.pulley_diameter != pulley_diameter_row or
                item.weight_kg != weight_kg_row or
                item.weight_n != weight_n_row or
                item.top_width != top_width_row or
                item.top_width_plus != top_width_plus_row or
                item.top_width_minus != top_width_minus_row or
                item.thickness != thickness_row or
                item.thickness_plus != thickness_plus_row or
                item.thickness_minus != thickness_minus_row
            ):
                # If any field has changed, update its fields
                item.item_desc = item_desc_row
                item.spec = spec_row
                item.poc = poc_row
                item.poc_lower = poc_lower_row
                item.poc_upper = poc_upper_row
                item.vib = vib_row
                item.run_out = run_out_row
                item.tipe_pulley = tipe_pulley_row
                item.pulley_diameter = pulley_diameter_row
                item.weight_kg = weight_kg_row
                item.weight_n = weight_n_row
                item.top_width = top_width_row
                item.top_width_plus = top_width_plus_row
                item.top_width_minus = top_width_minus_row
                item.thickness = thickness_row
                item.thickness_plus = thickness_plus_row
                item.thickness_minus = thickness_minus_row
                item.tipe_belt = tipe_belt_row

                updates.append(item)
        else:
            # If the record does not exist, check if the item already exists in the creates list
            item_exists_in_creates = any(item.item_no == item_no_row for item in creates)
            if not item_exists_in_creates:
                # If the item does not exist in the creates list, append it
                creates.append(masterTagVL(
                    item_no=item_no_row,
                    item_desc=item_desc_row,
                    spec=spec_row,
                    poc=poc_row,
                    poc_lower=poc_lower_row,
                    poc_upper=poc_upper_row,
                    vib=vib_row,
                    run_out=run_out_row,
                    tipe_pulley=tipe_pulley_row,
                    pulley_diameter=pulley_diameter_row,
                    weight_kg=weight_kg_row,
                    weight_n=weight_n_row,
                    top_width=top_width_row,
                    top_width_plus=top_width_plus_row,
                    top_width_minus=top_width_minus_row,
                    thickness=thickness_row,
                    thickness_plus=thickness_plus_row,
                    thickness_minus=thickness_minus_row,
                    tipe_belt=tipe_belt_row,
                ))

    # Bulk update existing records
    if updates:
        masterTagVL.objects.bulk_update(updates, [
            'item_desc', 'spec', 'poc', 'poc_lower', 'poc_upper', 'vib',
            'run_out', 'tipe_pulley', 'pulley_diameter', 'weight_kg',
            'weight_n', 'top_width', 'top_width_plus', 'top_width_minus',
            'thickness', 'thickness_plus', 'thickness_minus', 'tipe_belt',
        ])

    # Bulk create new records
    if creates:
        masterTagVL.objects.bulk_create(creates)

    return updates, creates

def UpdateMasterMedical(request):
    # mari kita check apakah Filesnya di upload atau tidak
    if 'file' not in request.FILES:
        return None, None
    
    # mari kita dapatkan Upload File  dari yang form sudah ada
    file = request.FILES['file']

    # Mari kita baca csv file yang sudah ada
    csv_data = []
    try:
        for line in file:
            csv_data.append(line.decode('utf-8')) 
    except UnicodeDecodeError:
        return None, None
    
    # Mari kita parse CSV Data
    reader = csv.reader(csv_data)
    data = list(reader)

    updates = [] # jadi ini file file yang akan masuk kedalam Update
    creates = [] # jadi ini file fiel yang akan ke create 

    for username_row, marital_status_row, limit_row, used_row, remain_row, *__ in data:
        user_row = User.objects.filter(username__icontains=username_row).first()
        medical = medicalRemain.objects.filter(user=user_row).first()
        if medical:
            if(
            medical.user.username != username_row or
            medical.marital_status != marital_status_row or
            medical.limit != limit_row or
            medical.used != used_row or
            medical.remain != remain_row ):
                medical.user = user_row 
                medical.marital_status = marital_status_row
                medical.limit = limit_row
                medical.used = used_row
                medical.remain = remain_row
                updates.append(medical)
        else:
            # If the record does not exist, check if the item already exists in the creates list
            item_exists_in_creates = any(medical.user == user_row for medical in creates)
            if not item_exists_in_creates:
                # If the item does not exist in the creates list, append it
                creates.append(medicalRemain(
                    user=user_row,
                    marital_status=marital_status_row,
                    limit=limit_row,
                    used=used_row,
                    remain=remain_row,
 
                ))
        # Bulk update existing records
    if updates:
        medicalRemain.objects.bulk_update(updates, [
            'marital_status', 'limit', 'used', 'remain',
        ])

    # Bulk create new records
    if creates:
        medicalRemain.objects.bulk_create(creates)

    return updates,creates

# UPDATE END

import os

# VL START 

# UPLOAD START
def handle_uploaded_vlAttachment_file(file):
    # Specify the destination folder within your Django project's directory structure
    destination_folder = os.path.join(os.path.dirname(__file__), 'templates', 'csv')
    # Create the destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)
    
    # Rename the file to a custom name
    custom_name = 'updateMasterVL.csv'  # Provide your desired custom name here
    
    # Construct the file path where the uploaded file will be saved with the custom name
    file_path = os.path.join(destination_folder, custom_name)
    
    # Open the destination file in write-binary mode
    with open(file_path, 'wb') as destination:
        # Iterate over chunks of the uploaded file and write them to the destination file
        for chunk in file.chunks():
            destination.write(chunk)

def UploadMasterVL(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            handle_uploaded_vlAttachment_file(file)
            updates, creates = UpdateMasterVL(request)
            list_mastertag = masterTagVL.objects.all
            context = {
                'list_mastertags' : list_mastertag,
                'updated_items': updates,
                'created_items': creates,
            }
            return render(request, 'master_app/UploadMasterVL.html', context)
    else:
        list_mastertag = masterTagVL.objects.all
        context = {
            'list_mastertags' : list_mastertag,
        }
        return render(request, 'master_app/UploadMasterVL.html', context)

def handle_uploaded_LowModulusAttachment_file(file):
    destination_folder = os.path.join(os.path.dirname(__file__), 'templates', 'csv')
    os.makedirs(destination_folder, exist_ok=True)
    custom_name = 'updateMasterLowModulus'
    file_path = os.path.join(destination_folder,custom_name)
    with open(file_path, 'wb') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

def UploadMasterLowModulus(request):
    if request.method == "POST":
        file = request.FILES.get('file')
        if file:
            handle_uploaded_LowModulusAttachment_file(file)
            updates, creates = UpdateMasterLowModulus(request)
            list_mastertag = masterTagLowModulus.objects.all
            context = {
                'list_mastertags' : list_mastertag,
                'updated_items': updates,
                'created_items': creates,
            }
            return render(request, 'master_app/UploadMasterLowModulus.html', context)
    else:
        list_mastertag = masterTagLowModulus.objects.all
        context = {
            'list_mastertags' : list_mastertag,
        }
        return render(request, 'master_app/UploadMasterLowModulus.html', context)


# UPLOAD END

# DOWNLOAD START
def download_csv_mastervl(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="master_tag_vl.csv"'

    writer = csv.writer(response)
    writer.writerow(['id', 'item_no', 'item_desc', 'spec', 'poc', 'poc_lower', 'poc_upper', 'vib',
                     'run_out', 'tipe_pulley', 'pulley_diameter', 'weight_kg', 'weight_n', 'top_width',
                     'top_width_plus', 'top_width_minus', 'thickness', 'thickness_plus', 'thickness_minus',
                     'tipe_belt'])

    # Replace `YourModel` with the actual model name you are using for Master Tags
    master_tags = masterTagVL.objects.all()

    for tag in master_tags:
        writer.writerow([tag.id, tag.item_no, tag.item_desc, tag.spec, tag.poc, tag.poc_lower, tag.poc_upper,
                         tag.vib, tag.run_out, tag.tipe_pulley, tag.pulley_diameter, tag.weight_kg,
                         tag.weight_n, tag.top_width, tag.top_width_plus, tag.top_width_minus, tag.thickness,
                         tag.thickness_plus, tag.thickness_minus, tag.tipe_belt])

    return response

def download_csv_masterLowModulus(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="master_tag_LowModulus.csv"'

    writer = csv.writer(response)
    writer.writerow(['id','item_no','item_desc','spec','poc','tension','tension_plus','tension_minus','ride_out','ride_out_plus','ride_out_minus','tipe_pulley','pulley_diameter','top_width','top_width_plus','top_width_minus','thickness','thickness_plus','thickness_minus','cpl100mm','cpl1round','high_speed','low_speed','rpm', 'DOC'])

    # Replace `YourModel` with the actual model name you are using for Master Tags
    master_tags = masterTagLowModulus.objects.all()

    for tag in master_tags:
        writer.writerow([tag.id ,tag.item_no ,tag.item_desc ,tag.spec ,tag.poc ,tag.tension ,tag.tension_plus ,tag.tension_minus ,tag.ride_out ,tag.ride_out_plus ,tag.ride_out_minus ,tag.tipe_pulley ,tag.pulley_diameter ,tag.top_width ,tag.top_width_plus ,tag.top_width_minus ,tag.thickness ,tag.thickness_plus ,tag.thickness_minus ,tag.cpl100mm ,tag.cpl1round, tag.high_speed, tag.low_speed, tag.rpm, tag.is_doc])
    return response
# DOWNLOAD END

# VL END 

# MEDICAL START

# UPLOAD START
def handle_uploaded_medicalAttachment_file(file):
    # Specify the destination folder within your Django project's directory structure
    destination_folder = os.path.join(os.path.dirname(__file__), 'templates', 'csv')
    # Create the destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)
    
    # Rename the file to a custom name
    custom_name = 'updateMasterMedical.csv'  # Provide your desired custom name here
    
    # Construct the file path where the uploaded file will be saved with the custom name
    file_path = os.path.join(destination_folder, custom_name)
    
    # Open the destination file in write-binary mode
    with open(file_path, 'wb') as destination:
        # Iterate over chunks of the uploaded file and write them to the destination file
        for chunk in file.chunks():
            destination.write(chunk)

def UploadMasterMedical(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            handle_uploaded_medicalAttachment_file(file)
            updates, creates = UpdateMasterMedical(request)
            list_mastermedical = medicalRemain.objects.all
            context = {
                'list_mastermedicals' : list_mastermedical,
                'updated_items': updates,
                'created_items': creates,
            }
            return render(request, 'master_app/UploadMasterMedical.html', context)
    else:
        list_mastermedical = medicalRemain.objects.all
        context = {
            'list_mastermedicals' : list_mastermedical,
        }
        return render(request, 'master_app/UploadMasterMedical.html', context)
    
# UPLOAD END

# DOWNLOAD START
def download_csv_mastermedical(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="master_medicals.csv"'

    writer = csv.writer(response)
    writer.writerow(['id', 'username', 'marital_status', 'limit', 'used', 'remain'])

    # Replace `YourModel` with the actual model name you are using for Master Tags
    master_medicals = medicalRemain.objects.all()
    for tag in master_medicals:
        if tag.user:
            writer.writerow([tag.id, tag.user.username, tag.marital_status, tag.limit, tag.used, tag.remain])

    return response
# DOWNLOAD END

# MEDICAL END
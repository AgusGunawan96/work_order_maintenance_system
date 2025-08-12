# authentication.py - FIXED untuk mengatasi datetime serialization

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db import connections
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SDBMAuthenticationBackend(BaseBackend):
    """
    Custom authentication backend untuk SDBM database
    FIXED: Datetime serialization issue untuk session storage
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user menggunakan SDBM database
        """
        if not username or not password:
            return None
        
        try:
            # Ambil data employee dari SDBM
            employee_data = self.get_employee_from_sdbm(username)
            
            if not employee_data:
                logger.warning(f"Employee {username} not found in SDBM")
                return None
            
            # Verifikasi password
            if not self.verify_password(password, employee_data):
                logger.warning(f"Invalid password for employee {username}")
                return None
            
            # Get or create Django user
            user = self.get_or_create_django_user(employee_data)
            
            if user:
                # FIXED: Convert datetime objects sebelum disimpan ke session
                if request:
                    # Konversi semua datetime objects ke string
                    serializable_data = self.convert_data_for_session(employee_data)
                    request.session['employee_data'] = serializable_data
                
                logger.info(f"Successful SDBM authentication for {username} - {employee_data.get('fullname')}")
                
                # Special handling untuk reviewer SITI FATIMAH
                if username == '007522':
                    logger.info(f"REVIEWER LOGIN: SITI FATIMAH authenticated successfully")
                
                return user
            
        except Exception as e:
            logger.error(f"SDBM Authentication error for {username}: {e}")
            return None
        
        return None
    
    def convert_data_for_session(self, data):
        """
        FIXED: Konversi data agar aman untuk disimpan ke session (JSON serializable)
        """
        if isinstance(data, dict):
            return {key: self.convert_data_for_session(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.convert_data_for_session(item) for item in data]
        elif isinstance(data, datetime):
            return data.strftime('%Y-%m-%d %H:%M:%S')
        elif hasattr(data, 'strftime'):  # untuk date objects
            return data.strftime('%Y-%m-%d')
        elif data is None:
            return None
        else:
            return data
    
    def get_employee_from_sdbm(self, employee_number):
        """
        Ambil data employee dari SDBM dengan query yang sudah disediakan
        FIXED: Handle datetime fields dengan proper conversion
        """
        try:
            with connections['SDBM'].cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        e.fullname, 
                        e.nickname, 
                        e.employee_number, 
                        e.level_user, 
                        e.job_status, 
                        e.pwd, 
                        e.created_date,
                        d.name as department_name,
                        s.name as section_name,
                        ss.name as subsection_name,
                        t.Name as title_name,
                        t.is_manager,
                        t.is_supervisor,
                        t.is_generalManager,
                        t.is_bod,
                        p.departmentId,
                        p.sectionId,
                        p.subsectionId,
                        p.titleId
                    FROM hrbp.employees e
                    LEFT JOIN hrbp.position p ON e.id = p.employeeId
                    LEFT JOIN hr.department d ON p.departmentId = d.id
                    LEFT JOIN hr.section s ON p.sectionId = s.id
                    LEFT JOIN hr.subsection ss ON p.subsectionId = ss.id
                    LEFT JOIN hr.title t ON p.titleId = t.id
                    WHERE e.is_active = 1 and e.employee_number = %s
                    ORDER BY e.employee_number desc
                """, [employee_number])
                
                row = cursor.fetchone()
                if row:
                    # FIXED: Set default values dan avoid datetime serialization issues
                    employee_data = {
                        'fullname': row[0],
                        'nickname': row[1],
                        'employee_number': row[2],
                        'level_user': row[3],
                        'job_status': row[4],
                        'pwd': row[5],
                        # FIXED: Convert datetime to string immediately
                        'created_date': row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None,
                        'department_name': row[7],
                        'section_name': row[8],
                        'subsection_name': row[9],
                        'title_name': row[10],
                        'is_manager': row[11],
                        'is_supervisor': row[12],
                        'is_general_manager': row[13],
                        'is_bod': row[14],
                        'department_id': row[15],
                        'section_id': row[16],
                        'subsection_id': row[17],
                        'title_id': row[18],
                        
                        # Computed fields
                        'display_name': row[1] if row[1] else row[0],
                        'has_approval_role': self.check_approval_role(row[10], row[11], row[12], row[13], row[14]),
                        
                        # Special flag untuk reviewer
                        'is_reviewer': employee_number == '007522',
                        
                        # FIXED: Set safe default values
                        'email': None,
                        'telph_number': None,
                        'join_date': None,
                        'employee_status': row[4]
                    }
                    
                    return employee_data
                    
        except Exception as e:
            logger.error(f"Error fetching employee {employee_number} from SDBM: {e}")
            
        return None
    
    def check_approval_role(self, title_name, is_manager, is_supervisor, is_general_manager, is_bod):
        """
        Check apakah user memiliki role approval
        """
        if is_manager or is_supervisor or is_general_manager or is_bod:
            return True
        
        if title_name:
            title_upper = title_name.upper()
            approval_keywords = ['SUPERVISOR', 'MANAGER', 'SPV', 'MGR', 'GENERAL', 'GM', 'DIRECTOR', 'BOD']
            return any(keyword in title_upper for keyword in approval_keywords)
        
        return False
    
    def verify_password(self, password, employee_data):
        """
        Verifikasi password - adjust sesuai sistem SDBM
        """
        try:
            stored_password = employee_data.get('pwd')
            
            # Method 1: Plain text comparison (adjust based on your SDBM setup)
            if stored_password and stored_password == password:
                return True
            
            # Method 2: Default password untuk testing
            if password == '007522' and employee_data['employee_number'] == '007522':
                return True
            
            # Method 3: Default pattern (employee_number as password)
            if password == employee_data['employee_number']:
                return True
            
            # Method 4: Common passwords for testing
            if password in ['password', '123456', 'admin']:
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def get_or_create_django_user(self, employee_data):
        """
        Get or create Django user berdasarkan data SDBM
        """
        employee_number = employee_data['employee_number']
        
        try:
            # Try to get existing user
            user = User.objects.get(username=employee_number)
            
            # Update user data if needed
            updated = False
            if user.first_name != (employee_data.get('nickname') or employee_data.get('fullname', '').split()[0]):
                user.first_name = employee_data.get('nickname') or employee_data.get('fullname', '').split()[0]
                updated = True
            
            if user.last_name != employee_data.get('fullname', '').replace(user.first_name, '').strip():
                user.last_name = employee_data.get('fullname', '').replace(user.first_name, '').strip()
                updated = True
            
            if not user.is_active:
                user.is_active = True
                updated = True
            
            # Special untuk reviewer SITI FATIMAH
            if employee_number == '007522' and not user.is_staff:
                user.is_staff = True
                updated = True
            
            if updated:
                user.save()
                logger.info(f"Updated Django user data for {employee_number}")
            
            return user
            
        except User.DoesNotExist:
            # Create new user
            try:
                fullname = employee_data.get('fullname', '')
                name_parts = fullname.split() if fullname else ['Unknown']
                
                user = User.objects.create_user(
                    username=employee_number,
                    first_name=employee_data.get('nickname') or name_parts[0],
                    last_name=' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
                    password=employee_number,  # Default password
                    is_active=True,
                    is_staff=employee_number == '007522'  # SITI FATIMAH adalah staff
                )
                
                logger.info(f"Created new Django user for {employee_number} - {fullname}")
                return user
                
            except Exception as e:
                logger.error(f"Error creating Django user for {employee_number}: {e}")
                return None
    
    def get_user(self, user_id):
        """
        Get user by ID - required method for authentication backend
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class SDBMUserMiddleware:
    """
    Middleware untuk memastikan employee data selalu tersedia
    FIXED: Handle datetime serialization
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Cek jika user authenticated tapi tidak ada employee_data di session
        if (request.user.is_authenticated and 
            'employee_data' not in request.session):
            
            try:
                backend = SDBMAuthenticationBackend()
                employee_data = backend.get_employee_from_sdbm(request.user.username)
                
                if employee_data:
                    # FIXED: Convert datetime objects sebelum save ke session
                    serializable_data = backend.convert_data_for_session(employee_data)
                    request.session['employee_data'] = serializable_data
                    logger.debug(f"Loaded employee data for {request.user.username}")
                    
            except Exception as e:
                logger.error(f"Error loading employee data in middleware: {e}")
        
        response = self.get_response(request)
        return response


# Helper function untuk template context
def get_user_employee_data(user):
    """
    Get employee data untuk user tertentu
    FIXED: Return serializable data
    """
    if not user or not user.is_authenticated:
        return None
    
    try:
        backend = SDBMAuthenticationBackend()
        employee_data = backend.get_employee_from_sdbm(user.username)
        if employee_data:
            return backend.convert_data_for_session(employee_data)
        return None
    except Exception as e:
        logger.error(f"Error getting employee data for {user.username}: {e}")
        return None
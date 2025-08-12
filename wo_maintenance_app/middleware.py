# wo_maintenance_app/middleware.py - Employee Data Session Middleware
import logging
from django.utils.deprecation import MiddlewareMixin
from wo_maintenance_app.utils import get_employee_hierarchy_data

logger = logging.getLogger(__name__)

class EmployeeDataMiddleware(MiddlewareMixin):
    """
    Middleware untuk memastikan employee_data ada di session untuk setiap authenticated user
    """
    
    def process_request(self, request):
        """
        Process request untuk menambahkan employee_data ke session jika user authenticated
        """
        # Skip jika user tidak authenticated
        if not request.user.is_authenticated:
            return None
        
        # Skip jika employee_data sudah ada di session
        if 'employee_data' in request.session and request.session['employee_data']:
            return None
        
        # Skip untuk AJAX requests dan debug endpoints
        if request.is_ajax() or '/debug/' in request.path or '/api/' in request.path:
            return None
        
        try:
            # Ambil employee hierarchy data
            employee_data = get_employee_hierarchy_data(request.user)
            
            if employee_data:
                # Simpan ke session
                request.session['employee_data'] = employee_data
                logger.info(f"Employee data loaded for user {request.user.username}: {employee_data.get('fullname')}")
            else:
                # Log warning jika employee data tidak ditemukan
                logger.warning(f"Employee data not found for user {request.user.username}")
                # Set empty dict untuk mencegah repeated queries
                request.session['employee_data'] = {}
                
        except Exception as e:
            logger.error(f"Error loading employee context for user {request.user.username}: {e}")
            # Set empty dict untuk mencegah repeated queries
            request.session['employee_data'] = {}
        
        return None
    
    def process_response(self, request, response):
        """
        Process response - no action needed
        """
        return response
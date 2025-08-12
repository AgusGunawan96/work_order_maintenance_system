# wo_maintenance_app/routers.py
"""
Database router untuk WO Maintenance System
Mengatur routing query ke database yang tepat
"""

class WOMaintenanceRouter:
    """
    Router untuk mengatur database connections untuk WO Maintenance
    - SDBM: untuk data karyawan dan hierarki
    - DB_Maintenance: untuk data work order
    - default: untuk data aplikasi lainnya
    """
    
    def __init__(self):
        self.wo_models = {
            'wo_maintenance_app',
        }
        
        self.sdbm_tables = {
            'employees', 'position', 'department', 'section', 
            'subsection', 'title'
        }
        
        self.maintenance_tables = {
            'tabel_pengajuan', 'tabel_mesin', 'tabel_line', 
            'tabel_msection', 'tabel_pekerjaan', 'tabel_wo_activity_log'
        }
    
    def db_for_read(self, model, **hints):
        """Suggest the database to read from."""
        
        # Jika ada hint instance, cek dari instance tersebut
        if hints.get('instance'):
            instance = hints['instance']
            if hasattr(instance, '_state') and hasattr(instance._state, 'db'):
                return instance._state.db
        
        # Routing berdasarkan model
        if model._meta.app_label in self.wo_models:
            # Model WO Maintenance menggunakan default database
            return 'default'
        
        # Default routing
        return None
    
    def db_for_write(self, model, **hints):
        """Suggest the database to write to."""
        
        # Jika ada hint instance, cek dari instance tersebut
        if hints.get('instance'):
            instance = hints['instance']
            if hasattr(instance, '_state') and hasattr(instance._state, 'db'):
                return instance._state.db
        
        # Routing berdasarkan model
        if model._meta.app_label in self.wo_models:
            # Model WO Maintenance menggunakan default database
            return 'default'
        
        # Default routing
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same app."""
        
        # Allow relations within the same database
        db_set = {'default', 'SDBM', 'DB_Maintenance'}
        
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that certain models get created on the right database."""
        
        # WO Maintenance app models
        if app_label in self.wo_models:
            return db == 'default'
        
        # Models lain
        if db in ['SDBM', 'DB_Maintenance']:
            return False
        
        return db == 'default'


class QueryRouter:
    """
    Helper class untuk menentukan database connection berdasarkan query
    """
    
    @staticmethod
    def get_connection_for_table(table_name):
        """Determine which database connection to use for a table"""
        
        sdbm_tables = {
            'hrbp.employees', 'hrbp.position', 'hr.department', 
            'hr.section', 'hr.subsection', 'hr.title'
        }
        
        maintenance_tables = {
            'tabel_pengajuan', 'tabel_mesin', 'tabel_line',
            'tabel_msection', 'tabel_pekerjaan', 'tabel_wo_activity_log'
        }
        
        if any(table_name.startswith(table) for table in sdbm_tables):
            return 'SDBM'
        elif table_name in maintenance_tables:
            return 'DB_Maintenance'
        else:
            return 'default'
    
    @staticmethod
    def execute_query(query, params=None, database=None):
        """Execute query with proper database connection"""
        from django.db import connections
        
        if database is None:
            database = 'default'
        
        try:
            with connections[database].cursor() as cursor:
                cursor.execute(query, params or [])
                
                # Determine if it's a SELECT query
                query_upper = query.strip().upper()
                if query_upper.startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    return cursor.rowcount
                    
        except Exception as e:
            import logging
            logger = logging.getLogger('wo_maintenance_app')
            logger.error(f"Query execution error on {database}: {e}")
            raise


class DatabaseManager:
    """
    Manager class untuk operasi database WO Maintenance
    """
    
    def __init__(self):
        self.router = QueryRouter()
    
    def get_employee_data(self, employee_number):
        """Get employee data from SDBM"""
        query = """
            SELECT 
                e.id, e.fullname, e.nickname, e.employee_number,
                e.level_user, e.employee_status, e.email,
                p.departmentId, p.sectionId, p.subsectionId, p.titleId,
                d.name as department_name, s.name as section_name,
                sub.name as subsection_name, t.Name as title_name,
                t.is_supervisor, t.is_manager, t.is_generalManager, t.is_bod
            FROM hrbp.employees e
            LEFT JOIN hrbp.position p ON e.id = p.employeeId AND p.is_active = 1
            LEFT JOIN hr.department d ON p.departmentId = d.id
            LEFT JOIN hr.section s ON p.sectionId = s.id
            LEFT JOIN hr.subsection sub ON p.subsectionId = sub.id
            LEFT JOIN hr.title t ON p.titleId = t.id
            WHERE e.employee_number = %s AND e.is_active = 1
        """
        
        result = self.router.execute_query(query, [employee_number], 'SDBM')
        return result[0] if result else None
    
    def get_wo_list(self, filters=None, limit=None, offset=None):
        """Get WO list from DB_Maintenance"""
        
        base_query = """
            SELECT 
                tp.history_id, tp.oleh, tm.mesin, ts.seksi,
                tkj.pekerjaan, tp.deskripsi_perbaikan, tp.status,
                tp.tgl_insert, tp.number_wo, tl.line
            FROM tabel_pengajuan tp
            LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
            LEFT JOIN tabel_msection ts ON tp.id_section = ts.id_section
            LEFT JOIN tabel_pekerjaan tkj ON tp.id_pekerjaan = tkj.id_pekerjaan
            LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
            WHERE tp.history_id IS NOT NULL
        """
        
        params = []
        
        # Apply filters
        if filters:
            if filters.get('status'):
                base_query += " AND tp.status = %s"
                params.append(filters['status'])
            
            if filters.get('date_from'):
                base_query += " AND CAST(tp.tgl_insert AS DATE) >= %s"
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                base_query += " AND CAST(tp.tgl_insert AS DATE) <= %s"
                params.append(filters['date_to'])
            
            if filters.get('pengaju'):
                base_query += " AND tp.oleh LIKE %s"
                params.append(f"%{filters['pengaju']}%")
        
        base_query += " ORDER BY tp.tgl_insert DESC"
        
        # Apply pagination
        if limit:
            base_query += f" OFFSET {offset or 0} ROWS FETCH NEXT {limit} ROWS ONLY"
        
        return self.router.execute_query(base_query, params, 'DB_Maintenance')
    
    def get_wo_detail(self, history_id):
        """Get WO detail from DB_Maintenance"""
        
        query = """
            SELECT 
                tp.history_id, tp.tgl_his, tp.jam_his, tp.oleh,
                tm.mesin, ts.seksi, tkj.pekerjaan, tp.deskripsi_perbaikan,
                tp.status, tp.approve, tp.number_wo, tp.user_insert,
                tp.tgl_insert, tl.line, tp.id_mesin, tp.id_section,
                tp.id_pekerjaan, tp.id_line
            FROM tabel_pengajuan tp
            LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
            LEFT JOIN tabel_msection ts ON tp.id_section = ts.id_section
            LEFT JOIN tabel_pekerjaan tkj ON tp.id_pekerjaan = tkj.id_pekerjaan
            LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
            WHERE tp.history_id = %s
        """
        
        result = self.router.execute_query(query, [history_id], 'DB_Maintenance')
        return result[0] if result else None
    
    def update_wo_status(self, history_id, status, approve_status, description=None):
        """Update WO status in DB_Maintenance"""
        
        if description:
            query = """
                UPDATE tabel_pengajuan 
                SET status = %s, approve = %s, deskripsi_perbaikan = %s
                WHERE history_id = %s
            """
            params = [status, approve_status, description, history_id]
        else:
            query = """
                UPDATE tabel_pengajuan 
                SET status = %s, approve = %s
                WHERE history_id = %s
            """
            params = [status, approve_status, history_id]
        
        return self.router.execute_query(query, params, 'DB_Maintenance')
    
    def log_activity(self, activity_data):
        """Log activity to database"""
        
        query = """
            INSERT INTO tabel_wo_activity_log 
            (history_id, user_id, action, details, timestamp, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = [
            activity_data.get('history_id'),
            activity_data.get('user_id'),
            activity_data.get('action'),
            activity_data.get('details'),
            activity_data.get('timestamp'),
            activity_data.get('ip_address')
        ]
        
        try:
            return self.router.execute_query(query, params, 'DB_Maintenance')
        except Exception as e:
            # Table might not exist, just log the error
            import logging
            logger = logging.getLogger('wo_maintenance_app')
            logger.warning(f"Could not log activity: {e}")
            return 0
    
    def get_dashboard_stats(self, employee_data=None):
        """Get dashboard statistics"""
        
        stats = {}
        
        # Basic stats
        query = "SELECT COUNT(*) FROM tabel_pengajuan WHERE history_id IS NOT NULL"
        result = self.router.execute_query(query, [], 'DB_Maintenance')
        stats['total_wo'] = result[0][0] if result else 0
        
        # Status breakdown
        query = """
            SELECT status, COUNT(*) 
            FROM tabel_pengajuan 
            WHERE history_id IS NOT NULL
            GROUP BY status
        """
        result = self.router.execute_query(query, [], 'DB_Maintenance')
        stats['status_breakdown'] = {str(row[0]): row[1] for row in result} if result else {}
        
        # Recent WO for approval (if user is approver)
        if employee_data and (employee_data.get('is_supervisor') or employee_data.get('is_manager')):
            query = """
                SELECT TOP 5 
                    tp.history_id, tm.mesin, tp.oleh, tp.status, 
                    tp.tgl_insert, tl.line, tp.deskripsi_perbaikan
                FROM tabel_pengajuan tp
                LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
                LEFT JOIN tabel_line tl ON tp.id_line = tl.id_line
                WHERE tp.status = '0' AND tp.history_id IS NOT NULL
                    AND tp.oleh != %s
                ORDER BY tp.tgl_insert ASC
            """
            result = self.router.execute_query(
                query, 
                [employee_data.get('fullname', '')], 
                'DB_Maintenance'
            )
            stats['pending_approval'] = result if result else []
        
        return stats
    
    def cleanup_old_logs(self, retention_days=90):
        """Cleanup old activity logs"""
        
        query = """
            DELETE FROM tabel_wo_activity_log 
            WHERE timestamp < DATEADD(day, -%s, GETDATE())
        """
        
        try:
            return self.router.execute_query(query, [retention_days], 'DB_Maintenance')
        except Exception as e:
            import logging
            logger = logging.getLogger('wo_maintenance_app')
            logger.warning(f"Could not cleanup logs: {e}")
            return 0


# Singleton instance
db_manager = DatabaseManager()
# wo_maintenance_app/management/commands/wo_health_check.py
from django.core.management.base import BaseCommand
from django.db import connections
from django.conf import settings
import logging

logger = logging.getLogger('wo_maintenance_app')

class Command(BaseCommand):
    help = 'Perform health check on WO Maintenance system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix issues found',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting WO Maintenance health check...'))
        
        issues = []
        
        # Check database connections
        issues.extend(self.check_database_connections())
        
        # Check required tables
        issues.extend(self.check_required_tables())
        
        # Check data consistency
        issues.extend(self.check_data_consistency())
        
        # Check system configuration
        issues.extend(self.check_system_configuration())
        
        # Check permissions
        issues.extend(self.check_permissions())
        
        # Report results
        if not issues:
            self.stdout.write(self.style.SUCCESS('✅ All health checks passed!'))
        else:
            self.stdout.write(self.style.WARNING(f'Found {len(issues)} issues:'))
            for i, issue in enumerate(issues, 1):
                self.stdout.write(f"  {i}. {issue}")
            
            if options['fix']:
                self.attempt_fixes(issues)
    
    def check_database_connections(self):
        """Check database connections"""
        issues = []
        
        required_dbs = ['default', 'SDBM', 'DB_Maintenance']
        
        for db_name in required_dbs:
            try:
                with connections[db_name].cursor() as cursor:
                    cursor.execute("SELECT 1")
                self.stdout.write(f"✅ Database {db_name}: OK")
            except Exception as e:
                issue = f"❌ Database {db_name}: {e}"
                issues.append(issue)
                self.stdout.write(self.style.ERROR(issue))
        
        return issues
    
    def check_required_tables(self):
        """Check required tables exist"""
        issues = []
        
        # SDBM tables
        sdbm_tables = [
            'hrbp.employees', 'hrbp.position', 'hr.department',
            'hr.section', 'hr.subsection', 'hr.title'
        ]
        
        for table in sdbm_tables:
            try:
                with connections['SDBM'].cursor() as cursor:
                    cursor.execute(f"SELECT TOP 1 1 FROM {table}")
                self.stdout.write(f"✅ SDBM Table {table}: OK")
            except Exception as e:
                issue = f"❌ SDBM Table {table}: {e}"
                issues.append(issue)
                self.stdout.write(self.style.ERROR(issue))
        
        # DB_Maintenance tables
        maintenance_tables = [
            'tabel_pengajuan', 'tabel_mesin', 'tabel_line',
            'tabel_msection', 'tabel_pekerjaan'
        ]
        
        for table in maintenance_tables:
            try:
                with connections['DB_Maintenance'].cursor() as cursor:
                    cursor.execute(f"SELECT TOP 1 1 FROM {table}")
                self.stdout.write(f"✅ Maintenance Table {table}: OK")
            except Exception as e:
                issue = f"❌ Maintenance Table {table}: {e}"
                issues.append(issue)
                self.stdout.write(self.style.ERROR(issue))
        
        return issues
    
    def check_data_consistency(self):
        """Check data consistency"""
        issues = []
        
        try:
            # Check for orphaned WO records
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM tabel_pengajuan tp
                    LEFT JOIN tabel_mesin tm ON tp.id_mesin = tm.id_mesin
                    WHERE tp.history_id IS NOT NULL AND tm.id_mesin IS NULL
                """)
                
                orphaned_count = cursor.fetchone()[0]
                if orphaned_count > 0:
                    issue = f"❌ Found {orphaned_count} WO records with invalid mesin references"
                    issues.append(issue)
                    self.stdout.write(self.style.WARNING(issue))
                else:
                    self.stdout.write("✅ WO-Mesin relationships: OK")
                
                # Check for duplicate history_id
                cursor.execute("""
                    SELECT history_id, COUNT(*) 
                    FROM tabel_pengajuan 
                    WHERE history_id IS NOT NULL
                    GROUP BY history_id 
                    HAVING COUNT(*) > 1
                """)
                
                duplicates = cursor.fetchall()
                if duplicates:
                    issue = f"❌ Found {len(duplicates)} duplicate history_id records"
                    issues.append(issue)
                    self.stdout.write(self.style.ERROR(issue))
                else:
                    self.stdout.write("✅ History ID uniqueness: OK")
                    
        except Exception as e:
            issue = f"❌ Data consistency check failed: {e}"
            issues.append(issue)
            self.stdout.write(self.style.ERROR(issue))
        
        return issues
    
    def check_system_configuration(self):
        """Check system configuration"""
        issues = []
        
        # Check middleware
        middleware = getattr(settings, 'MIDDLEWARE', [])
        required_middleware = [
            'wo_maintenance_app.middleware.SDBMSessionMiddleware',
            'wo_maintenance_app.middleware.WOMaintenancePermissionMiddleware'
        ]
        
        for mw in required_middleware:
            if mw not in middleware:
                issue = f"❌ Missing middleware: {mw}"
                issues.append(issue)
                self.stdout.write(self.style.WARNING(issue))
            else:
                self.stdout.write(f"✅ Middleware {mw}: OK")
        
        # Check WO settings
        wo_settings = getattr(settings, 'WO_MAINTENANCE_SETTINGS', {})
        if not wo_settings:
            issue = "❌ WO_MAINTENANCE_SETTINGS not configured"
            issues.append(issue)
            self.stdout.write(self.style.WARNING(issue))
        else:
            self.stdout.write("✅ WO_MAINTENANCE_SETTINGS: OK")
        
        return issues
    
    def check_permissions(self):
        """Check file and directory permissions"""
        issues = []
        
        import os
        
        # Check log directory
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
                self.stdout.write(f"✅ Created log directory: {log_dir}")
            except Exception as e:
                issue = f"❌ Cannot create log directory: {e}"
                issues.append(issue)
                self.stdout.write(self.style.ERROR(issue))
        else:
            if os.access(log_dir, os.W_OK):
                self.stdout.write(f"✅ Log directory writable: {log_dir}")
            else:
                issue = f"❌ Log directory not writable: {log_dir}"
                issues.append(issue)
                self.stdout.write(self.style.ERROR(issue))
        
        return issues
    
    def attempt_fixes(self, issues):
        """Attempt to fix issues automatically"""
        self.stdout.write(self.style.SUCCESS('\nAttempting automatic fixes...'))
        
        fixed_count = 0
        
        for issue in issues:
            if 'log directory' in issue.lower():
                try:
                    import os
                    os.makedirs('logs', exist_ok=True)
                    os.chmod('logs', 0o755)
                    self.stdout.write(f"✅ Fixed: {issue}")
                    fixed_count += 1
                except Exception as e:
                    self.stdout.write(f"❌ Could not fix: {issue} - {e}")
        
        self.stdout.write(f"\n🔧 Fixed {fixed_count} out of {len(issues)} issues")
        self.stdout.write("⚠️  Some issues may require manual intervention")

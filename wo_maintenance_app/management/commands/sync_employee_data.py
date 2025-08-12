# wo_maintenance_app/management/__init__.py
# Empty file

# wo_maintenance_app/management/commands/__init__.py
# Empty file

# wo_maintenance_app/management/commands/sync_employee_data.py
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.contrib.auth.models import User
import logging

logger = logging.getLogger('wo_maintenance_app')

class Command(BaseCommand):
    help = 'Sync employee data from SDBM to local cache for WO system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--employee-number',
            type=str,
            help='Sync specific employee by number',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sync even if data exists',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without actually syncing',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting employee data sync...'))
        
        try:
            if options['employee_number']:
                self.sync_single_employee(options['employee_number'], options['dry_run'])
            else:
                self.sync_all_employees(options['force'], options['dry_run'])
                
        except Exception as e:
            logger.error(f"Employee sync error: {e}")
            raise CommandError(f"Sync failed: {e}")
    
    def sync_single_employee(self, employee_number, dry_run=False):
        """Sync single employee data"""
        
        self.stdout.write(f"Syncing employee: {employee_number}")
        
        try:
            with connections['SDBM'].cursor() as cursor:
                cursor.execute("""
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
                """, [employee_number])
                
                result = cursor.fetchone()
                
                if result:
                    if not dry_run:
                        # Create or update User if not exists
                        user, created = User.objects.get_or_create(
                            username=employee_number,
                            defaults={
                                'first_name': result[1] or '',
                                'email': result[6] or '',
                                'is_active': True
                            }
                        )
                        
                        if created:
                            user.set_password(employee_number)  # Default password
                            user.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"{'[DRY RUN] ' if dry_run else ''}Successfully synced: {result[1]} ({employee_number})"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Employee {employee_number} not found in SDBM")
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to sync {employee_number}: {e}")
            )
    
    def sync_all_employees(self, force=False, dry_run=False):
        """Sync all active employees"""
        
        self.stdout.write("Syncing all active employees...")
        
        try:
            with connections['SDBM'].cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT e.employee_number, e.fullname
                    FROM hrbp.employees e
                    INNER JOIN hrbp.position p ON e.id = p.employeeId
                    WHERE e.is_active = 1 AND p.is_active = 1
                    ORDER BY e.fullname
                """)
                
                employees = cursor.fetchall()
                
                self.stdout.write(f"Found {len(employees)} active employees")
                
                synced_count = 0
                skipped_count = 0
                
                for emp_number, emp_name in employees:
                    try:
                        # Check if user already exists
                        if not force and User.objects.filter(username=emp_number).exists():
                            skipped_count += 1
                            continue
                        
                        self.sync_single_employee(emp_number, dry_run)
                        synced_count += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Failed to sync {emp_name} ({emp_number}): {e}")
                        )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{'[DRY RUN] ' if dry_run else ''}Sync completed: {synced_count} synced, {skipped_count} skipped"
                    )
                )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Bulk sync failed: {e}"))
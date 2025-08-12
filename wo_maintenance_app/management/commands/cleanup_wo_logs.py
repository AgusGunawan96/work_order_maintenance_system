# wo_maintenance_app/management/commands/cleanup_wo_logs.py
from django.core.management.base import BaseCommand
from django.db import connections
from django.conf import settings
import logging

logger = logging.getLogger('wo_maintenance_app')

class Command(BaseCommand):
    help = 'Cleanup old WO activity logs and optimize database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--retention-days',
            type=int,
            default=getattr(settings, 'WO_MAINTENANCE_SETTINGS', {}).get('ACTIVITY_LOG_RETENTION_DAYS', 90),
            help='Number of days to retain logs (default: 90)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned without actually cleaning',
        )
    
    def handle(self, *args, **options):
        retention_days = options['retention_days']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(
                f"{'[DRY RUN] ' if dry_run else ''}Starting cleanup of logs older than {retention_days} days..."
            )
        )
        
        try:
            # Cleanup activity logs
            self.cleanup_activity_logs(retention_days, dry_run)
            
            # Cleanup session data
            self.cleanup_session_data(dry_run)
            
            # Cleanup cache
            self.cleanup_cache(dry_run)
            
            self.stdout.write(self.style.SUCCESS('Cleanup completed successfully'))
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            self.stdout.write(self.style.ERROR(f"Cleanup failed: {e}"))
    
    def cleanup_activity_logs(self, retention_days, dry_run=False):
        """Cleanup old activity logs"""
        
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Check how many records would be deleted
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM tabel_wo_activity_log 
                    WHERE timestamp < DATEADD(day, -%s, GETDATE())
                """, [retention_days])
                
                count = cursor.fetchone()[0] if cursor.fetchone() else 0
                
                if count > 0:
                    self.stdout.write(f"Found {count} old activity log records")
                    
                    if not dry_run:
                        cursor.execute("""
                            DELETE FROM tabel_wo_activity_log 
                            WHERE timestamp < DATEADD(day, -%s, GETDATE())
                        """, [retention_days])
                        
                        self.stdout.write(
                            self.style.SUCCESS(f"Deleted {count} old activity log records")
                        )
                    else:
                        self.stdout.write(f"[DRY RUN] Would delete {count} activity log records")
                else:
                    self.stdout.write("No old activity logs found")
                    
        except Exception as e:
            # Table might not exist
            self.stdout.write(self.style.WARNING(f"Could not cleanup activity logs: {e}"))
    
    def cleanup_session_data(self, dry_run=False):
        """Cleanup expired sessions"""
        
        try:
            from django.contrib.sessions.models import Session
            from django.utils import timezone
            
            expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
            count = expired_sessions.count()
            
            if count > 0:
                self.stdout.write(f"Found {count} expired sessions")
                
                if not dry_run:
                    expired_sessions.delete()
                    self.stdout.write(
                        self.style.SUCCESS(f"Deleted {count} expired sessions")
                    )
                else:
                    self.stdout.write(f"[DRY RUN] Would delete {count} expired sessions")
            else:
                self.stdout.write("No expired sessions found")
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not cleanup sessions: {e}"))
    
    def cleanup_cache(self, dry_run=False):
        """Clear WO maintenance cache"""
        
        try:
            from django.core.cache import cache
            
            # Clear specific WO cache keys
            cache_keys = [
                'wo_employee_data_*',
                'wo_dashboard_stats_*',
                'wo_approval_queue_*'
            ]
            
            if not dry_run:
                cache.clear()
                self.stdout.write(self.style.SUCCESS("Cache cleared"))
            else:
                self.stdout.write("[DRY RUN] Would clear cache")
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not clear cache: {e}"))
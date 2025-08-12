# management/commands/clear_sessions.py
# Buat file ini di: master_app/management/commands/clear_sessions.py
# Direktori structure: master_app/management/__init__.py dan master_app/management/commands/__init__.py

from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.db import connections
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clear all sessions to fix datetime serialization issues'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS('=== CLEARING SESSIONS untuk fix datetime serialization ==='))
        
        try:
            # Count current sessions
            session_count = Session.objects.count()
            
            if session_count == 0:
                self.stdout.write(self.style.SUCCESS('✅ No sessions found to clear.'))
                return
            
            self.stdout.write(f"Found {session_count} sessions to clear.")
            
            if dry_run:
                self.stdout.write(self.style.WARNING('DRY RUN - Would delete all sessions'))
                return
            
            if not force:
                confirm = input(f"Are you sure you want to delete {session_count} sessions? (y/N): ")
                if confirm.lower() != 'y':
                    self.stdout.write('Operation cancelled.')
                    return
            
            # Clear all sessions
            deleted_count = Session.objects.all().delete()[0]
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully deleted {deleted_count} sessions')
            )
            
            # Optional: Also clear cache if using cache sessions
            try:
                from django.core.cache import cache
                cache.clear()
                self.stdout.write('✅ Cache cleared as well')
            except:
                self.stdout.write('ℹ️  Cache clear skipped (not configured or error)')
            
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('SESSION CLEAR COMPLETED!'))
            self.stdout.write('Next steps:')
            self.stdout.write('1. All users akan auto-logout')
            self.stdout.write('2. Login ulang dengan employee number 007522')
            self.stdout.write('3. Test apakah error datetime sudah hilang')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error clearing sessions: {e}')
            )


# USAGE:
# python manage.py clear_sessions --dry-run  # Preview
# python manage.py clear_sessions --force     # Execute
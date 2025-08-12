# wo_maintenance_app/signals.py
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import Count, Q
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Import models
from wo_maintenance_app.models import (
    TabelPengajuan, TabelPengajuanAssignment, 
    MaintenanceStatistics, TabelReviewLog, TabelApprovalLog
)

@receiver(post_save, sender=TabelPengajuan)
def update_statistics_on_pengajuan_save(sender, instance, created, **kwargs):
    """Update statistics when pengajuan is saved"""
    try:
        if instance.tgl_insert:
            date = instance.tgl_insert.date()
            
            # Calculate stats for the date
            stats = TabelPengajuan.objects.filter(
                tgl_insert__date=date
            ).aggregate(
                total=Count('id_pengajuan'),
                pending=Count('id_pengajuan', filter=Q(status='0')),
                approved=Count('id_pengajuan', filter=Q(status='1')),
                completed=Count('id_pengajuan', filter=Q(status='4')),
                pending_review=Count('id_pengajuan', filter=Q(
                    status='1', 
                    approve='1', 
                    review_status__in=['0', None]
                ))
            )
            
            # Get active assignments count for the date
            try:
                active_assignments = TabelPengajuanAssignment.objects.filter(
                    assignment_date__date=date,
                    is_active=True
                ).count()
            except Exception as e:
                logger.warning(f"Could not get assignment count: {e}")
                active_assignments = 0
            
            # Update or create statistics
            MaintenanceStatistics.objects.update_or_create(
                date=date,
                defaults={
                    'total_pengajuan': stats['total'] or 0,
                    'pending_pengajuan': stats['pending'] or 0,
                    'approved_pengajuan': stats['approved'] or 0,
                    'completed_pengajuan': stats['completed'] or 0,
                    'pending_review': stats['pending_review'] or 0,
                    'active_assignments': active_assignments,
                }
            )
            
            logger.debug(f"Updated statistics for {date}: {stats}")
            
    except Exception as e:
        # Log error but don't break the save operation
        logger.error(f"Error updating maintenance statistics: {e}")


@receiver(post_save, sender=TabelPengajuanAssignment)
def log_assignment_activity(sender, instance, created, **kwargs):
    """Log assignment activity"""
    try:
        if created:
            logger.info(f"New assignment created: {instance.history_id} -> {instance.assigned_to_employee}")
        else:
            logger.info(f"Assignment updated: {instance.history_id} -> {instance.assigned_to_employee} (Active: {instance.is_active})")
    except Exception as e:
        logger.error(f"Error logging assignment activity: {e}")


@receiver(post_save, sender=TabelReviewLog)
def log_review_activity(sender, instance, created, **kwargs):
    """Log review activity"""
    try:
        if created:
            logger.info(f"New review logged: {instance.history_id} {instance.action} by {instance.reviewer_employee}")
            
            # Update main pengajuan record if needed
            if instance.history_id and instance.action:
                try:
                    pengajuan = TabelPengajuan.objects.get(history_id=instance.history_id)
                    pengajuan.reviewed_by = instance.reviewer_employee
                    pengajuan.review_date = instance.review_date
                    pengajuan.review_notes = instance.review_notes
                    pengajuan.final_section_id = instance.final_section_id
                    
                    if instance.action == 'approve':
                        pengajuan.review_status = '1'
                    elif instance.action == 'reject':
                        pengajuan.review_status = '2'
                        pengajuan.status = '2'  # Also reject the main status
                    
                    pengajuan.save()
                    logger.info(f"Updated pengajuan {instance.history_id} based on review")
                    
                except TabelPengajuan.DoesNotExist:
                    logger.warning(f"Could not find pengajuan {instance.history_id} to update from review")
                except Exception as e:
                    logger.error(f"Error updating pengajuan from review: {e}")
                    
    except Exception as e:
        logger.error(f"Error logging review activity: {e}")


@receiver(post_save, sender=TabelApprovalLog)
def log_approval_activity(sender, instance, created, **kwargs):
    """Log approval activity"""
    try:
        if created:
            action_text = "APPROVED" if instance.action == '1' else "REJECTED" if instance.action == '2' else instance.action
            logger.info(f"New approval logged: {instance.history_id} {action_text} by {instance.approver_user}")
    except Exception as e:
        logger.error(f"Error logging approval activity: {e}")


@receiver(pre_save, sender=TabelPengajuan)
def validate_pengajuan_before_save(sender, instance, **kwargs):
    """Validate pengajuan data before saving"""
    try:
        # Auto-generate history_id if not provided
        if not instance.history_id and instance.tgl_insert:
            from datetime import datetime
            today = instance.tgl_insert if instance.tgl_insert else datetime.now()
            prefix = f"WO{today.strftime('%Y%m%d')}"
            
            # Find last number for today
            try:
                last_pengajuan = TabelPengajuan.objects.filter(
                    history_id__startswith=prefix
                ).order_by('-history_id').first()
                
                if last_pengajuan and last_pengajuan.history_id:
                    try:
                        last_number = int(last_pengajuan.history_id[-3:])
                        next_number = last_number + 1
                    except (ValueError, IndexError):
                        next_number = 1
                else:
                    next_number = 1
                
                instance.history_id = f"{prefix}{str(next_number).zfill(3)}"
                logger.debug(f"Auto-generated history_id: {instance.history_id}")
                
            except Exception as e:
                logger.error(f"Error generating history_id: {e}")
                # Fallback to timestamp-based ID
                instance.history_id = f"{prefix}{today.strftime('%H%M%S')}"
        
        # Validate required fields
        if not instance.user_insert:
            logger.warning(f"Pengajuan {instance.history_id} has no user_insert")
        
        if not instance.oleh:
            logger.warning(f"Pengajuan {instance.history_id} has no oleh (pengaju)")
            
    except Exception as e:
        logger.error(f"Error in pre_save validation: {e}")


# Signal untuk cleanup otomatis
@receiver(post_delete, sender=TabelPengajuan)
def cleanup_related_data_on_delete(sender, instance, **kwargs):
    """Cleanup related data when pengajuan is deleted"""
    try:
        if instance.history_id:
            # Deactivate assignments
            TabelPengajuanAssignment.objects.filter(
                history_id=instance.history_id
            ).update(is_active=False)
            
            logger.info(f"Cleaned up data for deleted pengajuan {instance.history_id}")
            
    except Exception as e:
        logger.error(f"Error cleaning up related data: {e}")


# Signal untuk auto-update timestamps pada assignment
@receiver(pre_save, sender=TabelPengajuanAssignment)
def update_assignment_timestamp(sender, instance, **kwargs):
    """Update timestamp on assignment changes"""
    try:
        if not instance.pk:  # New record
            instance.assignment_date = timezone.now()
        else:
            # Check if active status changed
            try:
                old_instance = TabelPengajuanAssignment.objects.get(pk=instance.pk)
                if old_instance.is_active != instance.is_active:
                    logger.info(f"Assignment {instance.history_id} active status changed: {old_instance.is_active} -> {instance.is_active}")
            except TabelPengajuanAssignment.DoesNotExist:
                pass
                
    except Exception as e:
        logger.error(f"Error updating assignment timestamp: {e}")


# Signal untuk maintenance statistik harian
from django.db.models.signals import post_migrate

@receiver(post_migrate)
def create_maintenance_settings(sender, **kwargs):
    """Create default maintenance settings after migration"""
    if sender.name == 'wo_maintenance_app':
        try:
            from wo_maintenance_app.models import MaintenanceSettings
            
            default_settings = [
                {
                    'key': 'REVIEWER_EMPLOYEE_NUMBER',
                    'value': '007522',
                    'description': 'Employee number for default reviewer (Siti Fatimah)'
                },
                {
                    'key': 'AUTO_ASSIGN_ENABLED',
                    'value': 'true',
                    'description': 'Enable automatic assignment to section supervisors after review'
                },
                {
                    'key': 'ASSIGNMENT_NOTIFICATION_ENABLED',
                    'value': 'false',
                    'description': 'Enable email notifications for assignments'
                },
                {
                    'key': 'DASHBOARD_REFRESH_INTERVAL',
                    'value': '300',
                    'description': 'Dashboard refresh interval in seconds'
                },
                {
                    'key': 'MAX_PENGAJUAN_PER_PAGE',
                    'value': '20',
                    'description': 'Maximum number of pengajuan per page in lists'
                }
            ]
            
            for setting in default_settings:
                MaintenanceSettings.objects.get_or_create(
                    key=setting['key'],
                    defaults={
                        'value': setting['value'],
                        'description': setting['description']
                    }
                )
            
            logger.info("Default maintenance settings created/updated")
            
        except Exception as e:
            logger.warning(f"Could not create default maintenance settings: {e}")


# Manual signal connection (jika diperlukan)
def connect_signals():
    """Manually connect signals if needed"""
    logger.info("WO Maintenance signals connected")


# Utility function untuk trigger manual update statistik
def update_daily_statistics(date=None):
    """Manually update statistics for a specific date"""
    try:
        if not date:
            date = timezone.now().date()
            
        # Trigger the statistics update
        latest_pengajuan = TabelPengajuan.objects.filter(
            tgl_insert__date=date
        ).order_by('-tgl_insert').first()
        
        if latest_pengajuan:
            # This will trigger the signal
            latest_pengajuan.save()
            logger.info(f"Manually updated statistics for {date}")
        else:
            logger.info(f"No pengajuan found for {date} to update statistics")
            
    except Exception as e:
        logger.error(f"Error manually updating statistics: {e}")


logger.info("WO Maintenance signals module loaded")
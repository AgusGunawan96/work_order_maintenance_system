# wo_maintenance_app/apps.py
from django.apps import AppConfig


class WoMaintenanceAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wo_maintenance_app'
    verbose_name = 'WO Maintenance'
    
    def ready(self):
        # Import signals jika diperlukan di masa depan
        pass
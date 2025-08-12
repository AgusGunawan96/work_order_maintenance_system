# wo_maintenance_app/database_router.py - MINIMAL VERSION
class MaintenanceDatabaseRouter:
    """
    Database router untuk wo_maintenance_app - SIMPLIFIED
    """

    def db_for_read(self, model, **hints):
        """Suggest the database that should be read from for model."""
        if model._meta.app_label == 'wo_maintenance_app':
            # Model-model tertentu menggunakan DB_Maintenance
            maintenance_models = [
                'TabelPengajuan', 'TabelMesin', 'TabelLine', 
                'TabelMsection', 'TabelPekerjaan', 'ViewMain'
            ]
            
            if model.__name__ in maintenance_models:
                return 'DB_Maintenance'
        
        return None  # Use default database

    def db_for_write(self, model, **hints):
        """Suggest the database that should be written to for model."""
        if model._meta.app_label == 'wo_maintenance_app':
            # Model-model tertentu menggunakan DB_Maintenance
            maintenance_models = [
                'TabelPengajuan', 'TabelMesin', 'TabelLine', 
                'TabelMsection', 'TabelPekerjaan'
            ]
            
            if model.__name__ in maintenance_models:
                return 'DB_Maintenance'
        
        return None  # Use default database

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Determine if the migration operation is allowed to run on the database."""
        if app_label == 'wo_maintenance_app':
            # Sebagian besar model menggunakan default database untuk migration
            return db == 'default'
        
        return None  # Default behavior
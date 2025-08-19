# dailyactivity_app/routers.py - Update router yang udah ada

class DailyActivityDatabaseRouter:
    """
    Router khusus untuk dailyactivity_app models
    Handle routing antara default database dan DB_Maintenance
    """
    
    # Model yang menggunakan database DB_Maintenance
    maintenance_models = ['tabelline', 'tabelmesin', 'tabelpekerjaan']
    
    def db_for_read(self, model, **hints):
        """Tentukan database untuk READ operations"""
        if model._meta.app_label == 'dailyactivity_app':
            if model._meta.model_name.lower() in self.maintenance_models:
                return 'DB_Maintenance'
        return None  # Return None agar router lain bisa handle
    
    def db_for_write(self, model, **hints):
        """Tentukan database untuk WRITE operations"""
        if model._meta.app_label == 'dailyactivity_app':
            if model._meta.model_name.lower() in self.maintenance_models:
                # Model maintenance adalah read-only, jangan izinkan write
                return None  # Atau bisa return 'DB_Maintenance' kalau mau allow write
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations antara objects dalam app yang sama"""
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Pastikan maintenance models tidak di-migrate ke database default
        """
        if app_label == 'dailyactivity_app':
            if model_name and model_name.lower() in self.maintenance_models:
                # Maintenance models jangan di-migrate sama sekali (managed=False)
                return False
            elif db == 'DB_Maintenance':
                # App lain jangan migrate ke DB_Maintenance
                return False
            else:
                # Model dailyactivity_app lainnya migrate ke default
                return db == 'default'
        elif db == 'DB_Maintenance':
            # Database DB_Maintenance hanya untuk maintenance models
            return False
        return None
# wo_maintenance_app/models.py
from django.db import models
from django.contrib.auth.models import User

class MaintenanceDatabaseRouter:
    """
    A router to control all database operations on models for the
    maintenance application
    """

    route_app_labels = {'wo_maintenance_app'}

    def db_for_read(self, model, **hints):
        """Suggest the database that should be read from for objects of type model."""
        if model._meta.app_label == 'wo_maintenance_app':
            return 'DB_Maintenance'
        return None

    def db_for_write(self, model, **hints):
        """Suggest the database that should be written to for objects of type model."""
        if model._meta.app_label == 'wo_maintenance_app':
            return 'DB_Maintenance'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if a model in the maintenance app is involved."""
        db_set = {'default', 'DB_Maintenance'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that the maintenance app's models get created on the right database."""
        if app_label == 'wo_maintenance_app':
            return db == 'DB_Maintenance'
        return None


# ===== MODELS UNTUK TABEL MAINTENANCE =====

class TabelPengajuan(models.Model):
    """Model untuk tabel_pengajuan di DB_Maintenance"""
    
    history_id = models.CharField(max_length=15, null=True, blank=True)
    tgl_his = models.DateTimeField(null=True, blank=True)
    jam_his = models.CharField(max_length=12, null=True, blank=True)
    id_line = models.FloatField(null=True, blank=True)
    id_mesin = models.FloatField(null=True, blank=True)
    number_wo = models.CharField(max_length=15, null=True, blank=True)
    deskripsi_perbaikan = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=1, null=True, blank=True, help_text="0=Pending, 1=Approved, 2=Rejected, 3=In Progress, 4=Completed")
    user_insert = models.CharField(max_length=50, null=True, blank=True)
    tgl_insert = models.DateTimeField(null=True, blank=True)
    oleh = models.CharField(max_length=500, null=True, blank=True)
    approve = models.CharField(max_length=10, null=True, blank=True, help_text="0=Not Approved, 1=Approved, 2=Rejected")
    status_pekerjaan = models.CharField(max_length=1, null=True, blank=True)
    id_pengajuan = models.IntegerField(null=True, blank=True)
    id_section = models.FloatField(null=True, blank=True)
    id_pekerjaan = models.FloatField(null=True, blank=True)
    idpengajuan = models.FloatField(null=True, blank=True)
    
    # ===== REVIEW SYSTEM FIELDS =====
    review_status = models.CharField(max_length=1, null=True, blank=True, default='0', 
                                   help_text="0=Pending Review, 1=Reviewed Approved, 2=Reviewed Rejected")
    reviewed_by = models.CharField(max_length=50, null=True, blank=True, 
                                 help_text="Employee number of reviewer (007522)")
    review_date = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(null=True, blank=True)
    final_section_id = models.FloatField(null=True, blank=True, 
                                       help_text="Final section assigned by reviewer")

    class Meta:
        managed = False
        db_table = 'tabel_pengajuan'
        verbose_name = 'Pengajuan Maintenance'
        verbose_name_plural = 'Pengajuan Maintenance'

    def __str__(self):
        return self.history_id or f"Pengajuan {self.id}"

    @property
    def status_display(self):
        """Display status pengajuan"""
        status_map = {
            '0': 'Pending',
            '1': 'Approved',
            '2': 'Rejected',
            '3': 'In Progress',
            '4': 'Completed'
        }
        return status_map.get(self.status, 'Unknown')

    @property
    def review_status_display(self):
        """Display status review"""
        review_map = {
            '0': 'Pending Review',
            '1': 'Reviewed (Approved)',
            '2': 'Reviewed (Rejected)'
        }
        return review_map.get(self.review_status, 'Pending Review')

    @property
    def needs_review(self):
        """Cek apakah pengajuan perlu di-review"""
        return (self.status == '1' and self.approve == '1' and 
                (self.review_status is None or self.review_status == '0'))


class TabelMesin(models.Model):
    """Model untuk tabel_mesin di DB_Maintenance"""
    
    id_mesin = models.FloatField(primary_key=True)
    mesin = models.CharField(max_length=75, null=True, blank=True)
    id_line = models.CharField(max_length=10, null=True, blank=True)
    nomer = models.CharField(max_length=10, null=True, blank=True)
    keterangan = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=1, null=True, blank=True)
    user_insert = models.CharField(max_length=30, null=True, blank=True)
    user_edit = models.CharField(max_length=30, null=True, blank=True)
    tgl_insert = models.DateTimeField(null=True, blank=True)
    tgl_edit = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'tabel_mesin'
        verbose_name = 'Mesin'
        verbose_name_plural = 'Mesin'

    def __str__(self):
        return self.mesin or f"Mesin {self.id_mesin}"


class TabelLine(models.Model):
    """Model untuk tabel_line di DB_Maintenance"""
    
    id_line = models.FloatField(primary_key=True)
    line = models.CharField(max_length=35, null=True, blank=True)
    keterangan = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=1, null=True, blank=True)
    user_insert = models.CharField(max_length=30, null=True, blank=True)
    user_edit = models.CharField(max_length=30, null=True, blank=True)
    tgl_insert = models.DateTimeField(null=True, blank=True)
    tgl_edit = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'tabel_line'
        verbose_name = 'Line Production'
        verbose_name_plural = 'Line Production'

    def __str__(self):
        return self.line or f"Line {self.id_line}"


class TabelMsection(models.Model):
    """Model untuk tabel_msection di DB_Maintenance"""
    
    id_section = models.FloatField(primary_key=True)
    seksi = models.CharField(max_length=50, null=True, blank=True)
    keterangan = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    user_insert = models.CharField(max_length=50, null=True, blank=True)
    user_edit = models.CharField(max_length=50, null=True, blank=True)
    tgl_insert = models.DateTimeField(null=True, blank=True)
    tgl_edit = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'tabel_msection'
        verbose_name = 'Section Maintenance'
        verbose_name_plural = 'Section Maintenance'

    def __str__(self):
        return self.seksi or f"Section {self.id_section}"


class TabelPekerjaan(models.Model):
    """Model untuk tabel_pekerjaan di DB_Maintenance"""
    
    id_pekerjaan = models.FloatField(primary_key=True)
    pekerjaan = models.CharField(max_length=50, null=True, blank=True)
    keterangan = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=1, null=True, blank=True)
    user_insert = models.CharField(max_length=50, null=True, blank=True)
    user_edit = models.CharField(max_length=50, null=True, blank=True)
    tgl_insert = models.DateTimeField(null=True, blank=True)
    tgl_edit = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'tabel_pekerjaan'
        verbose_name = 'Jenis Pekerjaan'
        verbose_name_plural = 'Jenis Pekerjaan'

    def __str__(self):
        return self.pekerjaan or f"Pekerjaan {self.id_pekerjaan}"


# ===== REVIEW SYSTEM MODELS =====

class TabelPengajuanAssignment(models.Model):
    """Model untuk tabel_pengajuan_assignment - Assignment System"""
    
    id = models.AutoField(primary_key=True)
    history_id = models.CharField(max_length=15, null=True, blank=True)
    assigned_to_employee = models.CharField(max_length=50, null=True, blank=True, 
                                          help_text="Employee number yang di-assign")
    assigned_by_employee = models.CharField(max_length=50, null=True, blank=True, 
                                          help_text="Employee number yang melakukan assign")
    assignment_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'tabel_pengajuan_assignment'
        verbose_name = 'Assignment Pengajuan'
        verbose_name_plural = 'Assignment Pengajuan'

    def __str__(self):
        return f"Assignment {self.history_id} to {self.assigned_to_employee}"


class TabelReviewLog(models.Model):
    """Model untuk tabel_review_log - Review Activity Log"""
    
    id = models.AutoField(primary_key=True)
    history_id = models.CharField(max_length=15, null=True, blank=True)
    reviewer_employee = models.CharField(max_length=50, null=True, blank=True)
    action = models.CharField(max_length=10, null=True, blank=True, 
                            help_text="approve, reject")
    final_section_id = models.FloatField(null=True, blank=True)
    review_notes = models.TextField(null=True, blank=True)
    review_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'tabel_review_log'
        verbose_name = 'Review Log'
        verbose_name_plural = 'Review Log'

    def __str__(self):
        return f"Review {self.history_id} by {self.reviewer_employee}"


class TabelApprovalLog(models.Model):
    """Model untuk tabel_approval_log - Approval Activity Log"""
    
    id = models.AutoField(primary_key=True)
    history_id = models.CharField(max_length=15, null=True, blank=True)
    approver_user = models.CharField(max_length=50, null=True, blank=True)
    action = models.CharField(max_length=10, null=True, blank=True, 
                            help_text="1=approve, 2=reject")
    keterangan = models.TextField(null=True, blank=True)
    tgl_approval = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'tabel_approval_log'
        verbose_name = 'Approval Log'
        verbose_name_plural = 'Approval Log'

    def __str__(self):
        return f"Approval {self.history_id} by {self.approver_user}"


# ===== HELPER MODELS untuk Django Integration =====

class WorkOrderStats(models.Model):
    """Model virtual untuk statistik work order (tidak menyimpan ke database)"""
    
    total_pengajuan = models.IntegerField(default=0)
    pending_approval = models.IntegerField(default=0)
    pending_review = models.IntegerField(default=0)
    approved = models.IntegerField(default=0)
    completed = models.IntegerField(default=0)
    today_count = models.IntegerField(default=0)
    this_week_count = models.IntegerField(default=0)

    class Meta:
        managed = False
        verbose_name = 'Work Order Statistics'
        verbose_name_plural = 'Work Order Statistics'


class ReviewerProfile(models.Model):
    """Model untuk profile reviewer (Siti Fatimah)"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reviewer_profile')
    employee_number = models.CharField(max_length=50, unique=True, default='007522')
    fullname = models.CharField(max_length=200, default='SITI FATIMAH')
    is_active_reviewer = models.BooleanField(default=True)
    review_authority = models.TextField(help_text="Areas of review authority", blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reviewer Profile'
        verbose_name_plural = 'Reviewer Profiles'

    def __str__(self):
        return f"Reviewer: {self.fullname} ({self.employee_number})"

    @property
    def is_siti_fatimah(self):
        """Check if this is Siti Fatimah's profile"""
        return self.employee_number == '007522'


# ===== CUSTOM MANAGERS =====

class ActivePengajuanManager(models.Manager):
    """Manager untuk pengajuan yang aktif"""
    
    def get_queryset(self):
        return super().get_queryset().filter(history_id__isnull=False)

    def pending_approval(self):
        return self.filter(status='0', approve='0')

    def approved(self):
        return self.filter(status='1', approve='1')

    def pending_review(self):
        return self.filter(status='1', approve='1', review_status__in=['0', None])

    def reviewed(self):
        return self.filter(review_status__in=['1', '2'])

    def assigned_to_sections(self):
        return self.filter(final_section_id__isnull=False)


class ReviewPengajuanManager(models.Manager):
    """Manager khusus untuk review pengajuan"""
    
    def get_queryset(self):
        return super().get_queryset().filter(
            status='1', 
            approve='1',
            history_id__isnull=False
        )

    def pending_review(self):
        return self.filter(review_status__in=['0', None])

    def reviewed_approved(self):
        return self.filter(review_status='1')

    def reviewed_rejected(self):
        return self.filter(review_status='2')

    def by_reviewer(self, employee_number):
        return self.filter(reviewed_by=employee_number)


# ===== ADD MANAGERS TO MODELS =====

# Tambahkan custom managers ke TabelPengajuan
TabelPengajuan.add_to_class('objects', models.Manager())
TabelPengajuan.add_to_class('active', ActivePengajuanManager())
TabelPengajuan.add_to_class('for_review', ReviewPengajuanManager())


# ===== UTILITY FUNCTIONS =====

def get_reviewer_employee_number():
    """Get reviewer employee number"""
    return '007522'  # Siti Fatimah

def get_reviewer_fullname():
    """Get reviewer fullname"""
    return 'SITI FATIMAH'

def create_history_id():
    """Generate new history ID"""
    from datetime import datetime
    today = datetime.now()
    prefix = f"WO{today.strftime('%Y%m%d')}"
    
    try:
        from django.db import connections
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                SELECT TOP 1 history_id 
                FROM tabel_pengajuan 
                WHERE history_id LIKE %s 
                ORDER BY history_id DESC
            """, [f"{prefix}%"])
            
            result = cursor.fetchone()
            if result:
                last_number = int(result[0][-3:])
                return f"{prefix}{str(last_number + 1).zfill(3)}"
            else:
                return f"{prefix}001"
    except Exception:
        # Fallback jika terjadi error
        import random
        return f"{prefix}{str(random.randint(1, 999)).zfill(3)}"

def create_number_wo():
    """Generate new number WO"""
    from datetime import datetime
    today = datetime.now()
    number_wo = f"WO{today.strftime('%y%m%d%H%M%S')}"
    return number_wo[:15]  # Limit to 15 characters
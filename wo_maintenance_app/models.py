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

class TabelMain(models.Model):
    """
    Model untuk tabel_main - History pengajuan yang udah di-review
    Data dari tabel_pengajuan yang udah di-approve SITI FATIMAH masuk kesini
    """
    
    history_id = models.CharField(max_length=11, null=True, blank=True)
    tgl_his = models.DateTimeField(null=True, blank=True)
    jam_his = models.CharField(max_length=12, null=True, blank=True)
    id_line = models.FloatField(null=True, blank=True)
    id_mesin = models.FloatField(null=True, blank=True)
    nomer = models.CharField(max_length=10, null=True, blank=True)
    id_section = models.FloatField(null=True, blank=True)
    id_pekerjaan = models.FloatField(null=True, blank=True)
    number_wo = models.CharField(max_length=15, null=True, blank=True)
    deskripsi_perbaikan = models.TextField(null=True, blank=True)
    
    # Kolom-kolom yang bisa di-edit di history
    id_penyebab = models.FloatField(null=True, blank=True)
    penyebab = models.TextField(null=True, blank=True)
    akar_masalah = models.TextField(null=True, blank=True)
    tindakan_perbaikan = models.TextField(null=True, blank=True)
    tindakan_pencegahan = models.TextField(null=True, blank=True)
    status_pekerjaan = models.CharField(max_length=1, null=True, blank=True, 
                                      help_text="0=Open, 1=Close")
    
    # Waktu pekerjaan
    tgl_wp_dari = models.DateTimeField(null=True, blank=True)
    jam_wp_dari = models.CharField(max_length=12, null=True, blank=True)
    tgl_wp_sampai = models.DateTimeField(null=True, blank=True)
    jam_wp_sampai = models.CharField(max_length=12, null=True, blank=True)
    
    # Lead time
    tgl_lt_dari = models.DateTimeField(null=True, blank=True)
    jam_lt_dari = models.CharField(max_length=12, null=True, blank=True)
    tgl_lt_sampai = models.DateTimeField(null=True, blank=True)
    jam_lt_sampai = models.CharField(max_length=12, null=True, blank=True)
    
    # Downtime
    tgl_dt_dari = models.DateTimeField(null=True, blank=True)
    jam_dt_dari = models.CharField(max_length=12, null=True, blank=True)
    tgl_dt_sampai = models.DateTimeField(null=True, blank=True)
    jam_dt_sampai = models.CharField(max_length=12, null=True, blank=True)
    alasan_dt = models.CharField(max_length=240, null=True, blank=True, default='')
    
    # Estimasi dan selesai
    tgl_estimasidt = models.DateTimeField(null=True, blank=True)
    jam_estimasidt = models.CharField(max_length=12, null=True, blank=True)
    tgl_selesai = models.DateTimeField(null=True, blank=True)
    jam_selesai = models.CharField(max_length=12, null=True, blank=True)
    
    # Status dan PIC
    status_sparepart = models.CharField(max_length=1, null=True, blank=True)
    pic_produksi = models.TextField(default='-')  # NOT NULL dengan default
    pic_maintenance = models.TextField(default='-')  # NOT NULL dengan default
    status = models.CharField(max_length=1, null=True, blank=True, 
                            help_text="0=Open, 1=Close")
    
    # User tracking
    user_insert = models.CharField(max_length=50, null=True, blank=True)
    usert_edit = models.CharField(max_length=50, null=True, blank=True)  # Typo di DB, keep as is
    tgl_insert = models.DateTimeField(null=True, blank=True)
    tgl_edit = models.DateTimeField(null=True, blank=True)
    
    # Additional fields
    id_dethis = models.CharField(max_length=15, null=True, blank=True)
    do_date = models.DateTimeField(null=True, blank=True)
    do_date_sampai = models.DateTimeField(null=True, blank=True)
    alasan_delay = models.TextField(null=True, blank=True)
    
    # Custom fields
    satu = models.CharField(max_length=2, null=True, blank=True)
    dua = models.CharField(max_length=2, null=True, blank=True)
    tiga = models.CharField(max_length=2, null=True, blank=True)
    masalah = models.CharField(max_length=500, null=True, blank=True)
    oleh = models.CharField(max_length=500, null=True, blank=True)
    waktusetting = models.CharField(max_length=50, null=True, blank=True)
    
    # Supervisor fields
    PriMa = models.CharField(max_length=5, null=True, blank=True)
    SpvProd = models.CharField(max_length=10, null=True, blank=True)
    SpvMain = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'tabel_main'
        verbose_name = 'History Pengajuan'
        verbose_name_plural = 'History Pengajuan'

    def __str__(self):
        return f"History {self.history_id} - {self.oleh}"

    # @property
    # def status_display(self):
    #     """Display status pekerjaan"""
    #     if self.status == '0':
    #         return 'Open'
    #     elif self.status == '1':
    #         return 'Close'
    #     else:
    #         return 'Unknown'

    # @property
    # def status_pekerjaan_display(self):
    #     """Display status pekerjaan"""
    #     if self.status_pekerjaan == '0':
    #         return 'Open'
    #     elif self.status_pekerjaan == '1':
    #         return 'Close'
    #     else:
    #         return 'Unknown'

    # @property
    # def is_open(self):
    #     """Check if status is open"""
    #     return self.status == '0'

    # @property
    # def is_closed(self):
    #     """Check if status is closed"""
    #     return self.status == '1'

    @property
    def status_display(self):
        """Display status dengan sistem O/C yang baru"""
        if self.status == 'O':
            return 'Open'
        elif self.status == 'C':
            return 'Close'
        else:
            # Backward compatibility untuk data lama
            if self.status == '0':
                return 'Open'
            elif self.status == '1':
                return 'Close'
            else:
                return 'Unknown'

    @property
    def status_pekerjaan_display(self):
        """Display status pekerjaan dengan sistem O/C yang baru"""
        if self.status_pekerjaan == 'O':
            return 'Open'
        elif self.status_pekerjaan == 'C':
            return 'Close'
        else:
            # Backward compatibility untuk data lama
            if self.status_pekerjaan == '0':
                return 'Open'
            elif self.status_pekerjaan == '1':
                return 'Close'
            else:
                return 'Unknown'

    @property
    def is_open(self):
        """Check if status is open - support O/C dan backward compatibility"""
        return self.status in ['O', '0']

    @property
    def is_closed(self):
        """Check if status is closed - support O/C dan backward compatibility"""
        return self.status in ['C', '1']

    @property
    def is_pekerjaan_open(self):
        """Check if status pekerjaan is open - support O/C dan backward compatibility"""
        return self.status_pekerjaan in ['O', '0']

    @property
    def is_pekerjaan_closed(self):
        """Check if status pekerjaan is closed - support O/C dan backward compatibility"""
        return self.status_pekerjaan in ['C', '1']

    @property
    def mesin_info(self):
        """Get mesin info"""
        try:
            from django.db import connections
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT mesin FROM tabel_mesin 
                    WHERE id_mesin = %s
                """, [self.id_mesin])
                result = cursor.fetchone()
                return result[0] if result else 'Unknown'
        except:
            return 'Unknown'

    @property
    def line_info(self):
        """Get line info"""
        try:
            from django.db import connections
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT line FROM tabel_line 
                    WHERE id_line = %s
                """, [self.id_line])
                result = cursor.fetchone()
                return result[0] if result else 'Unknown'
        except:
            return 'Unknown'

    @property
    def section_info(self):
        """Get section info"""
        try:
            from django.db import connections
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT seksi FROM tabel_msection 
                    WHERE id_section = %s
                """, [self.id_section])
                result = cursor.fetchone()
                return result[0] if result else 'Unknown'
        except:
            return 'Unknown'

# Custom Manager untuk TabelMain
class ActiveHistoryManager(models.Manager):
    """Manager untuk history yang aktif"""
    
    def get_queryset(self):
        return super().get_queryset().filter(history_id__isnull=False)

    def open_status(self):
        return self.filter(status='0')

    def closed_status(self):
        return self.filter(status='1')

    def by_user(self, user_insert):
        return self.filter(user_insert=user_insert)

    def recent(self, days=30):
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        return self.filter(tgl_insert__gte=cutoff_date)


# Add custom manager ke TabelMain
TabelMain.add_to_class('objects', models.Manager())
TabelMain.add_to_class('active', ActiveHistoryManager())

# Helper function untuk transfer data dari pengajuan ke main
def transfer_pengajuan_to_main(pengajuan_data, reviewed_by=None):
    """
    Transfer data dari tabel_pengajuan ke tabel_main setelah di-review
    
    Args:
        pengajuan_data: Data pengajuan dari tabel_pengajuan
        reviewed_by: Employee number yang melakukan review
    
    Returns:
        bool: Success status
    """
    try:
        from django.db import connections
        from datetime import datetime
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Insert data ke tabel_main
            cursor.execute("""
                INSERT INTO tabel_main (
                    history_id, tgl_his, jam_his, id_line, id_mesin, 
                    id_section, id_pekerjaan, number_wo, deskripsi_perbaikan,
                    pic_produksi, pic_maintenance, status, user_insert, 
                    tgl_insert, oleh, status_pekerjaan
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, [
                pengajuan_data.get('history_id'),
                pengajuan_data.get('tgl_his'),
                pengajuan_data.get('jam_his'),
                pengajuan_data.get('id_line'),
                pengajuan_data.get('id_mesin'),
                pengajuan_data.get('id_section'),
                pengajuan_data.get('id_pekerjaan'),
                pengajuan_data.get('number_wo'),
                pengajuan_data.get('deskripsi_perbaikan'),
                pengajuan_data.get('oleh', '-'),  # pic_produksi default ke pengaju
                '-',  # pic_maintenance default kosong
                '0',  # status default Open
                pengajuan_data.get('user_insert'),
                datetime.now(),
                pengajuan_data.get('oleh'),
                '0'   # status_pekerjaan default Open
            ])
            
            return True
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error transferring pengajuan to main: {e}")
        return False


# Export untuk digunakan di utils
__all__ = [
    'TabelMain',
    'ActiveHistoryManager',
    'transfer_pengajuan_to_main'
]

def create_new_history_id():
    """
    Generate new history ID dengan format: 25-08-0001
    Format: YY-MM-NNNN (tahun 2 digit - bulan - 4 digit urut)
    """
    from datetime import datetime
    from django.db import connections
    
    today = datetime.now()
    year_month = today.strftime('%y-%m')  # Format: 25-08
    
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Cari nomor terakhir untuk bulan ini
            cursor.execute("""
                SELECT TOP 1 history_id 
                FROM tabel_pengajuan 
                WHERE history_id LIKE %s 
                ORDER BY history_id DESC
            """, [f"{year_month}-%"])
            
            result = cursor.fetchone()
            if result:
                # Extract 4 digit terakhir dan increment
                last_history = result[0]
                last_number = int(last_history.split('-')[-1])
                new_number = last_number + 1
            else:
                # Pertama kali untuk bulan ini
                new_number = 1
            
            # Format: 25-08-0001
            history_id = f"{year_month}-{str(new_number).zfill(4)}"
            return history_id
            
    except Exception as e:
        # Fallback jika error
        import random
        fallback_number = random.randint(1, 9999)
        return f"{year_month}-{str(fallback_number).zfill(4)}"


def validate_section_id_strict(section_id):
    """
    STRICT validation untuk section ID
    
    Args:
        section_id: Section ID untuk divalidate
    
    Returns:
        int: Valid section ID (1-5), default 1 jika invalid
    """
    try:
        section_id_int = int(float(section_id)) if section_id else 1
        
        # HANYA terima 1, 2, 3, 4, 5
        if section_id_int in [1, 2, 3, 4, 5]:
            return section_id_int
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"VALIDATE STRICT: Invalid section_id {section_id_int}, defaulting to 1 (IT)")
            return 1
            
    except (ValueError, TypeError):
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"VALIDATE STRICT: Error converting section_id {section_id}, defaulting to 1 (IT)")
        return 1
    
def get_section_display_name_strict(section_id):
    """
    Get display name dengan strict validation
    """
    section_id_validated = validate_section_id_strict(section_id)
    
    names = {
        1: 'IT',
        2: 'Elektrik', 
        3: 'Mekanik',
        4: 'Utility',
        5: 'Civil'
    }
    
    return names.get(section_id_validated, 'IT')  # Default IT jika tidak ada

def create_history_id():
    """DEPRECATED: Use create_new_history_id() instead"""
    return create_new_history_id()

def create_number_wo():
    """DEPRECATED: Use create_number_wo_with_section() instead"""
    from datetime import datetime
    today = datetime.now()
    # Return fallback format for compatibility
    return f"WO{today.strftime('%y%m%d%H%M%S')}"[:15]


def get_section_code_mapping_fixed():
    """
    FIXED: Mapping section ID ke kode huruf sesuai database aktual
    Mapping sesuai permintaan:
    - id_section = 4 seksi Mekanik = M
    - id_section = 5 seksi Elektrik = E  
    - id_section = 6 seksi Utility = U
    - id_section = 8 seksi IT = I
    
    Returns: dict mapping section_id to code
    """
    return {
        4: 'M',   # Mekanik
        5: 'E',   # Elektrik
        6: 'U',   # Utility
        8: 'I'    # IT
    }


def create_number_wo_with_section_fixed(section_id):
    """
    FIXED: Generate number WO dengan mapping section yang benar sesuai database
    Format: YY-S-MM-NNNN (tahun - section code - bulan - 4 digit urut)
    
    Mapping yang benar:
    - section_id = 4 (Mekanik) = M -> 25-M-08-0001
    - section_id = 5 (Elektrik) = E -> 25-E-08-0001  
    - section_id = 6 (Utility) = U -> 25-U-08-0001
    - section_id = 8 (IT) = I -> 25-I-08-0001
    
    Args:
        section_id: ID section tujuan (4=Mekanik, 5=Elektrik, 6=Utility, 8=IT)
    
    Returns:
        str: Number WO dengan format yang sesuai database
    """
    from datetime import datetime
    from django.db import connections
    import logging
    
    logger = logging.getLogger(__name__)
    
    today = datetime.now()
    
    # Convert section_id to int dengan validation yang ketat
    try:
        section_id_int = int(float(section_id)) if section_id else 8  # Default ke IT
        logger.info(f"FIXED CREATE WO: Processing section_id = {section_id_int}")
    except (ValueError, TypeError) as e:
        logger.error(f"FIXED CREATE WO: Error converting section_id {section_id}: {e}")
        section_id_int = 8  # Default ke IT jika error
    
    # Get section code dengan mapping yang BENAR sesuai database
    correct_mapping = get_section_code_mapping_fixed()  # {4:'M', 5:'E', 6:'U', 8:'I'}
    
    if section_id_int in correct_mapping:
        section_code = correct_mapping[section_id_int]
        logger.info(f"FIXED CREATE WO: Using correct mapping - section {section_id_int} = code {section_code}")
    else:
        # Section lain: Default ke IT sebagai fallback
        section_code = 'I'  # IT sebagai default yang aman
        logger.warning(f"FIXED CREATE WO: Section {section_id_int} not in mapping [4,5,6,8], using IT fallback")
    
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # Cari nomor terakhir untuk section dan bulan ini
            search_pattern = f"{today.strftime('%y')}-{section_code}-{today.strftime('%m')}-%"
            
            logger.info(f"FIXED CREATE WO: Searching pattern: {search_pattern}")
            
            # Query ke tabel_main untuk cari number_wo terakhir dengan pattern
            cursor.execute("""
                SELECT TOP 1 number_wo 
                FROM tabel_main 
                WHERE number_wo LIKE %s 
                ORDER BY number_wo DESC
            """, [search_pattern])
            
            result = cursor.fetchone()
            if result:
                try:
                    last_number_wo = result[0]
                    # Extract 4 digit terakhir
                    last_number = int(last_number_wo.split('-')[-1])
                    new_number = last_number + 1
                    logger.info(f"FIXED CREATE WO: Found last number {last_number}, using {new_number}")
                except (ValueError, IndexError) as e:
                    logger.warning(f"FIXED CREATE WO: Error parsing last number from {last_number_wo}: {e}")
                    new_number = 1
            else:
                new_number = 1
                logger.info(f"FIXED CREATE WO: First time for this section/month, using 1")
            
            # Format dengan mapping yang benar
            number_wo = f"{today.strftime('%y')}-{section_code}-{today.strftime('%m')}-{str(new_number).zfill(4)}"
            
            logger.info(f"FIXED CREATE WO: Generated number_wo = {number_wo} for section {section_id_int}")
            
            return number_wo
            
    except Exception as e:
        logger.error(f"FIXED CREATE WO: Database error: {e}")
        # Fallback dengan timestamp untuk hindari duplikasi
        import random
        fallback_number = random.randint(1, 9999)
        fallback_wo = f"{today.strftime('%y')}-{section_code}-{today.strftime('%m')}-{str(fallback_number).zfill(4)}"
        
        logger.error(f"FIXED CREATE WO: FALLBACK number_wo = {fallback_wo}")
        return fallback_wo


def get_section_display_name_fixed(section_id):
    """
    FIXED: Get display name dari section ID sesuai database
    
    Args:
        section_id: Section ID (4, 5, 6, 8)
    
    Returns:
        str: Display name section
    """
    try:
        section_id_int = int(float(section_id)) if section_id else 8
        
        names = {
            4: 'Mekanik',
            5: 'Elektrik', 
            6: 'Utility',
            8: 'IT'
        }
        
        return names.get(section_id_int, 'IT')  # Default IT jika tidak ada
        
    except (ValueError, TypeError):
        return 'IT'  # Default IT jika error


def validate_section_id_fixed(section_id):
    """
    FIXED: Validation untuk section ID sesuai mapping database
    
    Args:
        section_id: Section ID untuk divalidate
    
    Returns:
        int: Valid section ID (4, 5, 6, 8), default 8 jika invalid
    """
    try:
        section_id_int = int(float(section_id)) if section_id else 8
        
        # HANYA terima 4, 5, 6, 8
        if section_id_int in [4, 5, 6, 8]:
            return section_id_int
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"VALIDATE FIXED: Invalid section_id {section_id_int}, defaulting to 8 (IT)")
            return 8  # Default ke IT
            
    except (ValueError, TypeError):
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"VALIDATE FIXED: Error converting section_id {section_id}, defaulting to 8 (IT)")
        return 8


def debug_section_code_generation_fixed(section_id):
    """
    FIXED: Debug function untuk troubleshoot section code generation
    Dengan mapping yang benar: 4=M, 5=E, 6=U, 8=I
    """
    import logging
    logger = logging.getLogger(__name__)
    
    debug_info = {
        'input_section_id': section_id,
        'input_type': type(section_id).__name__,
        'steps': [],
        'mapping_used': 'FIXED: 4=M, 5=E, 6=U, 8=I'
    }
    
    # Step 1: Validation
    try:
        section_id_int = int(float(section_id)) if section_id else 8
        debug_info['steps'].append(f"Step 1: Converted to int = {section_id_int}")
    except Exception as e:
        debug_info['steps'].append(f"Step 1: Error converting = {e}")
        section_id_int = 8
    
    # Step 2: Range check dengan mapping yang benar
    if section_id_int in [4, 5, 6, 8]:
        debug_info['steps'].append(f"Step 2: Valid range [4,5,6,8] = True")
    else:
        debug_info['steps'].append(f"Step 2: Invalid range, forcing to 8 (IT)")
        section_id_int = 8
    
    # Step 3: Get code dengan mapping yang benar
    mapping = get_section_code_mapping_fixed()
    section_code = mapping.get(section_id_int)
    debug_info['steps'].append(f"Step 3: Mapping lookup = {section_code}")
    
    # Step 4: Validation kode
    valid_codes = ['M', 'E', 'U', 'I']
    if section_code in valid_codes:
        debug_info['steps'].append(f"Step 4: Valid code = True")
    else:
        debug_info['steps'].append(f"Step 4: Invalid code, forcing to I")
        section_code = 'I'
    
    debug_info['final_result'] = {
        'section_id': section_id_int,
        'section_code': section_code,
        'section_name': get_section_display_name_fixed(section_id_int)
    }
    
    logger.info(f"DEBUG SECTION CODE FIXED: {debug_info}")
    return debug_info


def test_number_wo_generation_fixed():
    """
    FIXED: Test generation untuk semua section dengan mapping yang benar
    """
    import logging
    logger = logging.getLogger(__name__)
    
    test_results = {}
    
    # Test dengan section mapping yang benar
    for section_id in [4, 5, 6, 8]:
        try:
            test_wo = create_number_wo_with_section_fixed(section_id)
            debug_info = debug_section_code_generation_fixed(section_id)
            
            # Check apakah ada error 'X' di number WO
            has_x = 'X' in test_wo
            
            # Expected codes
            expected_codes = {4: 'M', 5: 'E', 6: 'U', 8: 'I'}
            expected_code = expected_codes[section_id]
            has_correct_code = f"-{expected_code}-" in test_wo
            
            test_results[f'section_{section_id}'] = {
                'section_id': section_id,
                'expected_code': expected_code,
                'generated_wo': test_wo,
                'has_x_error': has_x,
                'has_correct_code': has_correct_code,
                'debug_info': debug_info,
                'success': not has_x and has_correct_code
            }
            
            if has_x:
                logger.error(f"TEST ERROR: Section {section_id} generated 'X' in {test_wo}")
            elif not has_correct_code:
                logger.error(f"TEST ERROR: Section {section_id} expected '{expected_code}' but got {test_wo}")
            else:
                logger.info(f"TEST SUCCESS: Section {section_id} = {test_wo}")
                
        except Exception as e:
            test_results[f'section_{section_id}'] = {
                'section_id': section_id,
                'error': str(e),
                'success': False
            }
            logger.error(f"TEST ERROR: Section {section_id} failed: {e}")
    
    return test_results


# Helper function untuk backward compatibility
def create_number_wo_with_section(section_id):
    """
    DEPRECATED: Use create_number_wo_with_section_fixed() instead
    Wrapper untuk backward compatibility
    """
    return create_number_wo_with_section_fixed(section_id)

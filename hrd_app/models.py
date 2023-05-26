from django.db import models
from django.contrib.auth.models import User
from master_app.models import GenderField
from django.utils import timezone
# Create your models here.

# BIODATA START
# BIODATA END

# CUTI START
# CUTI END

# KESEJAHTERAAN START
# KESEJAHTERAAN END

# MEDICAL TRAIN START
class medicalHubungan(models.TextChoices):
    ISTRI   = 'Istri'
    ANAK    = 'Anak'

class medicalTempatPelayanan(models.TextChoices):
    RUMAH_SAKIT     = 'Rumah Sakit'
    KLINIK          = 'klinik'
    PRAKTEK_DOKTER  = 'Praktek Dokter'
    BIDAN           = 'Bidan'

class medicalJenisPelayanan(models.TextChoices):
    RAWAT_JALAN     = 'Rawat Jalan'
    RAWAT_INAP      = 'Rawat Inap'
    KACAMATA        = 'Kacamata'
    PERSALINAN      = 'Persalinan'

class medicalJenisMelahirkan(models.TextChoices):
    NORMAL          = 'Normal'
    CAESAR          = 'Caesar'
    KEGUGURAN       = 'Keguguran'

class medicalStatus(models.TextChoices):
    KLAIM_TIDAK_LENGKAP = 'Klaim tidak lengkap'
    KLAIM_DITOLAK       = 'Klaim ditolak'

class medicalApprovalList(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_foreman      = models.BooleanField(default=False, blank=True, null=True)
    is_supervisor   = models.BooleanField(default=False, blank=True, null=True)
    is_manager      = models.BooleanField(default=False, blank=True, null=True)
    is_hr           = models.BooleanField(default=False, blank=True, null=True)
    created_at = models.DateTimeField('created at', auto_now_add = True)
    updated_at = models.DateTimeField('updated at', auto_now = True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
    
class medicalHeader(models.Model):
    user          = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    hr            = models.ForeignKey(medicalApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    medical_no    = models.CharField(max_length=128, null=True, blank=True)
    rp_total      = models.PositiveBigIntegerField(null=True, blank=True)
    is_foreman    = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    is_manager    = models.BooleanField(default=False)
    is_complete   = models.BooleanField(default=False)
    is_reject     = models.BooleanField(default=False)
    is_delete     = models.BooleanField(default=False)
    created_at    = models.DateTimeField('created at', auto_now_add = True)
    updated_at    = models.DateTimeField('updated at', auto_now = True)
    def __str__(self):
        return self.medical_no  
    
class medicalDetailPasienKeluarga(models.Model):
    medical         = models.ForeignKey(medicalHeader, on_delete=models.CASCADE, blank=True, null=True)
    nama_pasien     = models.CharField(max_length=128,null=True, blank=True)
    tanggal_lahir   = models.DateTimeField('tanggal lahir', blank=True, null=True)
    jenis_kelamin   = GenderField(null=True, blank=True)
    hubungan        = models.CharField(max_length=25, choices=medicalHubungan.choices, default=False, null=True, blank=True)
    created_at      = models.DateTimeField('created at', auto_now_add = True)
    updated_at      = models.DateTimeField('updated at', auto_now = True)

class medicalDetailDokter(models.Model):
    medical             = models.ForeignKey(medicalHeader, on_delete=models.CASCADE, blank=True, null=True)
    nama_dokter         = models.CharField(max_length=128)
    tempat_pelayanan    = models.CharField(max_length=25, choices=medicalTempatPelayanan.choices)
    nama_tempat         = models.CharField(max_length=128)
    alamat              = models.TextField()
    no_telp             = models.CharField(max_length=128)
    created_at          = models.DateTimeField('created at', auto_now_add = True)
    updated_at          = models.DateTimeField('updated at', auto_now = True)

class medicalDetailInformation(models.Model):
    medical                 = models.ForeignKey(medicalHeader, on_delete=models.CASCADE, blank=True, null=True)
    jenis_pelayanan         = models.CharField(max_length=25, choices=medicalJenisPelayanan.choices, default=False)
    melahirkan              = models.CharField(max_length=25, choices=medicalJenisMelahirkan.choices, default=False, null=True, blank=True)
    tanggal_berobat_mulai   = models.DateTimeField('tanggal berobat mulai', default=timezone.now)
    tanggal_berobat_selesai = models.DateTimeField('tanggal berobat selesai', default=timezone.now)
    diagnosa                = models.CharField(max_length=128)
    created_at              = models.DateTimeField('created at', auto_now_add = True)
    updated_at              = models.DateTimeField('updated at', auto_now = True)

class medicalClaimStatus(models.Model):
    medical         = models.ForeignKey(medicalHeader, on_delete=models.CASCADE, blank=True, null=True)
    is_lengkap      = models.BooleanField(default=False)
    tidak_lengkap   = models.CharField(max_length=25, choices=medicalStatus.choices, default=False, null=True, blank=True)
    created_at      = models.DateTimeField('created at', auto_now_add = True)
    updated_at      = models.DateTimeField('updated at', auto_now = True)

class medicalAttachment(models.Model):
    medical         = models.ForeignKey(medicalHeader, on_delete=models.CASCADE, blank=True, null=True)
    attachment      = models.FileField(upload_to='MedicalAttachment/', null=False, blank=True)

# APPROVAL MEDICAL START

    
class medicalApprovalForeman(models.Model):
    medical    = models.ForeignKey(medicalHeader, on_delete=models.CASCADE, blank=True, null=True)
    foreman    = models.ForeignKey(medicalApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    is_approve = models.BooleanField(default=False, blank=True, null=True)
    is_reject  = models.BooleanField(default=False, blank=True, null=True)
    reason     = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField('created at', auto_now_add = True)
    updated_at = models.DateTimeField('updated at', auto_now = True)
    
    def __str__(self):
        return self.foreman.user.first_name + " " + self.foreman.user.last_name
    
class medicalApprovalSupervisor(models.Model):
    medical    = models.ForeignKey(medicalHeader, on_delete=models.CASCADE, blank=True, null=True)
    supervisor = models.ForeignKey(medicalApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    is_approve = models.BooleanField(default=False, blank=True, null=True)
    is_reject  = models.BooleanField(default=False, blank=True, null=True)
    reason     = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField('created at', auto_now_add = True)
    updated_at = models.DateTimeField('updated at', auto_now = True)

    def __str__(self):
        return self.supervisor.user.first_name + " " + self.supervisor.user.last_name
    
class medicalApprovalManager(models.Model):
    medical    = models.ForeignKey(medicalHeader, on_delete=models.CASCADE, blank=True, null=True)
    manager    = models.ForeignKey(medicalApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    is_approve = models.BooleanField(default=False, blank=True, null=True)
    is_reject  = models.BooleanField(default=False, blank=True, null=True)
    reason     = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField('created at', auto_now_add = True)
    updated_at = models.DateTimeField('updated at', auto_now = True)

    def __str__(self):
        return self.manager.user.first_name + " " + self.manager.user.last_name
    
class medicalApprovalHR(models.Model):
    medical    = models.ForeignKey(medicalHeader, on_delete=models.CASCADE, blank=True, null=True)
    hr         = models.ForeignKey(medicalApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    is_approve = models.BooleanField(default=False, blank=True, null=True)
    is_reject  = models.BooleanField(default=False, blank=True, null=True)
    reason     = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField('created at', auto_now_add = True)
    updated_at = models.DateTimeField('updated at', auto_now = True)

    def __str__(self):
        return self.hr.user.first_name + " " + self.hr.user.last_name

# APPROVAL MEDICAL END

# MEDICAL TRAIN END

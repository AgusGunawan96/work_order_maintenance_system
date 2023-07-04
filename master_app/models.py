from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

# FUNCTION START

class Province(models.Model):
    province_name   = models.CharField(max_length=128)
    created_at      = models.DateTimeField('created at', auto_now_add=True)
    updated_at      = models.DateTimeField('updated at', auto_now=True)
    def __str__(self):
        return self.province_name
    
class Regency(models.Model):
    province        = models.ForeignKey(Province, on_delete = models.CASCADE)
    regency_name    = models.CharField(max_length=128)
    created_at      = models.DateTimeField('created at', auto_now_add=True)
    updated_at      = models.DateTimeField('updated at', auto_now=True)
    def __str__(self):
        return self.regency_name
    
class District(models.Model):
    regency         = models.ForeignKey(Regency, on_delete = models.CASCADE)
    district_name   = models.CharField(max_length = 128)
    created_at      = models.DateTimeField('created at', auto_now_add=True)
    updated_at      = models.DateTimeField('updated at', auto_now=True)
    def __str__(self):
        return self.district_name
    
class Village(models.Model):
    district        = models.ForeignKey(District, on_delete=models.CASCADE)
    village_name    = models.CharField(max_length=128)
    created_at      = models.DateTimeField('created at', auto_now_add=True)
    updated_at      = models.DateTimeField('updated at', auto_now=True)
    def __str__(self):
        return self.village_name

class GenderField(models.CharField):
    MALE = 'M'
    FEMALE = 'F'
    NONBINARY = 'NB'
    CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (NONBINARY, 'Non-binary'),
    ]
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 2)
        kwargs.setdefault('choices', self.CHOICES)
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get('max_length') == 2:
            del kwargs['max_length']
        if kwargs.get('choices') == self.CHOICES:
            del kwargs['choices']
        return name, path, args, kwargs


# FUNCTION END

# USER START
class Department(models.Model):
    department_name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.department_name

class Division(models.Model):
    department      = models.ForeignKey(Department,on_delete=models.CASCADE)
    division_name   = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.division_name

class Section(models.Model):
    division        = models.ForeignKey(Division,on_delete=models.CASCADE)
    section_name    = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.section_name

class noTelp2Hub(models.TextChoices):
    SUAMI_ATAU_ISTRI    = 'SUAMI/ISTRI'
    ORANGTUA            = 'ORANGTUA'
    ANAK                = 'ANAK'
    SAUDARA             = 'SAUDARA'

class userKeluarga(models.TextChoices):
    ISTRI               = 'Istri'
    ANAK                = 'Anak'

class userWarisHub(models.TextChoices):
    SUAMI_ATAU_ISTRI    = 'SUAMI/ISTRI'
    ORANGTUA            = 'ORANGTUA'
    ANAK                = 'ANAK'
    SAUDARA             = 'SAUDARA'

class PendTer(models.TextChoices):
    SMA_ATAU_SEDERAJAT  = 'SMA/SEDERAJAT'
    D1                  = 'D-1'
    D2                  = 'D-2'
    D3                  = 'D-3'
    S1                  = 'S1'
    S2                  = 'S2'
    LAINNYA             = 'LAINNYA'

class TeMiNo(models.TextChoices):
    MILIK_SENDIRI       = 'SMA/SEDERAJAT'
    IKUT_ORANGTUA       = 'D-1'
    KONTRAK             = 'D-2'
    KOST                = 'D-3'
    LAINNYA             = 'LAINNYA'

class pekerjaan(models.TextChoices):
    PNS_ATAU_BUMN       = 'PNS/BUMN'
    KARYAWAN_SWASTA     = 'Karyawan Swasta'
    IRT                 = 'IRT'
    WIRAUSAHA           = 'Wirausaha'
    LAINNYA             = 'LAINNYA'

class UserProfileInfo(models.Model):
    user                          = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    department                    = models.ForeignKey(Department,on_delete=models.CASCADE, null=True, blank=True)
    division                      = models.ForeignKey(Division,on_delete=models.CASCADE, null=True, blank=True)
    section                       = models.ForeignKey(Section,on_delete=models.CASCADE, default=False , related_name = 'sections', null=True, blank=True)
    employee_ext                  = models.CharField(max_length=8, blank=True, null=True)
    is_supervisor                 = models.BooleanField(default=False, blank=True, null=True)
    is_manager                    = models.BooleanField(default=False, blank=True, null=True)
    is_bod                        = models.BooleanField(default=False, blank=True, null=True)
    is_contract                   = models.BooleanField(default=False, blank=True, null=True)
    is_permanent                  = models.BooleanField(default=False, blank=True, null=True)
    is_operate_computer           = models.BooleanField(default=False, blank=True, null=True)
    tempat                        = models.ForeignKey(Regency, on_delete=models.CASCADE, null=True, blank=True)
    tanggal_lahir                 = models.DateTimeField('Tanggal Lahir', default=timezone.now)
    noktp                         = models.PositiveBigIntegerField(default=False)
    no_telepon                    = models.IntegerField(default=False)
    no_telepon2                   = models.IntegerField(default=False, null=True, blank=True)
    no_telp2_hubungan             = models.CharField(max_length=25, choices=noTelp2Hub.choices, default=False, null=True, blank=True)
    pendidikan_terakhir           = models.CharField(max_length=25, choices=PendTer.choices, default=False, null=True, blank=True)
    pendidikan_terakhir_others    = models.CharField(max_length=128, unique=False, default=False, blank=True, null=True)
    gender                        = GenderField(default='NB')
    position                      = models.CharField(max_length=128, unique=False, default=False, blank=True, null=True)
    profile_pic                   = models.ImageField(upload_to='profile_pics',blank=True, null=True)

class UserProfileKTP(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    alamat_ktp          = models.TextField(default=False)
    is_surat_ktp        = models.BooleanField(default=False)
    rt_ktp              = models.IntegerField(max_length=8)
    rw_ktp              = models.IntegerField(max_length=8)
    provinsi_ktp        = models.ForeignKey(Province, on_delete=models.CASCADE, default=False)
    kelurahan_ktp       = models.ForeignKey(Village, on_delete=models.CASCADE)
    kecamatan_ktp       = models.ForeignKey(District, on_delete=models.CASCADE)
    kota_ktp            = models.ForeignKey(Regency, on_delete=models.CASCADE)
    is_same_ktp         = models.BooleanField(default=False)

class UserProfileKTPNow(models.Model):
    userKTP             = models.ForeignKey(UserProfileKTP, default=False,on_delete=models.CASCADE)
    alamat_now          = models.TextField(default=False)
    is_surat_now        = models.BooleanField(default=False)
    rt_now              = models.IntegerField(max_length=8)
    rw_now              = models.IntegerField(max_length=8)
    provinsi_now        = models.ForeignKey(Province, on_delete=models.CASCADE, default=False)
    kelurahan_now       = models.ForeignKey(Village, on_delete=models.CASCADE)
    kecamatan_now       = models.ForeignKey(District, on_delete=models.CASCADE)
    kota_now            = models.ForeignKey(Regency, on_delete=models.CASCADE)
    tempat_milik_now    = models.CharField(max_length=25, choices=TeMiNo.choices, default=False, null=True, blank=True)
    nama_pemilik        = models.CharField(max_length=128, default=False, null=True, blank=True)
    no_telp_pemilik     = models.IntegerField(default=False, null=True, blank=True)


class UserKeluargaHeader(models.Model):
    nokk                = models.PositiveBigIntegerField(default=False)
    

class UserKeluargaInfo(models.Model):
    keluarga            = models.ForeignKey(UserKeluargaHeader, on_delete=models.CASCADE, null=True, blank=True, default=False)
    user                = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    gender              = GenderField(default='NB')
    tempat              = models.ForeignKey(Regency, on_delete=models.CASCADE, null=True, blank=True)
    tanggal_lahir       = models.DateTimeField('Tanggal Lahir', default=timezone.now)
    hubungan            = models.CharField(max_length=25, choices=userKeluarga.choices, default=False)
    nama_lengkap        = models.CharField(max_length=200, unique=False, default=False, blank=True, null=True)
    noktp               = models.PositiveBigIntegerField(default=False, null=True, blank=True)
    pekerjaan           = models.CharField(max_length=25, choices=pekerjaan.choices, default=False, null=True, blank=True)
    pekerjaan_others    = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.nama_lengkap +' ( '+ self.hubungan + ' ) '
    
class UserAhliWaris(models.Model):
    nama_lengkap        = models.CharField(max_length=200, unique=False, default=False, blank=True, null=True)
    tempat              = models.ForeignKey(Regency, on_delete=models.CASCADE, null=True, blank=True)
    tanggal_lahir       = models.DateTimeField('Tanggal Lahir', default=timezone.now)
    noktp               = models.PositiveBigIntegerField(default=False, null=True, blank=True)
    hubungan            = models.CharField(max_length=25, choices=userWarisHub.choices, default=False, null=True, blank=True)
    
    
class Notification(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp   = models.DateTimeField(auto_now_add = True)
    message     = models.TextField()
    is_read     = models.BooleanField(default=False)
    link        = models.CharField(max_length=128, unique=True)
    category    = models.CharField(max_length=128, unique=True, default=False)




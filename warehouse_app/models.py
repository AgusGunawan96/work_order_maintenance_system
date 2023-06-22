from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from POSEIWA.models import TPo, MasterSupplier
# Create your models here.

class KendaraanType(models.TextChoices):
    MOBIL        = 'Mobil'
    MOTOR        = 'Motor'

class TujuanTamu(models.TextChoices):
    MEETING     = 'Meeting'
    PICKUP      = 'Pickup Barang'

class GudangType(models.TextChoices):
    RM          = 'R/M'
    OTHERS      = 'OTHERS'

# GATE PASS IN START

class GatePassSecurity(models.Model):
    user        = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    is_security = models.BooleanField(default=False, blank=True, null=True)

class GatePassInHeader(models.Model):
    Security            = models.ForeignKey(GatePassSecurity, on_delete = models.CASCADE, blank = True, null = True)
    gatepass_no         = models.CharField(max_length = 128)
    nama                = models.CharField(max_length = 128)
    nomor_identitas     = models.PositiveBigIntegerField(null=True, blank=True)
    nomor_kendaraan     = models.CharField(max_length = 128)
    jenis_kendaraan     = models.CharField(max_length=25, choices=KendaraanType.choices, null=True)
    status              = models.CharField(default = 'In', max_length = 128)
    created_at          = models.DateTimeField('created at', auto_now_add = True)
    updated_at          = models.DateTimeField('updated at', auto_now = True)


class GatePassInDetailTamu(models.Model):
    gatepass_header     = models.ForeignKey(GatePassInHeader, on_delete = models.CASCADE, blank = True, null = True)
    nomor_surat_jalan   = models.CharField(max_length = 128)
    nama_perusahaan     = models.CharField(max_length = 128)
    nomor_identitas     = models.PositiveBigIntegerField(null=True, blank=True)
    created_at          = models.DateTimeField('created at', auto_now_add = True)
    updated_at          = models.DateTimeField('updated at', auto_now = True)

class GatePassInDetailKirimBarang(models.Model):
    gatepass_header     = models.ForeignKey(GatePassInHeader, on_delete = models.CASCADE, blank = True, null = True)
    tujuan              = models.CharField(max_length=25, choices=TujuanTamu.choices, null=True)
    nama_perusahaan     = models.CharField(max_length = 128)
    bertemu_dengan      = models.CharField(max_length = 128)
    nomor_surat_jalan   = models.CharField(max_length = 128)
    departemen          = models.CharField(max_length = 128, blank = True, null = True)
    created_at          = models.DateTimeField('created at', auto_now_add = True)
    updated_at          = models.DateTimeField('updated at', auto_now = True)

class rel_gatepass_po:
    gatepass_header     = models.ForeignKey(GatePassInHeader, on_delete = models.CASCADE, blank = True, null = True)
    no_po               = models.ForeignKey(TPo, on_delete = models.CASCADE, blank = True, null = True)
    quantity            = models.PositiveBigIntegerField(blank=True, null=True)
    created_at          = models.DateTimeField('created at', auto_now_add = True)
    updated_at          = models.DateTimeField('updated at', auto_now = True)

# GATE PASS IN END
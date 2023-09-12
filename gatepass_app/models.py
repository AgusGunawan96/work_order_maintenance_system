from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone
# Create your models here.

class gatepassPermision(models.Model):
    user       = models.ForeignKey(User, on_delete = models.CASCADE, blank= True, null= True)
    position   = models.CharField(max_length = 64, null=True, blank=True)
    created_at = models.DateTimeField('created at', auto_now_add = True)
    updated_at = models.DateTimeField('updated at', auto_now = True)

class gatepassHeader(models.Model):
    security        = models.ForeignKey(gatepassPermision, on_delete=models.CASCADE, blank=True, null=True)
    ngatepass       = models.CharField(max_length=64, null=True, blank=True)
    nama_tamu       = models.CharField(max_length=128, null=True , blank=True)
    nomor_identitas = models.CharField(max_length=64, null=True, blank=True)
    nomor_kendaraan = models.CharField(max_length=64, null=True, blank=True)
    jenis_kendaraan = models.CharField(max_length=64, null=True, blank=True)
    tipe            = models.CharField(max_length=64, null=True, blank=True)
    tanggal_masuk   = models.DateTimeField('tanggal_masuk', null=True, blank=True)
    tanggal_keluar  = models.DateTimeField('tanggal_keluar', null=True, blank=True )
    status          = models.CharField(max_length=16, null=True, blank=True)
    created_at      = models.DateTimeField('created at', auto_now_add = True)
    updated_at      = models.DateTimeField('updated at', auto_now = True)

class gatepassDetail(models.Model):
    gatepassH           = models.ForeignKey(gatepassHeader, on_delete=models.CASCADE, blank=True, null=True)
    nama_perusahaan     = models.CharField(max_length=128, null=True, blank=True)
    bertemu_dengan      = models.CharField(max_length=64, null=True, blank=True)
    department          = models.CharField(max_length=64, null=True, blank=True)
    tujuanH             = models.CharField(max_length=128, null=True, blank=True)
    tujuanD             = models.CharField(max_length=256 , null=True, blank=True)
    no_surat_jalan      = models.CharField(max_length=64, null=True, blank=True)
    tujuan_pengiriman   = models.CharField(max_length=128, null=True, blank=True)
    tipe_gudang         = models.CharField(max_length=64, null=True, blank=True)
    created_at          = models.DateTimeField('created at', auto_now_add = True)
    updated_at          = models.DateTimeField('updated at', auto_now = True)

class gatepassPO(models.Model):
    gatepassH  = models.ForeignKey(gatepassHeader, on_delete = models.CASCADE, blank=True, null=True)
    po_no      = models.CharField(max_length=64, null=True, blank=True)
    quantity   = models.FloatField(null=True,blank=True)
    created_at = models.DateTimeField('created at', auto_now_add = True)
    updated_at = models.DateTimeField('updated at', auto_now = True)



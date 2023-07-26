from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

# POC VL START
class masterTagVL(models.Model):
    item_no         = models.CharField(max_length=128, null=True, blank=True)
    item_desc       = models.CharField(max_length=128, null=True, blank=True)
    spec            = models.CharField(max_length=128, null=True, blank=True) 
    poc             = models.FloatField(max_length=128, null=True, blank=True) 
    poc_lower       = models.FloatField(max_length=128, null=True, blank=True)
    poc_upper       = models.FloatField(max_length=128, null=True, blank=True)
    vib             = models.FloatField(max_length=128, null=True, blank=True)
    run_out         = models.FloatField(max_length=128, null=True, blank=True)
    # ro_low          = models.FloatField(max_length=128, null=True, blank=True)
    # ro_upper        = models.FloatField(max_length=128, null=True, blank=True)
    tipe_pulley     = models.CharField(max_length=128, null=True, blank=True)
    pulley_diameter = models.FloatField(max_length=128, null=True, blank=True)
    weight_kg       = models.PositiveBigIntegerField(null=True, blank=True)
    weight_n        = models.FloatField(null=True, blank=True)
    top_width       = models.FloatField(max_length=128, null=True, blank=True)
    top_width_plus  = models.FloatField(max_length=128, null=True, blank=True)
    top_width_minus = models.FloatField(max_length=128, null=True, blank=True)
    thickness       = models.FloatField(max_length=128, null=True, blank=True)
    thickness_plus  = models.FloatField(max_length=128, null=True, blank=True)
    thickness_minus = models.FloatField(max_length=128, null=True, blank=True)
    tipe_belt       = models.BooleanField(default=False)

class POCVLRecord(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    so_no               = models.CharField(max_length=128,null=True, blank=True)
    item_no             = models.CharField(max_length=128, null=True, blank=True)
    item_desc           = models.CharField(max_length=128, null=True, blank=True)
    poc                 = models.FloatField(max_length=128, null=True, blank=True)
    poc_status          = models.BooleanField(default=False)
    vib                 = models.FloatField(max_length=128, null=True, blank=True)
    vib_status          = models.BooleanField(default=False)
    run_out             = models.FloatField(max_length=128, null=True, blank=True)
    run_out_status      = models.BooleanField(default=False)
    center_distance     = models.FloatField(max_length=128, null=True, blank=True)
    weight_kg           = models.PositiveBigIntegerField(null=True, blank=True)
    weight_n            = models.FloatField(null=True, blank=True)
    top_width           = models.FloatField(max_length=128, null=True, blank=True)
    top_width_status    = models.BooleanField(default=False)
    thickness_status    = models.BooleanField(default=False)
    shift               = models.PositiveIntegerField(null=True, blank=True)
    thickness           = models.FloatField(max_length=128, null=True, blank=True)
    created_at          = models.DateTimeField('created at', auto_now_add=True)
    updated_at          = models.DateTimeField('updated at', auto_now=True)
    # ro_low         = models.FloatField(max_length=128, null=True, blank=True)
    # ro_upper       = models.FloatField(max_length=128, null=True, blank=True)
# POC VL END

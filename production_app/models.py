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

class POCVLPermission(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at          = models.DateTimeField('created at', auto_now_add=True)
    updated_at          = models.DateTimeField('updated at', auto_now=True)
    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
    
class masterTagLowModulus(models.Model):
    item_no             = models.CharField(max_length=128, null=True, blank=True)
    item_desc           = models.CharField(max_length=128, null=True, blank=True)
    spec                = models.CharField(max_length=128, null=True, blank=True) 
    poc                 = models.PositiveBigIntegerField(null=True, blank=True)
    tension             = models.PositiveBigIntegerField(null=True, blank=True)
    tension_plus        = models.FloatField(max_length=128, null=True, blank=True)
    tension_minus       = models.FloatField(max_length=128, null=True, blank=True)
    ride_out            = models.FloatField(max_length=128, null=True, blank=True)
    ride_out_plus       = models.FloatField(max_length=128, null=True, blank=True)
    ride_out_minus      = models.FloatField(max_length=128, null=True, blank=True)
    tipe_pulley         = models.CharField(max_length=128, null=True, blank=True) 
    pulley_diameter     = models.FloatField(max_length=128, null=True, blank=True)
    top_width           = models.FloatField(max_length=128, null=True, blank=True)
    top_width_plus      = models.FloatField(max_length=128, null=True, blank=True)
    top_width_minus     = models.FloatField(max_length=128, null=True, blank=True)
    thickness           = models.FloatField(max_length=128, null=True, blank=True)
    thickness_plus      = models.FloatField(max_length=128, null=True, blank=True)
    thickness_minus     = models.FloatField(max_length=128, null=True, blank=True)
    cpl100mm            = models.FloatField(max_length=128, null=True, blank=True)
    cpl1round           = models.FloatField(max_length=128, null=True, blank=True)
    high_speed          = models.FloatField(max_length=128, null=True, blank=True)
    low_speed           = models.FloatField(max_length=128, null=True, blank=True)
    rpm                 = models.FloatField(max_length=128, null=True, blank=True)

class POCLowModulusRecord(models.Model):
    created_at          = models.DateTimeField('created at', auto_now_add=True)
    updated_at          = models.DateTimeField('updated at', auto_now=True)

class POCLowModulusPermission(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at          = models.DateTimeField('created at', auto_now_add=True)
    updated_at          = models.DateTimeField('updated at', auto_now=True)
    def __str__(self):
        return self.user.first_name + " " + self.user.last_name



# POC VL END

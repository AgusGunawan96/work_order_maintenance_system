from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class IncomingType(models.TextChoices):
    INCOMING_EKSTERNAL  = 'Incoming Eksternal'
    INCOMING_INTERNAL   = 'Incoming Internal'

class CategoryType(models.TextChoices):
    FABRICS             = 'Fabrics'
    CHEMICALS           = 'Chemicals'
    POLYMER             = 'Polymer'
    ROPES               = 'Ropes'
    CHOPPED_FIBERS      = 'Chopped Fibers'
    CHLOROPRENE_POLYMER = 'Chloroprene Polymer'

class rirHeader (models.Model):
    incoming_type           = models.CharField(max_length=25, choices=IncomingType.choices, null=True)
    category                = models.CharField(max_length=25, choices=CategoryType.choices, null=True)
    material                = models.CharField(max_length=200, null=True, blank=True)
    vendor                  = models.CharField(max_length=200, null=True, blank=True)
    po_number               = models.CharField(max_length=200, null=True, blank=True)
    lot_no                  = models.CharField(max_length=200, null=True, blank=True)
    quantity                = models.CharField(max_length=200, null=True, blank=True)
    rir_no                  = models.CharField(max_length=128, null=True, blank=True)
    is_special_judgement    = models.BooleanField(default=False, blank=True, null=True)
    incoming_at             = models.DateTimeField('incoming at',auto_now_add = True)
    expired_at              = models.DateTimeField('expired at', auto_now = True)
    created_at              = models.DateTimeField('created at', auto_now_add = True)
    updated_at              = models.DateTimeField('updated at', auto_now = True)

class rirDetail (models.Model):
    header                          = models.OneToOneField(rirHeader, on_delete = models.CASCADE, null=True, blank=True)
    coa_content_judgement           = models.BooleanField(default=False, blank=True, null=True)
    appearence_judgement            = models.BooleanField(default=False, blank=True, null=True)
    restricted_substance_judgement  = models.BooleanField(default=False, blank=True, null=True)
    environmental_issue_judgement   = models.BooleanField(default=False, blank=True, null=True)
    sample_test_judgement           = models.BooleanField(default=False, blank=True, null=True)
    coa_content_checked_by          = models.BooleanField(default=False, blank=True, null=True)
    appearence_checked_by           = models.BooleanField(default=False, blank=True, null=True)
    restricted_substance_checked_by = models.BooleanField(default=False, blank=True, null=True)
    environmental_issue_checked_by  = models.BooleanField(default=False, blank=True, null=True)
    sample_test_checked_by          = models.BooleanField(default=False, blank=True, null=True)
    coa_content_remark              = models.CharField(max_length=200, null=True, blank=True)
    appearence_remark               = models.CharField(max_length=200, null=True, blank=True)
    restricted_substance_remark     = models.CharField(max_length=200, null=True, blank=True)
    environmental_issue_remark      = models.CharField(max_length=200, null=True, blank=True)
    sample_test_remark              = models.CharField(max_length=200, null=True, blank=True)

class specialJudgement(models.Model):
    rir         = models.OneToOneField(rirHeader, on_delete=models.CASCADE, null=True, blank=True)
    is_pass     = models.BooleanField(default=False, blank=True, null=True)
    is_return   = models.BooleanField(default=False, blank=True, null=True)
    remark      = models.CharField(max_length=200, null=True, blank=True) #remark yang tulis siapa
    created_at  = models.DateTimeField('created at', auto_now_add = True)
    updated_at  = models.DateTimeField('updated at', auto_now = True)

class rirApprovalSupervisor(models.Model):
    specialjudgement            = models.OneToOneField(rirHeader, on_delete=models.CASCADE, null=True, blank=True)
    is_approve_supervisor       = models.BooleanField(default=False, blank=True, null=True)
    is_rejected_supervisor      = models.BooleanField(default=False, blank=True, null=True)
    is_checked_supervisor       = models.BooleanField(default=False, blank=True, null=True)
    reject_reason_supervisor    = models.TextField(blank=True, null=True)
    created_at                  = models.DateTimeField('created_at', auto_now_add=True)
    updated_at                  = models.DateTimeField('updated_at', auto_now=True)

class rirApprovalManager(models.Model):
    rir_approval_manager    = models.OneToOneField(rirApprovalSupervisor, on_delete=models.CASCADE, null=True, blank=True)
    is_approve_manager      = models.BooleanField(default=False, blank=True, null=True)
    is_rejected_manager     = models.BooleanField(default=False, blank=True, null=True)
    is_checked_manager      = models.BooleanField(default=False, blank=True, null=True)
    reject_reason_manager   = models.TextField(blank=True, null=True)
    created_at              = models.DateTimeField('created_at', auto_now_add=True)
    updated_at              = models.DateTimeField('updated_at', auto_now=True)
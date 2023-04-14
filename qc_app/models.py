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
    RAW_CORDS           = 'Raw Cords'
    
# RIR START
class rirApprovalList(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_judgement    = models.BooleanField(default=False, blank=True, null=True)
    is_checked_by   = models.BooleanField(default=False, blank=True, null=True)
    is_supervisor   = models.BooleanField(default=False, blank=True, null=True)
    is_manager      = models.BooleanField(default=False, blank=True, null=True)

class rirHeader (models.Model):
    incoming_type           = models.CharField(max_length=25, choices=IncomingType.choices)
    category                = models.CharField(max_length=25, choices=CategoryType.choices)
    material                = models.CharField(max_length=200)
    vendor                  = models.CharField(max_length=200)
    po_number               = models.CharField(max_length=200)
    lot_no                  = models.CharField(max_length=200)
    quantity                = models.CharField(max_length=200)
    rir_no                  = models.CharField(max_length=128, null=True, blank=True)
    status                  = models.CharField(max_length=128, null=True, blank=True)
    is_special_judgement    = models.BooleanField(default=False, blank=True, null=True)
    incoming_at             = models.DateTimeField('incoming at')
    expired_at              = models.DateTimeField('expired at')
    created_at              = models.DateTimeField('created at', auto_now_add = True)
    updated_at              = models.DateTimeField('updated at', auto_now = True)

class rirDetailCoaContentJudgement (models.Model):
    header                          = models.OneToOneField(rirHeader, on_delete = models.CASCADE, null=True, blank=True)
    coa_content_user_judgement      = models.ForeignKey(rirApprovalList, on_delete=models.CASCADE, blank=True, null=True) 
    coa_content_judgement           = models.BooleanField(default=False, blank=True, null=True)
    coa_content_remark              = models.CharField(max_length=200, null=True, blank=True)

class rirDetailCoaContentCheckedby (models.Model):
    coa_content_judgement           = models.OneToOneField(rirDetailCoaContentJudgement, on_delete = models.CASCADE, null=True, blank=True)
    coa_content_user_checked_by     = models.ForeignKey(rirApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    coa_content_checked_by          = models.BooleanField(default=False, blank=True, null=True)
    coa_content_remark              = models.CharField(max_length=200, null=True, blank=True)

class rirDetailAppearenceJudgement (models.Model):
    header                          = models.OneToOneField(rirHeader, on_delete = models.CASCADE, null=True, blank=True)
    appearence_user_judgement       = models.ForeignKey(rirApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    appearence_judgement            = models.BooleanField(default=False, blank=True, null=True)
    appearence_remark               = models.CharField(max_length=200, null=True, blank=True)

class rirDetailAppearenceCheckedby (models.Model):
    appearence_judgement            = models.OneToOneField(rirDetailAppearenceJudgement, on_delete = models.CASCADE, null=True, blank=True)
    appearence_user_checked_by      = models.ForeignKey(rirApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    appearence_checked_by           = models.BooleanField(default=False, blank=True, null=True)
    appearence_remark               = models.CharField(max_length=200, null=True, blank=True)

class rirDetailRestrictedSubstanceJudgement (models.Model):
    header                                  = models.OneToOneField(rirHeader, on_delete = models.CASCADE, null=True, blank=True)
    restricted_substance_user_judgement     = models.ForeignKey(rirApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    restricted_substance_judgement          = models.BooleanField(default=False, blank=True, null=True)
    restricted_substance_remark             = models.CharField(max_length=200, null=True, blank=True)

class rirDetailRestrictedSubstanceCheckedby (models.Model):
    restricted_substance_judgement          = models.OneToOneField(rirDetailRestrictedSubstanceJudgement, on_delete = models.CASCADE, null=True, blank=True)
    restricted_substance_user_checked_by    = models.ForeignKey(rirApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    restricted_substance_checked_by         = models.BooleanField(default=False, blank=True, null=True)
    restricted_substance_remark             = models.CharField(max_length=200, null=True, blank=True)

class rirDetailEnvironmentalIssueJudgement (models.Model):
    header                              = models.OneToOneField(rirHeader, on_delete = models.CASCADE, null=True, blank=True)
    environmental_issue_user_judgement  = models.ForeignKey(rirApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    environmental_issue_judgement       = models.BooleanField(default=False, blank=True, null=True)
    environmental_issue_remark          = models.CharField(max_length=200, null=True, blank=True)

class rirDetailEnvironmentalIssueCheckedby (models.Model):
    environmental_issue_judgement       = models.OneToOneField(rirDetailEnvironmentalIssueJudgement, on_delete = models.CASCADE, null=True, blank=True)
    environmental_issue_user_checked_by = models.ForeignKey(rirApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    environmental_issue_checked_by      = models.BooleanField(default=False, blank=True, null=True)
    environmental_issue_remark          = models.CharField(max_length=200, null=True, blank=True)

class rirDetailSampleTestJudgement (models.Model):
    header                      = models.OneToOneField(rirHeader, on_delete = models.CASCADE, null=True, blank=True)
    sample_test_user_judgement  = models.ForeignKey(rirApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    sample_test_judgement       = models.BooleanField(default=False, blank=True, null=True)
    sample_test_remark          = models.CharField(max_length=200, null=True, blank=True)

class rirDetailSampleTestCheckedby (models.Model):
    sample_test_judgement       = models.OneToOneField(rirDetailSampleTestJudgement, on_delete = models.CASCADE, null=True, blank=True)
    sample_test_user_checked_by = models.ForeignKey(rirApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    sample_test_checked_by      = models.BooleanField(default=False, blank=True, null=True)
    sample_test_remark          = models.CharField(max_length=200, null=True, blank=True)

class rirMaterial(models.Model):
    name                           = models.CharField(max_length=200)
    classification                 = models.CharField(max_length=50, choices=CategoryType.choices)
    condition                      = models.CharField(max_length=200, null=True, blank=True)
    location                       = models.CharField(max_length=200, null=True, blank=True)
    classification_status          = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name + " " + self.classification
    
# RIR END

# SPECIAL JUDGEMENT START

class specialJudgement(models.Model):
    rir         = models.OneToOneField(rirHeader, on_delete=models.CASCADE, null=True, blank=True)
    is_pass     = models.BooleanField(default=False, blank=True, null=True)
    is_return   = models.BooleanField(default=False, blank=True, null=True)
    created_at  = models.DateTimeField('created at', auto_now_add = True)
    updated_at  = models.DateTimeField('updated at', auto_now = True)

class rirApprovalSupervisor(models.Model):
    specialjudgement            = models.OneToOneField(rirHeader, on_delete=models.CASCADE, null=True, blank=True)
    supervisor                  = models.ForeignKey(rirApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    is_approve_supervisor       = models.BooleanField(default=False, blank=True, null=True)
    is_rejected_supervisor      = models.BooleanField(default=False, blank=True, null=True)
    is_checked_supervisor       = models.BooleanField(default=False, blank=True, null=True)
    return_reason_supervisor    = models.TextField(blank=True, null=True)
    review_supervisor           = models.TextField(blank=True, null=True)
    created_at                  = models.DateTimeField('created_at', auto_now_add=True)
    updated_at                  = models.DateTimeField('updated_at', auto_now=True)

class rirApprovalManager(models.Model):
    rir_approval_supervisor = models.OneToOneField(rirApprovalSupervisor, on_delete=models.CASCADE, null=True, blank=True)
    manager                 = models.ForeignKey(rirApprovalList, on_delete=models.CASCADE, blank=True, null=True)
    is_approve_manager      = models.BooleanField(default=False, blank=True, null=True)
    is_rejected_manager     = models.BooleanField(default=False, blank=True, null=True)
    is_checked_manager      = models.BooleanField(default=False, blank=True, null=True)
    return_reason_manager   = models.TextField(blank=True, null=True)
    review_manager          = models.TextField(blank=True, null=True)
    created_at              = models.DateTimeField('created_at', auto_now_add=True)
    updated_at              = models.DateTimeField('updated_at', auto_now=True)
# SPECIAL JUDGEMENT END
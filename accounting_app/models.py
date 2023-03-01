from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class cashPayment (models.Model):
    assignee = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    description_1 = models.TextField(null=True, blank=True)
    description_2 = models.TextField(null=True, blank=True)
    description_3 = models.TextField(null=True, blank=True)
    description_4 = models.TextField(null=True, blank=True)
    description_5 = models.TextField(null=True, blank=True)
    description_6 = models.TextField(null=True, blank=True)
    rp_detail_1 = models.PositiveBigIntegerField(null=True, blank=True)
    rp_detail_2 = models.PositiveBigIntegerField(null=True, blank=True)
    rp_detail_3 = models.PositiveBigIntegerField(null=True, blank=True)
    rp_detail_4 = models.PositiveBigIntegerField(null=True, blank=True)
    rp_detail_5 = models.PositiveBigIntegerField(null=True, blank=True)
    rp_detail_6 = models.PositiveBigIntegerField(null=True, blank=True)
    rp_total = models.PositiveBigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField('created at', auto_now_add = True)
    updated_at = models.DateTimeField('updated at', auto_now = True)
    cashPayment_attachment = models.FileField(upload_to='attachments/')

    def __str__(self):
        return self.assignee
    
class cashPaymentApprovalManager(models.Model):
    cashPayment = models.OneToOneField(cashPayment, on_delete=models.CASCADE, null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_approve_manager = models.BooleanField(default=False, blank=True, null=True )
    is_rejected_manager = models.BooleanField(default=False, blank=True, null=True )
    reject_reason_manager = models.TextField( blank=True, null=True)
    created_at = models.DateTimeField('created_at', auto_now_add=True)
    updated_at = models.DateTimeField('updated_at', auto_now=True)

class cashPaymentApprovalAccountingManager(models.Model):
    cashPayment_approval_manager = models.OneToOneField(cashPaymentApprovalManager, on_delete=models.CASCADE, null=True, blank=True)
    manager_accounting = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_approve_manager_accounting = models.BooleanField(default=False, blank=True, null=True )
    is_rejected_manager_accounting = models.BooleanField(default=False, blank=True, null=True )
    reject_reason_manager_accounting = models.TextField( blank=True, null=True)
    created_at = models.DateTimeField('created_at', auto_now_add=True)
    updated_at = models.DateTimeField('updated_at', auto_now=True)

class cashPaymentApprovalPresident(models.Model):
    cashPayment_approval_accounting_manager = models.OneToOneField(cashPaymentApprovalAccountingManager, on_delete=models.CASCADE, null=True, blank=True)
    president = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_approve_president = models.BooleanField(default=False, blank=True, null=True )
    is_rejected_president = models.BooleanField(default=False, blank=True, null=True )
    reject_reason_president = models.TextField( blank=True, null=True)
    created_at = models.DateTimeField('created_at', auto_now_add=True)
    updated_at = models.DateTimeField('updated_at', auto_now=True)

class cashPaymentApprovalCashier(models.Model):
    cashPayment_approval_president = models.OneToOneField(cashPaymentApprovalPresident, on_delete=models.CASCADE ,blank=True, null=True)
    cashier = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    ticket_no =models.CharField(max_length=128, null=True, blank=True)
    is_approve_cashier = models.BooleanField(default=False, blank=True, null=True )
    is_rejected_cashier = models.BooleanField(default=False, blank=True, null=True )
    reject_reason_cashier = models.TextField( blank=True, null=True)
    created_at = models.DateTimeField('created_at', auto_now_add=True)
    updated_at = models.DateTimeField('updated_at', auto_now=True)
    

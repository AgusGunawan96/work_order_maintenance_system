from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class TransferType(models.TextChoices):
    TRANSFER_CASH        = 'Transfer Cash'
    TRANSFER_BANK        = 'Transfer Bank'

class cashPaymentBalance (models.Model):
    balance_cashPayment_open    = models.BigIntegerField(null=True, blank=True)
    balance_cashPayment_close   = models.BigIntegerField(null=True, blank=True)
    exchange_rate_open          = models.PositiveBigIntegerField(null=True, blank=True)
    exchange_rate_close         = models.PositiveBigIntegerField(null=True, blank=True)
    cashPayment_balance_no      = models.CharField(max_length=128, null=True, blank=True)
    created_at                  = models.DateTimeField('created_at', auto_now_add=True)
    updated_at                  = models.DateTimeField('updated_at', auto_now=True)

class cashPayment (models.Model):
    assignee        = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    created_at      = models.DateTimeField('created at', auto_now_add = True)
    updated_at      = models.DateTimeField('updated at', auto_now = True)
    is_debit        = models.BooleanField(default=False, blank=True, null=True )
    is_credit       = models.BooleanField(default=False, blank=True, null=True )
    is_settle       = models.BooleanField(default=False, blank=True, null=True )
    is_adv          = models.BooleanField(default=False, blank=True, null=True )
    adv             = models.CharField(max_length=200, null=True, blank=True)
    settle          = models.CharField(max_length=200, null=True, blank=True)
    type            = models.CharField(max_length=25, choices=TransferType.choices, null=True)
    remark          = models.CharField(max_length=200, null=True, blank=True)
    ticket_no       = models.CharField(max_length=128, null=True, blank=True)
    rp_total        = models.PositiveBigIntegerField(null=True, blank=True)
    description_1   = models.TextField(blank=True, null=True)
    rp_detail_1     = models.PositiveBigIntegerField(null=True, blank=True)
    description_2   = models.TextField(blank=True, null=True)
    rp_detail_2     = models.PositiveBigIntegerField(null=True, blank=True)
    description_3   = models.TextField(blank=True, null=True)
    rp_detail_3     = models.PositiveBigIntegerField(null=True, blank=True)
    description_4   = models.TextField(blank=True, null=True)
    rp_detail_4     = models.PositiveBigIntegerField(null=True, blank=True)
    description_5   = models.TextField(blank=True, null=True)
    rp_detail_5     = models.PositiveBigIntegerField(null=True, blank=True)
    description_6   = models.TextField(blank=True, null=True)
    rp_detail_6     = models.PositiveBigIntegerField(null=True, blank=True)
    description_7   = models.TextField(blank=True, null=True)
    rp_detail_7     = models.PositiveBigIntegerField(null=True, blank=True)
    description_8   = models.TextField(blank=True, null=True)
    rp_detail_8     = models.PositiveBigIntegerField(null=True, blank=True)
    description_9   = models.TextField(blank=True, null=True)
    rp_detail_9     = models.PositiveBigIntegerField(null=True, blank=True)
    description_10  = models.TextField(blank=True, null=True)
    rp_detail_10    = models.PositiveBigIntegerField(null=True, blank=True)
    description_11  = models.TextField(blank=True, null=True)
    rp_detail_11    = models.PositiveBigIntegerField(null=True, blank=True)
    description_12  = models.TextField(blank=True, null=True)
    rp_detail_12    = models.PositiveBigIntegerField(null=True, blank=True)

class coaCode(models.Model):
    account_code    = models.CharField(max_length=126, null=True, blank=True)
    cost_centre     = models.CharField(max_length=126, null=True, blank=True)
    description     = models.CharField(max_length=126, null=True, blank=True)
    status          = models.CharField(max_length=126, null=True, blank=True)
    structure_code  = models.CharField(max_length=126, null=True, blank=True)
    created_at      = models.DateTimeField('created_at', auto_now_add=True)
    updated_at      = models.DateTimeField('updated_at', auto_now=True)
    def __str__(self):
        return self.account_code +' ('+ self.description +') '

class rel_cashPayment_accountcode(models.Model):
    cashPayment   = models.ForeignKey(cashPayment, on_delete=models.CASCADE, blank=True, null=True)
    account_code  = models.ForeignKey(coaCode, on_delete=models.CASCADE, blank=True, null=True)
    created_at    = models.DateTimeField('created_at', auto_now_add=True)
    updated_at    = models.DateTimeField('updated_at', auto_now=True)


# ATTACHMENT START
class cashPaymentAttachment(models.Model):
    cashPayment = models.ForeignKey(cashPayment, on_delete=models.CASCADE, blank=True, null=True)
    attachment  = models.FileField(upload_to='cashPaymentAttachments/', null=False, blank=True)

class cashierAttachment(models.Model):
    cashPayment = models.ForeignKey(cashPayment, on_delete=models.CASCADE, blank=True, null=True)
    attachment  = models.FileField(upload_to='cashierAttachments/', null=False, blank=True)

class settleAttachment(models.Model):
    cashPayment = models.ForeignKey(cashPayment, on_delete=models.CASCADE, blank=True, null=True)
    attachment  = models.FileField(upload_to='settleAttachments/', null=False, blank=True)

class advAttachment(models.Model):
    cashPayment = models.ForeignKey(cashPayment, on_delete=models.CASCADE, blank=True, null=True)
    attachment  = models.FileField(upload_to='advAttachments/', null=False, blank=True)
# ATTACHMENT END

# ADVANCE APPROVAL START
class advanceApprovalManager(models.Model):
    advance               = models.OneToOneField(cashPayment, on_delete = models.CASCADE, null=True, blank=True)
    manager               = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_approve_manager    = models.BooleanField(default=False, blank=True, null=True)
    is_rejected_manager   = models.BooleanField(default=False, blank=True, null=True)
    is_checked_manager    = models.BooleanField(default=False, blank=True, null=True)
    reject_reason_manager = models.TextField(blank=True, null=True)
    created_at            = models.DateTimeField('created_at', auto_now_add=True)
    updated_at            = models.DateTimeField('updated_at', auto_now=True)

class advanceApprovalAccountingManager(models.Model):
    advance_approval_manager            = models.OneToOneField(advanceApprovalManager, on_delete = models.CASCADE, null=True, blank=True)
    manager_accounting                  = models.ForeignKey(User, on_delete = models.CASCADE, blank=True, null=True)
    is_approve_manager_accounting       = models.BooleanField(default=False, blank=True, null=True)
    is_rejected_manager_accounting      = models.BooleanField(default=False, blank=True, null=True)
    is_checked_manager_accounting       = models.BooleanField(default=False, blank=True, null=True)
    reject_reason_manager_accounting    = models.TextField(blank=True, null=True)
    created_at                          = models.DateTimeField('created_at', auto_now_add=True)
    updated_at                          = models.DateTimeField('updated_at', auto_now=True)

class advanceApprovalPresident(models.Model):
    advance_approval_accounting_manager = models.OneToOneField(advanceApprovalAccountingManager, on_delete=models.CASCADE, null=True, blank=True)
    president               = models.ForeignKey(User, on_delete = models.CASCADE, blank=True , null=True)
    is_approve_president    = models.BooleanField(default=False, blank=True, null=True)
    is_rejected_president   = models.BooleanField(default=False, blank=True, null=True)
    is_checked_president    = models.BooleanField(default=False, blank=True, null=True)
    reject_reason_president = models.TextField(blank=True, null=True)
    created_at              = models.DateTimeField('created_at', auto_now_add=True)
    updated_at              = models.DateTimeField('updated_at', auto_now=True)
    
class advanceApprovalCashier(models.Model):
    advance_approval_president  = models.OneToOneField(advanceApprovalPresident, on_delete= models.CASCADE, null=True, blank=True)
    cashier                     = models.ForeignKey(User, on_delete = models.CASCADE, blank=True, null=True)
    is_approve_cashier          = models.BooleanField(default=False, blank=True, null=True)
    is_checked_cashier          = models.BooleanField(default=False, blank=True, null=True)
    created_at                  = models.DateTimeField('created_at', auto_now_add=True)
    updated_at                  = models.DateTimeField('updated_at', auto_now=True)
# ADVANCE APPROVAL END

# CASHPAYMENT APPROVAL START
class cashPaymentApprovalManager(models.Model):
    cashPayment           = models.OneToOneField(cashPayment, on_delete=models.CASCADE, null=True, blank=True)
    manager               = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_approve_manager    = models.BooleanField(default=False, blank=True, null=True )
    is_rejected_manager   = models.BooleanField(default=False, blank=True, null=True )
    is_checked_manager    = models.BooleanField(default=False, blank=True, null=True )
    reject_reason_manager = models.TextField( blank=True, null=True)
    created_at            = models.DateTimeField('created_at', auto_now_add=True)
    updated_at            = models.DateTimeField('updated_at', auto_now=True)


class cashPaymentApprovalAccountingManager(models.Model):
    cashPayment_approval_manager        = models.OneToOneField(cashPaymentApprovalManager, on_delete=models.CASCADE, null=True, blank=True)
    manager_accounting                  = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_approve_manager_accounting       = models.BooleanField(default=False, blank=True, null=True )
    is_rejected_manager_accounting      = models.BooleanField(default=False, blank=True, null=True )
    is_checked_manager_accounting       = models.BooleanField(default=False, blank=True, null=True )
    reject_reason_manager_accounting    = models.TextField( blank=True, null=True)
    created_at                          = models.DateTimeField('created_at', auto_now_add=True)
    updated_at                          = models.DateTimeField('updated_at', auto_now=True)

class cashPaymentApprovalPresident(models.Model):
    cashPayment_approval_accounting_manager = models.OneToOneField(cashPaymentApprovalAccountingManager, on_delete=models.CASCADE, null=True, blank=True)
    president                               = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_approve_president                    = models.BooleanField(default=False, blank=True, null=True )
    is_rejected_president                   = models.BooleanField(default=False, blank=True, null=True )
    is_checked_president                    = models.BooleanField(default=False, blank=True, null=True )
    reject_reason_president                 = models.TextField( blank=True, null=True)
    created_at                              = models.DateTimeField('created_at', auto_now_add=True)
    updated_at                              = models.DateTimeField('updated_at', auto_now=True)

class cashPaymentApprovalCashier(models.Model):
    cashPayment_approval_president          = models.OneToOneField(cashPaymentApprovalPresident, on_delete=models.CASCADE ,blank=True, null=True)
    cashier                                 = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_approve_cashier                      = models.BooleanField(default=False, blank=True, null=True )
    is_rejected_cashier                     = models.BooleanField(default=False, blank=True, null=True )
    is_checked_cashier                      = models.BooleanField(default=False, blank=True, null=True )
    reject_reason_cashier                   = models.TextField( blank=True, null=True)
    created_at                              = models.DateTimeField('created_at', auto_now_add=True)
    updated_at                              = models.DateTimeField('updated_at', auto_now=True)

# CASHPAYMENT APPROVAL END
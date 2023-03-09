from django import forms
from accounting_app.models import cashPayment, cashPaymentApprovalManager, cashPaymentApprovalAccountingManager, cashPaymentApprovalPresident, cashPaymentApprovalCashier, cashPaymentAttachment, cashPaymentBalance
from django.forms import ClearableFileInput

class cashPaymentForms(forms.ModelForm):
    class Meta():
        model = cashPayment
        fields = ('description_1','description_2','description_3','description_4','description_5','description_6','description_7','description_8','description_9','description_10','description_11','description_12', 'rp_detail_1', 'rp_detail_2', 'rp_detail_3', 'rp_detail_4', 'rp_detail_5', 'rp_detail_6', 'rp_detail_7', 'rp_detail_8', 'rp_detail_9', 'rp_detail_10', 'rp_detail_11', 'rp_detail_12', 'assignee', 'remark','rp_total','ticket_no',)
        widgets = {
            'assignee'                  : forms.HiddenInput(),
            'remark'                    : forms.HiddenInput(),
            'rp_total'                  : forms.HiddenInput(),
            'ticket_no'                 : forms.HiddenInput(),
            'description_1'             : forms.Textarea(attrs={'rows':2, 'cols':15}),
            'description_2'             : forms.Textarea(attrs={'rows':2, 'cols':15}),
            'description_3'             : forms.Textarea(attrs={'rows':2, 'cols':15}),
            'description_4'             : forms.Textarea(attrs={'rows':2, 'cols':15}),
            'description_5'             : forms.Textarea(attrs={'rows':2, 'cols':15}),
            'description_6'             : forms.Textarea(attrs={'rows':2, 'cols':15}),
            'description_7'             : forms.Textarea(attrs={'rows':2, 'cols':15}),
            'description_8'             : forms.Textarea(attrs={'rows':2, 'cols':15}),
            'description_9'             : forms.Textarea(attrs={'rows':2, 'cols':15}),
            'description_10'            : forms.Textarea(attrs={'rows':2, 'cols':15}),
            'description_11'            : forms.Textarea(attrs={'rows':2, 'cols':15}),
            'description_12'            : forms.Textarea(attrs={'rows':2, 'cols':15}),
            }
class cashPaymentCreditForms(forms.ModelForm):
    class Meta():
        model = cashPayment
        fields = ('remark',)

class cashPaymentDebitForms(forms.ModelForm):
    class Meta():
        model = cashPayment
        fields = ('remark','rp_total','ticket_no',)
        widgets = {
            'ticket_no': forms.HiddenInput(),
        }
        
class cashPaymentSettleForms(forms.ModelForm):
    class Meta():
        model = cashPayment
        fields = ('settle', 'is_credit', 'is_debit', 'is_settle', 'rp_total' )
        widgets = {
            'is_settle': forms.HiddenInput(),
        }

class cashPaymentAttachmentForms(forms.ModelForm):
    class Meta():
        model = cashPaymentAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }

class cashPaymentBalanceForms(forms.ModelForm):
    class Meta():
        model = cashPaymentBalance
        fields = ('balance_cashPayment_open','balance_cashPayment_close','exchange_rate_open','exchange_rate_close','cashPayment_balance_no',)

class cashPaymentApprovalManagerForms(forms.ModelForm):
    class Meta():
        model = cashPaymentApprovalManager
        fields = ('reject_reason_manager','is_approve_manager','is_rejected_manager', 'manager', 'is_checked_manager')
        widgets = {'is_approve_manager': forms.HiddenInput, 'is_rejected_manager': forms.HiddenInput, 'is_checked_manager': forms.HiddenInput , 'manager': forms.HiddenInput}

class cashPaymentApprovalAccountingManagerForms(forms.ModelForm):
    class Meta():
        model = cashPaymentApprovalAccountingManager
        fields = ('reject_reason_manager_accounting','is_approve_manager_accounting','is_rejected_manager_accounting','is_checked_manager_accounting' , 'manager_accounting')
        widgets = {'is_approve_manager_accounting': forms.HiddenInput, 'is_rejected_manager_accounting': forms.HiddenInput , 'is_checked_manager_accounting': forms.HiddenInput, 'manager_accounting': forms.HiddenInput}

class cashPaymentApprovalPresidentForms(forms.ModelForm):
    class Meta():
        fields = ('reject_reason_president','is_approve_president','is_rejected_president','is_checked_president' , 'president')
        widgets = {'is_approve_president': forms.HiddenInput, 'is_rejected_president': forms.HiddenInput, 'is_checked_president': forms.HiddenInput , 'president': forms.HiddenInput}
        model = cashPaymentApprovalPresident

class cashPaymentApprovalCashierForms(forms.ModelForm):
    class Meta():
        fields = ('reject_reason_cashier','is_approve_cashier','is_rejected_cashier','is_checked_cashier', 'cashier')
        widgets = {'is_approve_cashier': forms.HiddenInput, 'is_rejected_cashier': forms.HiddenInput , 'is_checked_cashier': forms.HiddenInput, 'cashier': forms.HiddenInput}
        model = cashPaymentApprovalCashier
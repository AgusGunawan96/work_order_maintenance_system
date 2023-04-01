from django.contrib import admin
from accounting_app.models import cashPaymentBalance, cashPayment, cashPaymentApprovalCashier
import datetime

# Register your models here.
class AuthorAccountingCashPaymentBalance(admin.ModelAdmin):
    list_display = ('cashPayment_balance_no','month','balance_cashPayment_close', 'balance_cashPayment_open', 'exchange_rate_close', 'exchange_rate_open', )
    def month(self, obj):
        return datetime.datetime.strptime(obj.cashPayment_balance_no, '%Y%m')

class AuthorAccountingCashPayment(admin.ModelAdmin):
    search_fields = ['ticket_no', 'remark', 'settle', 'adv',]
    list_display = ('ticket_no', 'created_at','updated_at','remark', 'settle', 'adv', 'debit', 'kredit', )

    def debit(self, obj):
        if(obj.is_debit):
            debit = obj.rp_total
        else:
            debit = 0
        return debit
    
    def kredit(self, obj):
        if(obj.is_credit):
            kredit = obj.rp_total
        else:
            kredit = 0
        return kredit
    
admin.site.register(cashPaymentBalance, AuthorAccountingCashPaymentBalance)
admin.site.register(cashPayment, AuthorAccountingCashPayment)
admin.site.register(cashPaymentApprovalCashier)
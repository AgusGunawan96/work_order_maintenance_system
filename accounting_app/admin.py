from django.contrib import admin
from accounting_app.models import cashPaymentBalance
import datetime

# Register your models here.
class AuthorAccounting(admin.ModelAdmin):
    list_display = ('cashPayment_balance_no','month','balance_cashPayment_close', 'balance_cashPayment_open', 'exchange_rate_close', 'exchange_rate_open', )
    def month(self, obj):
        return datetime.datetime.strptime(obj.cashPayment_balance_no, '%Y%m')

admin.site.register(cashPaymentBalance, AuthorAccounting)

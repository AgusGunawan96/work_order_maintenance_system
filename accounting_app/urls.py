from django.urls import path
from accounting_app import views
from django.conf.urls.static import static
from django.conf import settings

app_name ='accounting_app'

urlpatterns = [
    path('dashboard/', views.dashboard, name = 'accounting_dashboard'),
    path('cashPayment', views.cashPayment_index, name = 'cashPayment_index'),
    path('cashReceived', views.cashReceived_index, name='cashReceived_index'),
    path('Advance', views.advance_index, name = 'advance_index'),
    path('settle', views.cashPayment_settle_index, name = "cashPayment_settle_index"),
    path('adv', views.cashPayment_adv_index, name = "cashPayment_adv_index"),

    # CASHPAYMENT START
    path('cashPayment/add/', views.cashPayment_add, name='cashPayment_add'),
    path('cashPayment/add_debit/', views.cashPayment_debit_add, name='cashPayment_debit_add'),
    path('cashPayment/add_settle/', views.cashPayment_settle_add, name='cashPayment_settle_add'),
    path('cashPayment/add_adv/', views.cashPayment_adv_add, name='cashPayment_adv_add'),
    path('cashPayment/cashPayment_detail/<int:cashPayment_id>', views.cashPayment_detail, name='cashPayment_detail'),
    path('cashPayment/cashPayment_monitoring/', views.cashPayment_monitoring, name='cashPayment_monitoring'),

    path('cashPayment/cashPayment_manager_checked/<int:cashPayment_id>', views.cashPayment_manager_check, name='cashPayment_manager_check'),
    path('cashPayment/cashPayment_manager_approve/<int:cashPayment_id>', views.cashPayment_manager_approve, name='cashPayment_manager_approve'),
    path('cashPayment/cashPayment_manager_reject/<int:cashPayment_id>', views.cashPayment_manager_reject, name='cashPayment_manager_reject'),

    path('cashPayment/cashPayment_accounting_manager_checked/<int:cashPayment_id>', views.cashPayment_accounting_manager_check, name='cashPayment_accounting_manager_check'),
    path('cashPayment/cashPayment_accounting_manager_approve/<int:cashPayment_id>', views.cashPayment_accounting_manager_approve, name='cashPayment_accounting_manager_approve'),
    path('cashPayment/cashPayment_accounting_manager_reject/<int:cashPayment_id>', views.cashPayment_accounting_manager_reject, name='cashPayment_accounting_manager_reject'),

    path('cashPayment/cashPayment_president_checked/<int:cashPayment_id>', views.cashPayment_president_check, name='cashPayment_president_check'),
    path('cashPayment/cashPayment_president_approve/<int:cashPayment_id>', views.cashPayment_president_approval, name='cashPayment_president_approve'),
    path('cashPayment/cashPayment_president_reject/<int:cashPayment_id>', views.cashPayment_president_reject, name='cashPayment_president_reject'),

    path('cashPayment/cashPayment_cashier_checked/<int:cashPayment_id>', views.cashPayment_cashier_check, name='cashPayment_cashier_check'),
    path('cashPayment/cashPayment_cashier_approve/<int:cashPayment_id>', views.cashPayment_cashier_approval, name='cashPayment_cashier_approve'),
    path('cashPayment/cashPayment_cashier_reject/<int:cashPayment_id>', views.cashPayment_cashier_reject, name='cashPayment_cashier_reject'),

    path('cashPayment/accoounting_cashPayment_report/<int:cashPayment_id>', views.accounting_cashPayment_report, name='accounting_cashPayment_report'),

    # CASHPAYMENT END

    # CASHRECEIVED END
    path('cashReceived/add/', views.cashReceived_add, name='cashReceived_add'),
    path('cashReceived/add_debit/', views.cashReceived_debit_add, name='cashPayment_debit_add'),
    path('cashReceived/add_settle/', views.cashPayment_settle_add, name='cashPayment_settle_add'),
    path('cashReceived/add_adv/', views.cashPayment_adv_add, name='cashPayment_adv_add'),
    path('cashReceived/cashPayment_detail/<int:cashPayment_id>', views.cashPayment_detail, name='cashPayment_detail'),
    path('cashReceived/cashPayment_monitoring/', views.cashPayment_monitoring, name='cashPayment_monitoring'),

    path('cashReceived/cashPayment_manager_checked/<int:cashPayment_id>', views.cashPayment_manager_check, name='cashPayment_manager_check'),
    path('cashReceived/cashPayment_manager_approve/<int:cashPayment_id>', views.cashPayment_manager_approve, name='cashPayment_manager_approve'),
    path('cashReceived/cashPayment_manager_reject/<int:cashPayment_id>', views.cashPayment_manager_reject, name='cashPayment_manager_reject'),

    path('cashReceived/cashPayment_accounting_manager_checked/<int:cashPayment_id>', views.cashPayment_accounting_manager_check, name='cashPayment_accounting_manager_check'),
    path('cashReceived/cashPayment_accounting_manager_approve/<int:cashPayment_id>', views.cashPayment_accounting_manager_approve, name='cashPayment_accounting_manager_approve'),
    path('cashReceived/cashPayment_accounting_manager_reject/<int:cashPayment_id>', views.cashPayment_accounting_manager_reject, name='cashPayment_accounting_manager_reject'),

    path('cashReceived/cashPayment_president_checked/<int:cashPayment_id>', views.cashPayment_president_check, name='cashPayment_president_check'),
    path('cashReceived/cashPayment_president_approve/<int:cashPayment_id>', views.cashPayment_president_approval, name='cashPayment_president_approve'),
    path('cashReceived/cashPayment_president_reject/<int:cashPayment_id>', views.cashPayment_president_reject, name='cashPayment_president_reject'),

    path('cashReceived/cashPayment_cashier_checked/<int:cashPayment_id>', views.cashPayment_cashier_check, name='cashPayment_cashier_check'),
    path('cashReceived/cashPayment_cashier_approve/<int:cashPayment_id>', views.cashPayment_cashier_approval, name='cashPayment_cashier_approve'),
    path('cashReceived/cashPayment_cashier_reject/<int:cashPayment_id>', views.cashPayment_cashier_reject, name='cashPayment_cashier_reject'),

    path('cashReceived/accoounting_cashPayment_report/<int:cashPayment_id>', views.accounting_cashPayment_report, name='accounting_cashPayment_report'), 
    # CASHRECEIVED START

     # CASHRECEIVED END

    # ADVANCE START
    path('advance/advaance_detail/<int:cashPayment_id>', views.advance_detail, name='advance_detail'),
    path('advance/advance_monitoring/', views.advance_monitoring, name='advance_monitoring'),
    path('advance/add/', views.advance_add, name='advance_add'),
    path('advance/advance_manager_checked/<int:cashPayment_id>', views.advance_manager_check, name='advance_manager_check'),
    path('advance/advance_manager_approve/<int:cashPayment_id>', views.advance_manager_approve, name='advance_manager_approve'),
    path('advance/advance_manager_reject/<int:cashPayment_id>', views.advance_manager_reject, name='advance_manager_reject'),
    path('advance/advance_accounting_manager_checked/<int:cashPayment_id>', views.advance_accounting_manager_check, name='advance_accounting_manager_check'),
    path('advance/advance_accounting_manager_approve/<int:cashPayment_id>', views.advance_accounting_manager_approve, name='advance_accounting_manager_approve'),
    path('advance/advance_accounting_manager_reject/<int:cashPayment_id>', views.advance_accounting_manager_reject, name='advance_accounting_manager_reject'),
    path('advance/advance_president_checked/<int:cashPayment_id>', views.advance_president_check, name='advance_president_check'),
    path('advance/advance_president_approve/<int:cashPayment_id>', views.advance_president_approval, name='advance_president_approve'),
    path('advance/advance_president_reject/<int:cashPayment_id>', views.advance_president_reject, name='advance_president_reject'),
    path('advance/advance_cashier_checked/<int:cashPayment_id>', views.advance_cashier_check, name='advance_cashier_check'),
    path('advance/advance_cashier_approve/<int:cashPayment_id>', views.advance_cashier_approval, name='advance_cashier_approve'),
    path('advance/advance_cashier_reject/<int:cashPayment_id>', views.advance_cashier_reject, name='advance_cashier_reject'),
    path('advance/accounting_advance_report/<int:cashPayment_id>', views.accounting_advance_report, name='accounting_advance_report'),
    # ADVANCE END

    path('cashPayment/cashPayment_download_csv', views.export_cashPayment_csv, name = 'cashPayment_download_csv'),
    path('cashPayment/export_cashPayment_csv', views.export_cashPayment_csv, name = 'export_cashPayment_csv'),
    path('cashPayment/export_cashPayment_xls', views.export_cashPayment_xls, name = 'export_cashPayment_xls'),
    # IMPORT START
    # path('cashPayment/import_cashPayment', views.CreateCashPayment, name='CreateCashPayment'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

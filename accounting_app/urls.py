from django.urls import path
from accounting_app import views

app_name ='accounting_app'

urlpatterns = [
    path('', views.dashboard, name = 'dashboard'),
    path('cashPayment', views.cashPayment_index, name = 'cashPayment_index'),
    path('cashPayment/add/', views.cashPayment_add, name='cashPayment_add'),
    path('cashPayment/add_debit/', views.cashPayment_debit_add, name='cashPayment_debit_add'),
    path('cashPayment/add_settle/', views.cashPayment_settle_add, name='cashPayment_settle_add'),
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
    path('cashPayment/cashPayment_download_csv', views.export_cashPayment_csv, name = 'cashPayment_download_csv'),
    path('cashPayment/export_cashPayment_csv', views.export_cashPayment_csv, name = 'export_cashPayment_csv'),
    path('cashPayment/export_cashPayment_xls', views.export_cashPayment_xls, name = 'export_cashPayment_xls'),
    # IMPORT START
    # path('cashPayment/import_cashPayment', views.CreateCashPayment, name='CreateCashPayment'),
]

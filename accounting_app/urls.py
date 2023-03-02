from django.urls import path
from accounting_app import views

app_name ='accounting_app'

urlpatterns = [
    path('', views.dashboard, name = 'dashboard'),
    path('cashPayment', views.cashPayment_index, name = 'cashPayment_index'),
    path('cashPayment/add/', views.cashPayment_add, name='cashPayment_add'),
    path('cashPayment/cashPayment_detail/<int:cashPayment_id>', views.cashPayment_detail, name='cashPayment_detail'),
    path('cashPayment/cashPayment_manager_approve/<int:cashPayment_id>', views.cashPayment_manager_approve, name='cashPayment_manager_approve'),
    path('cashPayment/cashPayment_manager_reject/<int:cashPayment_id>', views.cashPayment_manager_reject, name='cashPayment_manager_reject'),
    path('cashPayment/cashPayment_accounting_manager_approve/<int:cashPayment_id>', views.cashPayment_accounting_manager_approve, name='cashPayment_accounting_manager_approve'),
    path('cashPayment/cashPayment_accounting_manager_reject/<int:cashPayment_id>', views.cashPayment_accounting_manager_reject, name='cashPayment_accounting_manager_reject'),
    path('cashPayment/cashPayment_president_approve/<int:cashPayment_id>', views.cashPayment_president_approval, name='cashPayment_president_approve'),
    path('cashPayment/cashPayment_president_reject/<int:cashPayment_id>', views.cashPayment_president_reject, name='cashPayment_president_reject'),
    path('cashPayment/cashPayment_cashier_approve/<int:cashPayment_id>', views.cashPayment_cashier_approval, name='cashPayment_cashier_approve'),
    path('cashPayment/cashPayment_cashier_reject/<int:cashPayment_id>', views.cashPayment_cashier_reject, name='cashPayment_cashier_reject'),
]

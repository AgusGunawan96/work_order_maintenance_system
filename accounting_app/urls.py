from django.urls import path
from accounting_app import views

app_name ='accounting_app'

urlpatterns = [
    path('', views.dashboard, name = 'dashboard'),
    path('cashPayment', views.cashPayment_index, name = 'cashPayment_index'),
    path('cashPayment/add/', views.cashPayment_add, name='cashPayment_add'),
]

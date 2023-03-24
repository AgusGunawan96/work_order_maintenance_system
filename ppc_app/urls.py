from django.urls import path
from ppc_app import views

app_name ='ppc_app'

urlpatterns = [
    path('', views.index, name = 'dashboard'),
    path('customerRevice', views.customerRevice_index, name = 'customerRevice_index'),
    path('millingSchedule', views.millingSchedule_index, name = 'millingSchedule_index'),
]

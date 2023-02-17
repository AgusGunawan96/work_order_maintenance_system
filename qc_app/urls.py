from django.urls import path
from qc_app import views

app_name ='qc_app'

urlpatterns = [
    path('', views.index, name = 'index'),
]

from django.urls import path
from ppc_app import views

app_name ='ppc_app'

urlpatterns = [
    path('', views.index, name = 'index'),
]

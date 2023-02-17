from django.urls import path
from master_app import views

app_name ='master_app'

urlpatterns = [
    path('', views.index, name = 'index'),
]

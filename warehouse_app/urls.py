from django.urls import path
from warehouse_app import views

app_name ='warehouse_app'

urlpatterns = [
    path('', views.index, name = 'index'),
]

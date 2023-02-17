from django.urls import path
from sales_app import views

app_name ='sales_app'

urlpatterns = [
    path('', views.index, name = 'index'),
]

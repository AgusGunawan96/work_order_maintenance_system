from django.urls import path
from accounting_app import views

app_name ='accounting_app'

urlpatterns = [
    path('', views.index, name = 'index'),
]

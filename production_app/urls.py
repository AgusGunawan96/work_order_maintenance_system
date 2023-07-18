from django.urls import path
from production_app import views

app_name ='production_app'

urlpatterns = [
    path('', views.index, name = 'index'),
]

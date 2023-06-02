from django.urls import path
from timing_app import views

app_name ='timing_app'

urlpatterns = [
    path('', views.index, name = 'index'),
]

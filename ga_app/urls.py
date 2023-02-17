from django.urls import path
from ga_app import views

app_name ='ga_app'

urlpatterns = [
    path('', views.index, name = 'index'),
]

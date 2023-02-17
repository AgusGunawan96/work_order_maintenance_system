from django.urls import path
from engineering_app import views

app_name ='engineering_app'

urlpatterns = [
    path('', views.index, name = 'index'),
]

from django.urls import path
from it_app import views

app_name ='it_app'

urlpatterns = [
    path('', views.index, name = 'index'),
]

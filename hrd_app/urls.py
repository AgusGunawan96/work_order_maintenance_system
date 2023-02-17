from django.urls import path
from hrd_app import views

app_name ='hrd_app'

urlpatterns = [
    path('', views.index, name = 'index'),
]

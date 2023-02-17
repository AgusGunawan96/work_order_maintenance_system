from django.urls import path
from costcontrol_app import views

app_name ='costcontrol_app'

urlpatterns = [
    path('', views.index, name = 'index'),
]

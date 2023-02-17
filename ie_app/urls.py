from django.urls import path
from ie_app import views

app_name ='ie_app'

urlpatterns = [
    path('', views.index, name = 'index'),
]

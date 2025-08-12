# sfc_2/urls.py
from django.urls import path
from django.http import HttpResponse

def sfc_2_index(request):
    return HttpResponse("SFC 2 App - Under Development")

app_name = 'sfc_2'

urlpatterns = [
    path('', sfc_2_index, name='index'),
]
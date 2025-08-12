# POSEIWA/urls.py
# Buat file ini jika belum ada atau replace isinya jika ada

from django.urls import path
from django.http import HttpResponse

# Temporary view untuk POSEIWA jika belum ada views
def poseiwa_index(request):
    return HttpResponse("POSEIWA App - Under Development")

app_name = 'POSEIWA'

urlpatterns = [
    # Temporary URL pattern untuk mencegah error
    path('', poseiwa_index, name='index'),
    
    # Tambahkan URL patterns lain untuk POSEIWA di sini jika diperlukan
    # path('dashboard/', views.dashboard, name='dashboard'),
    # path('reports/', views.reports, name='reports'),
]
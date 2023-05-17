from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def index(request):
    
    return render(request, 'hrd_app/index.html')

# BIODATA START
def biodata_index(request):
    return HttpResponse('Biodata Index')
# BIODATA END

# CUTI START
def cuti_index(request):
    return HttpResponse('Cuti Index')
# CUTI END

# KESEJAHTERAAN START
def kesejahteraan_index(request):
    return HttpResponse('kesejahteraan Index')
# KESEJAHTERAAN END

# MEDICAL TRAIN START
def medical_train_index(request):
    return HttpResponse('Medical Train Index')

def medical_train_download_report(request):
    return render(request, 'hrd_app/medical_train_download_report.html')

def medical_add(request):
    return HttpResponse('Merupakan Medical Add')

def medical_submit_atasan(request, medical_id):
    return HttpResponse('merupakan Submit dari atasan, Apakah Approve atau Reject')

def medical_submit_hr(request, medical_id):
    return HttpResponse('Merupakan Submit dari HR, Apakah Approve atau Reject')

# MEDICAL TRAIN END
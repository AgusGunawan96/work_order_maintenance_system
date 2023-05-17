from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.http import Http404, HttpResponse, JsonResponse
import datetime
import csv
import xlwt
from dateutil.relativedelta import relativedelta
from csv import reader
from hrd_app.models import medicalApprovalForeman, medicalApprovalHR, medicalApprovalList, medicalApprovalManager, medicalApprovalSupervisor, medicalAttachment, medicalClaimStatus, medicalDetailDokter, medicalDetailInformation, medicalDetailPasienKeluarga, medicalHeader, medicalHubungan, medicalJenisMelahirkan, medicalJenisPelayanan, medicalTempatPelayanan
from hrd_app.forms import medicalHeaderForms, medicalAttachmentForms, medicalStatusKlaimForms, medicalDataKeluargaForms, medicalPemberiLayananForms, medicalApprovalForeman
from django.http import HttpResponse
# Create your views here.
def index(request):
    return render(request, 'hrd_app/index.html')

# BIODATA START
@login_required
def biodata_index(request):
    return HttpResponse('Biodata Index')
# BIODATA END


@login_required# CUTI START
def cuti_index(request):
    return HttpResponse('Cuti Index')
# CUTI END


@login_required# KESEJAHTERAAN START
def kesejahteraan_index(request):
    return HttpResponse('kesejahteraan Index')
# KESEJAHTERAAN END


@login_required# MEDICAL TRAIN START
def medical_train_index(request):
    return HttpResponse('Medical Train Index')

@login_required
def medical_train_download_report(request):
    return render(request, 'hrd_app/medical_train_download_report.html')

@login_required
def medical_add(request):
    return HttpResponse('Merupakan Medical Add')

@login_required
def medical_submit_atasan(request, medical_id):
    return HttpResponse('merupakan Submit dari atasan, Apakah Approve atau Reject')

@login_required
def medical_submit_hr(request, medical_id):
    return HttpResponse('Merupakan Submit dari HR, Apakah Approve atau Reject')

# MEDICAL TRAIN END
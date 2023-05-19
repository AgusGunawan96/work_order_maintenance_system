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
from hrd_app.forms import medicalHeaderForms, medicalAttachmentForms, medicalStatusKlaimForms, medicalDataKeluargaForms, medicalPemberiLayananForms, medicalPelayananKesehatanForms
from django.http import HttpResponse
# Create your views here.
def index(request):
    return render(request, 'hrd_app/index.html')

# BIODATA START
@login_required
def biodata_index(request):
    return HttpResponse('Biodata Index')
# BIODATA END

# CUTI START
@login_required
def cuti_index(request):
    return HttpResponse('Cuti Index')
# CUTI END

# KESEJAHTERAAN START
@login_required
def kesejahteraan_index(request):
    return HttpResponse('kesejahteraan Index')
# KESEJAHTERAAN END

# MEDICAL TRAIN START
@login_required
def medical_train_index(request):
    medical = medicalHeader.objects.all()
    context = {
        'medical'  : medical,
    }
    return render(request, 'hrd_app/medical_train_index.html', context)

@login_required
def medical_train_download_report(request):
    return render(request, 'hrd_app/medical_train_download_report.html')

@login_required
def medical_train_add(request):
    if request.method == "POST":
        medical_form = medicalHeaderForms(data=request.POST)
        if medical_form.is_valid():
            return redirect('hrd_app:medical_train_index')
        else:
            print(medical_form.errors)
    else:
        medical_header = medicalHeaderForms()
        medical_data_keluarga = medicalDataKeluargaForms()
        medical_pemberi_layananan = medicalPemberiLayananForms()
        medical_pelayanan_kesehatan = medicalPelayananKesehatanForms()
        medical_status_claim    = medicalStatusKlaimForms()
        medical_attachment      = medicalAttachmentForms()
    context = {
        'medical_header_form'  :medical_header ,
        'medical_data_keluarga_form'  :medical_data_keluarga ,
        'medical_pemberi_layanan_form'  :medical_pemberi_layananan ,
        'medical_pelayanan_kesehatan_form'  :medical_pelayanan_kesehatan ,
        'medical_status_claim_form'  :medical_status_claim ,
        'medical_attachment_form'  :medical_attachment ,
    }
    return render(request, 'hrd_app/medical_train_add.html', context)

@login_required
def medical_train_detail(request, medical_id):
    medical_header                  = medicalHeader.objects.get(pk=medical_id)
    medical_detail_pasien_keluarga  = medicalDetailPasienKeluarga.objects.filter(medical_id=medical_header).first()
    medical_dokter                  = medicalDetailDokter.objects.filter(medical_id = medical_header)
    medical_detail_information      = medicalDetailInformation.objects.filter(medical_id = medical_header)
    medical_claim_status            = medicalClaimStatus.objects.filter(medical_id = medical_header)
    medical_attachment              = medicalAttachment.objects.filter(medical_id = medical_header).values('attachment')
    
    context = {
        'medical_header'                    :   medical_header,
        'medical_detail_pasien_keluarga'    :   medical_detail_pasien_keluarga,
        'medical_dokter'                    :   medical_dokter,
        'medical_detail_information'        :   medical_detail_information,
        'medical_claim_status'              :   medical_claim_status,
        'medical_attachment'                :   medical_attachment,
    }
    return render(request, 'hrd_app/medical_train_detail.html', context)

@login_required
def medical_submit_atasan(request, medical_id):
    return HttpResponse('merupakan Submit dari atasan, Apakah Approve atau Reject')
    return render(request, 'hrd_app/medical_train_add.html', context)

@login_required
def medical_submit_hr(request, medical_id):
    return HttpResponse('Merupakan Submit dari HR, Apakah Approve atau Reject')

# MEDICAL TRAIN END
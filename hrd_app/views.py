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
from hrd_app.forms import medicalHeaderForms, medicalAttachmentForms, medicalStatusKlaimForms, medicalDataKeluargaForms, medicalPemberiLayananForms, medicalPelayananKesehatanForms, medicalReasonForemanForms, medicalReasonHRForms, medicalReasonManagerForms, medicalReasonSupervisorForms
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
    medical_approval_list       = medicalApprovalList.objects.filter(user_id = request.user).first()
    medical_header              = medicalHeader.objects.filter(user_id = request.user).order_by('-id')
    # Kondisi Approval 
    if medical_approval_list:
        if medical_approval_list.is_foreman:
            medical_approval_foreman    = medicalApprovalForeman.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(is_approve = False).filter(is_reject = False).order_by('-id')
        if medical_approval_list.is_supervisor:
            medical_approval_supervisor = medicalApprovalSupervisor.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(is_approve = False).filter(is_reject = False).order_by('-id')
        if medical_approval_list.is_manager:
            medical_approval_manager    = medicalApprovalManager.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(is_approve = False).filter(is_reject = False).order_by('-id')
        if medical_approval_list.is_hr:
            medical_approval_hr         = medicalApprovalHR.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(is_approve = False).filter(is_reject = False).order_by('-id')
    else:
        medical_approval_foreman    = None
        medical_approval_supervisor = None
        medical_approval_manager    = None
        medical_approval_hr         = None

    context = {
        'medical_header'                : medical_header,
        'medical_approval_foreman'      : medical_approval_foreman, 
        'medical_approval_supervisor'   : medical_approval_supervisor, 
        'medical_approval_manager'      : medical_approval_manager, 
        'medical_approval_hr'           : medical_approval_hr, 
        'medical_approval_list'         : medical_approval_list,
    }
        
    return render(request, 'hrd_app/medical_train_index.html', context)

@login_required
def medical_train_complete_index(request):
    return HttpResponse('jadi ini merupakan kondisi complete Train ')

@login_required
def medical_train_reject_index(request):
    return HttpResponse('jadi ini merupakan kondisi reject Train')

@login_required
def medical_train_download_report(request, medical_id):
    medical_header                  = medicalHeader.objects.get(pk=medical_id)
    medical_detail_pasien_keluarga  = medicalDetailPasienKeluarga.objects.filter(medical_id=medical_header).first()
    medical_dokter                  = medicalDetailDokter.objects.filter(medical_id = medical_header).first()
    medical_detail_information      = medicalDetailInformation.objects.filter(medical_id = medical_header).first()
    medical_claim_status            = medicalClaimStatus.objects.filter(medical_id = medical_header).first()
    medical_attachment              = medicalAttachment.objects.filter(medical_id = medical_header).values('attachment')
    context = {
        'medical_header'                    :   medical_header,
        'medical_detail_pasien_keluarga'    :   medical_detail_pasien_keluarga,
        'medical_dokter'                    :   medical_dokter,
        'medical_detail_information'        :   medical_detail_information,
        'medical_claim_status'              :   medical_claim_status,
        'medical_attachment'                :   medical_attachment,
    }
    return render(request, 'hrd_app/medical_train_download_report.html', context)

@login_required
def medical_train_add(request):
    if request.method == "POST":
        medical_header_form                 = medicalHeaderForms(data=request.POST)
        medical_data_keluarga_form          = medicalDataKeluargaForms(data=request.POST)
        medical_pemberi_layanan_form        = medicalPemberiLayananForms(data=request.POST)     
        medical_pelayanan_kesehatan_form    = medicalPelayananKesehatanForms(data=request.POST)
        medical_status_claim_form           = medicalStatusKlaimForms(data=request.POST)
        medical_attachment_form             = medicalAttachmentForms(data=request.POST)
        if medical_header_form.is_valid() and medical_pemberi_layanan_form.is_valid() and medical_pelayanan_kesehatan_form.is_valid() and medical_status_claim_form.is_valid() and medical_attachment_form.is_valid():
            #Save apa yang sudah di post
            medical_header = medical_header_form.save(commit=False)
            medical_data_keluarga = medical_data_keluarga_form.save(commit=False)
            medical_pemberi_layanan = medical_pemberi_layanan_form.save(commit=False)
            medical_pelayanan_kesehatan = medical_pelayanan_kesehatan_form.save(commit=False)
            medical_status_claim = medical_status_claim_form.save(commit=False)
            # Simpan data data yang ada sudah ada
            medical_maks = medicalHeader.objects.filter(medical_no__contains=datetime.datetime.now().strftime('%Y%m')).count() + 1
            medical_no = "MDC" + datetime.datetime.now().strftime('%Y%m') + str("%003d" % ( medical_maks, ))  
            medical_header.medical_no = medical_no   
            medical_header.user = request.user
            medical_header.save()
            if medical_data_keluarga:
                medical_data_keluarga.medical = medical_header
                medical_data_keluarga.save()

            medical_pemberi_layanan.medical = medical_header
            medical_pemberi_layanan.save()

            medical_pelayanan_kesehatan.medical = medical_header
            medical_pelayanan_kesehatan.save()

            medical_status_claim.medical = medical_header
            medical_status_claim.save()
            # Simpan Attachment Apppearance Judgement (Apabila ada)
            files = request.FILES.getlist('attachment')
            for f in files:
                attachment = medicalAttachment(attachment=f)
                attachment.medical = medical_header
                attachment.save()
            # Nanti akan lanjut ke proses approval
            medical_approval_foreman = medicalReasonForemanForms().save(commit=False)
            medical_approval_supervisor = medicalReasonSupervisorForms().save(commit=False)
            medical_approval_manager = medicalReasonManagerForms().save(commit=False)
            medical_approval_hr = medicalReasonHRForms().save(commit=False)
            # Memasukan Nilai medical ke masing masing approval
            medical_approval_foreman.medical = medical_header
            medical_approval_supervisor.medical = medical_header
            medical_approval_manager.medical = medical_header
            medical_approval_hr.medical = medical_header
            # save nilai approval 
            medical_approval_foreman.save()
            medical_approval_supervisor.save()
            medical_approval_manager.save()
            medical_approval_hr.save()
            messages.success(request, 'Medical Train Added')    
            return redirect('hrd_app:medical_train_index')
        
        else:
            print(medical_header_form.errors, medical_pemberi_layanan_form.errors,medical_pelayanan_kesehatan_form.errors,medical_status_claim_form.errors,medical_attachment_form.errors)

    else:
        medical_header              = medicalHeaderForms()
        medical_data_keluarga       = medicalDataKeluargaForms()
        medical_pemberi_layananan   = medicalPemberiLayananForms()
        medical_pelayanan_kesehatan = medicalPelayananKesehatanForms()
        medical_status_claim        = medicalStatusKlaimForms()
        medical_attachment          = medicalAttachmentForms()
    context = {
        'medical_header_form'               :   medical_header ,
        'medical_data_keluarga_form'        :   medical_data_keluarga ,
        'medical_pemberi_layanan_form'      :   medical_pemberi_layananan ,
        'medical_pelayanan_kesehatan_form'  :   medical_pelayanan_kesehatan ,
        'medical_status_claim_form'         :   medical_status_claim ,
        'medical_attachment_form'           :   medical_attachment ,
    }
    return render(request, 'hrd_app/medical_train_add.html', context)
@login_required
def medical_train_delete(request, medical_id):
    HttpResponse('jadi ini merupakan medical Delete')

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
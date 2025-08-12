from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator # tambahan
from django.shortcuts import get_object_or_404 # tambahan
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import check_password
from django.http import Http404, HttpResponse, JsonResponse
from dateutil.parser import parse
from datetime import datetime as dt, timedelta
import datetime, calendar
import csv
import xlwt
from django.db.models import F
from django.db.models.functions import Substr
from dateutil.relativedelta import relativedelta
from csv import reader
from hrd_app.models import medicalApprovalForeman, medicalApprovalHR, medicalApprovalList, medicalApprovalManager, medicalApprovalSupervisor, medicalAttachment, medicalClaimStatus, medicalDetailDokter, medicalDetailInformation, medicalDetailPasienKeluarga, medicalHeader, medicalHubungan, medicalJenisMelahirkan, medicalJenisPelayanan, medicalTempatPelayanan, medicalRemain, medicalLogDownloadAccounting
from master_app.models import UserProfileInfo, Village, Regency, District
from hrd_app.forms import medicalHeaderForms, medicalAttachmentForms, medicalStatusKlaimForms, medicalDataKeluargaForms, medicalPemberiLayananForms, medicalPelayananKesehatanForms, medicalReasonForemanForms, medicalReasonHRForms, medicalReasonManagerForms, medicalReasonSupervisorForms, medicalRejectStatusKlaimForms, RegistrationForm, EditProfileForm, RegistrationUserProfileInfo, RegistrationUserKtp, RegistrationUserKtpNow, FileUploadRemainResetForm
from master_app.views import UpdateRemain
# from escpos.printer import Usb
# from escpos.constants import *
# import usb1
from PIL import Image, ImageWin, ImageDraw
import win32print
import win32print
import win32ui
import win32con
import barcode
from barcode.writer import ImageWriter
from django.utils.dateparse import parse_date
from django.contrib.auth import get_user_model
import os
from django.conf import settings
from django.utils import timezone
from django.core.paginator import Paginator

# import usb.core
# import usb.util
# import ctypes
import locale
# Create your views here.
def index(request):
    return render(request, 'hrd_app/index.html')

# BIODATA START
@login_required
def biodata_index(request):
    biodata_user    = User.objects.all()
    context = {
        'biodata_user'  : biodata_user,
    }
        
    return render(request, 'hrd_app/biodata_index.html', context)

@login_required
def biodata_detail(request, user_id):
    biodata_user_detail = User.objects.get(pk=user_id)
    context = {
        'user_detail'   : biodata_user_detail
    }
    return render(request, 'hrd_app/biodata_detail.html', context)
    return HttpResponse('ini merupakan user Detail')

@login_required
def biodata_add(request):
    User = get_user_model()
    if request.method == "POST":
        return HttpResponse('ini merupakan POST')
    else:
        context = {
            'user_form'             : RegistrationForm(),
            'userprofileinfo_form'  : RegistrationUserProfileInfo(),
            'ktp_form'              : RegistrationUserKtp(),
            'ktpnow_form'           : RegistrationUserKtpNow(),

        }
        return render(request, 'hrd_app/biodata_add.html', context)
        return HttpResponse('ini merupakan add yang bukan detail')

def get_kota_options(request):
    provinsi_id = request.GET.get('province_id')
    # Filter kota options based on selected kota_ktp value
    kotas = Regency.objects.filter(province_id=provinsi_id)
    # Generate HTML for options
    options = '<option value="">---------</option>'
    for kota in kotas:
        options += f'<option value="{kota.id}">{kota.regency_name}</option>'
        
    return JsonResponse(options, safe=False)

def get_kecamatan_options(request):
    kota_id = request.GET.get('regency_id')
    # Filter kecamatan options based on selected kota_ktp value
    kecamatans = District.objects.filter(regency=kota_id)
    
    # Generate HTML for options
    options = '<option value="">---------</option>'
    for kecamatan in kecamatans:
        options += f'<option value="{kecamatan.id}">{kecamatan.district_name}</option>'
        
    return JsonResponse(options, safe=False)

def get_kelurahan_options(request):
    kecamatan_id = request.GET.get('district_id')
    # Filter kelurahan options based on selected kecamatan_ktp value
    kelurahans = Village.objects.filter(district=kecamatan_id)
    
    # Generate HTML for options
    options = '<option value="">---------</option>'
    for kelurahan in kelurahans:
        options += f'<option value="{kelurahan.id}">{kelurahan.village_name}</option>'
        
    return JsonResponse(options, safe=False)
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
# @login_required
# def medical_train_index(request):
#     medical_approval_list       = medicalApprovalList.objects.filter(user_id = request.user).first()
#     medical_header              = medicalHeader.objects.filter(user_id = request.user).order_by('-id')
#     medical_modal               = medicalHeader.objects.order_by('-id')
#     medical_log_accounting      = medicalLogDownloadAccounting.objects.order_by('-id').first()
#     medical_remain_user = medicalRemain.objects.filter(user = request.user).first()
#     medical_atasan = False
#     medical_date = medicalHeader.objects.annotate(
#         year_month=Substr('medical_no', 4, 6)
#     ).values('year_month').distinct().all()
#     year_month_list = [entry['year_month'] for entry in medical_date]
#     yml = []
#     for year_month in year_month_list:
#         year = year_month[:4]
#         month_number = int(year_month[4:])
#         month_name = calendar.month_name[month_number]
#         yml.append(f"{month_name} {year}")

#     if not medical_header:
#         medical_header = None
#     # Kondisi Approval 
#     if medical_approval_list:
#         if medical_approval_list.is_foreman:
#             medical_approval_foreman    = medicalApprovalForeman.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(medical__is_foreman = False).filter(medical__is_supervisor = False).filter(medical__is_manager = False).filter(is_approve = False).filter(is_reject = False).filter(medical__is_reject = False).order_by('-id')
#             medical_approval_reason_foreman = medicalReasonForemanForms()
#             medical_atasan = True
#         else:
#             medical_approval_foreman = None
#             medical_approval_reason_foreman = None

#         if medical_approval_list.is_supervisor:
#             medical_approval_supervisor = medicalApprovalSupervisor.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(medical__is_supervisor = False).filter(medical__is_foreman = False).filter(medical__is_manager = False).filter(is_approve = False).filter(is_reject = False).filter(medical__is_reject = False).order_by('-id')
#             medical_approval_reason_supervisor = medicalReasonSupervisorForms()
#             medical_atasan = True
#         else:
#             medical_approval_supervisor = None
#             medical_approval_reason_supervisor = None

#         if medical_approval_list.is_manager:
#             medical_approval_manager    = medicalApprovalManager.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(medical__is_manager = False).filter(medical__is_foreman = False).filter(medical__is_supervisor = False).filter(is_approve = False).filter(is_reject = False).filter(medical__is_reject = False).order_by('-id')
#             medical_approval_reason_manager = medicalReasonManagerForms()
#             medical_atasan = True
#         else:
#             medical_approval_manager = None
#             medical_approval_reason_manager = None

#         if medical_approval_list.is_hr:
#             medical_approval_hr         = medicalApprovalHR.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(is_approve = False).filter(is_reject = False).filter(medical__is_reject = False).order_by('-id')
#             medical_approval_reason_hr  = medicalReasonHRForms()
#             medical_klaim_status        = medicalStatusKlaimForms()
#             medical_reject_klaim_status = medicalRejectStatusKlaimForms()
#             medical_atasan = True
#         else:
#             medical_approval_hr         = None
#             medical_approval_reason_hr  = None
#             medical_klaim_status        = None
#             medical_reject_klaim_status = None
#     else:
#         medical_approval_foreman            = None
#         medical_approval_supervisor         = None
#         medical_approval_manager            = None
#         medical_approval_hr                 = None
#         medical_approval_reason_foreman     = None
#         medical_approval_reason_supervisor  = None
#         medical_approval_reason_manager     = None
#         medical_approval_reason_hr          = None
#         medical_klaim_status                = None
#         medical_reject_klaim_status         = None
    
#     medical_update_remain                   = FileUploadRemainResetForm()

#     context = {
#         'medical_header'                            : medical_header,
#         'medical_approval_foreman'                  : medical_approval_foreman, 
#         'medical_approval_supervisor'               : medical_approval_supervisor, 
#         'medical_approval_manager'                  : medical_approval_manager, 
#         'medical_approval_hr'                       : medical_approval_hr, 
#         'medical_approval_list'                     : medical_approval_list,
#         'medical_modal'                             : medical_modal,
#         'medical_date'                              : yml,
#         'medical_atasan'                            : medical_atasan,
#         'medical_remain_user'                       : medical_remain_user,
#         'log'                                       : medical_log_accounting,
#         'form_medical_approval_reason_foreman'      : medical_approval_reason_foreman ,
#         'form_medical_approval_reason_supervisor'   : medical_approval_reason_supervisor ,
#         'form_medical_approval_reason_manager'      : medical_approval_reason_manager ,
#         'form_medical_approval_reason_hr'           : medical_approval_reason_hr ,
#         'form_medical_klaim_status'                 : medical_klaim_status ,
#         'form_medical_reject_klaim_status'          : medical_reject_klaim_status,
#         'form_medical_update_remain'          : medical_update_remain,
#     }
        
#     return render(request, 'hrd_app/medical_train_index.html', context)

@login_required
def medical_train_index(request):
    # user = request.user
    # medical_approval_list = medicalApprovalList.objects.filter(user=user).first()

    user = request.user
    medical_approval_list = medicalApprovalList.objects.filter(user=user).first()

    # Ambil informasi pengguna terkait departemen
    user_profile = user.userprofileinfo  # Pastikan ini sesuai dengan relasi model Anda

    # Cek apakah pengguna berada di departemen yang diizinkan akses tanpa batas
    allowed_departments = ['Human Resource & General Affairs', 'Engineering']

    # Ambil nama departemen pengguna
    user_department_name = user_profile.department.department_name if user_profile.department else None

    # Cek apakah departemen pengguna termasuk dalam departemen yang diizinkan
    is_allowed_department = user_department_name in allowed_departments

    # Dapatkan jam saat ini (timezone lokal server)
    current_time = timezone.now()  # Dapatkan waktu lokal
    current_hour = current_time.hour
    current_minute = current_time.minute

    # Logika akses waktu terbatas (menambahkan interval waktu yang diizinkan)
    allowed_times = [
        (6, 0, 7, 0),     # 09:30 - 10:00
        (9, 30, 9, 40),    # 11:40 - 13:00
        (11, 45, 12, 45),     # 14:00 - 14:30
        (14, 5, 14, 15),    # 15:55 - 16:30
        (18, 0, 18, 30),    # 17:50 - 18:30
        (22, 0, 22, 30),    # 19:40 - 20:10
    ]

    # Cek apakah waktu saat ini berada dalam rentang waktu yang diizinkan
    is_within_allowed_time = any(
        (start_hour < current_hour < end_hour) or
        (start_hour == current_hour and current_minute >= start_minute) and
        (end_hour == current_hour and current_minute <= end_minute) or
        (start_hour == current_hour and current_minute >= start_minute and
        end_hour == current_hour and current_minute <= end_minute)
        for start_hour, start_minute, end_hour, end_minute in allowed_times
    )

    # Jika pengguna bukan dari departemen yang diizinkan akses tanpa batas dan tidak dalam waktu akses yang diperbolehkan
    if not is_allowed_department and not is_within_allowed_time:
        return render(request, 'hrd_app/restricted_access.html')  # Halaman tanpa akses

    
    # Gunakan select_related untuk mengurangi query ke database
    medical_header = medicalHeader.objects.filter(user=user).order_by('-id').select_related('hr')[:10]
    medical_modal = medicalHeader.objects.order_by('-id').select_related('hr')[:10]
    medical_log_accounting = medicalLogDownloadAccounting.objects.order_by('-id').first()
    medical_remain_user = medicalRemain.objects.filter(user=user).first()
    
    # Paginate jika data sangat besar
    paginator = Paginator(medical_header, 10)  # 10 items per page
    page_number = request.GET.get('page')
    medical_header_page = paginator.get_page(page_number)
    
    # Optimalisasi distinct query
    medical_date = medicalHeader.objects.annotate(
        year_month=Substr('medical_no', 4, 6)
    ).values_list('year_month', flat=True).distinct()

    yml = []
    for year_month in medical_date:
        year = year_month[:4]
        month_number = int(year_month[4:])
        month_name = calendar.month_name[month_number]
        yml.append(f"{month_name} {year}")

    medical_atasan = False
    if medical_approval_list:
        if medical_approval_list.is_foreman:
            medical_approval_foreman = medicalApprovalForeman.objects.filter(
                medical__is_delete=False, medical__is_complete=False, medical__is_foreman=False,
                medical__is_supervisor=False, medical__is_manager=False, is_approve=False,
                is_reject=False, medical__is_reject=False
            ).order_by('-id')
            medical_approval_reason_foreman = medicalReasonForemanForms()
            medical_atasan = True
        else:
            medical_approval_foreman = None
            medical_approval_reason_foreman = None

        if medical_approval_list.is_supervisor:
            medical_approval_supervisor = medicalApprovalSupervisor.objects.filter(
                medical__is_delete=False, medical__is_complete=False, medical__is_supervisor=False,
                medical__is_foreman=False, medical__is_manager=False, is_approve=False,
                is_reject=False, medical__is_reject=False
            ).order_by('-id')
            medical_approval_reason_supervisor = medicalReasonSupervisorForms()
            medical_atasan = True
        else:
            medical_approval_supervisor = None
            medical_approval_reason_supervisor = None

        if medical_approval_list.is_manager:
            medical_approval_manager = medicalApprovalManager.objects.filter(
                medical__is_delete=False, medical__is_complete=False, medical__is_manager=False,
                medical__is_foreman=False, medical__is_supervisor=False, is_approve=False,
                is_reject=False, medical__is_reject=False
            ).order_by('-id')
            medical_approval_reason_manager = medicalReasonManagerForms()
            medical_atasan = True
        else:
            medical_approval_manager = None
            medical_approval_reason_manager = None

        if medical_approval_list.is_hr:
            medical_approval_hr = medicalApprovalHR.objects.filter(
                medical__is_delete=False, medical__is_complete=False, is_approve=False,
                is_reject=False, medical__is_reject=False
            ).order_by('-id')
            medical_approval_reason_hr = medicalReasonHRForms()
            medical_klaim_status = medicalStatusKlaimForms()
            medical_reject_klaim_status = medicalRejectStatusKlaimForms()
            medical_atasan = True
        else:
            medical_approval_hr = None
            medical_approval_reason_hr = None
            medical_klaim_status = None
            medical_reject_klaim_status = None
    else:
        medical_approval_foreman = None
        medical_approval_supervisor = None
        medical_approval_manager = None
        medical_approval_hr = None
        medical_approval_reason_foreman = None
        medical_approval_reason_supervisor = None
        medical_approval_reason_manager = None
        medical_approval_reason_hr = None
        medical_klaim_status = None
        medical_reject_klaim_status = None
    
    medical_update_remain = FileUploadRemainResetForm()

    context = {
        'medical_header': medical_header_page,  # gunakan paginated medical_header
        'medical_approval_foreman': medical_approval_foreman,
        'medical_approval_supervisor': medical_approval_supervisor,
        'medical_approval_manager': medical_approval_manager,
        'medical_approval_hr': medical_approval_hr,
        'medical_approval_list': medical_approval_list,
        'medical_modal': medical_modal,
        'medical_date': yml,
        'medical_atasan': medical_atasan,
        'medical_remain_user': medical_remain_user,
        'log': medical_log_accounting,
        'form_medical_approval_reason_foreman': medical_approval_reason_foreman,
        'form_medical_approval_reason_supervisor': medical_approval_reason_supervisor,
        'form_medical_approval_reason_manager': medical_approval_reason_manager,
        'form_medical_approval_reason_hr': medical_approval_reason_hr,
        'form_medical_klaim_status': medical_klaim_status,
        'form_medical_reject_klaim_status': medical_reject_klaim_status,
        'form_medical_update_remain': medical_update_remain,
    }

    return render(request, 'hrd_app/medical_train_index.html',context)

@login_required
def medical_train_complete_index(request):
    medical_header = medicalHeader.objects.filter(is_complete = True).order_by('-id')
    context = {
        'medical_header'    : medical_header,
    }
    return render(request, 'hrd_app/medical_train_complete_index.html', context)

@login_required
def medical_train_reject_index(request):
    medical_header = medicalHeader.objects.filter(is_reject = True).order_by('-id')
    context = {
        'medical_header'    : medical_header,
    }
    return render(request, 'hrd_app/medical_train_reject_index.html', context)


@login_required
def medical_train_add(request):
    if request.method == "POST":
        curr_user = request.user
        medical_header_form                 = medicalHeaderForms(data=request.POST)
        medical_data_keluarga_form          = medicalDataKeluargaForms(data=request.POST)
        medical_pemberi_layanan_form        = medicalPemberiLayananForms(data=request.POST)     
        medical_pelayanan_kesehatan_form    = medicalPelayananKesehatanForms(data=request.POST, user=curr_user)
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
            # Pembuatan Approval Massal
                # Nanti akan lanjut ke proses approval
                # medical_approval_foreman = medicalReasonForemanForms().save(commit=False)
                # medical_approval_supervisor = medicalReasonSupervisorForms().save(commit=False)
                # medical_approval_manager = medicalReasonManagerForms().save(commit=False)
                # medical_approval_hr = medicalReasonHRForms().save(commit=False)
                # Memasukan Nilai medical ke masing masing approval
                # medical_approval_foreman.medical = medical_header
                # medical_approval_supervisor.medical = medical_header
                # medical_approval_manager.medical = medical_header
                # medical_approval_hr.medical = medical_header
                # save nilai approval 
                # medical_approval_foreman.save()
                # medical_approval_supervisor.save()
                # medical_approval_manager.save()
                # medical_approval_hr.save()
            # Pembuatan Approval Atasan
            # Nanti akan lanjut ke proses approval
            medical_approval_foreman = medicalReasonForemanForms().save(commit=False)
            medical_approval_supervisor = medicalReasonSupervisorForms().save(commit=False)
            medical_approval_manager = medicalReasonManagerForms().save(commit=False)
            # Memasukan Nilai medical ke masing masing approval
            medical_approval_foreman.medical = medical_header
            medical_approval_supervisor.medical = medical_header
            medical_approval_manager.medical = medical_header
            # save nilai approval 
            medical_approval_foreman.save()
            medical_approval_supervisor.save()
            medical_approval_manager.save()

            medical_print_atasan(None, int(medical_header.id))
            messages.success(request, 'Medical Train Added')    
            return redirect('hrd_app:medical_train_index')
        
        else:
            print(medical_header_form.errors, medical_pemberi_layanan_form.errors,medical_pelayanan_kesehatan_form.errors,medical_status_claim_form.errors,medical_attachment_form.errors)

    else:
        curr_user = request.user
        medical_header              = medicalHeaderForms()
        medical_data_keluarga       = medicalDataKeluargaForms(request.POST or None, user=curr_user)
        # return HttpResponse(medical_data_keluarga)
        medical_pemberi_layananan   = medicalPemberiLayananForms()
        medical_pelayanan_kesehatan = medicalPelayananKesehatanForms(request.POST or None, user=curr_user)
        medical_status_claim        = medicalStatusKlaimForms()
        medical_attachment          = medicalAttachmentForms()  
        medical_remain_user         = medicalRemain.objects.filter(user = request.user).first()
        value_without_commas        = str( medical_remain_user.remain).replace(',', '')
    context = {
        'medical_header_form'               :   medical_header ,
        'medical_data_keluarga_form'        :   medical_data_keluarga ,
        'medical_pemberi_layanan_form'      :   medical_pemberi_layananan ,
        'medical_pelayanan_kesehatan_form'  :   medical_pelayanan_kesehatan ,
        'medical_status_claim_form'         :   medical_status_claim ,
        'medical_attachment_form'           :   medical_attachment ,
        'value_without_commas'              :   value_without_commas,
        'medical_remain_user'               :   medical_remain_user,
    }
    return render(request, 'hrd_app/medical_train_add.html', context)

@login_required
def medical_train_complete(request, medical_id):
    medical_approval = medicalApprovalList.objects.filter(user = request.user).first()
    medical = medicalHeader.objects.get(pk = medical_id)
    medical.is_complete = True
    medical.hr = medical_approval
    medical.save()
    messages.success(request, 'Medical Train '+ medical.medical_no +' Completed')
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def medical_train_delete(request, medical_id):
    medical = medicalHeader.objects.get(pk = medical_id)
    medical.is_delete = True
    medical.save()
    messages.success(request, 'Medical Train '+ medical.medical_no +' Deleted')
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def medical_train_detail(request, medical_id):
    medical_approval_list       = medicalApprovalList.objects.filter(user_id = request.user).first()
    medical_header                  = medicalHeader.objects.get(pk=medical_id)
    medical_detail_pasien_keluarga  = medicalDetailPasienKeluarga.objects.filter(medical_id=medical_header).first()
    medical_dokter                  = medicalDetailDokter.objects.filter(medical_id = medical_header).first()
    medical_detail_information      = medicalDetailInformation.objects.filter(medical_id = medical_header).first()
    medical_claim_status            = medicalClaimStatus.objects.filter(medical_id = medical_header).first()
    medical_attachment              = medicalAttachment.objects.filter(medical_id = medical_header).values('attachment')
    medical_foreman                 = medicalApprovalForeman.objects.filter(medical_id = medical_header).first()
    medical_supervisor              = medicalApprovalSupervisor.objects.filter(medical_id = medical_header).first()
    medical_manager                 = medicalApprovalManager.objects.filter(medical_id = medical_header).first()
    medical_hr                      = medicalApprovalHR.objects.filter(medical_id = medical_header).first()

    if not medical_foreman:
        medical_foreman = None
    if not medical_supervisor:
        medical_supervisor = None
    if not medical_manager:
        medical_manager = None
    if not medical_hr:
        medical_hr      = None

    if medical_approval_list:
        if medical_approval_list.is_foreman:
            medical_approval_foreman    = medicalApprovalForeman.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(medical__is_foreman = False).filter(medical__is_supervisor = False).filter(medical__is_manager = False).filter(is_approve = False).filter(is_reject = False).filter(medical__is_reject = False).filter(medical_id = medical_header.id).first()
            medical_approval_reason_foreman = medicalReasonForemanForms()
        else:
            medical_approval_foreman = None
            medical_approval_reason_foreman = None

        if medical_approval_list.is_supervisor:
            medical_approval_supervisor = medicalApprovalSupervisor.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(medical__is_supervisor = False).filter(medical__is_foreman = False).filter(medical__is_manager = False).filter(is_approve = False).filter(is_reject = False).filter(medical__is_reject = False).filter(medical_id = medical_header.id).first()
            medical_approval_reason_supervisor = medicalReasonSupervisorForms()
        else:
            medical_approval_supervisor = None
            medical_approval_reason_supervisor = None

        if medical_approval_list.is_manager:
            medical_approval_manager    = medicalApprovalManager.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(medical__is_manager = False).filter(medical__is_foreman = False).filter(medical__is_supervisor = False).filter(is_approve = False).filter(is_reject = False).filter(medical__is_reject = False).filter(medical_id = medical_header.id).first()
            medical_approval_reason_manager = medicalReasonManagerForms()
        else:
            medical_approval_manager = None
            medical_approval_reason_manager = None

        if medical_approval_list.is_hr:
            medical_approval_hr         = medicalApprovalHR.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(is_approve = False).filter(is_reject = False).filter(medical__is_reject = False).filter(medical_id = medical_header.id).first()
            medical_approval_reason_hr  = medicalReasonHRForms()
            medical_klaim_status        = medicalStatusKlaimForms()
            medical_reject_klaim_status = medicalRejectStatusKlaimForms()
        else:
            medical_approval_hr         = None
            medical_approval_reason_hr  = None
            medical_klaim_status        = None
            medical_reject_klaim_status = None
    else:
        medical_approval_foreman            = None
        medical_approval_supervisor         = None
        medical_approval_manager            = None
        medical_approval_hr                 = None
        medical_approval_reason_foreman     = None
        medical_approval_reason_supervisor  = None
        medical_approval_reason_manager     = None
        medical_approval_reason_hr          = None
        medical_klaim_status                = None
        medical_reject_klaim_status         = None

    context = {
        'medical_header'                            :   medical_header,
        'medical_detail_pasien_keluarga'            :   medical_detail_pasien_keluarga,
        'medical_dokter'                            :   medical_dokter,
        'medical_detail_information'                :   medical_detail_information,
        'medical_claim_status'                      :   medical_claim_status,
        'medical_attachment'                        :   medical_attachment,
        'medical_foreman'                           :   medical_foreman,
        'medical_supervisor'                        :   medical_supervisor,
        'medical_manager'                           :   medical_manager,
        'medical_hr'                                :   medical_hr,
        'form_medical_approval_reason_hr'           :   medical_approval_reason_hr ,
        'form_medical_klaim_status'                 :   medical_klaim_status ,
        'form_medical_reject_klaim_status'          :   medical_reject_klaim_status,
        'medical_approval_foreman'                  :   medical_approval_foreman, 
        'medical_approval_supervisor'               :   medical_approval_supervisor, 
        'medical_approval_manager'                  :   medical_approval_manager, 
        'medical_approval_hr'                       :   medical_approval_hr, 
        'medical_approval_list'                     :   medical_approval_list,
        'form_medical_approval_reason_foreman'      :   medical_approval_reason_foreman ,
        'form_medical_approval_reason_supervisor'   :   medical_approval_reason_supervisor ,
        'form_medical_approval_reason_manager'      :   medical_approval_reason_manager ,
    }
    return render(request, 'hrd_app/medical_train_detail.html', context)

@login_required
def medical_submit_atasan(request, medical_id, is_approve, is_reject):
    medical_approval = medicalApprovalList.objects.filter(user = request.user).first()
    if is_approve == 'True':
        # Approve Foreman
        foreman =  medicalApprovalForeman.objects.filter(medical_id = medical_id).first()
        if foreman and medical_approval.is_foreman:
            foreman.is_approve = True
            foreman.foreman = medical_approval
            foreman.save()
            # Approve Medical apabila Foreman
            medical = medicalHeader.objects.get(pk=medical_id)
            medical.is_foreman = True
            medical.save()
        # Approve Supervisor
        supervisor = medicalApprovalSupervisor.objects.filter(medical_id = medical_id).first()
        if supervisor and medical_approval.is_supervisor:
            supervisor.is_approve = True
            supervisor.supervisor = medical_approval
            supervisor.save()
            # Approve Medical apabila Supervisor
            medical = medicalHeader.objects.get(pk=medical_id)
            medical.is_supervisor = True
            medical.save()
        # Approve Manager
        manager = medicalApprovalManager.objects.filter(medical_id = medical_id).first()
        if manager and medical_approval.is_manager:
            manager.is_approve = True
            manager.manager = medical_approval
            manager.save()
            # Approve Medical apavbila manager
            medical = medicalHeader.objects.get(pk=medical_id)
            medical.is_manager = True
            medical.save()

        # Membuat Approval HR
        medical_approval_hr = medicalReasonHRForms().save(commit=False)
        medical = medicalHeader.objects.get(pk=medical_id)
        medical_approval_hr.medical = medical
        medical_approval_hr.save()

        messages.success(request, 'Medical Train Approved')    
        return redirect('hrd_app:medical_train_index')
    elif is_reject == 'True':
        # Reject Foreman
        foreman =  medicalApprovalForeman.objects.filter(medical_id = medical_id).first()
        if foreman and medical_approval.is_foreman:
            foreman.is_reject = True
            foreman.foreman = medical_approval
            foreman.save()
            # Approve Medical apabila Foreman
            medical = medicalHeader.objects.get(pk=medical_id)
            medical.is_foreman = True
            medical.is_reject  = True
            medical.save()
            # Reject Reason Foreman
            medical_foreman_reject_form = medicalReasonForemanForms(data=request.POST, instance=foreman)
            medical_foreman_reject = medical_foreman_reject_form.save(commit=False)
            medical_foreman_reject.save(

            )
        # Reject Supervisor
        supervisor = medicalApprovalSupervisor.objects.filter(medical_id = medical_id).first()
        if supervisor and medical_approval.is_supervisor:
            supervisor.is_reject = True
            supervisor.supervisor = medical_approval
            supervisor.save()
            # Approve Medical apabila Supervisor
            medical = medicalHeader.objects.get(pk=medical_id)
            medical.is_supervisor = True
            medical.is_reject     = True
            medical.save()
            # Reject Supervisor Reason
            medical_supervisor_reject_form = medicalReasonSupervisorForms(data=request.POST, instance=supervisor)
            medical_supervisor_reject = medical_supervisor_reject_form.save(commit=False)
            medical_supervisor_reject.save()
        # Reject manager
        manager = medicalApprovalManager.objects.filter(medical_id = medical_id).first()
        if manager and medical_approval.is_manager:
            manager.is_reject = True
            manager.manager = medical_approval
            manager.save()
            # Approve Medical apavbila manager
            medical = medicalHeader.objects.get(pk=medical_id)
            medical.is_manager = True
            medical.is_reject  = True
            medical.save()
            # Reject Manager Reason
            medical_manager_reject_form = medicalReasonManagerForms(data=request.POST, instance=manager)
            medical_manager_reject = medical_manager_reject_form.save(commit=False)
            medical_manager_reject.save()

        messages.success(request, 'Medical Train Rejected')    
        return redirect('hrd_app:medical_train_index')
    # jadi ini merupakan approval yang berisikan di Approve atau reject
    # return render(request, 'hrd_app/medical_train_add.html', context)

@login_required
def medical_submit_hr(request, medical_id, is_approve, is_reject):
    medical_approval = medicalApprovalList.objects.filter(user = request.user).first()
    medical_header = medicalHeader.objects.get(pk = medical_id)
    medical_info = medicalDetailInformation.objects.filter(medical_id = medical_header.id).first()

    if is_approve == 'True':
        # Approve HR
        hr = medicalApprovalHR.objects.filter(medical_id = medical_id).first()
        if hr and medical_approval.is_hr:
            hr.is_approve = True
            hr.hr = medical_approval
            hr.save()
        # Mengubah klaim status menjadi lengkap
        medical_claim_status = medicalClaimStatus.objects.filter(medical_id = medical_id).first()
        if medical_claim_status and medical_approval.is_hr:
            medical_claim_status.is_lengkap = True
            medical_claim_status.save()
        # Mengubah is_complete yang False menjadi True
        medical_header = medicalHeader.objects.get(pk = medical_id)
        if medical_header:
            medical_header.is_complete = True
            medical_header.save()
        # Menambahkan used dan mengurangi remain dan menambahkan kondisi apabila rawat jalan 
        if medical_info.jenis_pelayanan == 'Rawat Jalan':
            medical_remain = medicalRemain.objects.filter(user = medical_header.user).first()
            medical_remain.used += medical_header.rp_total
            medical_remain.remain -= medical_header.rp_total
            medical_remain.save()

        messages.success(request, 'Medical Train Verified')
        return redirect('hrd_app:medical_train_index')
    elif is_reject == 'True':
        # get Data Approval HR dan Klaim status
        medical_train_approval_hr = medicalApprovalHR.objects.filter(medical_id = medical_id).first()
        medical_train_klaim_status = medicalClaimStatus.objects.filter(medical_id = medical_id).first()
        # Memasukan data dari HR
        medical_reject_hr_form = medicalReasonHRForms(data=request.POST, instance = medical_train_approval_hr)
        medical_reject_hr = medical_reject_hr_form.save(commit=False)
        medical_reject_hr.save()
        # Mengubah Klaim Status
        medical_claim_status_form = medicalRejectStatusKlaimForms(data=request.POST, instance = medical_train_klaim_status)
        medical_claim_status_reject = medical_claim_status_form.save(commit=False)
        medical_claim_status_reject.save()
        # Reject dari HR
        hr = medicalApprovalHR.objects.filter(medical_id = medical_id).first()
        if hr and medical_approval.is_hr:
            hr.is_reject = True
            hr.hr = medical_approval
            hr.save()
        # Reject dari Medical
        medical_header = medicalHeader.objects.get(pk = medical_id)
        if medical_header:
            medical_header.is_reject = True
            medical_header.save()
        messages.success(request, 'Medical Train Rejected')
        return redirect('hrd_app:medical_train_index')

    return HttpResponse('Merupakan Submit dari HR, Apakah Approve atau Reject')

@login_required
def medical_train_download_report(request, medical_id):
    medical_header                  = medicalHeader.objects.get(pk=medical_id)
    medical_detail_pasien_keluarga  = medicalDetailPasienKeluarga.objects.filter(medical_id=medical_header).first()
    medical_dokter                  = medicalDetailDokter.objects.filter(medical_id = medical_header).first()
    medical_detail_information      = medicalDetailInformation.objects.filter(medical_id = medical_header).first()
    medical_claim_status            = medicalClaimStatus.objects.filter(medical_id = medical_header).first()
    medical_attachment              = medicalAttachment.objects.filter(medical_id = medical_header).values('attachment')
    medical_foreman                 = medicalApprovalForeman.objects.filter(medical_id = medical_header).first()
    medical_supervisor              = medicalApprovalSupervisor.objects.filter(medical_id = medical_header).first()
    medical_manager                 = medicalApprovalManager.objects.filter(medical_id = medical_header).first()
    medical_hr                      = medicalApprovalHR.objects.filter(medical_id = medical_header).first()

    if not medical_foreman:
        medical_foreman = None
    if not medical_supervisor:
        medical_supervisor = None
    if not medical_manager:
        medical_manager = None
    if not medical_hr:
        medical_hr      = None

    context = {
        'medical_header'                    :   medical_header,
        'medical_detail_pasien_keluarga'    :   medical_detail_pasien_keluarga,
        'medical_dokter'                    :   medical_dokter,
        'medical_detail_information'        :   medical_detail_information,
        'medical_claim_status'              :   medical_claim_status,
        'medical_attachment'                :   medical_attachment,
        'medical_foreman'                   :   medical_foreman,
        'medical_supervisor'                :   medical_supervisor,
        'medical_manager'                   :   medical_manager,
        'medical_hr'                        :   medical_hr,
    }
    return render(request, 'hrd_app/medical_train_download_report.html', context)


def medical_print_atasan(request, medical_id):
    # Specify the printer name or provide the full printer path
    medical_header = medicalHeader.objects.get(pk=medical_id)
    assignee = UserProfileInfo.objects.filter(id=medical_header.user.id).first()
    remain   = medicalRemain.objects.filter(user_id=medical_header.user.id).first()
    ip_address = "172.16.202.72"
    name = "EPSON TM-T82 Receipt"

    # printer_name = r"\\" + ip_address + "\\" + name
    printer_name = name

    try:
        # Open a connection to the printer
        printer_handle = win32print.OpenPrinter(printer_name)

        # Create a new print job
        win32print.StartDocPrinter(printer_handle, 1, ("Sample Receipt", None, "RAW"))

        try:
            # Start the page
            win32print.StartPagePrinter(printer_handle)

            # Set the font size
            font_size_command = b'\x1B\x21\x08'  # Set font size to double-width and double-height
            win32print.WritePrinter(printer_handle, font_size_command)

            # Print the receipt content
            content = "MY SEIWA Medical Train\n"
            content += "------------------------------\n"
            content += medical_header.medical_no + "\n"
            content += medical_header.created_at.strftime("%Y-%m-%d %H:%M") + "\n"
            content += "------------------------------\n"
            content += "Name         : " + medical_header.user.first_name +" "+ medical_header.user.last_name + "\n"
            content += "No. Karyawan : " + medical_header.user.username + "\n"
            content += "Department   : " + assignee.department.department_name + "\n"
            content += "------------------------------\n"

            # Format the total as IDR manually
            total_formatted = "IDR " + "{:,.2f}".format(medical_header.rp_total)
            total_formatted_remain = "IDR " + "{:,.2f}".format(remain.remain)
            content += "Remain Berobat      : " + total_formatted_remain + "\n"
            content += "Total biaya berobat : " + total_formatted + "\n"

            # Calculate the remaining space needed for justification
            max_line_length = 48  # Maximum line length for your printer
            lines = content.split('\n')
            justified_content = ''
            for line in lines:
                remaining_space = max_line_length - len(line)
                justified_line = line + ' ' * remaining_space
                justified_content += justified_line + '\n'

            # Print the justified content
            win32print.WritePrinter(printer_handle, justified_content.encode("ascii"))

            # # Generate and print the barcode
            barcode_data = medical_header.medical_no
            barcode_image = barcode.Code128(barcode_data, writer=ImageWriter())
            barcode_image.save('barcode')

            # printer_name = win32print.GetDefaultPrinter ()
            file_name = "barcode.png"

            # Add some space
            # space_command = b'\n\n'  # Two line breaks
            # win32print.WritePrinter(printer_handle, space_command)

            # Send the automatic cut command
            # cut_command = b'\x1D\x56\x42\x00'  # Full cut command
            # win32print.WritePrinter(printer_handle, cut_command)

            # End the page
            win32print.EndPagePrinter(printer_handle)
        finally:
            # End the print job
            win32print.EndDocPrinter(printer_handle)
    except Exception as e:
        return HttpResponse("Error printing receipt: {}".format(str(e)))
    finally:
        # Close the printer connection
        Flag = print_barcode(file_name)
        if Flag == False:
            # Open a connection to the printer
            printer_handle = win32print.OpenPrinter(printer_name)

            # Create a new print job
            win32print.StartDocPrinter(printer_handle, 1, ("Sample Receipt", None, "RAW"))
            win32print.StartPagePrinter(printer_handle)
            # Add some space
            space_command = b'\n\n'  # Two line breaks
            win32print.WritePrinter(printer_handle, space_command)

            # Send the automatic cut command
            cut_command = b'\x1D\x56\x42\x00'  # Full cut command
            win32print.WritePrinter(printer_handle, cut_command)
            win32print.EndDocPrinter(printer_handle)

        win32print.ClosePrinter(printer_handle)

    return redirect('hrd_app:medical_train_index')

def print_barcode(file_name):
    try:
        printer_name = win32print.GetDefaultPrinter()
        hDC = win32ui.CreateDC ()
        hDC.CreatePrinterDC(printer_name)
        # printer_size = hDC.GetDeviceCaps (PHYSICALWIDTH), hDC.GetDeviceCaps (PHYSICALHEIGHT)
        bmp = Image.open (file_name)
        if bmp.size[0] < bmp.size[1]:
          bmp = bmp.rotate (90)
        hDC.StartDoc (file_name)
        hDC.StartPage ()
        dib = ImageWin.Dib (bmp)
        dib.draw (hDC.GetHandleOutput (), (0,0,bmp.size[0],bmp.size[1]))
        hDC.EndPage ()
        hDC.EndDoc ()
        hDC.DeleteDC ()
        return True
    except Exception as e:
        return False

@login_required
def medical_train_remain_reset(request):
    medical_remain = medicalRemain.objects.all()
    # Update the values
    medical_remain.update(remain=F('limit'), used=0)
    # Optionally, you can fetch the updated medical_remain
    updated_records = medical_remain.values()
    # Return the updated records or any other response
    return redirect('hrd_app:medical_train_index')

def handle_uploaded_medicalAttachment_file(file):
    # Specify the destination folder within your Django project's directory structure
    destination_folder = os.path.join(os.path.dirname(__file__), 'templates', 'csv')
    # Create the destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)
    
    # Rename the file to a custom name
    custom_name = 'updateremain.csv'  # Provide your desired custom name here
    
    # Construct the file path where the uploaded file will be saved with the custom name
    file_path = os.path.join(destination_folder, custom_name)
    
    # Open the destination file in write-binary mode
    with open(file_path, 'wb') as destination:
        # Iterate over chunks of the uploaded file and write them to the destination file
        for chunk in file.chunks():
            destination.write(chunk)

@login_required
def medical_train_remain_update(request):
    file = request.FILES.get('file')
    if file:
        # Save the file to the 'MedicalAttachment' folder within the media folder
            # Specify the destination folder within your Django project's directory structure
        handle_uploaded_medicalAttachment_file(file)
        
        # Process the file or perform any other necessary operations
        UpdateRemain(request)
        return redirect('hrd_app:medical_train_index')
        
    
    return HttpResponse('No file found.')

@login_required
def medical_train_remain_download(request):
    # kita akan panggil remain dari medical 
    medical_remain = medicalRemain.objects.filter(limit=F('remain')).all().values_list('id','user__username','marital_status','limit','used','remain')
    # Memanggil RIR dari tahun awal sampai tahun akhir
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=MedicalTrainCashBack.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('MedicalTrainAccounting', cell_overwrite_ok=True) # this will make a sheet named Users Data
    
    # Dimulai dari Row 1
    row_num = 1
    font_style_bold = xlwt.XFStyle()
    font_style_bold.font.bold = True
    columns = ['No. Karyawan','Marital Status','Limit','Used','Remain']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style_bold) # at 0 row 0 column 
    #Format Currency
    currency_idr = xlwt.XFStyle()
    currency_idr.num_format_str = f'#,##0.00'
    # masuk kedalam body
    font_style = xlwt.XFStyle()
    # Body dari excel laporan yang akan dibuat
    for body in medical_remain:
            # Kita akan panggil setiap model yang ada di HR
            row_num += 1
            row = [
                body[1],
                body[2],
                body[3],
                body[4],
                body[5],
            ]
            for col_num in range(len(row)):
                if col_num==2 or col_num==3 or col_num==4:
                    ws.write(row_num, col_num, row[col_num], currency_idr)
                else:
                    ws.write(row_num, col_num, row[col_num], font_style)
        
    wb.save(response)
    return response
    return HttpResponse('jadi ini pembuatan report untuk download Accounting')


@login_required
def medical_train_download_report_excel(request):
    # kita akan panggil header dari medical 
    medical_header = medicalHeader.objects.all().values_list('id','medical_no','created_at','rp_total','user__first_name','user__last_name','is_foreman','is_supervisor','is_manager','is_complete', 'is_reject')
    # Memanggil RIR dari tahun awal sampai tahun akhir
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=MedicalTrain.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('MedicalTrain', cell_overwrite_ok=True) # this will make a sheet named Users Data
    
    # Dimulai dari Row 1
    row_num = 1
    font_style_bold = xlwt.XFStyle()
    font_style_bold.font.bold = True
    columns = ['Medical No','Tanggal dibuat','Diserahkan Oleh','Mengetahui Atasan ybs','Diterima Oleh', 'Anggota Keluarga', 'Nama Anggota Keluarga', 'Hubungan Keluarga', 'Jenis Kelamin', 'Tanggal lahir keluarga', 'Nama Dokter', 'Tempat Pelayanan', 'Nama Tempat', 'Alamat', 'No Telp. Pelayanan', 'Jenis Pelayanan', 'Melahirkan', 'Jenis Persalinan', 'Tanggal Berobat Mulai', 'Tanggal Berobat Selesai', 'Diagnosa', 'Kelengkapan','Status']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style_bold) # at 0 row 0 column 

    # masuk kedalam body
    font_style = xlwt.XFStyle()
    # Body dari excel laporan yang akan dibuat
    for body in medical_header:
        # Kita akan panggil setiap model yang ada di HR
        medical_detail_pasien_keluarga  = medicalDetailPasienKeluarga.objects.filter(medical_id = body[0]).first()
        medical_dokter                  = medicalDetailDokter.objects.filter(medical_id = body[0]).first()
        medical_detail_information      = medicalDetailInformation.objects.filter(medical_id = body[0]).first()
        medical_claim_status            = medicalClaimStatus.objects.filter(medical_id = body[0]).first()
        medical_foreman                 = medicalApprovalForeman.objects.filter(medical_id = body[0]).first()
        medical_supervisor              = medicalApprovalSupervisor.objects.filter(medical_id = body[0]).first()
        medical_manager                 = medicalApprovalManager.objects.filter(medical_id = body[0]).first()
        medical_hr                      = medicalApprovalHR.objects.filter(medical_id = body[0]).first()
        
        # Akan membuat none apabila tidak ada
        if not medical_foreman:
            medical_foreman = None
        if not medical_supervisor:
            medical_supervisor = None
        if not medical_manager:
            medical_manager = None
        if not medical_hr:
            medical_hr = None

        # Membuat kondisi apabila diketahui oleh atasan 
        if body[6]:
            atasan = medical_foreman.foreman.user.first_name +' '+ medical_foreman.foreman.user.last_name
        elif body[7]:
            atasan = medical_supervisor.supervisor.user.first_name +' '+ medical_supervisor.supervisor.user.last_name
        elif body[8]:
            atasan = medical_manager.manager.user.first_name +' '+ medical_manager.manager.user.last_name
        else:
            atasan = '-'

        
        # Membuat kondisi apabiula diketahui oleh HR
        if medical_hr:
            if not medical_hr.hr == None:
                hr = medical_hr.hr.user.first_name +' '+medical_hr.hr.user.last_name
            else:
                hr = '-'
        else:
            hr = '-'

        #Konversi tanggal yang ada di database
        if body[2]:
            tanggal_dibuat = body[2].strftime("%d-%m-%Y")

        # Cek apakah keluarga atau bukan yang sedang di klaim
        if medical_detail_pasien_keluarga.keluarga:
            is_keluarga = 'Yes'
            nama_pasien = medical_detail_pasien_keluarga.keluarga.nama_lengkap
            hubungan = medical_detail_pasien_keluarga.keluarga.hubungan
            jenis_kelamin = medical_detail_pasien_keluarga.keluarga.gender
            tanggal_lahir_keluarga = medical_detail_pasien_keluarga.keluarga.tanggal_lahir.strftime("%d-%m-%Y")
        else:
            is_keluarga = 'No'
            nama_pasien = '-'
            hubungan    = '-'
            jenis_kelamin = '-'
            tanggal_lahir_keluarga = '-'

        # kondisi melahirkan
        if medical_detail_information.melahirkan:
            melahirkan = 'Yes'
        else:
            melahirkan = 'No'
        # Kondisi kelengkapan
        if medical_claim_status.is_lengkap and medical_claim_status.tidak_lengkap == '':
            kelengkapan = 'Dokumen sudah lengkap'
        elif body[10] :
            kelengkapan = medical_claim_status.tidak_lengkap
        else:
            kelengkapan = '-'
        # Kondisi status
        if body[9] == True:
            status = 'Completed'
        elif body[10] == True:
            status = 'Rejected'
        else:
            status = 'Waiting for Approval'

        row_num += 1
        row = [
            body[1],
            tanggal_dibuat,
            body[4] +' '+ body[5],
            atasan,
            hr,
            is_keluarga,
            nama_pasien,
            hubungan,
            jenis_kelamin,
            tanggal_lahir_keluarga,
            medical_dokter.nama_dokter,
            medical_dokter.tempat_pelayanan,
            medical_dokter.nama_tempat,
            medical_dokter.alamat,
            medical_dokter.no_telp,
            medical_detail_information.jenis_pelayanan,
            melahirkan,
            medical_detail_information.melahirkan,
            medical_detail_information.tanggal_berobat_mulai.strftime("%d-%m-%Y"),
            medical_detail_information.tanggal_berobat_selesai.strftime("%d-%m-%Y"),
            medical_detail_information.diagnosa,
            kelengkapan,
            status,
        ]
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    
    wb.save(response)
    return response
    return HttpResponse('ini adalah report yang akan diexcel')

def convert_month_year_to_ym(month_year):
    # Parse the input string as a date
    date_obj = parse(month_year)
    
    # Format the date object to the desired output format
    year_month = date_obj.strftime("%Y%m")
    
    return year_month

@login_required 
def medical_train_download_daterange_accounting(request):
    start_date_str = request.POST.get('id_startdate')
    end_date_str = request.POST.get('id_enddate')
    # Check if either start or end date is empty:

    date_format = '%m/%d/%Y'

    
    if not (start_date_str and end_date_str):
        raise ValueError("Both 'start_date' and 'end_date' must be provided.")

    # Parse dates into datetime objects:
    start_datetime = dt.strptime(start_date_str, date_format).date()
    end_datetime = dt.strptime(end_date_str, date_format).date()

   # Check if either date could not be parsed correctly:
    if not (start_datetime and end_datetime):
       raise ValueError("Invalid format for one of the input datetimes.")

    log_obj = medicalLogDownloadAccounting(
        start_date=start_datetime,
        end_date=end_datetime,
        user=request.user
    )
    
    log_obj.save()

    start_date = request.POST['id_startdate']
    end_date   = request.POST['id_enddate']
    if start_date and end_date:
        start_datetime = dt.strptime(start_date, '%m/%d/%Y')
        end_datetime = dt.strptime(end_date, '%m/%d/%Y') + timedelta(days=1)
        medical_header = medicalHeader.objects.filter(is_complete = True, updated_at__range=[start_datetime, end_datetime]).all().values_list('id','medical_no','user__first_name','user__last_name','user__username','user__userprofileinfo__department__department_name','user__userprofileinfo__section__section_name', 'rp_total')
    else:
        medical_header = medicalHeader.objects.all()
    # Memanggil RIR dari tahun awal sampai tahun akhir
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=MedicalTrainAccounting.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('MedicalTrainAccounting', cell_overwrite_ok=True) # this will make a sheet named Users Data
    
    # Dimulai dari Row 1
    row_num = 1
    font_style_bold = xlwt.XFStyle()
    font_style_bold.font.bold = True
    columns = ['Medical No','Nama','No. Karyawan','Department','Section','RP Total']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style_bold) # at 0 row 0 column 
    #Format Currency
    currency_idr = xlwt.XFStyle()
    currency_idr.num_format_str = f'#,##0.00'
    # masuk kedalam body
    font_style = xlwt.XFStyle()
    # Body dari excel laporan yang akan dibuat
    for body in medical_header:
            # Kita akan panggil setiap model yang ada di HR
            row_num += 1
            row = [
                body[1],
                body[2] + " " +body[3],
                body[4],
                body[5],
                body[6],
                body[7],

            ]
            for col_num in range(len(row)):
                if col_num==5:
                    ws.write(row_num, col_num, row[col_num], currency_idr)
                else:
                    ws.write(row_num, col_num, row[col_num], font_style)
        
    wb.save(response)
    return response
    return HttpResponse('jadi ini pembuatan report untuk download Accounting')
    return HttpResponse(request.POST['id_enddate'])

@login_required
def medical_train_download_accounting(request):
    month_year = request.POST['id_yearmonth']
    year_month = convert_month_year_to_ym(month_year)
    # kita akan panggil header dari medical 
    medical_header = medicalHeader.objects.filter(is_complete = True, medical_no__contains=year_month).all().values_list('id','medical_no','user__first_name','user__last_name','user__username','user__userprofileinfo__department__department_name','user__userprofileinfo__section__section_name', 'rp_total')
    # Memanggil RIR dari tahun awal sampai tahun akhir
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=MedicalTrainAccounting.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('MedicalTrainAccounting', cell_overwrite_ok=True) # this will make a sheet named Users Data
    
    # Dimulai dari Row 1
    row_num = 1
    font_style_bold = xlwt.XFStyle()
    font_style_bold.font.bold = True
    columns = ['Medical No','Nama','No. Karyawan','Department','Section','RP Total']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style_bold) # at 0 row 0 column 
    #Format Currency
    currency_idr = xlwt.XFStyle()
    currency_idr.num_format_str = f'#,##0.00'
    # masuk kedalam body
    font_style = xlwt.XFStyle()
    # Body dari excel laporan yang akan dibuat
    for body in medical_header:
            # Kita akan panggil setiap model yang ada di HR
            row_num += 1
            row = [
                body[1],
                body[2] + " " +body[3],
                body[4],
                body[5],
                body[6],
                body[7],

            ]
            for col_num in range(len(row)):
                if col_num==5:
                    ws.write(row_num, col_num, row[col_num], currency_idr)
                else:
                    ws.write(row_num, col_num, row[col_num], font_style)
        
    wb.save(response)
    return response
    return HttpResponse('jadi ini pembuatan report untuk download Accounting')

# MEDICAL TRAIN END
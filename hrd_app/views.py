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
from hrd_app.forms import medicalHeaderForms, medicalAttachmentForms, medicalStatusKlaimForms, medicalDataKeluargaForms, medicalPemberiLayananForms, medicalPelayananKesehatanForms, medicalReasonForemanForms, medicalReasonHRForms, medicalReasonManagerForms, medicalReasonSupervisorForms, medicalRejectStatusKlaimForms
from escpos.printer import Usb
from escpos.constants import *
import usb1
import win32print
import usb.core
import usb.util
import ctypes

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
    medical_modal               = medicalHeader.objects.order_by('-id')
    if not medical_header:
        medical_header = None
    # Kondisi Approval 
    if medical_approval_list:
        if medical_approval_list.is_foreman:
            medical_approval_foreman    = medicalApprovalForeman.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(medical__is_foreman = False).filter(is_approve = False).filter(is_reject = False).filter(medical__is_reject = False).order_by('-id')
            medical_approval_reason_foreman = medicalReasonForemanForms()
        else:
            medical_approval_foreman = None
            medical_approval_reason_foreman = None

        if medical_approval_list.is_supervisor:
            medical_approval_supervisor = medicalApprovalSupervisor.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(medical__is_supervisor = False).filter(is_approve = False).filter(is_reject = False).filter(medical__is_reject = False).order_by('-id')
            medical_approval_reason_supervisor = medicalReasonSupervisorForms()
        else:
            medical_approval_supervisor = None
            medical_approval_reason_supervisor = None

        if medical_approval_list.is_manager:
            medical_approval_manager    = medicalApprovalManager.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(medical__is_manager = False).filter(is_approve = False).filter(is_reject = False).filter(medical__is_reject = False).order_by('-id')
            medical_approval_reason_manager = medicalReasonManagerForms()
        else:
            medical_approval_manager = None
            medical_approval_reason_manager = None

        if medical_approval_list.is_hr:
            medical_approval_hr         = medicalApprovalHR.objects.filter(medical__is_delete = False).filter(medical__is_complete = False).filter(is_approve = False).filter(is_reject = False).filter(medical__is_reject = False).order_by('-id')
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
        'medical_header'                            : medical_header,
        'medical_approval_foreman'                  : medical_approval_foreman, 
        'medical_approval_supervisor'               : medical_approval_supervisor, 
        'medical_approval_manager'                  : medical_approval_manager, 
        'medical_approval_hr'                       : medical_approval_hr, 
        'medical_approval_list'                     : medical_approval_list,
        'medical_modal'                             : medical_modal,
        'form_medical_approval_reason_foreman'      : medical_approval_reason_foreman ,
        'form_medical_approval_reason_supervisor'   : medical_approval_reason_supervisor ,
        'form_medical_approval_reason_manager'      : medical_approval_reason_manager ,
        'form_medical_approval_reason_hr'           : medical_approval_reason_hr ,
        'form_medical_klaim_status'                 : medical_klaim_status ,
        'form_medical_reject_klaim_status'          : medical_reject_klaim_status,
    }
        
    return render(request, 'hrd_app/medical_train_index.html', context)

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


@login_required
def medical_print_atasan(request):
 # Specify the printer name or provide the full printer path
    #printer_name = "EPSON TM-T82 Receipt"
    ip_address = "172.16.202.72"
    name = "EPSON TM-T82 Receipt"

    printer_name = r"\\"+ip_address+"\\"+name
    try:
        # Open a connection to the printer
        printer_handle = win32print.OpenPrinter(printer_name)

        # Create a new print job
        win32print.StartDocPrinter(printer_handle, 1, ("Sample Receipt", None, "RAW"))

        try:
            # Start the page
            win32print.StartPagePrinter(printer_handle)

            # Print the receipt content
            content = "MY SEIWA Medical Train\n"
            content += "------------------------------\n"
            content += "Item\t\tQty\tPrice\n"
            content += "------------------------------\n"
            content += "Item 1\t\t1\t$10.00\n"
            content += "Item 2\t\t2\t$5.00\n"
            content += "------------------------------\n"
            content += "Total:\t\t\t$20.00\n"
            content += "------------------------------\n"

            win32print.WritePrinter(printer_handle, content.encode("utf-8"))

            # Add some space
            space_command = b'\n\n\n\n'  # Four line breaks
            win32print.WritePrinter(printer_handle, space_command)
            # Send the automatic cut command
            cut_command = b'\x1D\x56\x42\x00'  # Full cut command
            win32print.WritePrinter(printer_handle, cut_command)


            # End the page
            win32print.EndPagePrinter(printer_handle)
        finally:
            # End the print job
            win32print.EndDocPrinter(printer_handle)
    except Exception as e:
        return HttpResponse("Error printing receipt: {}".format(str(e)))
    finally:
        # Close the printer connection
        win32print.ClosePrinter(printer_handle)

    return HttpResponse("Receipt printed successfully!")


# @login_required
# def medical_print_atasan(request):
#     # Replace with the vendor ID and product ID of your Epson TM-T82 printer
#     vendor_id = 0x04B8
#     product_id = 0x0E27

#     # Find the USB device based on vendor ID and product ID
#     device = usb.core.find(idVendor=vendor_id, idProduct=product_id)

#     if device is None:
#         return HttpResponse("USB device not found.")

#     try:
#         # Set the active configuration of the device
#         device.set_configuration()
        
#         # Claim the interface
#         usb.util.claim_interface(device, 0)

#         # Set the printer properties (you may need to adjust these based on your printer's settings)
#         # Note: These settings might not be applicable to the Epson TM-T82 printer, please adjust accordingly.
#         device.write(1, b'\x1B\x40')  # Initialize printer
#         device.write(1, b'\x1B\x61\x01')  # Center alignment
#         device.write(1, b'\x1B\x21\x30')  # Set font size to double-width and double-height

#         # Print the receipt content
#         device.write(1, b'Sample Receipt\n')
#         device.write(1, b'------------------------------\n')
#         device.write(1, b'Item\t\tQty\tPrice\n')
#         device.write(1, b'------------------------------\n')
#         device.write(1, b'Item 1\t\t1\t$10.00\n')
#         device.write(1, b'Item 2\t\t2\t$5.00\n')
#         device.write(1, b'------------------------------\n')
#         device.write(1, b'Total:\t\t\t$20.00\n')
#         device.write(1, b'------------------------------\n')

#         # Send the automatic cut command
#         device.write(1, b'\x1D\x56\x41\x10')

#         return HttpResponse("Receipt printed successfully.")
#     except usb.core.USBError as e:
#         return HttpResponse("Error printing receipt: {}".format(str(e)))
#     finally:
#         # Release the claimed interface and reset the active configuration
#         usb.util.release_interface(device, 0)
#         device.reset()

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
        if not medical_hr.hr == None:
            hr = medical_hr.hr.user.first_name +' '+medical_hr.hr.user.last_name
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
# MEDICAL TRAIN END
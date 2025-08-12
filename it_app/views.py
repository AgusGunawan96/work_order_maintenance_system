from django.shortcuts import render, redirect
from it_app.models import Ticket, TicketApprovalSupervisor, TicketApprovalManager, TicketApprovalIT, TicketPriority, TicketStatus, TicketProgressIT, TicketAttachment, IPAddress, Hardware, ITComputerList, ITApprovalList, ITReportH, ITReportD, ITReportDAttachment
from django.contrib.auth.decorators import login_required
from it_app.forms import ticketForms, approvalSupervisorForms, approvalManagerForms, approvalITForms, progressITForms, ticketAttachmentForms, hardwareForms, computerListForms, ITCreateProjectForms, ITCreateTaskForms, ITReportAttachmentForms
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, QueryDict
from django.db.models import Count, F, Value
import datetime
from django.db.models.functions import Concat
import xlwt
from seiwa.models import TabelPemasukan
# from POSEIWA.models import TPo
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from .models import ITReportH
# Create your views here.

# def seiwa(request):
#     # pemasukan = TabelPemasukan.objects.using('seiwa_db').all()
#     # return HttpResponse(pemasukan)
#     tpo = TPo.objects.using('poseiwa_db').filter(status = 'k').all().values('kode_barang')
#     return HttpResponse(tpo)

@login_required
def dashboard(request):
    return render(request, 'it_app/dashboard.html')

@login_required
def profile(request):
    return render(request, 'it_app/profile.html')

# IP ADDRESS START
# @login_required
# def ipAddress_index(request):
#     ipAddress = IPAddress.objects.order_by('-id')
#     context = {
#         'ipAddresses'          : ipAddress, 
#         'form_ipAddress'       : ipAddressForms,
#         }
#     # return HttpResponse('IP Address Index')
#     return render(request, 'it_app/ipAddress_index.html', context)


# @login_required
# def ipAddress_add(request, ipAddress_id):
#     ipAddresses = IPAddress.objects.get(pk=ipAddress_id)
#     if request.method == "POST":
#         ipAddress_form = ipAddressForms(request.POST, instance=ipAddresses)
#         if ipAddress_form.is_valid():
#             ipAddress_register = ipAddress_form.save(commit=False)
#             ipAddress_register.is_used = True
#             ipAddress_register.save()
#     return redirect('it_app:ipAddress_index')

# @login_required
# def ipAddress_unreg(request, ipAddress_id):
#     ipAddresses = IPAddress.objects.get(pk=ipAddress_id)
#     post = request.POST.copy() 
#     post.update({'is_used': False})
#     request.POST = post
#     if request.method == "POST":
#         ipAddress_form = ipAddressForms(request.POST, instance=ipAddresses)
#         if ipAddress_form.is_valid():
#             ipAddress_unregister = ipAddress_form.save(commit=False)
#             ipAddress_unregister.name = ""
#             ipAddress_unregister.is_used = False
#             ipAddress_unregister.save()
#     # return HttpResponse(str(ipAddress_id) + " test")
#     return redirect('it_app:ipAddress_index')
# IP ADDRESS END

# COMPUTER LIST START 

def ipaddress_register(ipAddress_id):
    ipaddress = IPAddress.objects.filter(ip = ipAddress_id).first()
    ipaddress.is_used = True
    ipaddress.save()
    return True

@login_required
def computer_index(request):
    computer  = ITComputerList.objects.order_by('-created_at')
    count_windows_xp   = ITComputerList.objects.filter(os = 'Windows XP').count()
    count_windows_7    = ITComputerList.objects.filter(os = 'Windows 7').count()
    count_windows_8    = ITComputerList.objects.filter(os = 'Windows 8').count()
    count_windows_10   = ITComputerList.objects.filter(os = 'Windows 10').count()
    count_windows_11   = ITComputerList.objects.filter(os = 'Windows 11').count()
    count_oem          = ITComputerList.objects.filter(windows_type = 'OEM').count()  
    count_olp          = ITComputerList.objects.filter(windows_type = 'OLP').count()
    count_mcafee       = ITComputerList.objects.filter(antivirus = 'McAfee').count()
    count_cyber_reason = ITComputerList.objects.filter(antivirus = 'Cyber Reason').count()
    count_office_2003  = ITComputerList.objects.filter(is_office_2003 = True).count()
    count_office_2007  = ITComputerList.objects.filter(is_office_2007 = True).count()
    count_office_2010  = ITComputerList.objects.filter(is_office_2010 = True).count()
    count_office_2016  = ITComputerList.objects.filter(is_office_2016 = True).count()
    count_office_2019  = ITComputerList.objects.filter(is_office_2019 = True).count()

    context = {
        'computers'             : computer,
        'form_computer'         : computerListForms,
        'count_windows_xp'      : count_windows_xp,
        'count_windows_7'       : count_windows_7,
        'count_windows_8'       : count_windows_8,
        'count_windows_10'      : count_windows_10,
        'count_windows_11'      : count_windows_11,
        'count_oem'             : count_oem,
        'count_olp'             : count_olp,
        'count_mcafee'          : count_mcafee,
        'count_cyber_reason'    : count_cyber_reason,
        'count_office_2003'     : count_office_2003,
        'count_office_2007'     : count_office_2007,
        'count_office_2010'     : count_office_2010,
        'count_office_2016'     : count_office_2016,
        'count_office_2019'     : count_office_2019,
        
    }
    return render(request, 'it_app/computer_index.html', context)

@login_required
def computer_add(request):
    if request.method == "POST":
        user = User.objects.annotate(full_name = Concat('first_name',Value(' '),'last_name')).filter(full_name__contains=request.POST.get('user_computer')).first()
        # Create a mutable copy of request.POST
        post_data = request.POST.copy()
        post_data.pop('user_computer', None)
        # Modify the value corresponding to 'my_key'
        post_data['computer_user'] = user
        # Replace the original request POST data with our updated version.
        request.POST = post_data
        computer_form = computerListForms(data=request.POST)
        if computer_form.is_valid():
            computer = computer_form.save(commit=False)
            # Mengubah IP Address menjadi Is Used
            ipaddress_register(computer.ip)
            # Save Cmputer
            computer.save()
            return redirect('it_app:computer_index')
        else:
            print(computer_form.errors)
    else:
        computer_list_form = computerListForms()
    context = {
        'form_computer' : computer_list_form,
    }
    # return HttpResponse('Masuk kedalam menu add')
    return render(request, 'it_app/computer_add.html', context)

@login_required
def computer_download(request):
    # Kita akan panggil Computer
    computer = ITComputerList.objects.all().values_list('ip__ip', 'computer_name', 'os', 'windows_type', 'pc_type__name', 'is_office_2003', 'is_office_2007', 'is_office_2010', 'is_office_2016', 'computer_user__first_name', 'computer_user__last_name', 'computer_user__userprofileinfo__department__department_name', 'is_internet', 'antivirus', 'is_genba')
    # Memanggil RIR dari tahun awal sampai tahun akhir
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=ITListComputer.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('ITListComputer', cell_overwrite_ok=True) # this will make a sheet named Users Data
    # Dimulai dari Row 1
    row_num = 1
    font_style_bold = xlwt.XFStyle()
    font_style_bold.font.bold = True
    columns = ['IP Address','Name Computer','OS','Type OEM/OLM','Type PC','Office','User','Department','Internet','Antivirus','Genba']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style_bold) # at 0 row 0 column 
    # masuk kedalam body
    font_style = xlwt.XFStyle()
    # Body dari excel laporan yang akan dibuat
    for body in computer:
            # Kita akan kondisikan apabila dia office 2003, 2007, 2010, dan 2016
            if body[5]:
                office_2003 = '2003'
            else:
                office_2003 = ''
            if body[6]:
                office_2006 = '2006'
            else:
                office_2006 = ''
            if body[7]:
                office_2010 = '2010'
            else:
                office_2010 = ''
            if body[8]:
                office_2016 = '2016'
            else:
                office_2016 = ''
            
            office = office_2003 + ' ' + office_2006 + ' ' + office_2010+ ' ' + office_2016
            # Kita akan panggil setiap model yang ada di HR
            row_num += 1
            row = [
                body[0],
                body[1],
                body[2],
                body[3],
                body[4],
                office,
                body[9] +" "+ body[10],
                body[11],
                body[12],
                body[13],
                body[14],

            ]
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
        
    wb.save(response)
    return response
# COMPUTER LIST END
# HARDWARE START
@login_required
def hardware_index(request):
    hardware = Hardware.objects.order_by('-created_at')
    context = {
        'hardwares'          : hardware, 
        'form_hardware'      : hardwareForms,
        }
    # return HttpResponse(hardware)
    return render(request, 'it_app/hardware_index.html', context)


@login_required
def hardware_edit(request):
    # return HttpResponse('Hardware Add')
    return render(request, 'it_app/hardware_index.html')

# HARDWARE END
# TICKET START 
@login_required
def ticket_index(request):
    tickets = Ticket.objects.order_by('-created_at')
    supervisors = TicketApprovalSupervisor.objects.order_by('-id')
    managers = TicketApprovalManager.objects.order_by('-id')
    its = TicketApprovalIT.objects.order_by('-id')
    progress = TicketProgressIT.objects.annotate(percentage=F('function_start') / F('function_end')).order_by('-id')
    context = {
        'tickets'           : tickets, 
        'supervisors'       : supervisors, 
        'its'               : its, 
        'managers'          : managers, 
        'progress'          : progress, 
        'form_supervisor'   : approvalSupervisorForms, 
        'form_manager'      : approvalManagerForms, 
        'form_it'           : approvalITForms, 
        'form_progress'     : progressITForms,
        }
    return render(request,'it_app/ticket_index.html', context)

@login_required
def ticket_monitoring(request):
    tickets = Ticket.objects.order_by('created_at')
    current_datetime = datetime.datetime.strftime(datetime.datetime.now(), '%d%m%y')
    context = {
         'tickets'             : tickets,
         'current_datetime'    : current_datetime,
    }
    # return HttpResponse(current_datetime)
    return render(request, 'it_app/ticket_monitoring.html', context)

@login_required
def ticket_add(request):
    if request.method =="POST":
        ticket_form = ticketForms(data=request.POST)
        ticket_attachment_form = ticketAttachmentForms(data=request.POST)
        approval_supervisor_form = approvalSupervisorForms(data=request.POST)
        if ticket_form.is_valid() and approval_supervisor_form.is_valid() and ticket_attachment_form.is_valid():
            # Save IT Ticket
            ticket = ticket_form.save(commit=False)
            ticket.assignee = request.user
            ticket.is_pending = True
            ticket.save()
            # Save attachment
            files = request.FILES.getlist('attachment')
            for f in files:
                 attachment = TicketAttachment(attachment=f)
                 attachment.Ticket = ticket
                 attachment.save()
            # Apabila Manager yang Approve langsung membuat approval manager
            if request.user.userprofileinfo.is_manager:
                #  Membuat Approval Supervisor dengan kondisi True
                supervisor = approval_supervisor_form.save(commit=False)
                supervisor.ticket = ticket
                supervisor.is_approve_supervisor = True
                supervisor.save()
                #  Membuat Approval Manager
                manager = approvalManagerForms().save(commit=False)
                manager.ticket = ticket
                manager.ticket_approval_supervisor = supervisor
                manager.is_approve_manager = True
                manager.save()
            else:    
                # Membuat Approval Supervisor
                supervisor = approval_supervisor_form.save(commit=False)
                supervisor.ticket = ticket
                supervisor.save()
            messages.success(request, 'Success Add Services', 'success')
            return redirect('it_app:ticket_index')
        else:
            print(ticket_form.errors)
        # ticket.save()
    else:
        ticket_form = ticketForms()
        ticket_attachment_form = ticketAttachmentForms()
        approval_supervisor_form = approvalSupervisorForms()
        

    context = {
    'form': ticketForms,
    'supervisor_form': approvalSupervisorForms,
    'ticket_attachment_form': ticketAttachmentForms,
}

    return render(request, 'it_app/ticket_add.html', context)

@login_required
def ticket_detail(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    attachment = TicketAttachment.objects.filter(Ticket_id = ticket_id).values('attachment',)
    context = {
         'ticket'       : ticket,
         'attachment'   : attachment,
    }
    return render(request, 'it_app/ticket_detail.html', context)

@login_required
def ticket_supervisor_approve(request,ticket_id):
    try:
        # mengambil data task yang akan diapprove berdasarkan task id
        supervisor = TicketApprovalSupervisor.objects.get(pk=ticket_id)
        # mengapprove
        supervisor.is_approve_supervisor = True
        supervisor.supervisor = request.user
        supervisor.save()
        #membuat approval manager
        approval_manager_form = approvalManagerForms(data=request.POST)
        manager = approval_manager_form.save(commit=False)
        manager.ticket_approval_supervisor = supervisor
        manager.save()
        # mengeset pesan sukses dan redirect ke halaman daftar task
        messages.success(request, 'Approved Successfully')
        return redirect('it_app:ticket_index')
    except TicketApprovalSupervisor.DoesNotExist:
        # Jika data task tidak ditemukan,
        # maka akan di redirect ke halaman 404 (Page not found).
        raise Http404("Ticket tidak bisa di Approved.")

@login_required
def ticket_supervisor_reject(request,ticket_id):
    # try:
        # mengambil data task yang akan dihapus berdasarkan task id
        supervisor = TicketApprovalSupervisor.objects.get(pk=ticket_id)
        post = request.POST.copy() 
        post.update({'is_rejected_supervisor': True})
        request.POST = post
        approval_supervisor_form = approvalSupervisorForms(request.POST, instance=supervisor)
        if approval_supervisor_form.is_valid():
            reject = approval_supervisor_form.save(commit=False)
            reject.supervisor = request.user
            reject.save()
            return redirect('it_app:ticket_index')
        return HttpResponse(approval_supervisor_form)

@login_required
def ticket_manager_approve(request,ticket_id):
    try:
        # mengambil data task yang akan dihapus berdasarkan task id
        manager = TicketApprovalManager.objects.get(pk=ticket_id)
        # mengapprove
        manager.is_approve_manager = True
        manager.manager = request.user
        manager.save()
        #membuat Approval IT
        approval_it_forms = approvalITForms(data=request.POST)
        it = approval_it_forms.save(commit=False)
        it.ticket_approval_manager = manager
        it.save()
        # mengeset pesan sukses dan redirect ke halaman daftar task
        messages.success(request, 'Approved Successfully')
        return redirect('it_app:ticket_index')
    except TicketApprovalManager.DoesNotExist:
        # Jika data task tidak ditemukan,
        # maka akan di redirect ke halaman 404 (Page not found).
        raise Http404("Ticket tidak bisa di Approved.")

@login_required
def ticket_manager_reject(request,ticket_id):
    # try:
        # mengambil data task yang akan dihapus berdasarkan task id
        manager = TicketApprovalManager.objects.get(pk=ticket_id)
        post = request.POST.copy() 
        post.update({'is_rejected_manager': True})
        request.POST = post
        approval_manager_form = approvalManagerForms(request.POST, instance=manager)
        if approval_manager_form.is_valid():
            reject = approval_manager_form.save(commit=False)
            reject.manager = request.user
            reject.save()
            return redirect('it_app:ticket_index')
        return HttpResponse(approval_manager_form)

@login_required
def ticket_it_approve(request,ticket_id):
    try:
        # mengambil data task yang akan dihapus berdasarkan task id
        its = TicketApprovalIT.objects.get(pk=ticket_id)
        # mengapprove
        its.is_approve_it = True
        its.it = request.user
        its.save()
        #membuat Ticket Progress
        approval_it_forms = progressITForms(data=request.POST)
        ticket_maks = TicketProgressIT.objects.filter(ticket_no__contains=datetime.datetime.now().strftime('%Y%m')).count() + 1
        ticket_no = "HD" + datetime.datetime.now().strftime('%Y%m') + str("%003d" % ( ticket_maks, ))
        it = approval_it_forms.save(commit=False)
        it.ticket_approval_it = its
        it.ticket_no = ticket_no
        ticket = Ticket.objects.filter(id = it.ticket_approval_it.ticket_approval_manager.ticket_approval_supervisor.ticket.id).first()
        ticket.is_pending = False
        ticket.save()
        it.save()
        # mengeset pesan sukses dan redirect ke halaman daftar task
        messages.success(request, 'Approved Successfully')
        return redirect('it_app:ticket_index')
    except TicketApprovalIT.DoesNotExist:
        # Jika data task tidak ditemukan,
        # maka akan di redirect ke halaman 404 (Page not found).
        raise Http404("Ticket tidak bisa di Approved.")

@login_required
def ticket_it_reject(request,ticket_id):
    # try:
        # mengambil data task yang akan dihapus berdasarkan task id
        it = TicketApprovalIT.objects.get(pk=ticket_id)
        post = request.POST.copy() 
        post.update({'is_rejected_it': True})
        request.POST = post
        approval_it_form = approvalITForms(request.POST, instance=it)
        if approval_it_form.is_valid():
            reject = approval_it_form.save(commit=False)
            reject.it = request.user
            reject.save()
            return redirect('it_app:ticket_index')
        return HttpResponse(approval_it_form)
#TICKET END

#IT REPORT START

@login_required
def report_it_index(request):
    # Get all unverified ITReportH objects
    list_project_unverified = ITReportH.objects.filter(is_verified=False)
    list_project_ongoing = ITReportH.objects.filter(is_verified=True, is_complete=False)
    list_project_complete = ITReportH.objects.filter(is_verified=True, is_complete=True)

    # Set the number of items to display per page
    items_per_page = 10

    # Create a Paginator instance for each queryset
    paginator_unverified = Paginator(list_project_unverified, items_per_page)
    paginator_ongoing = Paginator(list_project_ongoing, items_per_page)
    paginator_complete = Paginator(list_project_complete, items_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    try:
        # Get the paginated data for the current page for each queryset
        paginated_project_unverified = paginator_unverified.get_page(page)
        paginated_project_ongoing = paginator_ongoing.get_page(page)
        paginated_project_complete = paginator_complete.get_page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page
        paginated_project_unverified = paginator_unverified.get_page(1)
        paginated_project_ongoing = paginator_ongoing.get_page(1)
        paginated_project_complete = paginator_complete.get_page(1)
    except EmptyPage:
        # If page is out of range, deliver the last page
        paginated_project_unverified = paginator_unverified.get_page(paginator_unverified.num_pages)
        paginated_project_ongoing = paginator_ongoing.get_page(paginator_ongoing.num_pages)
        paginated_project_complete = paginator_complete.get_page(paginator_complete.num_pages)

# SEKARANG KITA AKAN BIKIN VARIABLE APPROVE 
    supervisor_report = ITApprovalList.objects.filter(is_supervisor = True).filter(user_id = request.user.id).all()
    context = {
        'project_unverified': paginated_project_unverified,
        'project_ongoing': paginated_project_ongoing,
        'project_complete': paginated_project_complete,
        'supervisor': supervisor_report,
    }

    return render(request, 'it_app/report_it_index.html', context)

@login_required
def report_it_detail(request,report_id):
    return HttpResponse("jadi ini merupakan detail dari report yang di assign")
    return render(request, 'it_app/report_it_index.html', context)

@login_required
def report_it_create_project(request):
    if request.method == "POST":
        user = User.objects.annotate(full_name = Concat('first_name',Value(' '),'last_name')).filter(full_name__contains=request.POST.get('assignedto')).first()
        # Create a mutable copy of request.POST
        post_data = request.POST.copy()
        post_data.pop('assignedto', None)
        # Modify the value corresponding to 'my_key'
        post_data['assigned_to'] = user
        # Replace the original request POST data with our updated version.
        request.POST = post_data
        project_form = ITCreateProjectForms(data=request.POST)
        if project_form.is_valid():

            project = project_form.save(commit=False)
            # Save Cmputer
            project.save()
            return redirect('it_app:report_it_index')
        else:
            print(project_form.errors)
        return redirect('it_app:report_it_index')
    else:
        report_it_create_project_form = ITCreateProjectForms()
    context = {
        'form_report_it_create_project' : report_it_create_project_form,
    }
    return render(request, 'it_app/report_it_create_project.html', context)
    return HttpResponse("jadi ini merupakan create dari project")

@login_required
def report_it_create_task(request,report_id):
    report = ITReportH.objects.get(pk=report_id)
    pic_it = ITApprovalList.objects.filter(user = request.user).first()

    if request.method == "POST":
        task_form = ITCreateTaskForms(data=request.POST)
        it_attachment_form = ITReportAttachmentForms(data=request.POST)
        if task_form.is_valid():
            task = task_form.save(commit=False)
            task.smartFactory_H = report
            task.pic = pic_it
            # Save Cmputer
            task.save()

            # Save attachment
            files = request.FILES.getlist('attachment')
            for f in files:
                 attachment = ITReportDAttachment(attachment=f)
                 attachment.task = task
                 attachment.save()

            return redirect('it_app:report_it_index')
        else:
            print(task_form.errors)
        return redirect('it_app:report_it_index')
    else:
        report_it_create_task_form = ITCreateTaskForms(initial={'smartFactory_H': report})
        report_it_attachment_form = ITReportAttachmentForms()
    context = {
        'form_report_it_create_task' : report_it_create_task_form,
        'form_report_it_attachment_task' : report_it_attachment_form,
    }
    return render(request, 'it_app/report_it_create_task.html', context)
    return HttpResponse("jadi ini pembuatan create task")

@login_required
def report_it_edit_task(request, report_id):
    # jadi ini nanti dapetin report idnya terus kita edit
    return HttpResponse("jadi ini untuk edit task berdasarkan status, apabila sudah Complete maka nanti di konfirmasi")
    return render(request, 'it_app/report_it_index.html', context)

@login_required
def report_it_complete_project(request,report_id):
    return HttpResponse("jadi ini untuk confirm kalau complete")
    return render(request, 'it_app/report_it_index.html', context)

@login_required
def report_it_confirmed_task(request, report_id):
    return HttpResponse("jadi ini merupakan konfirmasi task oleh supervisor nantinya is_completenya jadi 1")
    return render(request, 'it_app/report_it_index.html', context)

@login_required
def report_it_verified_project(request, report_id):
    it_supervisor = ITApprovalList.objects.filter(user = request.user).filter(is_supervisor = True).first()
    report_header = ITReportH.objects.get(pk = report_id)
    report_header.is_verified = True
    report_header.verified_by = it_supervisor
    report_header.save()
    return redirect('it_app:report_it_index')


#IT REPORT END
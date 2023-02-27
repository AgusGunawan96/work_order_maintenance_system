from django.shortcuts import render, redirect
from it_app.models import Ticket, TicketApprovalSupervisor, TicketApprovalManager, TicketApprovalIT, TicketPriority, TicketStatus
from django.contrib.auth.decorators import login_required
from it_app.forms import ticketForms, approvalSupervisorForms, approvalManagerForms, approvalITForms, progressITForms
from django.contrib import messages
from django.http import Http404, HttpResponse
import datetime
# Create your views here.

@login_required
def dashboard(request):
    return render(request, 'it_app/dashboard.html')

@login_required
def profile(request):
    return render(request, 'it_app/profile.html')

@login_required
def ticket_index(request):
    tickets = Ticket.objects.order_by('-created_at')
    supervisors = TicketApprovalSupervisor.objects.order_by('-id')
    managers = TicketApprovalManager.objects.order_by('-id')
    its = TicketApprovalIT.objects.order_by('-id')
    return render(request,'it_app/ticket_index.html', {'tickets': tickets, 'supervisors': supervisors, 'its': its, 'managers': managers, 'form_supervisor': approvalSupervisorForms, 'form_manager': approvalManagerForms, 'form_it': approvalITForms, 'form_progress' : progressITForms})

@login_required
def ticket_add(request):
    if request.method =="POST":
        ticket_form = ticketForms(data=request.POST)
        approval_supervisor_form = approvalSupervisorForms(data=request.POST)
        if ticket_form.is_valid() and approval_supervisor_form.is_valid():
            ticket = ticket_form.save(commit=False)
            if 'ticket_pic' in request.FILES:
                ticket.ticket_pic = request.FILES['ticket_pic']
            ticket.assignee = request.user
            ticket.save()
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
        approval_supervisor_form = approvalSupervisorForms()
    
    context = {
    'form': ticketForms,
    'supervisor_form': approvalSupervisorForms,
}

    return render(request, 'it_app/ticket_add.html', context)

@login_required
def ticket_detail(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    return render(request, 'it_app/ticket_detail.html', {'ticket':ticket})

@login_required
def ticket_supervisor_approve(request,ticket_id):
    try:
        # mengambil data task yang akan dihapus berdasarkan task id
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
        it = TicketApprovalIT.objects.get(pk=ticket_id)
        # mengapprove
        it.is_approve_it = True
        it.it = request.user
        it.save()
        #membuat Ticket Progress
        approval_it_forms = progressITForms(data=request.POST)
        ticket_no = "TKT" + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(it.ticket_approval_manager.ticket_approval_supervisor.ticket.assignee)
        it = approval_it_forms.save(commit=False)
        it.ticket_approval_it = it
        it.priority = TicketPriority.LOW
        it.status = TicketStatus.IN_APPROVAL_IT
        it.ticket_no = ticket_no
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
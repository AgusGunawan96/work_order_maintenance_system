from django.shortcuts import render, redirect
from it_app.models import Ticket, TicketApprovalSupervisor
from django.contrib.auth.decorators import login_required
from it_app.forms import ticketForms, approvalSupervisorForms, approvalManagerForms, approvalITForms, progressITForms
from django.contrib import messages

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
    supervisors = TicketApprovalSupervisor.objects.order_by('-ticket_id')
    return render(request,'it_app/ticket_index.html', {'tickets': tickets, 'supervisors': supervisors})

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
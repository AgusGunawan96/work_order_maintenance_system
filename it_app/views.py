from django.shortcuts import render
from it_app.models import Ticket
from django.contrib.auth.decorators import login_required
from it_app.forms import ticketForms

# Create your views here.

@login_required
def dashboard(request):
    return render(request, 'it_app/dashboard.html')

@login_required
def profile(request):
    return render(request, 'it_app/profile.html')

@login_required
def ticket_index(request):
    tickets = Ticket.objects.order_by('-created_at')[:5]
    return render(request,'it_app/ticket_index.html', {'tickets': tickets})

@login_required
def ticket_add(request):
    if request.method =="POST":
        ticket_form = ticketForms(data=request.POST)

        if ticket_form.is_valid():
            ticket = ticket_form.save()
            if 'ticket_photo' in request.FILES:
                ticket.ticket_photo = request.FILES['ticket_photo']
        else:
            print(ticket_form.errors)
        
        ticket.save()
    else:
        ticket_form = ticketForms()
    
    context = {
    'form': ticketForms,
}

    return render(request, 'it_app/ticket_add.html', context)

@login_required
def ticket_detail(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    return render(request, 'it_app/ticket_by_id.html', {'ticket':ticket})

@login_required
def ticket_edit(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    return render(request, 'it_app/ticket_by_id.html', {'ticket':ticket})

@login_required
def ticket_delete(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    return render(request, 'it_app/ticket_by_id.html', {'ticket':ticket})
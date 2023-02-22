from django.shortcuts import render
from it_app.models import Ticket
from django.contrib.auth.decorators import login_required


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
def ticket_by_id(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    return render(request, 'it_app/ticket_by_id.html', {'ticket':ticket})


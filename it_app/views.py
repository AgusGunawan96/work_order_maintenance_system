from django.shortcuts import render
from it_app.models import Ticket

# Create your views here.
def index(request):
    return render(request, 'it_app/index.html')

def ticket_index(request):
    tickets = Ticket.objects.order_by('-created_at')[:5]
    return render(request,'it_app/ticket_index.html', {'tickets': tickets})

def ticket_by_id(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    return render(request, 'it_app/ticket_by_id.html', {'ticket':ticket})


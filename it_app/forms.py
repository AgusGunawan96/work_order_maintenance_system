from django import forms

from it_app.models import Ticket

class ticketForms(forms.ModelForm):
    class Meta():
        model = Ticket
        fields = ('type', 'hardware', 'quantity', 'title', 'description',  'ticket_photo')
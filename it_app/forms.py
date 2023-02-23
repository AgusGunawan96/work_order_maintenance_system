from django import forms

from it_app.models import Ticket

class ticketForms(forms.ModelForm):
    class Meta():
        model = Ticket
        fields = ('type', 'title', 'description',  'ticket_pic', 'hardware', 'quantity', 'assignee')
        widgets = {'assignee': forms.HiddenInput()}
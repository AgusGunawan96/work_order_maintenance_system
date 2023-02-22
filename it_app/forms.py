from django import forms

from it_app.models import Ticket

class ticketForms(forms.ModelForm):
    class Meta():
        model = Ticket
        fields = ('type', 'title', 'description',  'ticket_pic', 'assignee')
        widgets = {'assignee': forms.HiddenInput()}
from django import forms

from it_app.models import Ticket, TicketApprovalSupervisor, TicketApprovalManager, TicketApprovalIT, TicketProgressIT

class ticketForms(forms.ModelForm):
    class Meta():
        model = Ticket
        fields = ('type', 'title', 'description',  'ticket_pic', 'hardware', 'quantity', 'assignee')
        widgets = {'assignee': forms.HiddenInput()}

class approvalSupervisorForms(forms.ModelForm):
    class Meta():
        model = TicketApprovalSupervisor
        fields = ('reject_reason_supervisor','is_approve_supervisor','is_rejected_supervisor')
        

class approvalManagerForms(forms.ModelForm):
    class Meta():
        model = TicketApprovalManager
        fields = ('reject_reason_manager', 'is_approve_manager' ,'is_rejected_manager')

class approvalITForms(forms.ModelForm):
    class Meta():
        model = TicketApprovalIT
        fields = ('reject_reason_it','is_approve_it' ,'is_rejected_it')

class progressITForms(forms.ModelForm):
    class Meta():
        model = TicketProgressIT
        fields = ('status', 'priority', 'review_description')

from django import forms
from django.forms import ClearableFileInput
from django.contrib.auth.models import User
from it_app.models import Ticket, TicketApprovalSupervisor, TicketApprovalManager, TicketApprovalIT, TicketProgressIT, TicketAttachment, IPAddress, Hardware, ITComputerList, ListLocation, ListLocationDetail, ITApprovalList, ITReportD, ITReportDAttachment, ITReportH
from django_select2.forms import Select2Widget
from django.db.models.functions import Concat
from master_app.models import UserProfileInfo

from django.db.models import CharField, Value
# class ipAddressForms(forms.ModelForm):
#     class Meta():
#         model = IPAddress
#         fields = ('name', )
#         widgets = {'is_used': forms.HiddenInput()}

class hardwareForms(forms.ModelForm):
    class Meta():
        model = Hardware
        fields = ('name', 'quantity_whs', 'hardware', )

class computerListForms(forms.ModelForm):
    user_computer = forms.ModelChoiceField(
        queryset=User.objects.annotate(full_name = Concat('first_name',Value(' '),'last_name')).values_list('full_name', flat = True),
        widget = Select2Widget,
        required=False
    )
    ip = forms.ModelChoiceField(
        queryset=IPAddress.objects.all(),
        widget=Select2Widget,
        required=False
    )
    location = forms.ModelChoiceField(
    queryset=ListLocationDetail.objects.all(),
    widget=Select2Widget,
    required=False
    )
    is_office_2003 = forms.BooleanField(
        label='Office 2003',
        widget=forms.CheckboxInput(),
        required=False)
    is_office_2007 = forms.BooleanField(
        label='Office 2007',
        widget=forms.CheckboxInput(),
        required=False)
    is_office_2010 = forms.BooleanField(
        label='Office 2010',
        widget=forms.CheckboxInput(),
        required=False)
    is_office_2016 = forms.BooleanField(
        label='Office 2016',
        widget=forms.CheckboxInput(),
        required=False)
    is_internet = forms.BooleanField(
        label='Internet',
        widget=forms.CheckboxInput(),
        required=False)
    is_genba = forms.BooleanField(
        label='Genba',
        widget=forms.CheckboxInput(),
        required=False)
    is_dhcp = forms.BooleanField(
        label='DHCP',
        widget=forms.CheckboxInput(),
        required=False)
    class Meta():
        model = ITComputerList
        fields = ( "ip", "computer_name", "os", "windows_type", "location","pc_type", "is_office_2003", "is_office_2007", "is_office_2010", "is_office_2016", "user_computer", "is_internet",  "antivirus", "computer_user", "is_genba", "is_dhcp")
        widgets = {'computer_user': forms.HiddenInput,}
        
class ticketForms(forms.ModelForm):
    hardware = forms.ModelChoiceField(
        queryset=Hardware.objects.all(),
        widget=Select2Widget, 
        required=False
    )
    class Meta():
        model = Ticket
        fields = ('type', 'order', 'title', 'description',  'hardware', 'quantity', 'assignee')
        widgets = {'assignee': forms.HiddenInput()}
        
class ticketAttachmentForms(forms.ModelForm):
    class Meta():
        model = TicketAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }

class approvalSupervisorForms(forms.ModelForm):
    class Meta():
        model = TicketApprovalSupervisor
        fields = ('reject_reason_supervisor','is_approve_supervisor','is_rejected_supervisor', 'supervisor')
        widgets = {'is_approve_supervisor': forms.HiddenInput, 'is_rejected_supervisor': forms.HiddenInput , 'supervisor': forms.HiddenInput}

class approvalManagerForms(forms.ModelForm):
    class Meta():
        model = TicketApprovalManager
        fields = ('reject_reason_manager', 'is_approve_manager' ,'is_rejected_manager', 'manager')
        widgets = {'is_approve_manager': forms.HiddenInput, 'is_rejected_manager': forms.HiddenInput , 'manager': forms.HiddenInput}

class approvalITForms(forms.ModelForm):
    class Meta():
        model = TicketApprovalIT
        fields = ('reject_reason_it','is_approve_it' ,'is_rejected_it', 'it')
        widgets = {'is_approve_it': forms.HiddenInput, 'is_rejected_it': forms.HiddenInput, 'it': forms.HiddenInput }

class progressITForms(forms.ModelForm):
    class Meta():
        model = TicketProgressIT
        fields = ('status', 'priority', 'review_description', 'ticket_no', 'ticket_approval_it')
        widgets = {'ticket_approval_it' : forms.HiddenInput, 'ticket_no' : forms.HiddenInput}

class ITCreateProjectForms(forms.ModelForm):
    assignedto = forms.ModelChoiceField(
        queryset=User.objects.filter(userprofileinfo__division_id__division_name='IT').annotate(full_name=Concat('first_name', Value(' '), 'last_name')).values_list('full_name', flat=True),
        widget=Select2Widget,
        required=False,
        label='Assigned to'  # Set the label for the field
    )
    start_at = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date'}))
    plan_end_at = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date'}))
    class Meta:
        model = ITReportH
        fields = ('project_name','project_description','project_priority', 'start_at', 'plan_end_at', 'assignedto', 'assigned_to')
        widgets = {'assigned_to': forms.HiddenInput,}

class ITCreateTaskForms(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['smartFactory_H'].label = 'Project Name'
        self.fields['smartFactory_H'].widget.attrs['disabled'] = True

    class Meta:
        model = ITReportD
        fields = ('smartFactory_H', 'status', 'task_priority', 'is_confirmed', 'is_complete', 'task')
        widgets = {'is_confirmed': forms.HiddenInput, 'is_complete': forms.HiddenInput, 'pic': forms.HiddenInput, 'confirmed_by': forms.HiddenInput}


class ITReportAttachmentForms(forms.ModelForm):
    class Meta():
        model = ITReportDAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }



        
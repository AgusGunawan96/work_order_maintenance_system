from django import forms 
from qc_app.models import rirHeader, rirDetailCoaContentJudgement, rirDetailCoaContentCheckedby, rirDetailAppearenceJudgement, rirDetailAppearenceCheckedby, rirDetailRestrictedSubstanceJudgement, rirDetailRestrictedSubstanceCheckedby, rirDetailEnvironmentalIssueJudgement, rirDetailEnvironmentalIssueCheckedby,rirDetailSampleTestJudgement, rirDetailSampleTestCheckedby, rirApprovalSupervisor, rirApprovalManager, IncomingType, rirMaterial, categoryTypeRIR, rirAppearanceAttachment, rirCoaContentAttachment, rirSampleTestAttachment, rirEnvironmentalIssueAttachment, rirRestrictedSubstanceAttachment, specialJudgement, rirApprovalSupervisorAttachment, rirApprovalManagerAttachment, rirVendor
from django.forms import ClearableFileInput, formset_factory
from django_select2.forms import Select2Widget
from django.forms.widgets import DateTimeInput

# RIR START

# class OptionalDateTimeWidget(DateTimeInput):
#     def __init__(self, attrs=None, format=None):
#         optional_attrs = {'placeholder': 'YYYY-MM-DD HH:MM:SS'}
#         if attrs is not None:
#             optional_attrs.update(attrs)
#         super().__init__(attrs=optional_attrs, format=format)

class rirHeaderForms(forms.ModelForm):
    incoming_at = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date'}))
    expired_at = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date'}))
    incoming_at_external = forms.DateTimeField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    
    incoming_type = forms.TypedChoiceField(
        choices=IncomingType.choices,
        widget=Select2Widget,
        coerce=str,
    )

    material = forms.ModelChoiceField(
        queryset=rirMaterial.objects.all(),
        widget=Select2Widget
    )

    vendor = forms.ModelChoiceField(
    queryset=rirVendor.objects.all(),
    widget=Select2Widget
    )

    category = forms.ModelChoiceField(
        queryset=categoryTypeRIR.objects.all(),
        widget=Select2Widget
    )
    
    class Meta():
        model = rirHeader
        fields = ('incoming_type','category','material','po_number','vendor','lot_no','quantity', 'quantity_actual','incoming_at', 'incoming_at_external', 'expired_at' )

class rirDetailCoaContentJudgementForms(forms.ModelForm):
    is_special_judgement = forms.BooleanField(
        label='Special Judgement',
        widget=forms.CheckboxInput(),
        required=False)
    class Meta():
        model = rirDetailCoaContentJudgement
        fields = ('coa_content_remark','is_special_judgement')
        widgets = {
            'coa_content_remark'        : forms.Textarea(attrs={'rows':2, 'cols':15}),
            }
        
class rirDetailCoaContentCheckedByForms(forms.ModelForm):
    is_special_judgement = forms.BooleanField(
        label='Special Judgement',
        widget=forms.CheckboxInput(),
        required=False)
    class Meta():
        model = rirDetailCoaContentCheckedby
        fields = ('coa_content_remark','is_special_judgement')
        widgets = {
            'coa_content_remark'        : forms.Textarea(attrs={'rows':2, 'cols':15}),
            }
        
class rirCoaContentAttachmentForms(forms.ModelForm):
    class Meta():
        model = rirCoaContentAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }

class rirDetailAppearenceJudgementForms(forms.ModelForm):
    is_special_judgement = forms.BooleanField(
        label='Special Judgement',
        widget=forms.CheckboxInput(),
        required=False)
    class Meta():
        model = rirDetailAppearenceJudgement
        fields = ('appearence_remark','is_special_judgement')
        widgets = {
            'appearence_remark'        : forms.Textarea(attrs={'rows':2, 'cols':15}),
            }
        
class rirDetailAppearenceCheckedByForms(forms.ModelForm):
    is_special_judgement = forms.BooleanField(
        label='Special Judgement',
        widget=forms.CheckboxInput(),
        required=False)
    class Meta():
        model = rirDetailAppearenceCheckedby
        fields = ('appearence_remark','is_special_judgement')
        widgets = {
            'appearence_remark'        : forms.Textarea(attrs={'rows':2, 'cols':15}),
            }
        
class rirAppearanceAttachmentForms(forms.ModelForm):
    class Meta():
        model = rirAppearanceAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }

class rirDetailRestrictedSubstanceJudgementForms(forms.ModelForm):
    is_special_judgement = forms.BooleanField(
        label='Special Judgement',
        widget=forms.CheckboxInput(),
        required=False)
    class Meta():
        model = rirDetailRestrictedSubstanceJudgement
        fields = ('restricted_substance_remark','is_special_judgement')
        widgets = {
            'restricted_substance_remark'        : forms.Textarea(attrs={'rows':2, 'cols':15}),
            }
        
class rirDetailRestrictedSubstanceCheckedByForms(forms.ModelForm):
    is_special_judgement = forms.BooleanField(
        label='Special Judgement',
        widget=forms.CheckboxInput(),
        required=False)
    class Meta():
        model = rirDetailRestrictedSubstanceCheckedby
        fields = ('restricted_substance_remark','is_special_judgement')
        widgets = {
            'restricted_substance_remark'        : forms.Textarea(attrs={'rows':2, 'cols':15}),
            }
        
class rirRestrictedSubstanceAttachmentForms(forms.ModelForm):
    class Meta():
        model = rirRestrictedSubstanceAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }

class rirDetailEnvironmentalIssueJudgementForms(forms.ModelForm):
    is_special_judgement = forms.BooleanField(
        label='Special Judgement',
        widget=forms.CheckboxInput(),
        required=False)
    class Meta():
        model = rirDetailEnvironmentalIssueJudgement
        fields = ('environmental_issue_remark','is_special_judgement')
        widgets = {
            'environmental_issue_remark'        : forms.Textarea(attrs={'rows':2, 'cols':15}),
            }
        
class rirDetailEnvironmentalIssueCheckedByForms(forms.ModelForm):
    is_special_judgement = forms.BooleanField(
        label='Special Judgement',
        widget=forms.CheckboxInput(),
        required=False)
    class Meta():
        model = rirDetailEnvironmentalIssueCheckedby
        fields = ('environmental_issue_remark','is_special_judgement')
        widgets = {
            'environmental_issue_remark'        : forms.Textarea(attrs={'rows':2, 'cols':15}),
            }
        
class rirEnvironmentalIssueAttachmentForms(forms.ModelForm):
    class Meta():
        model = rirEnvironmentalIssueAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }

class rirDetailSampleTestJudgementForms(forms.ModelForm):
    is_special_judgement = forms.BooleanField(
        label='Special Judgement',
        widget=forms.CheckboxInput(),
        required=False)
    class Meta():
        model = rirDetailSampleTestJudgement
        fields = ('sample_test_remark','is_special_judgement')
        widgets = {
            'sample_test_remark'        : forms.Textarea(attrs={'rows':2, 'cols':15}),
            }
        
class rirDetailSampleTestCheckedByForms(forms.ModelForm):
    is_special_judgement = forms.BooleanField(
        label='Special Judgement',
        widget=forms.CheckboxInput(),
        required=False)
    class Meta():
        model = rirDetailSampleTestCheckedby
        fields = ('sample_test_remark','is_special_judgement')
        widgets = {
            'sample_test_remark'        : forms.Textarea(attrs={'rows':2, 'cols':15}),
            }
        
class rirSampleTestAttachmentForms(forms.ModelForm):
    class Meta():
        model = rirSampleTestAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }

# RIR END

# SPECIAL JUDGEMENT START
class rirSpecialJudgementForms(forms.ModelForm):
    class Meta():
        model = specialJudgement
        fields = ('rir',)

class rirApprovalSupervisorForms(forms.ModelForm):
    class Meta():
        model = rirApprovalSupervisor
        fields = ('specialjudgement',)

class rirApprovalManagerForms(forms.ModelForm):
    class Meta():
        model = rirApprovalManager
        fields = ('rir_approval_supervisor',)

class rirApprovalSupervisorPassReturnForms(forms.ModelForm):
    is_pass_supervisor = forms.BooleanField(
    label='Pass',
    widget=forms.CheckboxInput(),
    required=False)
    is_return_supervisor = forms.BooleanField(
    label='Return',
    widget=forms.CheckboxInput(),
    required=False)
    class Meta():
        model = rirApprovalSupervisor
        fields = ('is_pass_supervisor', 'is_return_supervisor',)


class rirApprovalSupervisorReasonForms(forms.ModelForm):
    class Meta():
        model = rirApprovalSupervisor
        fields = ('reason',)
        widgets = {
            'reason'        : forms.Textarea(attrs={'rows':2, 'cols':15}),
            }
        
class rirApprovalManagerPassReturnForms(forms.ModelForm):
    is_pass_manager = forms.BooleanField(
    label='Pass',
    widget=forms.CheckboxInput(),
    required=False)
    is_return_manager = forms.BooleanField(
    label='Return',
    widget=forms.CheckboxInput(),
    required=False)
    class Meta():
        model = rirApprovalManager
        fields = ('is_pass_manager', 'is_return_manager',)

class rirApprovalManagerReasonForms(forms.ModelForm):
    class Meta():
        model = rirApprovalManager
        fields = ('reason',)
        widgets = {
            'reason'        : forms.Textarea(attrs={'rows':2, 'cols':15}),
            }
        
class riApprovalSupervisorAttachmentForms(forms.ModelForm):
    class Meta():
        model = rirApprovalSupervisorAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }
        
class riApprovalManagerAttachmentForms(forms.ModelForm):
    class Meta():
        model = rirApprovalManagerAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }
# SPECIAL JUDGEMENT END
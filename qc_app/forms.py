from django import forms 
from qc_app.models import rirHeader, rirDetailCoaContentJudgement, rirDetailCoaContentCheckedby, rirDetailAppearenceJudgement, rirDetailAppearenceCheckedby, rirDetailRestrictedSubstanceJudgement, rirDetailRestrictedSubstanceCheckedby, rirDetailEnvironmentalIssueJudgement, rirDetailEnvironmentalIssueCheckedby,rirDetailSampleTestJudgement, rirDetailSampleTestCheckedby, rirApprovalSupervisor, rirApprovalManager, IncomingType, rirMaterial, categoryTypeRIR, rirAppearanceAttachment, rirCoaContentAttachment, rirSampleTestAttachment, rirEnvironmentalIssueAttachment, rirRestrictedSubstanceAttachment
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
    category = forms.ModelChoiceField(
        queryset=categoryTypeRIR.objects.all(),
        widget=Select2Widget
    )
    class Meta():
        model = rirHeader
        fields = ('incoming_type','category','material','vendor','po_number','lot_no','quantity','incoming_at', 'incoming_at_external', 'expired_at' )

class rirDetailCoaContentJudgementForms(forms.ModelForm):
    class Meta():
        model = rirDetailCoaContentJudgement
        fields = ('coa_content_remark',)

class rirDetailCoaContentCheckedByForms(forms.ModelForm):
    class Meta():
        model = rirDetailCoaContentCheckedby
        fields = ('coa_content_remark',)

class rirCoaContentAttachmentForms(forms.ModelForm):
    class Meta():
        model = rirCoaContentAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }

class rirDetailAppearenceJudgementForms(forms.ModelForm):
    class Meta():
        model = rirDetailAppearenceJudgement
        fields = ('appearence_remark',)

class rirDetailAppearenceCheckedByForms(forms.ModelForm):
    class Meta():
        model = rirDetailAppearenceCheckedby
        fields = ('appearence_remark',)

class rirAppearanceAttachmentForms(forms.ModelForm):
    class Meta():
        model = rirAppearanceAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }

class rirDetailRestrictedSubstanceJudgementForms(forms.ModelForm):
    class Meta():
        model = rirDetailRestrictedSubstanceJudgement
        fields = ('restricted_substance_remark',)

class rirDetailRestrictedSubstanceCheckedByForms(forms.ModelForm):
    class Meta():
        model = rirDetailRestrictedSubstanceCheckedby
        fields = ('restricted_substance_remark',)

class rirRestrictedSubstanceAttachmentForms(forms.ModelForm):
    class Meta():
        model = rirRestrictedSubstanceAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }

class rirDetailEnvironmentalIssueJudgementForms(forms.ModelForm):
    class Meta():
        model = rirDetailEnvironmentalIssueJudgement
        fields = ('environmental_issue_remark',)

class rirDetailEnvironmentalIssueCheckedByForms(forms.ModelForm):
    class Meta():
        model = rirDetailEnvironmentalIssueCheckedby
        fields = ('environmental_issue_remark',)

class rirEnvironmentalIssueAttachmentForms(forms.ModelForm):
    class Meta():
        model = rirEnvironmentalIssueAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }

class rirDetailSampleTestJudgementForms(forms.ModelForm):
    class Meta():
        model = rirDetailSampleTestJudgement
        fields = ('sample_test_remark',)

class rirDetailSampleTestCheckedByForms(forms.ModelForm):
    class Meta():
        model = rirDetailSampleTestCheckedby
        fields = ('sample_test_remark',)

class rirSampleTestAttachmentForms(forms.ModelForm):
    class Meta():
        model = rirSampleTestAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }

# RIR END

# SPECIAL JUDGEMENT START
class rirApprovalSupervisorReturnForms(forms.ModelForm):
    class Meta():
        model = rirApprovalSupervisor
        fields = ('return_reason_supervisor',)

class rirApprovalSupervisorPassForms(forms.ModelForm):
    class Meta():
        model = rirApprovalSupervisor
        fields = ('review_supervisor',)

class rirApprovalManagerReturnForms(forms.ModelForm):
    class Meta():
        model = rirApprovalManager
        fields = ('return_reason_manager',)

class rirApprovalManagerPassForms(forms.ModelForm):
    class Meta():
        model = rirApprovalManager
        fields = ('review_manager',)
# SPECIAL JUDGEMENT END
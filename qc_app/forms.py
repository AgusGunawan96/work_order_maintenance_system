from django import forms 
from qc_app.models import rirHeader, rirDetailCoaContentJudgement, rirDetailCoaContentCheckedby, rirDetailAppearenceJudgement, rirDetailAppearenceCheckedby, rirDetailRestrictedSubstanceJudgement, rirDetailRestrictedSubstanceCheckedby, rirDetailEnvironmentalIssueJudgement, rirDetailEnvironmentalIssueCheckedby,rirDetailSampleTestJudgement, rirDetailSampleTestCheckedby, rirApprovalSupervisor, rirApprovalManager
from django.forms import ClearableFileInput, formset_factory

# RIR START
class rirHeaderForms(forms.ModelForm):
    class Meta():
        model = rirHeader
        fields = ('incoming_type','category','material','vendor','po_number','lot_no','quantity','rir_no','incoming_at','expired_at',)

class rirDetailCoaContentJudgementForms(forms.ModelForm):
    class Meta():
        model = rirDetailCoaContentJudgement
        fields = ('coa_content_remark',)

class rirDetailCoaContentCheckedByForms(forms.ModelForm):
    class Meta():
        model = rirDetailCoaContentCheckedby
        fields = ('coa_content_remark',)

class rirDetailAppearenceJudgementForms(forms.ModelForm):
    class Meta():
        model = rirDetailAppearenceJudgement
        fields = ('appearence_remark',)

class rirDetailAppearenceCheckedByForms(forms.ModelForm):
    class Meta():
        model = rirDetailAppearenceCheckedby
        fields = ('appearence_remark',)

class rirDetailRestrictedSubstanceJudgementForms(forms.ModelForm):
    class Meta():
        model = rirDetailRestrictedSubstanceJudgement
        fields = ('restricted_substance_remark',)

class rirDetailRestrictedSubstanceCheckedByForms(forms.ModelForm):
    class Meta():
        model = rirDetailRestrictedSubstanceCheckedby
        fields = ('restricted_substance_remark',)

class rirDetailEnvironmentalIssueJudgementForms(forms.ModelForm):
    class Meta():
        model = rirDetailEnvironmentalIssueJudgement
        fields = ('environmental_issue_remark',)

class rirDetailEnvironmentalIssueCheckedByForms(forms.ModelForm):
    class Meta():
        model = rirDetailEnvironmentalIssueCheckedby
        fields = ('environmental_issue_remark',)

class rirDetailSampleTestJudgementForms(forms.ModelForm):
    class Meta():
        model = rirDetailSampleTestJudgement
        fields = ('sample_test_remark',)

class rirDetailSampleTestCheckedByForms(forms.ModelForm):
    class Meta():
        model = rirDetailSampleTestCheckedby
        fields = ('sample_test_remark',)
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
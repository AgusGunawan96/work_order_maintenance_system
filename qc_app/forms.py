from django import forms 
from qc_app.models import rirHeader, rirDetail, specialJudgement, rirApprovalSupervisor, rirApprovalManager
from django.forms import ClearableFileInput

class rirHeaderForms(forms.ModelForm):
    model = rirHeader

class rirFabricsForms(forms.ModelForm):
    model = rirDetail

class rirChemicalsForms(forms.ModelForm):
    model = rirDetail

class rirPolymerForms(forms.ModelForm):
    model = rirDetail

class rirRopesForms(forms.ModelForm):
    model = rirDetail

class rirChoppedFibersForms(forms.ModelForm):
    model = rirDetail

class rirChloroprenePolymerForms(forms.ModelForm):
    model = rirDetail


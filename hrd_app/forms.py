from django import forms 
from hrd_app.models import medicalApprovalForeman, medicalApprovalHR, medicalApprovalList, medicalApprovalManager, medicalApprovalSupervisor, medicalAttachment, medicalClaimStatus, medicalDetailDokter, medicalDetailInformation, medicalDetailPasienKeluarga, medicalHeader, medicalHubungan, medicalJenisMelahirkan, medicalJenisPelayanan, medicalTempatPelayanan
from django.forms import ClearableFileInput, formset_factory
from django_select2.forms import Select2Widget
from django.forms.widgets import DateTimeInput

# MEDICAL TRAIN START
class medicaForms(forms.ModelForm):
    model = medicalHeader


# MEDICAL TRAIN END

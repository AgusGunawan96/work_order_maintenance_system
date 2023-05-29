from django import forms 
from hrd_app.models import medicalApprovalForeman, medicalApprovalHR, medicalApprovalManager, medicalApprovalSupervisor, medicalAttachment, medicalClaimStatus, medicalDetailDokter, medicalDetailInformation, medicalDetailPasienKeluarga, medicalHeader
from master_app.models import UserKeluargaInfo
from django.forms import ClearableFileInput
from django_select2.forms import Select2Widget

# MEDICAL TRAIN START
class medicalHeaderForms(forms.ModelForm):
    class Meta():
        model = medicalHeader
        fields = ('rp_total',)
        widgets = {'rp_total': forms.HiddenInput()}

class medicalDataKeluargaForms(forms.ModelForm):
    # keluarga = forms.ModelChoiceField(
    #     queryset=UserKeluargaInfo.objects.all(),
    #     widget=Select2Widget, 
    #     required=False
    # )
        # Define your fields here...
    keluarga = forms.ModelChoiceField(queryset=UserKeluargaInfo.objects.all(),
                                        widget=Select2Widget, 
                                        required=False)
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['keluarga'].queryset = UserKeluargaInfo.objects.filter(user=user)
            
    class Meta():
        model = medicalDetailPasienKeluarga
        fields = ('keluarga',)

class medicalPemberiLayananForms(forms.ModelForm):
    class Meta():
        model = medicalDetailDokter
        fields = ('nama_dokter','tempat_pelayanan','nama_tempat','alamat','no_telp')

class medicalPelayananKesehatanForms(forms.ModelForm):
    tanggal_berobat_mulai = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date'}))
    tanggal_berobat_selesai = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date'}))
    class Meta():
        model = medicalDetailInformation
        fields = ('jenis_pelayanan','melahirkan','tanggal_berobat_mulai','tanggal_berobat_selesai','diagnosa',)

class medicalStatusKlaimForms(forms.ModelForm):
    class Meta():
        model = medicalClaimStatus
        fields = ('is_lengkap',)                                                                          

class medicalRejectStatusKlaimForms(forms.ModelForm):
    class Meta():
        model = medicalClaimStatus
        fields = ('tidak_lengkap',)

class medicalAttachmentForms(forms.ModelForm):
    class Meta():
        model = medicalAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }

class medicalReasonForemanForms(forms.ModelForm):
    class Meta():
        model = medicalApprovalForeman
        fields = ('reason',)


class medicalReasonSupervisorForms(forms.ModelForm):
    class Meta():
        model = medicalApprovalSupervisor
        fields = ('reason',)


class medicalReasonManagerForms(forms.ModelForm):
    class Meta():
        model = medicalApprovalManager
        fields = ('reason',)


class medicalReasonHRForms(forms.ModelForm):
    class Meta():
        model = medicalApprovalHR
        fields = ('reason',)
# MEDICAL TRAIN END

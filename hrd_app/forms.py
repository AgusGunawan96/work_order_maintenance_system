from django import forms 
from hrd_app.models import medicalApprovalForeman, medicalApprovalHR, medicalApprovalManager, medicalApprovalSupervisor, medicalAttachment, medicalClaimStatus, medicalDetailDokter, medicalDetailInformation, medicalDetailPasienKeluarga, medicalHeader
from django.forms import ClearableFileInput
# MEDICAL TRAIN START
class medicalHeaderForms(forms.ModelForm):
    class Meta():
        model = medicalHeader
        fields = ('rp_total',)
        widgets = {'rp_total': forms.HiddenInput()}

class medicalDataKeluargaForms(forms.ModelForm):
    tanggal_lahir = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date'}), required=False)
    class Meta():
        model = medicalDetailPasienKeluarga
        fields = ('nama_pasien','tanggal_lahir','jenis_kelamin','hubungan',)

class medicalPemberiLayananForms(forms.ModelForm):
    class Meta():
        model = medicalDetailDokter
        fields = ('nama_dokter','tempat_pelayanan','nama_klinik','alamat','no_telp')

class medicalPelayananKesehatanForms(forms.ModelForm):
    tanggal_berobat = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date'}))
    class Meta():
        model = medicalDetailInformation
        fields = ('jenis_pelayanan','melahirkan','tanggal_berobat','diagnosa',)

class medicalStatusKlaimForms(forms.ModelForm):
    class Meta():
        model = medicalClaimStatus
        fields = ('is_lengkap',)                                                                          

class medicalAttachmentForms(forms.ModelForm):
    class Meta():
        model = medicalAttachment
        fields = ('attachment',)
        widgets = {
            'attachment'    : ClearableFileInput(attrs={'multiple':True}),
        }

class medicalReasonForeman(forms.ModelForm):
    class Meta():
        model = medicalApprovalForeman
        fields = ('reason',)


class medicalReasonSupervisor(forms.ModelForm):
    class Meta():
        model = medicalApprovalSupervisor
        fields = ('reason',)


class medicalReasonManager(forms.ModelForm):
    class Meta():
        model = medicalApprovalManager
        fields = ('reason',)


class medicalReasonHR(forms.ModelForm):
    class Meta():
        model = medicalApprovalHR
        fields = ('reason',)
# MEDICAL TRAIN END

from django import forms 
from hrd_app.models import medicalApprovalForeman, medicalApprovalHR, medicalApprovalManager, medicalApprovalSupervisor, medicalAttachment, medicalClaimStatus, medicalDetailDokter, medicalDetailInformation, medicalDetailPasienKeluarga, medicalHeader, medicalJenisPelayanan, medicalJenisPelayananKartap, medicalJenisPelayananSetahun, medicalJenisPelayananKartapSetahun
from master_app.models import UserKeluargaInfo
from django.forms import ClearableFileInput
from django_select2.forms import Select2Widget
from datetime import date
from django.core.validators import RegexValidator
# Function
def get_current_year():
    return date.today().year

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
    no_telp = forms.IntegerField()
    class Meta():
        model = medicalDetailDokter
        fields = ('nama_dokter','tempat_pelayanan','nama_tempat','alamat','no_telp')

class medicalPelayananKesehatanForms(forms.ModelForm):
    tanggal_berobat_mulai = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date'}))
    tanggal_berobat_selesai = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date'}))
    jenis_pelayanan = forms.TypedChoiceField(
        widget=Select2Widget,
        coerce=str,
    )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
            # baru ini akan mulai pengkondisian apabila kartap atau bukan (dan ini setahuyn atau bukan)
        user_year = user.date_joined.year
        current_year = get_current_year()
        validate = current_year - user_year
        if validate >= 1:
            if user.userprofileinfo.is_contract:
                self.fields['jenis_pelayanan'].choices = medicalJenisPelayananSetahun.choices
            elif user.userprofileinfo.is_permanent:
                self.fields['jenis_pelayanan'].choices = medicalJenisPelayananKartapSetahun.choices
        else:
            if user.userprofileinfo.is_contract:
                self.fields['jenis_pelayanan'].choices = medicalJenisPelayanan.choices

            elif user.userprofileinfo.is_permanent:
                self.fields['jenis_pelayanan'].choices = medicalJenisPelayananKartap.choices


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

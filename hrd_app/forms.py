from django import forms 
from hrd_app.models import medicalApprovalForeman, medicalApprovalHR, medicalApprovalManager, medicalApprovalSupervisor, medicalAttachment, medicalClaimStatus, medicalDetailDokter, medicalDetailInformation, medicalDetailPasienKeluarga, medicalHeader, medicalJenisPelayanan, medicalJenisPelayananKartap, medicalJenisPelayananSetahun, medicalJenisPelayananKartapSetahun
from master_app.models import UserKeluargaInfo, UserProfileInfo, Regency, UserProfileKTP, UserProfileKTPNow, Province, District, Village
from django.forms import ClearableFileInput
from django_select2.forms import Select2Widget
from datetime import date
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm, UserChangeForm



# Function
def get_current_year():
    return date.today().year


# BIODATA START
class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('first_name','last_name','username', 'email')
        # Customize any additional fields if needed
        # For example: fields = ('username', 'email')

class EditProfileForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        fields = ('first_name','last_name','username', 'email' )
        # Customize any additional fields if needed
        # For example: fields = ('username', 'email')


class RegistrationUserProfileInfo(forms.ModelForm):

    tempat = forms.ModelChoiceField(
    queryset=Regency.objects.all(),
    widget=Select2Widget,
    required=True
    )

    status_karyawan_choices = [
    ('k', 'Karyawan Tetap'),
    ('c', 'Karyawan Kontrak'),
    ]
    
    status_karyawan = forms.ChoiceField(
        label='Status Karyawan',
        choices=status_karyawan_choices,
        widget=forms.RadioSelect()
    )

    gender_choices = [
    ('M', 'Laki-Laki'),
    ('F', 'Perempuan')
    ]
    
    gender = forms.ChoiceField(
        label='Jenis Kelamin',
        choices=gender_choices,
        widget=forms.RadioSelect()
    )

    no_telp2_hubungan_choices = [
    ('SUAMI/ISTRI', 'Suami/Istri'),
    ('ORANGTUA', 'Orangtua'),
    ('ANAK', 'Anak'),
    ('SAUDARA', 'Saudara')
    ]
    
    no_telp2_hubungan = forms.ChoiceField(
    label='Hubungan',
    choices=no_telp2_hubungan_choices,
    widget=forms.RadioSelect()
    )

    pendidikan_terakhir_choices = [
    ('SMA/SEDERAJAT', 'Suami/Istri'),
    ('D-1', 'D-1'),
    ('D-2', 'D-2'),
    ('D-3', 'D-3'),
    ('D-3', 'D-3'),
    ('S-1', 'S-1'),
    ('S-2', 'S-2'),
    ('S-3', 'S-3'),
    ('LAINNYA', 'Lainnya'),
    ]

    pendidikan_terakhir = forms.ChoiceField(
    label='Pendidikan Terakhir',
    choices=pendidikan_terakhir_choices,
    widget=forms.RadioSelect()
    )

    tanggal_lahir = forms.DateField(
        label='Tanggal Lahir',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta():
        model = UserProfileInfo
        fields = ('tempat','tanggal_lahir','status_karyawan', 'noktp', 'gender', 'no_telepon', 'no_telepon2', 'no_telp2_hubungan', 'pendidikan_terakhir', 'pendidikan_terakhir_others')

class RegistrationUserKtp(forms.ModelForm):
    provinsi_ktp = forms.ModelChoiceField(
        queryset=Province.objects.all(),
        widget=Select2Widget,
        required=True
    )
    kota_ktp = forms.ModelChoiceField(
        queryset=Regency.objects.none(),
        widget=Select2Widget,
        required=True
    )
    kecamatan_ktp = forms.ModelChoiceField(
        queryset=District.objects.none(),  # Empty initial queryset
        widget=Select2Widget,
        required=True
    )
    kelurahan_ktp = forms.ModelChoiceField(
        queryset=Village.objects.none(),
        widget=Select2Widget,
        required=True
    )
    alamat_tempat_saat_ini_choices = [
    ('False', 'Tidak sama dengan KTP'),
    ('True', 'Sama dengan KTP, jika sama kosongkan Alamat Tempat Tinggal')
    ]
    
    alamat_tempat_saat_ini = forms.ChoiceField(
        label='Alamat Tempat Tinggal Saat Ini',
        choices=alamat_tempat_saat_ini_choices,
        widget=forms.RadioSelect()
    )

    surat_menyurat_ktp_choices = [
    ('True', 'Ya'),
    ('False', 'Tidak')
    ]
    
    surat_menyurat_ktp = forms.ChoiceField(
        label='Alamat Surat Menyurat',
        choices=surat_menyurat_ktp_choices,
        widget=forms.RadioSelect()
    )

    class Meta:
      model = UserProfileKTP
      fields = ('alamat_ktp', 'provinsi_ktp','kelurahan_ktp', 'kecamatan_ktp', 'kota_ktp',
                'is_surat_ktp', 'is_same_ktp', 'rt_ktp', 'rw_ktp')

class RegistrationUserKtpNow(forms.ModelForm):
    provinsi_now = forms.ModelChoiceField(
    queryset=Province.objects.all(),
    widget=Select2Widget,
    required=True
    )
    kelurahan_now = forms.ModelChoiceField(
    queryset=Village.objects.none(),
    widget=Select2Widget,
    required=False
    )
    kecamatan_now = forms.ModelChoiceField(
    queryset=District.objects.none(),
    widget=Select2Widget,
    required=False
    )
    kota_now = forms.ModelChoiceField(
    queryset=Regency.objects.none(),
    widget=Select2Widget,
    required=False
    )

    alamat_tempat_saat_ini_choices = [
    ('Milik Sendiri', 'Milik Sendiri'),
    ('Ikut Orang tua', 'Kontrak'),
    ('Kost', 'Kost'),
    ('Lainnya', 'Lainnya')
    ]
    
    alamat_tempat_saat_ini = forms.ChoiceField(
    label='Alamat Tempat Tinggal Saat Ini',
    choices=alamat_tempat_saat_ini_choices,
    widget=forms.RadioSelect()
    )


    surat_menyurat_now_choices = [
    ('True', 'Ya'),
    ('False', 'Tidak')
    ]
    
    surat_menyurat_now = forms.ChoiceField(
        label='Alamat Surat Menyurat',
        choices=surat_menyurat_now_choices,
        widget=forms.RadioSelect()
    )

    class Meta():
        model = UserProfileKTPNow
        fields = ('alamat_now','kelurahan_now','kecamatan_now','kota_now','is_surat_now','rt_now','rw_now','tempat_milik_now','nama_pemilik','no_telp_pemilik')

# BIODATA END

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

class FileUploadRemainResetForm(forms.Form):
    file = forms.FileField(
        label='Select a CSV file',
        help_text='File should be in CSV format.'
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check if the file extension is .csv
            if not file.name.endswith('.csv'):
                raise forms.ValidationError('Only CSV files are allowed.')
        return file

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

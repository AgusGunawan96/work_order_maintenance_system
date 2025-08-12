# dailyactivity_app/forms.py
from django import forms
from dailyactivity_app.models import Shift, Location, Category, Status, Machinemechanical, Machineelectrical, Machineutility, MechanicalData, ElectricalData, UtilityData, PICMechanical, PICElectrical, PICUtility, MechanicalData2, PICMechanical2, UtilityData2, PICUtility2, PICIt, ItData, PICLaporan, LaporanData, PICLembur, PICLaporanMechanical, LaporanMechanicalData, PICLemburMechanical, ScheduleMechanicalData, Project, ProjectIssue

class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['name']

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name']

class MachinemechanicalForm(forms.ModelForm):
    class Meta:
        model = Machinemechanical
        fields = ['name','nomor']

class MachineelectricalForm(forms.ModelForm):
    class Meta:
        model = Machineelectrical
        fields = ['name','nomor']

class MachineutilityForm(forms.ModelForm):
    class Meta:
        model = Machineutility
        fields = ['name','nomor']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name']

class MechanicalDataForm(forms.ModelForm):

    pic = forms.ModelMultipleChoiceField(
        queryset=PICMechanical.objects.all(),  # Ambil data PIC dari model PICMechanical
        widget=forms.SelectMultiple,  # Gunakan SelectMultiple untuk mendukung lebih dari satu pilihan
        required=True
    )

    # Menambahkan kolom untuk nomor mesin baru (opsional)
    machine_number = forms.CharField(
        required=False,
        label="Nomor Mesin Baru",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan nomor mesin jika belum ada'
        })
    )

    class Meta:
        model = MechanicalData
        fields = [
            'tanggal', 'jam', 'shift', 'location', 'machine', 'category', 'status', 
            'masalah', 'penyebab', 'tindakan', 'image', 'pic', 'nomor_wo', 
            'waktu_pengerjaan', 'machine_number'  # Tambahkan machine_number ke dalam fields
        ]

class MechanicalData2Form(forms.ModelForm):
    pic = forms.ModelMultipleChoiceField(
        queryset=PICMechanical2.objects.all(),  # Ambil data PIC dari model PICMechanical2
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),  # Gunakan SelectMultiple dengan styling
        required=True
    )

    class Meta:
        model = MechanicalData2
        fields = [
            'tanggal', 'jam', 'shift', 'status', 'masalah', 'penyebab', 
            'line', 'mesin', 'nomer', 'pekerjaan', 'status_pekerjaan', 
            'tindakan_perbaikan', 'tindakan_pencegahan', 'image', 'pic', 
            'nomor_wo', 'waktu_pengerjaan'
        ]

        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'jam': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'shift': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'masalah': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'penyebab': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'line': forms.TextInput(attrs={'class': 'form-control'}),
            'mesin': forms.TextInput(attrs={'class': 'form-control'}),
            'nomer': forms.TextInput(attrs={'class': 'form-control'}),
            'pekerjaan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status_pekerjaan': forms.TextInput(attrs={'class': 'form-control'}),
            'tindakan_perbaikan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tindakan_pencegahan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nomor_wo': forms.TextInput(attrs={'class': 'form-control'}),
            'waktu_pengerjaan': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class PICMechanical2Form(forms.ModelForm):
    class Meta:
        model = PICMechanical2
        fields = ['name', 'nokar']  # Pastikan field yang ingin diupdate tercakup di sini

class PICMechanicalForm(forms.ModelForm):
    class Meta:
        model = PICMechanical
        fields = ['name', 'nokar']  # Pastikan field yang ingin diupdate tercakup di sini


class ElectricalDataForm(forms.ModelForm):
    pic = forms.ModelMultipleChoiceField(
        queryset=PICElectrical.objects.all(),  # Ambil data PIC dari model PICElectrical
        widget=forms.SelectMultiple,  # Gunakan SelectMultiple untuk mendukung lebih dari satu pilihan
        required=True
    )
    
    # Menambahkan kolom untuk nomor mesin baru (opsional)
    machine_number = forms.CharField(
        required=False,
        label="Nomor Mesin Baru",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan nomor mesin jika belum ada'
        })
    )

    class Meta:
        model = ElectricalData
        fields = [
            'tanggal', 'jam', 'shift', 'location', 'machine', 'category', 'status', 
            'masalah', 'penyebab', 'tindakan', 'image', 'pic', 'nomor_wo', 
            'waktu_pengerjaan', 'machine_number'  # Tambahkan machine_number ke dalam fields
        ]

class PICElectricalForm(forms.ModelForm):
    class Meta:
        model = PICElectrical
        fields = ['name', 'nokar']  # Pastikan field yang ingin diupdate tercakup di sini

class UtilityDataForm(forms.ModelForm):
     pic = forms.ModelMultipleChoiceField(
        queryset=PICUtility.objects.all(),  # Ambil data PIC dari model PICMechanical
        widget=forms.SelectMultiple,  # Gunakan SelectMultiple untuk mendukung lebih dari satu pilihan
        required=True
    )
     class Meta:
        model = UtilityData
        fields = ['tanggal', 'jam', 'shift', 'location', 'machine', 'category', 'status', 'masalah', 'penyebab', 'tindakan', 'image', 'pic', 'nomor_wo', 'waktu_pengerjaan']

class UtilityData2Form(forms.ModelForm):
    pic = forms.ModelMultipleChoiceField(
        queryset=PICUtility2.objects.all(),  # Ambil data PIC dari model PICMechanical2
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),  # Gunakan SelectMultiple dengan styling
        required=True
    )

    class Meta:
        model = UtilityData2
        fields = [
            'tanggal', 'jam', 'shift', 'status', 'masalah', 'penyebab', 
            'line', 'mesin', 'nomer', 'pekerjaan', 'status_pekerjaan', 
            'tindakan_perbaikan', 'tindakan_pencegahan', 'image', 'pic', 
            'nomor_wo', 'waktu_pengerjaan'
        ]

        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'jam': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'shift': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'masalah': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'penyebab': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'line': forms.TextInput(attrs={'class': 'form-control'}),
            'mesin': forms.TextInput(attrs={'class': 'form-control'}),
            'nomer': forms.TextInput(attrs={'class': 'form-control'}),
            'pekerjaan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status_pekerjaan': forms.TextInput(attrs={'class': 'form-control'}),
            'tindakan_perbaikan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tindakan_pencegahan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nomor_wo': forms.TextInput(attrs={'class': 'form-control'}),
            'waktu_pengerjaan': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class PICUtility2Form(forms.ModelForm):
    class Meta:
        model = PICUtility2
        fields = ['name', 'nokar']  # Pastikan field yang ingin diupdate tercakup di sini

class PICUtilityForm(forms.ModelForm):
    class Meta:
        model = PICUtility
        fields = ['name', 'nokar']  # Pastikan field yang ingin diupdate tercakup di sini


class ItDataForm(forms.ModelForm):
    pic = forms.ModelMultipleChoiceField(
        queryset=PICIt.objects.all(),  # Ambil data PIC dari model PICMechanical2
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),  # Gunakan SelectMultiple dengan styling
        required=True
    )

    class Meta:
        model = ItData
        fields = [
            'tanggal', 'jam', 'shift', 'status', 'masalah', 'penyebab', 
            'line', 'mesin', 'nomer', 'pekerjaan', 'status_pekerjaan', 
            'tindakan_perbaikan', 'tindakan_pencegahan', 'image', 'pic', 
            'nomor_wo', 'waktu_pengerjaan'
        ]

        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'jam': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'shift': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'masalah': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'penyebab': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'line': forms.TextInput(attrs={'class': 'form-control'}),
            'mesin': forms.TextInput(attrs={'class': 'form-control'}),
            'nomer': forms.TextInput(attrs={'class': 'form-control'}),
            'pekerjaan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status_pekerjaan': forms.TextInput(attrs={'class': 'form-control'}),
            'tindakan_perbaikan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tindakan_pencegahan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nomor_wo': forms.TextInput(attrs={'class': 'form-control'}),
            'waktu_pengerjaan': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class PICItForm(forms.ModelForm):
    class Meta:
        model = PICIt
        fields = ['name', 'nokar']  # Pastikan field yang ingin diupdate tercakup di sini

# class LaporanDataForm(forms.ModelForm):
#     pic = forms.ModelMultipleChoiceField(
#         queryset=PICLaporan.objects.all(),  # Ambil data PIC dari model PICMechanical2
#         widget=forms.SelectMultiple(attrs={'class': 'form-control'}),  # Gunakan SelectMultiple dengan styling
#         required=True
#     )

#     class Meta:
#         model = LaporanData
#         fields = [
#             'tanggal', 'shift', 'masalah', 'image', 'pic'
#         ]

#         widgets = {
#             'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'shift': forms.Select(attrs={'class': 'form-control'}),
#             'masalah': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#             'image': forms.FileInput(attrs={'class': 'form-control'}),
#         }

class LaporanDataForm(forms.ModelForm):
    pic = forms.ModelMultipleChoiceField(
        queryset=PICLaporan.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True
    )
    piclembur = forms.ModelMultipleChoiceField(  # Tambahkan field baru
        queryset=PICLembur.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False  # Opsional, jadi tidak wajib diisi
    )

    class Meta:
        model = LaporanData
        fields = [
            'tanggal', 'shift', 'masalah', 'catatan', 'image', 'pic', 'piclembur'  # Tambahkan piclembur
        ]

        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'shift': forms.Select(attrs={'class': 'form-control'}),
            'masalah': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'catatan': forms.Textarea(attrs={
                'class': 'form-control catatan-textarea', 
                'rows': 3, 
                'placeholder': 'Masukkan catatan penting di sini...'
            }),  # Widget khusus untuk catatan
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['catatan'].required = False  # Catatan tidak wajib diisi
        
        # Tambahkan CSS class untuk catatan jika sudah ada isinya
        if self.instance and self.instance.catatan:
            self.fields['catatan'].widget.attrs['class'] += ' has-catatan'


class PICLaporanForm(forms.ModelForm):
    class Meta:
        model = PICLaporan
        fields = ['name', 'nokar']  # Pastikan field yang ingin diupdate tercakup di sini

class PICLemburForm(forms.ModelForm):
    class Meta:
        model = PICLaporan
        fields = ['name', 'nokar']

# class LaporanMechanicalDataForm(forms.ModelForm):
#     pic = forms.ModelMultipleChoiceField(
#         queryset=PICLaporan.objects.all(),
#         widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
#         required=True
#     )
#     piclembur = forms.ModelMultipleChoiceField(  # Tambahkan field baru
#         queryset=PICLemburMechanical.objects.all(),
#         widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
#         required=False  # Opsional, jadi tidak wajib diisi
#     )

#     class Meta:
#         model = LaporanMechanicalData
#         fields = [
#             'tanggal', 'shift', 'masalah', 'image', 'pic', 'piclembur'  # Tambahkan piclembur
#         ]

#         widgets = {
#             'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'shift': forms.Select(attrs={'class': 'form-control'}),
#             'masalah': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#             'image': forms.FileInput(attrs={'class': 'form-control'}),
#         }

class LaporanMechanicalDataForm(forms.ModelForm):
    pic = forms.ModelMultipleChoiceField(
        queryset=PICLaporanMechanical.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True
    )
    piclembur = forms.ModelMultipleChoiceField(
        queryset=PICLemburMechanical.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = LaporanMechanicalData
        fields = ['tanggal', 'shift', 'masalah', 'image', 'pic', 'piclembur']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'shift': forms.Select(attrs={'class': 'form-control'}),
            'masalah': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['pic'].initial = self.instance.pic.values_list('id', flat=True)
            self.fields['piclembur'].initial = self.instance.piclembur.values_list('id', flat=True)


class PICLaporanMechanicalForm(forms.ModelForm):
    class Meta:
        model = PICLaporanMechanical
        fields = ['name', 'nokar']  # Pastikan field yang ingin diupdate tercakup di sini

class PICLemburMechanicalForm(forms.ModelForm):
    class Meta:
        model = PICLaporanMechanical
        fields = ['name', 'nokar']

class ScheduleMechanicalDataForm(forms.ModelForm):
    # Field tambahan untuk memilih `PICLemburMechanical` melalui `ManyToManyField`
    pic_lemburmechanical = forms.ModelMultipleChoiceField(
        queryset=PICLemburMechanical.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Menggunakan checkbox untuk memilih banyak data
        required=False,  # Tidak wajib diisi
        label="PIC Lembur Mechanical"
    )

    class Meta:
        model = ScheduleMechanicalData
        fields = ['tanggal', 'shift', 'jam', 'pekerjaan', 'image', 'user', 'pic_lemburmechanical']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date'}),
            'jam': forms.TimeInput(attrs={'type': 'time'}),
            'pekerjaan': forms.Textarea(attrs={'rows': 3}),
        }

    def save(self, commit=True):
        # Override metode save untuk mengelola hubungan ManyToManyField
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()  # Menyimpan relasi ManyToMany
        return instance
    

class IssueForm(forms.ModelForm):
    class Meta:
        model = ProjectIssue  # Model yang digunakan
        fields = ['issue', 'pic', 'due_date', 'status', 'remark']  # Fields yang digunakan dalam form

        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),  # Menampilkan input tanggal
        }
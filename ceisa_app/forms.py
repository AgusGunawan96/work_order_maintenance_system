from django import forms
from django.forms import formset_factory
from django.core.validators import RegexValidator
from ceisa_app.models import refrensiAsalBarang, refrensiAsalBarangFTZ, refrensiBank, refrensiCaraBayar, refrensiCaraDagang, refrensiDaerahAsal, refrensiDokumen, refrensiRespon, refrensiSatuanBarang, refrensiEntitas, refrensiFasilitas, refrensiFasilitasTarif, refrensiIjin, refrensiIncoterm, refrensiJenisEkspor, refrensiJenisJaminan, refrensiJenisKemasan, refrensiJenisPIB, refrensiJenisPungutan, refrensiJenisTPB, refrensiValuta, refrensiJenisTransaksiPerdagangan, refrensiJenisVD, refrensiKantor, refrensiKategoriBarang, refrensiKategoriEkspor, refrensiKategoriKeluarFTZ, refrensiKodeJenisImpor, refrensiKomoditiCukai, refrensiLokasiBayar, refrensiNegara, refrensiSpesifikasiKhusus, refrensiStatus,  refrensiStatusPengusaha, refrensiTujuanPemasukan, refrensiTujuanPengeluaran, refrensiTujuanPengiriman
from django_select2.forms import Select2Widget

class ceisaKirimImporHeaderForm(forms.Form):
    asalData = forms.CharField(label='Asal Data',max_length=255,widget=forms.HiddenInput(),initial='S')
    asuransi = forms.DecimalField(label='Asuransi',max_digits=24, decimal_places=2, required=True)
    biayaPengurang = forms.DecimalField(label='Biaya Pengurang yang dikenakan',max_digits=24, decimal_places=2, required=True)
    biayaTambahan = forms.DecimalField(label='Biaya Tambahan yang dikenakan',max_digits=24, decimal_places=2, required=True)
    bruto = forms.DecimalField(label='Bruto',max_digits=24, decimal_places=4, required=True)
    cif = forms.DecimalField(label='CIF',max_digits=24, decimal_places=2, required=True)
    disclaimer = forms.ChoiceField(
        label="Persetujuan pengguna dalam kirim dokumen pabean",
        choices=[
            ("0", "Tidak"),  # Value, Display text
            ("1", "Ya")
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'  # You can add additional attributes as needed
        }),
        initial="1"  # Set the initial value to "0" (Tidak)
    )
    flagVd = forms.ChoiceField(
        label="Flag Voluntary declaration",
        choices=[
            ("Y", "Ya"),  # Value, Display text
            ("T", "Tidak")
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'  # You can add additional attributes as needed
        }),
        initial="T"  # Set the initial value to "0" (Tidak)
    )
    fob = forms.DecimalField(label='FOB',max_digits=24, decimal_places=2, required=True)
    freight = forms.DecimalField(label='Freight',max_digits=24, decimal_places=2, required=True)
    hargaPenyerahan = forms.DecimalField(label='Harga Penyerahan',max_digits=24, decimal_places=4, required=True,widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    idPengguna = forms.CharField(label='ID Pengguna',max_length=255, required=True)
    # jabatanTtd = forms.CharField(label='ID Jabatan',max_length=255, required=True)
    jumlahKontainer = forms.IntegerField(label='jumlah peti kemas yang digunakan untuk mengangkut barang',required=True)
    jumlahTandaPengaman = forms.IntegerField(label='Jumlah Tanda Pengaman FTZ 03',required=True)
    kodeAsuransi = forms.ChoiceField(
        label="Kode Asuransi",
        choices=[
            ("LN", "Luar Negeri"),  # Value, Display text
            ("DN", "Dalam Negeri")
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'  # You can add additional attributes as needed
        }),
        initial="LN"  # Set the initial value to "0" (Tidak)
    )
    kodeCaraBayar = forms.ChoiceField(
        choices=refrensiCaraBayar.choices,
       widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    kodeDokumen = forms.ChoiceField(
        choices=refrensiDokumen.choices,
       widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    kodeIncoterm = forms.ChoiceField(
        choices=refrensiIncoterm.choices,
       widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    kodeJenisImpor = forms.ChoiceField(
        choices=refrensiKodeJenisImpor.choices,
       widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    kodeJenisEkspor = forms.ChoiceField(
        choices=refrensiJenisEkspor.choices,
       widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    kodeJenisNilai = forms.ChoiceField(
        choices=refrensiJenisTransaksiPerdagangan.choices,
       widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    kodeJenisProsedur = forms.ChoiceField(
        choices=refrensiJenisPIB.choices,
       widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    # kodeKantor = forms.ChoiceField(
    #     choices=refrensiKantor.choices,
    #    widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    # )
    kodeTps = forms.CharField(label='Kode TPS',max_length=255, required=True)
    kodePelTransit = forms.CharField(label='Kode Pel Transit',max_length=255, required=True)
    kodePelTujuan = forms.CharField(label='Kode Pel Tujuan',max_length=255, required=True)
    kodePelMuat = forms.CharField(label='Kode Pel Muat',max_length=255, required=True)

    kodeTutupPu = forms.ChoiceField(
        label="Referensi TutupPu",
        choices=[
            ("11", "BC 1.1"),  # Value, Display text
            ("12", "BC 1.2"),
            ("14", "BC 1.4")
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'  # You can add additional attributes as needed
        }),
        initial="11"  # Set the initial value to "0" (Tidak)
    )
    kodeValuta = forms.ChoiceField(
        choices=refrensiValuta.choices,
        widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    # kotaTtd = forms.CharField(label='Kota TTD',max_length=255, required=True)
    kotaTtd = forms.CharField(label='Kota TTD',max_length=255,widget=forms.HiddenInput(),initial='Bekasi')

    # namaTtd = forms.CharField(label='Nama TTD',max_length=255, required=True)
    ndpbm = forms.DecimalField(label='ndpbm',max_digits=24, decimal_places=4, required=True,widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    netto = forms.DecimalField(label='Netto',max_digits=24, decimal_places=4, required=True,widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    nilaiBarang = forms.DecimalField(label='Nilai Barang',max_digits=24, decimal_places=2, required=True)
    nilaiIncoterm = forms.DecimalField(label='Nilai Incoterm',max_digits=24, decimal_places=2, required=True)
    nilaiMaklon = forms.DecimalField(label='Nilai Maklon',max_digits=24, decimal_places=2, required=True)
    nomorAju = forms.CharField(
        label="Nomor Aju",
        max_length=26,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9]{26}$',
                message="Sesuaikan format nomor pengajuan dokumen impor terdiri 26 digit: 4 digit kode kantor, 2 digit kode dokumen pabean, 6 digit unik perusahaan, 8 digit tanggal pengajuan dengan format YYYYMMDD, 6 digit sequence/nomor urut pengajuan dokumen impor"
            )
        ]
    )
    nomorBc11 = forms.CharField(label='Nomor BC 11',max_length=255, required=True)
    posBc11 = forms.CharField(label='POS BC 11',max_length=255, required=True)
    seri = forms.IntegerField(label='Seri',required=True)
    subPosBc11 = forms.CharField(label='Sub Pos BC 11',max_length=255, required=True)
    totalDanaSawit = forms.DecimalField(label='Total Dana Sawit',max_digits=24, decimal_places=2, required=True)
    volume = forms.DecimalField(label='Volume',max_digits=24, decimal_places=4, required=True)
    vd = forms.DecimalField(label='Total nilai voluntary declaration',max_digits=24, decimal_places=4, required=True)

class ceisaKirimImporBarangTarifForm(forms.Form):
    jumlahSatuan            = forms.DecimalField(label='Jumlah Satuan barang tarif Bea Masuk',max_digits=24, decimal_places=4, required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    kodeFasilitasTarif = forms.ChoiceField(
        choices=refrensiFasilitasTarif.choices,
        widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    kodeJenisPungutan       = forms.CharField(label='Kode Jenis Pungutan',max_length=255,widget=forms.HiddenInput(),initial='BM')
    kodeJenisTarif          = forms.ChoiceField(
        label="Kode Jenis Tarif",
        choices=[
            ("1", "Advalorum"),  # Value, Display text
            ("2", "Spesifik")
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'  # You can add additional attributes as needed
        }),
        initial="1"  # Set the initial value to "0" (Tidak)
    )
    nilaiBayar              = forms.DecimalField(label='Nilai Barang tarif BM',max_digits=24, decimal_places=2, required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    nilaiFasilitas          = forms.DecimalField(label='Total nilai voluntary declaration',max_digits=24, decimal_places=2, required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    seriBarang              = forms.IntegerField(label='Seri Barang' , required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    tarif                   = forms.DecimalField(label='Tarif BM',max_digits=24, decimal_places=2, required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    tarifFasilitas          = forms.DecimalField(label='Tarif Fasilitas',max_digits=24, decimal_places=2, required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))

class ceisaKirimImporBarangVDForm(forms.Form):
    kodeJenisVd = forms.ChoiceField(
        choices=refrensiJenisVD.choices,
        widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    nilaiBarangVd   = forms.DecimalField(label='Nilai barang VD',max_digits=24, decimal_places=4, required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))

class ceisaKirimImporBarangSpekKhususForm(forms.Form):
    seriBarangSpekKhusus    = forms.IntegerField(label='Seri Barang spek Khusus', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    kodeSpekKhusus = forms.ChoiceField(
        choices=refrensiSpesifikasiKhusus.choices,
        widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    uraianSpekKhusus        = forms.CharField(label='Uraian Spek Khusus', max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

class ceisaKirimImporBarangPemilikForm(forms.Form):
    seriBarang        = forms.IntegerField(label='Seri Barang', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    seriBarangPemilik = forms.IntegerField(label='Seri Barang Pemilik', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    seriEntitas       = forms.IntegerField(label='Seri Entitas', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))

class ceisaKirimImporBarangDokumenForm(forms.Form):
    seriDokumen = forms.CharField(label='Seri Dokumen',max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

class ceisaKirimImporBarangForm(forms.Form):
    asuransi = forms.IntegerField(label = 'Asuransi', required=False)
    bruto   = forms.IntegerField(label = 'Bruto', required=False)
    cif = forms.IntegerField(label='CIF', required=False,widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    cifRupiah   = forms.IntegerField(label='CIF Rupiah', required=False,widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    diskon = forms.IntegerField(label='Diskon', required=False)
    fob = forms.IntegerField(label='FOB', required=False)
    freight = forms.IntegerField(label='Freight', required=False)
    hargaEkspor = forms.IntegerField(label='Harga Ekspor', required=False)
    hargaPatokan    = forms.IntegerField(label='Harga Patokan', required=False)
    hargaPenyerahan = forms.IntegerField(label='Harga Penyerahan', required=False,widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    hargaPerolehan  = forms.IntegerField(label='Harga Perolehan', required=False)
    hargaSatuan = forms.IntegerField(label='Harga Satuan', required=False)
    hjeCukai    = forms.IntegerField(label='Harga Jual Eceran Cukai', required=False)
    isiPerKemasan   = forms.IntegerField(label='Isi Per kemasan', required=False)
    jumlahBahanBaku = forms.IntegerField(label='Jumlah Bahan Baku', required=False)
    jumlahDilekatkan    = forms.IntegerField(label='Jumlah dilekatkan', required=False)
    jumlahKemasan   = forms.DecimalField(label='Volume',max_digits=24, decimal_places=2, required=True)
    jumlahPitaCukai = forms.IntegerField(label='Jumlah Pita Cukai', required=False)
    jumlahRealisasi = forms.IntegerField(label='Jumlah Realisasi', required=False)
    jumlahSatuan    = forms.DecimalField(label='Volume',max_digits=24, decimal_places=4, required=True)
    kapasitasSilinder   = forms.IntegerField(label='Kapasitas Silinder', required=False)
    kodeJenisKemasan = forms.ChoiceField(
        choices=refrensiJenisKemasan.choices,
        widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    kodeKondisiBarang = forms.ChoiceField(
        label="Kode Kondisi Barang",
        choices=[
            ("1", "Baik"),  # Value, Display text
            ("2", "Baru"),
            ("3", "Bekas"),
            ("4", "Segar"),
            ("5", "Beku"),
            ("6", "Baik/Baru"),
            ("7", "Baik/Beku"),
            ("8", "Baik/Bekas"),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'  # You can add additional attributes as needed
        }),
        initial="1"  # Set the initial value to "0" (Tidak)
    )
    kodeNegaraAsal = forms.CharField(
        label="Kode Negara Asal",
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{2}$',
                message="Sesuai kolom formulir BC 2.0 - D.32 Negara Asal Barang. Lihat Referensi Negara"
            )
        ]
    )
    kodeSatuanBarang = forms.ChoiceField(
        choices=refrensiSatuanBarang.choices,
        widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    merk    = forms.CharField(label='Merk',max_length=255, required=True)
    ndpbm   = forms.IntegerField(label='Nilai Dasar Penghitungan Bea Masuk', required=False,widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    netto   = forms.IntegerField(label='Netto', required=False,widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    nilaiBarang = forms.IntegerField(label='Nilai Barang', required=False)
    nilaiDanaSawit  = forms.IntegerField(label='Nilai Dana Sawit', required=False)
    nilaiDevisa = forms.IntegerField(label='Nilai Devisa', required=False)
    nilaiTambah = forms.IntegerField(label='Nilai Tambah', required=False)
    pernyataanLartas = forms.ChoiceField(
        label="Pernyataan Barang Lartas",
        choices=[
            ("Y", "Ya"),  # Value, Display text
            ("T", "Tidak"),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'  # You can add additional attributes as needed
        }),
        initial="Y"  # Set the initial value to "0" (Tidak)
    )
    persentaseImpor = forms.IntegerField(label='Presentase Impor', required=False)
    posTarif    = forms.CharField(label='Pos Tarif',max_length=255, required=True)
    saldoAkhir  = forms.IntegerField(label='Saldo Akhir', required=False)
    saldoAwal   = forms.IntegerField(label='Saldo Awal', required=False)
    seriBarang  = forms.IntegerField(label='Seri Barang', required=False)
    seriBarangDokAsal   = forms.IntegerField(label='Seri Barang Dok Asal', required=False)
    seriIjin    = forms.IntegerField(label='Seri Ijin Barang', required=False)
    tahunPembuatan  = forms.IntegerField(label='Tahun Pembuatan Barang', required=False)
    tarifCukai  = forms.IntegerField(label='Tarif Cukai', required=False)
    tipe    = forms.CharField(label='Tipe',max_length=255, required=True)
    uraian  = forms.CharField(label='Uraian',max_length=255, required=True)
    volume  = forms.DecimalField(label='Volume Barang',max_digits=24, decimal_places=4, required=True)
    barangDokumen_formset = formset_factory(ceisaKirimImporBarangDokumenForm, extra=2)
    barangPemilik_formset  = formset_factory(ceisaKirimImporBarangPemilikForm, extra=2)
    barangSpekKhusus_formset = formset_factory(ceisaKirimImporBarangSpekKhususForm, extra=2)
    barangVD_formset         = formset_factory(ceisaKirimImporBarangVDForm,extra=2)
    barangTarif_formset      = formset_factory(ceisaKirimImporBarangTarifForm,extra=2)
    


class ceisaKirimImporEntitasPengirimForm(forms.Form):
    namaEntitasPengirim = forms.CharField(label='Nama Entitas', max_length=255, required=False)
    alamatEntitasPengirim = forms.CharField(label='Alamat Entitas', max_length=255, required=False)
    kodeNegaraPengirim = forms.ChoiceField(
        choices=refrensiNegara.choices,
        widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
class ceisaKirimImporEntitasPenjualForm(forms.Form):
    namaEntitasPenjual = forms.CharField(label='Nama Entitas', max_length=255, required=False)
    alamatEntitasPenjual = forms.CharField(label='Alamat Entitas', max_length=255, required=False)
    kodeNegaraPenjual = forms.ChoiceField(
        choices=refrensiNegara.choices,
        widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    # kodeEntitas       = forms.CharField(label='Kode Entitas',max_length=255,widget=forms.HiddenInput(),initial='1')
    # kodeJenisApi = forms.ChoiceField(
    #     label="Kode Jenis API",
    #     choices=[
    #         ("01", "APIU"),  # Value, Display text
    #         ("02", "APIP")
    #     ],
    #     widget=forms.Select(attrs={
    #         'class': 'form-control'  # You can add additional attributes as needed
    #     }),
    #     initial="01"  # Set the initial value to "0" (Tidak)
    # )
    # kodeJenisIdentitas = forms.ChoiceField(
    #     label="Kode Jenis Identitas",
    #     choices=[
    #         ("0", "NPWP 12 Digit"),
    #         ("1", "NPWP 10 Digit"),  # Value, Display text
    #         ("2", "Paspor"),
    #         ("3", "KTP"),
    #         ("4", "Lainnya"),
    #         ("5", "NPWP 15 Digit"),
    #     ],
    #     widget=forms.Select(attrs={
    #         'class': 'form-control'  # You can add additional attributes as needed
    #     }),
    #     initial="0"  # Set the initial value to "0" (Tidak)
    # )
    # kodeStatus = forms.ChoiceField(
    #     choices=refrensiStatus.choices,
    #     widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    # )
    # nibEntitas = forms.CharField(label='NIB Entitas', max_length=255, required=False)
    # nomorIdentitas = forms.CharField(label='Nomor Identitas', max_length=255, required=False)
    # seriEntitas = forms.IntegerField(label='Seri Entitas',required=False)

class ceisaKirimImporKemasanForm(forms.Form):
    jumlahKemasan   = forms.IntegerField(label='Jumlah Kemasan', required=False)
    kodeJenisKemasan = forms.ChoiceField(
        choices=refrensiJenisKemasan.choices,
        widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    merkKemasan = forms.CharField(label='Merk Kemasan', max_length=255, required=False)
    seriKemasan = forms.IntegerField(label='Seri Kemasan', required=False)

class ceisaKirimImporKontainerForm(forms.Form):
    kodeJenisKontainer = forms.ChoiceField(
        label="Kode Jenis Kontainer",
        choices=[
            ("4", "Empty"),
            ("7", "LCL"),  # Value, Display text
            ("8", "FCL")
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'  # You can add additional attributes as needed
        }),
        initial="4"  # Set the initial value to "0" (Tidak)
    )
    kodeTipeKontainer = forms.ChoiceField(
        label="Kode Tipe Kontainer",
        choices=[
            ("1", "General/Dry Cargo"),
            ("2", "Tunne Type"),  # Value, Display text
            ("3", "Open Top Steel"),
            ("4", "Flat Rack"),
            ("5", "Reefer/Refregete"),
            ("6", "Barge Container"),
            ("7", "Bulk Container"),
            ("8", "Isotank"),
            ("99", "Lain-Lain"),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'  # You can add additional attributes as needed
        }),
        initial="1"  # Set the initial value to "0" (Tidak)
    )
    kodeUkuranKontainer = forms.ChoiceField(
        label="Kode Ukuran Kontainer",
        choices=[
            ("20", "20 feet"),
            ("40", "40 feet"),  # Value, Display text
            ("45", "45 feet"),
            ("60", "60 feet")
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'  # You can add additional attributes as needed
        }),
        initial="20"  # Set the initial value to "0" (Tidak)
    )
    nomorKontainer = forms.CharField(label='Nomor Kontainer',max_length=255, required=False)
    seriKontainer  = forms.IntegerField(label='Seri Kontainer', required=False)

class ceisaKirimImporDokumenForm(forms.Form):
    idDokumen       = forms.CharField(label='ID Dokumen', max_length=250, required=False)
    kodeDokumen     = forms.CharField(label='Kode Dokumen',max_length=255,widget=forms.HiddenInput(),initial='380')
    kodeFasilitas = forms.ChoiceField(
        choices=refrensiFasilitas.choices,
        widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    kodeIjin = forms.ChoiceField(
        choices=refrensiIjin.choices,
        widget=Select2Widget(attrs={'class': 'form-control select2'}),  # Add any widget attributes you need
    )
    namaFasilitas   = forms.CharField(label='Nama Fasilitas', max_length=255, required=False)
    nomorDokumen    = forms.CharField(label='Nomor Dokumen', max_length=255, required=False)
    seriDokumen     = forms.IntegerField(label='Seri Dokumen', required=False, )
    tanggalDokumen  = forms.DateField(label='Tanggal Dokumen', required=False,widget=forms.TextInput(attrs={'type': 'date'}))
    urlDokumen      = forms.CharField(label='URL Dokumen', max_length=255, required=False)


class ceisaKirimImporPengangkutForm(forms.Form):
    kodeBendera     = forms.CharField(label='Kode Bendera', max_length=255, required=False)
    namaPengangkut  = forms.CharField(label='Nama Pengangkut', max_length=255, required=False)
    nomorPengangkut = forms.CharField(label='Nomor Pengangkut', max_length=255, required=False)
    kodeCaraAngkut = forms.ChoiceField(
        label="Kode Cara Angkut",
        choices=[
            ("1", "Laut"),
            ("2", "Kereta Api"),  # Value, Display text
            ("3", "Darat"),
            ("4", "Udara"),
            ("5", "Pos"),
            ("6", "Multimoda"),
            ("7", "Instalasi/Pipa"),
            ("8", "Perairan"),
            ("9", "Lainnya")
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'  # You can add additional attributes as needed
        }),
        initial="1"  # Set the initial value to "0" (Tidak)
    )
    seriPengangkut  = forms.IntegerField(label='Seri Pengangkut', required=False)

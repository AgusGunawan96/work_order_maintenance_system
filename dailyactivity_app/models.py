# dailyactivity_app/models.py
from django.db import models
from django.contrib.auth.models import User

class Shift(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'dailyactivity_app_shift'

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'dailyactivity_app_location'

    def __str__(self):
        return self.name

class Machinemechanical(models.Model):
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    nomor = models.CharField(max_length=50, null=True, blank=True, )  # Menambahkan kolom nomor yang bisa kosong

    class Meta:
        db_table = 'dailyactivity_app_machine_mechanical'

    def __str__(self):
        return self.name
    

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'dailyactivity_app_category'

    def __str__(self):
        return self.name

class Status(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'dailyactivity_app_status'

    def __str__(self):
        return self.name

class Machineelectrical(models.Model):
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, default=2)
    nomor = models.CharField(max_length=50, null=True, blank=True, )  # Menambahkan kolom nomor yang bisa kosong

    class Meta:
        db_table = 'dailyactivity_app_machine_electrical'

    def __str__(self):
        return self.name

class Machineutility(models.Model):
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, default=2)
    nomor = models.CharField(max_length=50, null=True, blank=True, )  # Menambahkan kolom nomor yang bisa kosong

    class Meta:
        db_table = 'dailyactivity_app_machine_utility'

    def __str__(self):
        return self.name

class MechanicalData(models.Model):
    tanggal = models.DateField()
    jam = models.DateTimeField(null=True, blank=True)  # Menyimpan waktu jika ada, jika tidak ada bisa kosong
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machinemechanical, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)  # ID 1 atau ID lain yang ada
    status = models.ForeignKey(Status, on_delete=models.CASCADE, default=1)
    masalah = models.TextField()
    penyebab = models.TextField()
    tindakan = models.TextField()
    # TAMBAHKAN FIELD BARU INI:
    tindakan_perbaikan = models.TextField(null=True, blank=True)  # Field tambahan untuk tindakan perbaikan yang terpisah
    tindakan_pencegahan = models.TextField(null=True, blank=True)  # Field tambahan untuk tindakan pencegahan
    image = models.ImageField(upload_to='mechanical_images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # UPDATE PIC RELATIONSHIP:
    pic = models.ManyToManyField('PICMechanical2', blank=True, through='MechanicalDataPIC')  # Ganti ke PICMechanical2
    nomor_wo = models.CharField(max_length=100, blank=True, null=True)  # Menyimpan nomor WO
    waktu_pengerjaan = models.CharField(max_length=100, blank=True, null=True)  # Menyimpan waktu pengerjaan

    class Meta:
        db_table = 'dailyactivity_app_mechanical_data'

    def __str__(self):
        return f"{self.tanggal} - {self.machine.name} - {self.user.username}"

class MechanicalData2(models.Model):
    tanggal = models.DateField()
    jam = models.DateTimeField(null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, default=1)
    masalah = models.TextField()
    penyebab = models.TextField(null=True, blank=True)
    line = models.CharField(max_length=255, null=True, blank=True)
    mesin = models.CharField(max_length=255, null=True, blank=True)
    nomer = models.CharField(max_length=50, null=True, blank=True)
    pekerjaan = models.TextField(null=True, blank=True)
    status_pekerjaan = models.CharField(max_length=100, null=True, blank=True)
    tindakan_perbaikan = models.TextField(null=True, blank=True)
    tindakan_pencegahan = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='mechanical_images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pic = models.ManyToManyField('PICMechanical2', blank=True, through='MechanicalDataPIC2')  # Menggunakan PICMechanical2
    nomor_wo = models.CharField(max_length=100, blank=True, null=True)
    waktu_pengerjaan = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'dailyactivity_app_mechanical_data2'

    def __str__(self):
        return f"{self.tanggal} - {self.user.username}"

    
class PICMechanical2(models.Model):
    name = models.CharField(max_length=100)
    nokar = models.CharField(max_length=100)

    class Meta:
        db_table = 'dailyactivity_app_pic_mechanical2'

    def __str__(self):
        return self.name


class MechanicalDataPIC2(models.Model):
    mechanical_data = models.ForeignKey('MechanicalData2', on_delete=models.CASCADE)
    pic_mechanical = models.ForeignKey('PICMechanical2', on_delete=models.CASCADE)

    class Meta:
        db_table = 'dailyactivity_app_mechanical_data_pic2'


class PICMechanical(models.Model):
    name = models.CharField(max_length=100)
    nokar = models.CharField(max_length=100)

    class Meta:
        db_table = 'dailyactivity_app_pic_mechanical'

    def __str__(self):
        return self.name

# UPDATE THROUGH TABLE:
class MechanicalDataPIC(models.Model):
    mechanical_data = models.ForeignKey(MechanicalData, on_delete=models.CASCADE)
    pic_mechanical = models.ForeignKey('PICMechanical2', on_delete=models.CASCADE)  # Ganti ke PICMechanical2

    class Meta:
        db_table = 'dailyactivity_app_mechanical_data_pic'

class ElectricalData(models.Model):
    tanggal = models.DateField()
    # jam = models.TimeField()
    jam = models.DateTimeField(null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machineelectrical, on_delete=models.CASCADE)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)  # ID 1 atau ID lain yang ada
    status = models.ForeignKey(Status, on_delete=models.CASCADE, default=1)
    masalah = models.TextField()
    penyebab = models.TextField()
    tindakan = models.TextField()
    image = models.ImageField(upload_to='electrical_images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pic = models.ManyToManyField('PICElectrical', blank=True, through='ElectricalDataPIC')  # Menambahkan through
    nomor_wo = models.CharField(max_length=100, blank=True, null=True)  # Menyimpan nomor WO
    waktu_pengerjaan = models.CharField(max_length=100, blank=True, null=True)  # Menyimpan waktu pengerjaan

    class Meta:
        db_table = 'dailyactivity_app_electrical_data'

    def __str__(self):
        return f"{self.tanggal} - {self.machine.name} - {self.user.username}"
    
class PICElectrical(models.Model):
    name = models.CharField(max_length=100)
    nokar = models.CharField(max_length=100)

    class Meta:
        db_table = 'dailyactivity_app_pic_electrical'

    def __str__(self):
        return self.name

class ElectricalDataPIC(models.Model):
    electrical_data = models.ForeignKey(ElectricalData, on_delete=models.CASCADE)
    pic_electrical = models.ForeignKey('PICElectrical', on_delete=models.CASCADE)

    class Meta:
        db_table = 'dailyactivity_app_electrical_data_pic'

class UtilityData(models.Model):
    tanggal = models.DateField()
    jam = models.TimeField()
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machineutility, on_delete=models.CASCADE)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)  # ID 1 atau ID lain yang ada
    status = models.ForeignKey(Status, on_delete=models.CASCADE, default=1)
    masalah = models.TextField()
    penyebab = models.TextField()
    tindakan = models.TextField()
    image = models.ImageField(upload_to='utility_images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pic = models.ManyToManyField('PICUtility', blank=True, through='UtilityDataPIC')  # Menambahkan through
    nomor_wo = models.CharField(max_length=100, blank=True, null=True)  # Menyimpan nomor WO
    waktu_pengerjaan = models.CharField(max_length=100, blank=True, null=True)  # Menyimpan waktu pengerjaan

    class Meta:
        db_table = 'dailyactivity_app_utility_data'

    def __str__(self):
        return f"{self.tanggal} - {self.machine.name} - {self.user.username}"
    
class PICUtility(models.Model):
    name = models.CharField(max_length=100)
    nokar = models.CharField(max_length=100)

    class Meta:
        db_table = 'dailyactivity_app_pic_utility'

    def __str__(self):
        return self.name

class UtilityDataPIC(models.Model):
    utility_data = models.ForeignKey(UtilityData, on_delete=models.CASCADE)
    pic_utility = models.ForeignKey('PICUtility', on_delete=models.CASCADE)

    class Meta:
        db_table = 'dailyactivity_app_utility_data_pic'


class UtilityData2(models.Model):
    tanggal = models.DateField()
    jam = models.DateTimeField(null=True, blank=True)  # Menyimpan waktu jika ada, jika tidak ada bisa kosong
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, default=1)
    masalah = models.TextField()
    penyebab = models.TextField(null=True, blank=True)
    line = models.CharField(max_length=255, null=True, blank=True)   # Field line seperti di migration
    mesin = models.CharField(max_length=255, null=True, blank=True)  # Field mesin seperti di migration
    nomer = models.CharField(max_length=50, null=True, blank=True)   # Field nomer seperti di migration
    pekerjaan = models.TextField(null=True, blank=True)   # Field pekerjaan seperti di migration
    status_pekerjaan = models.CharField(max_length=100, null=True, blank=True)   # Field status_pekerjaan seperti di migration
    tindakan_perbaikan = models.TextField(null=True, blank=True)  # Field tambahan untuk tindakan perbaikan yang terpisah
    tindakan_pencegahan = models.TextField(null=True, blank=True)  # Field tambahan untuk tindakan pencegahan
    image = models.ImageField(upload_to='utility_images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pic = models.ManyToManyField('PICUtility2', blank=True, through='UtilityDataPIC2')  # Ganti ke PICUtility2
    nomor_wo = models.CharField(max_length=100, blank=True, null=True)  # Menyimpan nomor WO
    waktu_pengerjaan = models.CharField(max_length=100, blank=True, null=True)  # Menyimpan waktu pengerjaan

    class Meta:
        db_table = 'dailyactivity_app_utility_data2'

    def __str__(self):
        return f"{self.tanggal} - {self.user.username}"


    
class PICUtility2(models.Model):
    name = models.CharField(max_length=100)
    nokar = models.CharField(max_length=100)

    class Meta:
        db_table = 'dailyactivity_app_pic_utility2'

    def __str__(self):
        return self.name


class UtilityDataPIC2(models.Model):
    utility_data = models.ForeignKey('UtilityData2', on_delete=models.CASCADE)
    pic_utility = models.ForeignKey('PICUtility2', on_delete=models.CASCADE)

    class Meta:
        db_table = 'dailyactivity_app_utility_data_pic2'


class TabelMain(models.Model):
    history_id = models.CharField(max_length=11, null=True)
    tgl_his = models.DateTimeField(null=True)
    jam_his = models.CharField(max_length=12, null=True)
    id_line = models.FloatField(null=True)
    id_mesin = models.FloatField(null=True)
    nomer = models.CharField(max_length=10, null=True)
    id_section = models.FloatField(null=True)
    id_pekerjaan = models.FloatField(null=True)
    number_wo = models.CharField(max_length=15, null=True)
    deskripsi_perbaikan = models.TextField(null=True)
    id_penyebab = models.FloatField(null=True)
    penyebab = models.TextField(null=True)
    akar_masalah = models.TextField(null=True)
    tindakan_perbaikan = models.TextField(null=True)
    tindakan_pencegahan = models.TextField(null=True)
    status_pekerjaan = models.CharField(max_length=1, null=True)
    # ... (fields lainnya sesuai struktur tabel)

    class Meta:
        db_table = 'dbo.tabel_main'  # Nama tabel sesuai dengan nama asli di database
        managed = False  # Agar Django tidak melakukan migrasi pada tabel ini


class ItData(models.Model):
    tanggal = models.DateField()
    jam = models.DateTimeField(null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, default=1)
    masalah = models.TextField()
    penyebab = models.TextField(null=True, blank=True)
    line = models.CharField(max_length=255, null=True, blank=True)
    mesin = models.CharField(max_length=255, null=True, blank=True)
    nomer = models.CharField(max_length=50, null=True, blank=True)
    pekerjaan = models.TextField(null=True, blank=True)
    status_pekerjaan = models.CharField(max_length=100, null=True, blank=True)
    tindakan_perbaikan = models.TextField(null=True, blank=True)
    tindakan_pencegahan = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='it_images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pic = models.ManyToManyField('PICIt', blank=True, through='ItDataPIC')  # Menggunakan PICMechanical2
    nomor_wo = models.CharField(max_length=100, blank=True, null=True)
    waktu_pengerjaan = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'dailyactivity_app_it_data'

    def __str__(self):
        return f"{self.tanggal} - {self.user.username}"

    
class PICIt(models.Model):
    name = models.CharField(max_length=100)
    nokar = models.CharField(max_length=100)

    class Meta:
        db_table = 'dailyactivity_app_pic_it'

    def __str__(self):
        return self.name


class ItDataPIC(models.Model):
    it_data = models.ForeignKey('ItData', on_delete=models.CASCADE)
    pic_it = models.ForeignKey('PICIt', on_delete=models.CASCADE)

    class Meta:
        db_table = 'dailyactivity_app_utility_data_it'


# class LaporanData(models.Model):
#     tanggal = models.DateField()
#     shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
#     masalah = models.TextField()
#     catatan = models.TextField(blank=True, null=True)  # Field baru untuk catatan khusus
#     voice_note_masalah = models.FileField(upload_to='voice_notes/', blank=True, null=True)
#     voice_note_catatan = models.FileField(upload_to='voice_notes/', blank=True, null=True)
#     image = models.ImageField(upload_to='laporan_images/', null=True, blank=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     pic = models.ManyToManyField('PICLaporan', blank=True, through='LaporanDataPIC')  
#     piclembur = models.ManyToManyField('PICLembur', blank=True, through='LemburDataPIC')  
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = 'dailyactivity_app_laporan_data'
#         verbose_name = 'Laporan Data'
#         verbose_name_plural = 'Laporan Data'

#     def __str__(self):
#         return f"{self.tanggal} - {self.user.username}"

# class LaporanData(models.Model):
#     tanggal = models.DateField()
#     shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
#     masalah = models.TextField()  # Ini tetap jadi deskripsi pekerjaan
    
#     # KOLOM BARU YANG DITAMBAHKAN:
#     jenis_pekerjaan = models.CharField(max_length=200, null=True, blank=True)
#     lama_pekerjaan = models.CharField(max_length=100, null=True, blank=True) 
#     pic_pekerjaan = models.CharField(max_length=100, null=True, blank=True)
    
#     catatan = models.TextField(blank=True, null=True)
#     voice_note_masalah = models.FileField(upload_to='voice_notes/', blank=True, null=True)
#     voice_note_catatan = models.FileField(upload_to='voice_notes/', blank=True, null=True)
#     image = models.ImageField(upload_to='laporan_images/', null=True, blank=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     pic = models.ManyToManyField('PICLaporan', blank=True, through='LaporanDataPIC')
#     piclembur = models.ManyToManyField('PICLembur', blank=True, through='LemburDataPIC')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = 'dailyactivity_app_laporan_data'
#         verbose_name = 'Laporan Data'
#         verbose_name_plural = 'Laporan Data'

#     def __str__(self):
#         return f"{self.tanggal} - {self.user.username} - {self.jenis_pekerjaan or 'No Type'}"
class LaporanData(models.Model):
    # Field yang udah ada (JANGAN DIHAPUS)
    tanggal = models.DateField()
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    masalah = models.TextField()  # Ini tetap jadi deskripsi pekerjaan
    
    # KOLOM LAMA YANG UDAH ADA (JANGAN DIHAPUS):
    jenis_pekerjaan = models.CharField(max_length=200, null=True, blank=True)
    lama_pekerjaan = models.CharField(max_length=100, null=True, blank=True) 
    pic_pekerjaan = models.CharField(max_length=100, null=True, blank=True)
    
    catatan = models.TextField(blank=True, null=True)
    voice_note_masalah = models.FileField(upload_to='voice_notes/', blank=True, null=True)
    voice_note_catatan = models.FileField(upload_to='voice_notes/', blank=True, null=True)
    image = models.ImageField(upload_to='laporan_images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pic = models.ManyToManyField('PICLaporan', blank=True, through='LaporanDataPIC')
    piclembur = models.ManyToManyField('PICLembur', blank=True, through='LemburDataPIC')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # FIELD BARU YANG LO MINTA TAMBAHIN (GAUL STYLE):
    nomor_wo = models.CharField(max_length=50, null=True, blank=True, verbose_name="Nomor WO")
    status_utility = models.CharField(
        max_length=20, 
        choices=[
            ('proses', 'Proses'),
            ('selesai', 'Selesai'),
            ('hold', 'Hold')
        ],
        default='proses',
        verbose_name="Status Utility"
    )
    lokasi = models.CharField(max_length=100, null=True, blank=True, verbose_name="Lokasi")
    mesin = models.CharField(max_length=100, null=True, blank=True, verbose_name="Mesin")
    nomor_mesin = models.CharField(max_length=50, null=True, blank=True, verbose_name="Nomor Mesin")
    jenis_pekerjaan_maintenance = models.CharField(max_length=100, null=True, blank=True, verbose_name="Jenis Pekerjaan Maintenance")
    penyebab = models.TextField(null=True, blank=True, verbose_name="Penyebab")
    tindakan_perbaikan = models.TextField(null=True, blank=True, verbose_name="Tindakan Perbaikan")

    class Meta:
        db_table = 'dailyactivity_app_laporan_data'
        verbose_name = 'Laporan Data'
        verbose_name_plural = 'Laporan Data'

    def __str__(self):
        return f"{self.tanggal} - {self.user.username} - {self.jenis_pekerjaan or 'No Type'}"

class DetailPekerjaan(models.Model):
    laporan = models.ForeignKey(LaporanData, on_delete=models.CASCADE, related_name='detail_pekerjaan')
    deskripsi = models.TextField()  # deskripsi detail pekerjaan
    jenis_pekerjaan = models.CharField(max_length=200)
    lama_pekerjaan = models.CharField(max_length=100) 
    pic_pekerjaan = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dailyactivity_app_detail_pekerjaan'
        verbose_name = 'Detail Pekerjaan'
        verbose_name_plural = 'Detail Pekerjaan'

    def __str__(self):
        return f"{self.laporan.tanggal} - {self.jenis_pekerjaan} - {self.pic_pekerjaan}"
    
class LaporanUtility(models.Model):
    laporan_utility = models.ForeignKey(LaporanData, on_delete=models.CASCADE, related_name='laporan_utility')
    masalah = models.TextField()
    jenis_pekerjaan = models.CharField(max_length=200)
    lama_pekerjaan = models.CharField(max_length=100)
    pic_masalah = models.CharField(max_length=100)

    class Meta:
        db_table = 'dailyactivity_app_laporanutility'

    def __str__(self):
        return f"Pekerjaan: {self.masalah} - {self.jenis_pekerjaan}"


class PICLaporan(models.Model):
    name = models.CharField(max_length=100)
    nokar = models.CharField(max_length=100)

    class Meta:
        db_table = 'dailyactivity_app_pic_laporan'

    def __str__(self):
        return self.name


class LaporanDataPIC(models.Model):
    laporan_data = models.ForeignKey('LaporanData', on_delete=models.CASCADE)
    pic_laporan = models.ForeignKey('PICLaporan', on_delete=models.CASCADE)

    class Meta:
        db_table = 'dailyactivity_app_laporan_data_pic'


class PICLembur(models.Model):
    name = models.CharField(max_length=100)
    nokar = models.CharField(max_length=100)

    class Meta:
        db_table = 'dailyactivity_app_pic_lembur'

    def __str__(self):
        return self.name


class LemburDataPIC(models.Model):
    laporan_data = models.ForeignKey('LaporanData', on_delete=models.CASCADE)  # Perhatikan nama field ini
    pic_lembur = models.ForeignKey('PICLembur', on_delete=models.CASCADE)

    class Meta:
        db_table = 'dailyactivity_app_lembur_data_pic'

class LaporanMechanicalData(models.Model):
    tanggal = models.DateField()
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    masalah = models.TextField()
    image = models.ImageField(upload_to='laporan_images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pic = models.ManyToManyField('PICLaporanMechanical', blank=True, through='LaporanMechanicalDataPIC')  
    piclembur = models.ManyToManyField('PICLemburMechanical', blank=True, through='LemburMechanicalDataPIC') 
    catatan = models.CharField(max_length=200, null=True, blank=True)  # Tambahkan jenis pekerjaan
    lama_pekerjaan = models.CharField(max_length=100, null=True, blank=True) 
    pic_masalah = models.CharField(max_length=100, null=True, blank=True) 

    class Meta:
        db_table = 'dailyactivity_app_laporanmechanical_data'

    def __str__(self):
        return f"{self.tanggal} - {self.user.username}"
    
class LaporanPekerjaan(models.Model):
    laporan_data = models.ForeignKey(LaporanMechanicalData, on_delete=models.CASCADE, related_name='laporan_pekerjaan')
    masalah = models.TextField()
    jenis_pekerjaan = models.CharField(max_length=200)
    lama_pekerjaan = models.CharField(max_length=100)
    pic_masalah = models.CharField(max_length=100)

    class Meta:
        db_table = 'dailyactivity_app_laporanpekerjaan'

    def __str__(self):
        return f"Pekerjaan: {self.masalah} - {self.jenis_pekerjaan}"

class PICLaporanMechanical(models.Model):
    name = models.CharField(max_length=100)
    nokar = models.CharField(max_length=100)

    class Meta:
        db_table = 'dailyactivity_app_pic_laporanmechanical'
    def __str__(self):
        return self.name

class LaporanMechanicalDataPIC(models.Model):
    laporanmechanical_data = models.ForeignKey('LaporanMechanicalData', on_delete=models.CASCADE)
    pic_laporanmechanical = models.ForeignKey('PICLaporanMechanical', on_delete=models.CASCADE)

    class Meta:
        db_table = 'dailyactivity_app_laporanmechanical_data_pic'


class PICLemburMechanical(models.Model):
    name = models.CharField(max_length=100)
    nokar = models.CharField(max_length=100)

    class Meta:
        db_table = 'dailyactivity_app_pic_lemburmechanical'

    def __str__(self):
        return self.name


class LemburMechanicalDataPIC(models.Model):
    schedule_mechanical_data = models.ForeignKey(
        'ScheduleMechanicalData', on_delete=models.CASCADE, null=True, blank=True
    )  # Relasi ke ScheduleMechanicalData
    laporanmechanical_data = models.ForeignKey(
        'LaporanMechanicalData', on_delete=models.CASCADE, null=True, blank=True
    )  # Relasi ke LaporanMechanicalData
    pic_lemburmechanical = models.ForeignKey(
        'PICLemburMechanical', on_delete=models.CASCADE
    )  # Relasi ke PICLembur

    class Meta:
        db_table = 'dailyactivity_app_lemburmechanical_data_pic'

    def __str__(self):
        relasi = (
            f"Schedule: {self.schedule_mechanical_data}"
            if self.schedule_mechanical_data
            else f"Laporan: {self.laporanmechanical_data}"
        )
        return f"{relasi} - {self.pic_lemburmechanical}"


class ScheduleMechanicalData(models.Model):
    tanggal = models.DateField()
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    jam = models.TimeField(null=True, blank=True)  # Field baru untuk jam
    pekerjaan = models.TextField()
    image = models.ImageField(upload_to='laporan_images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pic_lemburmechanical = models.ManyToManyField(
        'PICLemburMechanical',  # Menggunakan string untuk menghindari masalah urutan
        through='LemburMechanicalDataPIC',  # Relasi melalui tabel `LemburMechanicalDataPIC`
        related_name='schedule_mechanical_data'
    )

    class Meta:
        db_table = 'dailyactivity_app_schedulemechanical_data'

    def __str__(self):
        return f"{self.tanggal} - {self.user.username}"
    
# Model untuk connect ke database external DB_Maintenance  
class TabelLine(models.Model):
    id_line = models.FloatField(primary_key=True)
    line = models.CharField(max_length=35, null=True, blank=True)
    keterangan = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=1, null=True, blank=True)
    user_insert = models.CharField(max_length=30, null=True, blank=True)
    user_edit = models.CharField(max_length=30, null=True, blank=True)
    tgl_insert = models.DateTimeField(null=True, blank=True)
    tgl_edit = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tabel_line'
        managed = False  # Biar ga di-migrate Django

    def __str__(self):
        return self.line or f"Line {self.id_line}"


class TabelMesin(models.Model):
    id_mesin = models.FloatField(primary_key=True)
    mesin = models.CharField(max_length=75, null=True, blank=True)
    id_line = models.CharField(max_length=10, null=True, blank=True)
    nomer = models.CharField(max_length=10, null=True, blank=True)
    keterangan = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=1, null=True, blank=True)
    user_insert = models.CharField(max_length=30, null=True, blank=True)
    user_edit = models.CharField(max_length=30, null=True, blank=True)
    tgl_insert = models.DateTimeField(null=True, blank=True)
    tgl_edit = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tabel_mesin'
        managed = False

    def __str__(self):
        return f"{self.mesin} - {self.nomer}" if self.mesin and self.nomer else f"Mesin {self.id_mesin}"
class TabelPekerjaan(models.Model):
    id_pekerjaan = models.FloatField(primary_key=True)
    pekerjaan = models.CharField(max_length=50, null=True, blank=True)
    keterangan = models.CharField(max_length=150, null=True, blank=True)
    gen_no = models.CharField(max_length=1, null=True, blank=True)
    status = models.CharField(max_length=1, null=True, blank=True)
    user_insert = models.CharField(max_length=35, null=True, blank=True)
    user_edit = models.CharField(max_length=35, null=True, blank=True)
    tgl_insert = models.DateTimeField(null=True, blank=True)
    tgl_edit = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tabel_pekerjaan'
        managed = False

    def __str__(self):
        return self.pekerjaan or f"Pekerjaan {self.id_pekerjaan}"


# Update model Project - tambahin field baru
class Project(models.Model):
    project_name = models.CharField(max_length=255)
    pic_project = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    start_date = models.DateField()
    finish_date = models.DateField()
    # Field baru untuk line, mesin, nomor dan waktu pengerjaan
    line = models.CharField(max_length=35, null=True, blank=True)
    mesin = models.CharField(max_length=75, null=True, blank=True)  
    nomor_mesin = models.CharField(max_length=10, null=True, blank=True)
    waktu_pengerjaan = models.CharField(max_length=100, null=True, blank=True)
    jenis_pekerjaan = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dailyactivity_app_projects'
    
    def __str__(self):
        return self.project_name


# Update model ProjectIssue - tambahin field tindakan dan perbaikan
class ProjectIssue(models.Model):
    STATUS_CHOICES = (
        ('0', '0%'),
        ('10', '10%'),
        ('20', '20%'),
        ('30', '30%'),
        ('40', '40%'),
        ('50', '50%'),
        ('60', '60%'),
        ('70', '70%'),
        ('80', '80%'),
        ('90', '90%'),
        ('100', '100%'),
    )
    
    project = models.ForeignKey(
        Project, 
        related_name='issues',
        on_delete=models.CASCADE
    )
    issue = models.TextField()
    # Field baru - tindakan dan perbaikan
    tindakan = models.TextField(null=True, blank=True, verbose_name='Tindakan')
    perbaikan = models.TextField(null=True, blank=True, verbose_name='Perbaikan')
    pic = models.CharField(max_length=255)
    due_date = models.DateField()
    status = models.CharField(max_length=20, null=True, blank=True, choices=STATUS_CHOICES) 
    remark = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dailyactivity_app_project_issues'
    
    def __str__(self):
        return f"Issue for {self.project.project_name}: {self.issue[:30]}..."
       
# class Project(models.Model):
#     project_name = models.CharField(max_length=255)
#     pic_project = models.CharField(max_length=255)
#     department = models.CharField(max_length=255)
#     start_date = models.DateField()
#     finish_date = models.DateField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = 'dailyactivity_app_projects'

#     def __str__(self):
#         return self.project_name


# class ProjectIssue(models.Model):
#     STATUS_CHOICES = (
#         ('0', '0%'),
#         ('10', '10%'),
#         ('20', '20%'),
#         ('30', '30%'),
#         ('40', '40%'),
#         ('50', '50%'),
#         ('60', '60%'),
#         ('70', '70%'),
#         ('80', '80%'),
#         ('90', '90%'),
#         ('100', '100%'),
#     )

#     project = models.ForeignKey(
#         Project, 
#         related_name='issues',
#         on_delete=models.CASCADE
#     )
#     issue = models.TextField()
#     pic = models.CharField(max_length=255)
#     due_date = models.DateField()
#     status = models.CharField(max_length=20, null=True, blank=True, choices=STATUS_CHOICES) 
#     remark = models.TextField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = 'dailyactivity_app_project_issues'

#     def __str__(self):
#         return f"Issue for {self.project.project_name}: {self.issue[:30]}..."
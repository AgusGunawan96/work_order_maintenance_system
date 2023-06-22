# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Aftermixing(models.Model):
    barcode = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'Aftermixing'


class BarcodeRm(models.Model):
    barcode = models.CharField(unique=True, max_length=255, blank=True, null=True)
    terpakai = models.FloatField(blank=True, null=True)
    barcodeasli = models.CharField(max_length=255, blank=True, null=True)
    no_transaksi = models.CharField(max_length=255, blank=True, null=True)
    no_keluar = models.CharField(max_length=255, blank=True, null=True)
    kd_barang = models.CharField(max_length=35, blank=True, null=True)
    no_lot = models.CharField(max_length=255, blank=True, null=True)
    jlmbarang = models.FloatField(blank=True, null=True)
    wip = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Barcode_RM'


class BarcodeRmt(models.Model):
    barcode = models.CharField(max_length=255, blank=True, null=True)
    terpakai = models.FloatField(blank=True, null=True)
    barcodeasli = models.CharField(max_length=255, blank=True, null=True)
    no_transaksi = models.CharField(max_length=255, blank=True, null=True)
    no_keluar = models.CharField(max_length=255, blank=True, null=True)
    kd_barang = models.CharField(max_length=255, blank=True, null=True)
    no_lot = models.CharField(max_length=255, blank=True, null=True)
    jlmbarang = models.FloatField(blank=True, null=True)
    wip = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Barcode_RMT'


class Calenders(models.Model):
    f1 = models.CharField(db_column='F1', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CalenderS'


class Fabrikstock(models.Model):
    no = models.FloatField(db_column='NO', blank=True, null=True)  # Field name made lowercase.
    code = models.CharField(db_column='CODE', max_length=255, blank=True, null=True)  # Field name made lowercase.
    materialname = models.CharField(db_column='MATERIALNAME', max_length=255, blank=True, null=True)  # Field name made lowercase.
    bbm = models.CharField(db_column='BBM', max_length=255, blank=True, null=True)  # Field name made lowercase.
    nolot = models.CharField(db_column='NOLOT', max_length=255, blank=True, null=True)  # Field name made lowercase.
    tanggaldatang = models.DateTimeField(db_column='TANGGALDATANG', blank=True, null=True)  # Field name made lowercase.
    qtym = models.DecimalField(db_column='QTYM', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qtykg = models.DecimalField(db_column='QTYKG', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'FabrikStock'


class ImportJanuary(models.Model):
    kode = models.CharField(max_length=255, blank=True, null=True)
    th = models.CharField(max_length=255, blank=True, null=True)
    bln = models.CharField(max_length=255, blank=True, null=True)
    usd = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Import_january'


class MBarang(models.Model):
    kode = models.CharField(max_length=35, blank=True, null=True)
    nama = models.CharField(max_length=50, blank=True, null=True)
    jenis = models.CharField(max_length=30, blank=True, null=True)
    merk = models.CharField(max_length=30, blank=True, null=True)
    sebutansatuan = models.CharField(max_length=30, blank=True, null=True)
    sebutandus = models.CharField(max_length=30, blank=True, null=True)
    jlmdus = models.FloatField(db_column='JlmDus', blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(max_length=30, blank=True, null=True)
    tglmasuk = models.CharField(max_length=10, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    minimal = models.CharField(db_column='Minimal', max_length=10, blank=True, null=True)  # Field name made lowercase.
    maxsimal = models.CharField(db_column='Maxsimal', max_length=10, blank=True, null=True)  # Field name made lowercase.
    maxpallet = models.FloatField(db_column='MaxPallet', blank=True, null=True)  # Field name made lowercase.
    tempat = models.CharField(db_column='Tempat', max_length=30, blank=True, null=True)  # Field name made lowercase.
    wip = models.CharField(db_column='WIP', max_length=1, blank=True, null=True)  # Field name made lowercase.
    expdt = models.CharField(max_length=4, blank=True, null=True)
    selang = models.CharField(max_length=2)
    qtyselang = models.CharField(db_column='QtySelang', max_length=10)  # Field name made lowercase.
    rdp = models.CharField(max_length=1)
    import_field = models.CharField(db_column='import', max_length=20, blank=True, null=True)  # Field renamed because it was a Python reserved word.

    class Meta:
        managed = False
        db_table = 'M_Barang'


class MBarangGroup(models.Model):
    kdgroup = models.CharField(db_column='KdGroup', max_length=15)  # Field name made lowercase.
    itemclass = models.CharField(db_column='Itemclass', max_length=20)  # Field name made lowercase.
    groupnya = models.CharField(db_column='GroupNya', max_length=20)  # Field name made lowercase.
    kategori = models.CharField(db_column='Kategori', max_length=20)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    tglinput = models.CharField(db_column='TglInput', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(max_length=10)
    groupkategori = models.CharField(db_column='GroupKategori', max_length=15, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_Barang_Group'


class MBarcodex(models.Model):
    barcode = models.CharField(db_column='BARCODE', max_length=10)  # Field name made lowercase.
    terpakai = models.CharField(db_column='TERPAKAI', max_length=1)  # Field name made lowercase.
    barcodeasli = models.CharField(db_column='BARCODEASLI', max_length=20, blank=True, null=True)  # Field name made lowercase.
    no_transaksi = models.CharField(db_column='NO_TRANSAKSI', max_length=20, blank=True, null=True)  # Field name made lowercase.
    no_keluar = models.CharField(db_column='No_Keluar', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kd_barang = models.CharField(max_length=20, blank=True, null=True)
    no_lot = models.CharField(db_column='No_Lot', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jlmbarang = models.DecimalField(max_digits=19, decimal_places=4)
    wip = models.CharField(db_column='WIP', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_Barcodex'


class MBoxMixing(models.Model):
    kode = models.CharField(db_column='Kode', max_length=9)  # Field name made lowercase.
    namabox = models.CharField(db_column='NamaBox', max_length=200)  # Field name made lowercase.
    beratbox = models.CharField(db_column='BeratBox', max_length=50)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=50)  # Field name made lowercase.
    tglmasuk = models.DateTimeField()
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    useredit = models.CharField(db_column='Useredit', max_length=50, blank=True, null=True)  # Field name made lowercase.
    tgledit = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'M_Box_Mixing'


class MCurrency(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    curr_date = models.DateTimeField(db_column='CURR_DATE', blank=True, null=True)  # Field name made lowercase.
    curr_rate = models.DecimalField(db_column='CURR_RATE', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    update_timestamp = models.DateTimeField(db_column='UPDATE_TIMESTAMP', blank=True, null=True)  # Field name made lowercase.
    update_user = models.CharField(db_column='UPDATE_USER', max_length=50, blank=True, null=True)  # Field name made lowercase.
    update_status = models.CharField(db_column='UPDATE_STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_CURRENCY'


class MCalExp(models.Model):
    itemno = models.CharField(max_length=255, blank=True, null=True)
    exp_hari = models.FloatField(db_column='EXP-HARI', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    sg = models.FloatField(db_column='SG', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_Cal_EXP'


class MGudang(models.Model):
    id_gudang = models.IntegerField(db_column='ID_GUDANG')  # Field name made lowercase.
    nama_gudang = models.CharField(db_column='NAMA_GUDANG', max_length=50, blank=True, null=True)  # Field name made lowercase.
    gudang_desc = models.CharField(db_column='GUDANG_DESC', max_length=50, blank=True, null=True)  # Field name made lowercase.
    location = models.CharField(db_column='LOCATION', max_length=50, blank=True, null=True)  # Field name made lowercase.
    update_timestamp = models.DateTimeField(db_column='UPDATE_TIMESTAMP', blank=True, null=True)  # Field name made lowercase.
    update_user = models.CharField(db_column='UPDATE_USER', max_length=50, blank=True, null=True)  # Field name made lowercase.
    update_status = models.CharField(db_column='UPDATE_STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_GUDANG'


class MJenisScrap(models.Model):
    seksi = models.CharField(db_column='Seksi', max_length=10)  # Field name made lowercase.
    jenis = models.CharField(db_column='Jenis', max_length=50)  # Field name made lowercase.
    usernya = models.CharField(max_length=50, blank=True, null=True)
    tglmasuk = models.CharField(max_length=10, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'M_Jenis_Scrap'


class MKanban(models.Model):
    kanban = models.CharField(db_column='Kanban', max_length=20)  # Field name made lowercase.
    lokasi = models.CharField(db_column='Lokasi', max_length=1)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    no_keluar = models.CharField(db_column='No_Keluar', max_length=15)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_Kanban'


class MLot(models.Model):
    nolot = models.CharField(db_column='NoLot', max_length=255, blank=True, null=True)  # Field name made lowercase.
    dayatampung = models.CharField(db_column='DayaTampung', max_length=255, blank=True, null=True)  # Field name made lowercase.
    jenisbarang = models.CharField(db_column='JenisBarang', max_length=255, blank=True, null=True)  # Field name made lowercase.
    kdbarang = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(db_column='Status', max_length=1, blank=True, null=True)  # Field name made lowercase.
    userid = models.CharField(db_column='Userid', max_length=30, blank=True, null=True)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_Lot'


class MLotAwal(models.Model):
    nolot = models.CharField(db_column='NoLot', max_length=10)  # Field name made lowercase.
    dayatampung = models.CharField(db_column='DayaTampung', max_length=30)  # Field name made lowercase.
    jenisbarang = models.CharField(db_column='JenisBarang', max_length=15)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=1)  # Field name made lowercase.
    userid = models.CharField(db_column='Userid', max_length=15)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=15)  # Field name made lowercase.
    tgledit = models.CharField(db_column='Tgledit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    kdbarang = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'M_Lot_Awal'


class MMaxAdjusment(models.Model):
    maxadjusment = models.DecimalField(db_column='MaxAdjusment', max_digits=19, decimal_places=4)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=15)  # Field name made lowercase.
    tgledit = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'M_Max_Adjusment'


class MMesin(models.Model):
    kodemesin = models.CharField(db_column='Kodemesin', max_length=3)  # Field name made lowercase.
    namamesin = models.CharField(db_column='NamaMesin', max_length=20)  # Field name made lowercase.
    lokasi = models.CharField(db_column='Lokasi', max_length=50, blank=True, null=True)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    waktumasuk = models.CharField(max_length=20, blank=True, null=True)
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    waktuupdate = models.CharField(max_length=20, blank=True, null=True)
    useredit = models.CharField(db_column='UserEdit', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_Mesin'


class MModul(models.Model):
    status = models.CharField(max_length=10, blank=True, null=True)
    tglmasuk = models.CharField(max_length=10, blank=True, null=True)
    tglupdate = models.CharField(max_length=10, blank=True, null=True)
    modul = models.CharField(db_column='Modul', max_length=10, blank=True, null=True)  # Field name made lowercase.
    nama = models.CharField(db_column='Nama', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_Modul'


class MModulAwal(models.Model):
    status = models.CharField(max_length=10, blank=True, null=True)
    tglmasuk = models.CharField(max_length=10, blank=True, null=True)
    tglupdate = models.CharField(max_length=10, blank=True, null=True)
    modul = models.CharField(db_column='Modul', max_length=10, blank=True, null=True)  # Field name made lowercase.
    nama = models.CharField(db_column='Nama', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_Modul_awal'


class MPegawai(models.Model):
    kode_peg = models.CharField(db_column='Kode_peg', max_length=6, blank=True, null=True)  # Field name made lowercase.
    nama_peg = models.CharField(db_column='Nama_peg', max_length=20, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_Pegawai'


class MPelanggan(models.Model):
    status = models.CharField(max_length=1)
    insdt = models.CharField(max_length=15, blank=True, null=True)
    upddt = models.CharField(max_length=15, blank=True, null=True)
    usrid = models.CharField(max_length=20, blank=True, null=True)
    kdcus = models.CharField(max_length=20)
    nmcus = models.CharField(max_length=70, blank=True, null=True)
    pic = models.CharField(max_length=70, blank=True, null=True)
    alamat = models.CharField(max_length=255, blank=True, null=True)
    telepon = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'M_Pelanggan'


class MRemilCalender(models.Model):
    kdremil = models.CharField(max_length=100, blank=True, null=True)
    kdcalender = models.CharField(max_length=100, blank=True, null=True)
    usernya = models.CharField(max_length=100, blank=True, null=True)
    tglmasuk = models.CharField(max_length=100, blank=True, null=True)
    useredit = models.CharField(max_length=100, blank=True, null=True)
    tgledit = models.CharField(max_length=100, blank=True, null=True)
    statusnya = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'M_Remil_Calender'


class MResep(models.Model):
    kdresep = models.CharField(db_column='KdResep', max_length=15, blank=True, null=True)  # Field name made lowercase.
    namaresep = models.CharField(db_column='NamaResep', max_length=30, blank=True, null=True)  # Field name made lowercase.
    kdbarang = models.CharField(db_column='KdBarang', max_length=15, blank=True, null=True)  # Field name made lowercase.
    kdbarangcadangan = models.CharField(db_column='KdBarangCadangan', max_length=15, blank=True, null=True)  # Field name made lowercase.
    nourut = models.FloatField(db_column='NoUrut', blank=True, null=True)  # Field name made lowercase.
    jumlahbarang = models.FloatField(db_column='JumlahBarang', blank=True, null=True)  # Field name made lowercase.
    lebih = models.FloatField(blank=True, null=True)
    kurang = models.FloatField(blank=True, null=True)
    status = models.CharField(db_column='Status', max_length=1, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(max_length=20, blank=True, null=True)
    tglmasuk = models.CharField(max_length=10, blank=True, null=True)
    tgledit = models.CharField(max_length=19, blank=True, null=True)
    groupresep = models.CharField(db_column='GroupResep', max_length=3, blank=True, null=True)  # Field name made lowercase.
    resep = models.CharField(db_column='Resep', max_length=20, blank=True, null=True)  # Field name made lowercase.
    fase = models.CharField(db_column='Fase', max_length=20, blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rb = models.CharField(db_column='RB', max_length=1, blank=True, null=True)  # Field name made lowercase.
    timbang = models.CharField(db_column='Timbang', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_Resep'


class MResepAktif(models.Model):
    resep = models.CharField(db_column='Resep', max_length=100)  # Field name made lowercase.
    statusya = models.CharField(db_column='Statusya', max_length=1)  # Field name made lowercase.
    tglin = models.DateTimeField()
    tgledit = models.DateTimeField(blank=True, null=True)
    userin = models.CharField(max_length=50)
    useredit = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'M_Resep_Aktif'


class MResepDrayer(models.Model):
    kddrayer = models.CharField(max_length=200)
    kdcalender = models.CharField(max_length=200)
    rmcode = models.CharField(db_column='RMcode', max_length=200)  # Field name made lowercase.
    usernya = models.CharField(max_length=200)
    tglin = models.DateTimeField()
    statusnya = models.CharField(max_length=1)
    useredit = models.CharField(max_length=200, blank=True, null=True)
    tgledit = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'M_Resep_Drayer'


class MResepMixing(models.Model):
    kdresep = models.CharField(db_column='KdResep', max_length=15, blank=True, null=True)  # Field name made lowercase.
    namaresep = models.CharField(db_column='NamaResep', max_length=30, blank=True, null=True)  # Field name made lowercase.
    kdbarang = models.CharField(db_column='KdBarang', max_length=15, blank=True, null=True)  # Field name made lowercase.
    kdbarangcadangan = models.CharField(db_column='KdBarangCadangan', max_length=15, blank=True, null=True)  # Field name made lowercase.
    nourut = models.FloatField(db_column='NoUrut', blank=True, null=True)  # Field name made lowercase.
    jumlahbarang = models.FloatField(db_column='JumlahBarang', blank=True, null=True)  # Field name made lowercase.
    lebih = models.FloatField(blank=True, null=True)
    kurang = models.FloatField(blank=True, null=True)
    status = models.CharField(db_column='Status', max_length=1, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(max_length=20, blank=True, null=True)
    tglmasuk = models.CharField(max_length=10, blank=True, null=True)
    tgledit = models.CharField(max_length=19, blank=True, null=True)
    useredit = models.CharField(db_column='Useredit', max_length=20, blank=True, null=True)  # Field name made lowercase.
    groupresep = models.CharField(db_column='GroupResep', max_length=3, blank=True, null=True)  # Field name made lowercase.
    resep = models.CharField(db_column='Resep', max_length=20, blank=True, null=True)  # Field name made lowercase.
    fase = models.CharField(db_column='Fase', max_length=20, blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jenis = models.CharField(db_column='Jenis', max_length=2, blank=True, null=True)  # Field name made lowercase.
    mesin = models.CharField(db_column='Mesin', max_length=3, blank=True, null=True)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    atas = models.FloatField(db_column='Atas', blank=True, null=True)  # Field name made lowercase.
    bawah = models.FloatField(db_column='Bawah', blank=True, null=True)  # Field name made lowercase.
    stepnya = models.CharField(max_length=2, blank=True, null=True)
    waktuproduksi = models.CharField(max_length=20, blank=True, null=True)
    rb = models.CharField(db_column='Rb', max_length=1)  # Field name made lowercase.
    exp = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    split = models.CharField(db_column='Split', max_length=1)  # Field name made lowercase.
    akhir = models.CharField(max_length=1)
    chamtempmax = models.CharField(db_column='ChamTempMax', max_length=5, blank=True, null=True)  # Field name made lowercase.
    chamtempmin = models.CharField(db_column='ChamTempMin', max_length=5, blank=True, null=True)  # Field name made lowercase.
    cooltempmax = models.CharField(db_column='CoolTempMax', max_length=5, blank=True, null=True)  # Field name made lowercase.
    cooltempmin = models.CharField(db_column='CoolTempMin', max_length=5, blank=True, null=True)  # Field name made lowercase.
    box = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'M_Resep_Mixing'


class MResepRemil(models.Model):
    seksi = models.CharField(max_length=20)
    kdresep = models.CharField(max_length=20)
    berat_box = models.DecimalField(db_column='Berat_Box', max_digits=19, decimal_places=4)  # Field name made lowercase.
    expr = models.CharField(max_length=2, blank=True, null=True)
    usernya = models.CharField(max_length=50, blank=True, null=True)
    tglmasuk = models.CharField(max_length=10, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'M_Resep_Remil'


class MStdCost(models.Model):
    cost_id = models.CharField(db_column='COST_ID', max_length=50)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='KODE_BARANG', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cost_value = models.CharField(db_column='COST_VALUE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    update_timestamp = models.DateTimeField(db_column='UPDATE_TIMESTAMP', blank=True, null=True)  # Field name made lowercase.
    update_user = models.CharField(db_column='UPDATE_USER', max_length=50, blank=True, null=True)  # Field name made lowercase.
    update_status = models.CharField(db_column='UPDATE_STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.
    rdp = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'M_STD_COST'


class MSection(models.Model):
    kode = models.CharField(db_column='Kode', primary_key=True, max_length=10)  # Field name made lowercase.
    section = models.CharField(db_column='Section', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    tglmasuk = models.CharField(max_length=10)
    useredit = models.CharField(max_length=10, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    untuk = models.CharField(db_column='Untuk', max_length=20)  # Field name made lowercase.
    barcode = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'M_Section'


class MSupplier(models.Model):
    status = models.CharField(max_length=1)
    insdt = models.CharField(max_length=15, blank=True, null=True)
    upddt = models.CharField(max_length=15, blank=True, null=True)
    usrid = models.CharField(max_length=15, blank=True, null=True)
    kdsup = models.CharField(max_length=20)
    nmsup = models.CharField(max_length=70)
    pic = models.CharField(max_length=70)
    alamat = models.CharField(max_length=255, blank=True, null=True)
    telepon = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'M_Supplier'


class MTftoCalender(models.Model):
    idnya = models.BigAutoField(primary_key=True)
    itemno = models.CharField(max_length=200)
    dispo = models.CharField(max_length=50)
    tfto = models.CharField(max_length=50)
    tglin = models.DateTimeField()
    userin = models.CharField(max_length=50)
    tgledit = models.DateTimeField(blank=True, null=True)
    useredit = models.CharField(max_length=50, blank=True, null=True)
    statusnya = models.CharField(max_length=1)
    tthiknes = models.CharField(max_length=50, blank=True, null=True)
    stdpotong = models.CharField(max_length=50, blank=True, null=True)
    tpotong = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'M_TFTO_Calender'


class MUser(models.Model):
    status = models.CharField(db_column='Status', max_length=1, blank=True, null=True)  # Field name made lowercase.
    insdt = models.CharField(max_length=10, blank=True, null=True)
    upddt = models.CharField(max_length=10, blank=True, null=True)
    idnya = models.CharField(db_column='IDnya', max_length=15, blank=True, null=True)  # Field name made lowercase.
    pwd = models.CharField(max_length=20, blank=True, null=True)
    akses = models.CharField(db_column='Akses', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_User'


class MUserAkunting(models.Model):
    status = models.CharField(db_column='Status', max_length=1, blank=True, null=True)  # Field name made lowercase.
    insdt = models.CharField(max_length=10, blank=True, null=True)
    upddt = models.CharField(max_length=10, blank=True, null=True)
    idnya = models.CharField(db_column='IDnya', max_length=15, blank=True, null=True)  # Field name made lowercase.
    pwd = models.CharField(max_length=20, blank=True, null=True)
    akses = models.CharField(db_column='Akses', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_User_Akunting'


class MBarangI(models.Model):
    kode = models.CharField(db_column='Kode', max_length=255, blank=True, null=True)  # Field name made lowercase.
    nama = models.CharField(db_column='Nama', max_length=255, blank=True, null=True)  # Field name made lowercase.
    incoming = models.CharField(db_column='INCOMING', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_barang_i'


class MGroupKeluarDrWh(models.Model):
    kodegroupkeluar = models.CharField(db_column='KODEGROUPKELUAR', max_length=6)  # Field name made lowercase.
    nmgroupkeluar = models.CharField(db_column='nmgroupKeluar', max_length=50)  # Field name made lowercase.
    status = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'M_group_keluar_dr_WH'


class MResepCalender(models.Model):
    rubber = models.CharField(max_length=50, blank=True, null=True)
    thickness = models.FloatField(db_column='Thickness', blank=True, null=True)  # Field name made lowercase.
    width = models.FloatField(db_column='Width', blank=True, null=True)  # Field name made lowercase.
    sheecut = models.CharField(db_column='Sheecut', max_length=255, blank=True, null=True)  # Field name made lowercase.
    keynya = models.CharField(max_length=255, blank=True, null=True)
    itemno = models.CharField(max_length=255, blank=True, null=True)
    desc = models.CharField(max_length=255, blank=True, null=True)
    batch_size_length = models.CharField(db_column='Batch Size length', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    batch_size_unit = models.CharField(db_column='Batch Size unit', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_item_1 = models.CharField(db_column='Child Item 1', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_quantity_1 = models.FloatField(db_column='Child Quantity 1', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_item_2 = models.CharField(db_column='Child Item 2', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_quantity_2 = models.FloatField(db_column='Child Quantity 2', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_item_3 = models.CharField(db_column='Child Item 3', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_quantity_3 = models.FloatField(db_column='Child Quantity 3', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_item_4 = models.CharField(db_column='Child Item 4', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_quantity_4 = models.FloatField(db_column='Child Quantity 4', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_item_5 = models.CharField(db_column='Child Item 5', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_quantity_5 = models.FloatField(db_column='Child Quantity 5', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    statusnya = models.CharField(max_length=255, blank=True, null=True)
    exp = models.FloatField(db_column='Exp', blank=True, null=True)  # Field name made lowercase.
    sg = models.CharField(db_column='SG', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fc1 = models.CharField(max_length=1, blank=True, null=True)
    fc2 = models.CharField(max_length=1, blank=True, null=True)
    fc3 = models.CharField(max_length=1, blank=True, null=True)
    fc4 = models.CharField(max_length=1, blank=True, null=True)
    fc5 = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'M_resep_Calender'


class MSebabRemil(models.Model):
    kodesebab = models.CharField(db_column='KodeSebab', max_length=3)  # Field name made lowercase.
    namasebab = models.CharField(max_length=20)
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    waktumasuk = models.CharField(max_length=20, blank=True, null=True)
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    waktuupdate = models.CharField(max_length=20, blank=True, null=True)
    useredit = models.CharField(db_column='UserEdit', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'M_sebab_remil'


class Mixings(models.Model):
    f1 = models.CharField(db_column='F1', max_length=255, blank=True, null=True)  # Field name made lowercase.
    f2 = models.CharField(db_column='F2', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MixingS'


class Modifcal(models.Model):
    kode = models.CharField(max_length=255, blank=True, null=True)
    item = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Modifcal'


class RmwAdjusment(models.Model):
    kodebrg = models.CharField(max_length=50, blank=True, null=True)
    bulan = models.CharField(max_length=2, blank=True, null=True)
    tahun = models.CharField(max_length=4, blank=True, null=True)
    us = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    rp = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    qty = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'RMW_adjusment'


class Revnya(models.Model):
    kdresep = models.CharField(max_length=15, blank=True, null=True)
    f2 = models.CharField(db_column='F2', max_length=255, blank=True, null=True)  # Field name made lowercase.
    f3 = models.CharField(db_column='F3', max_length=255, blank=True, null=True)  # Field name made lowercase.
    f4 = models.CharField(db_column='F4', max_length=255, blank=True, null=True)  # Field name made lowercase.
    resep = models.CharField(max_length=20, blank=True, null=True)
    fase = models.CharField(max_length=20, blank=True, null=True)
    f7 = models.CharField(db_column='F7', max_length=255, blank=True, null=True)  # Field name made lowercase.
    titel = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Revnya'


class Tjatwalsc(models.Model):
    idnya = models.BigAutoField(primary_key=True)
    keynya = models.CharField(db_column='KeyNya', max_length=75)  # Field name made lowercase.
    codenya = models.CharField(db_column='CodeNya', max_length=5)  # Field name made lowercase.
    thicknya = models.CharField(db_column='Thicknya', max_length=10)  # Field name made lowercase.
    widthnya = models.CharField(db_column='Widthnya', max_length=10)  # Field name made lowercase.
    lengthnya = models.CharField(db_column='Lengthnya', max_length=10)  # Field name made lowercase.
    qtynya = models.CharField(db_column='Qtynya', max_length=10)  # Field name made lowercase.
    fromnya = models.CharField(db_column='FromNya', max_length=10)  # Field name made lowercase.
    tonya = models.CharField(db_column='Tonya', max_length=10)  # Field name made lowercase.
    minnya = models.CharField(db_column='Minnya', max_length=10)  # Field name made lowercase.
    weightnya = models.CharField(db_column='Weightnya', max_length=10)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    waktuupload = models.CharField(db_column='waktuUpload', max_length=20)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    stjatwal = models.CharField(max_length=1)
    stuser = models.CharField(db_column='StUser', max_length=20, blank=True, null=True)  # Field name made lowercase.
    remil = models.CharField(db_column='Remil', max_length=1, blank=True, null=True)  # Field name made lowercase.
    selesai = models.CharField(db_column='Selesai', max_length=10, blank=True, null=True)  # Field name made lowercase.
    untuk = models.CharField(max_length=30, blank=True, null=True)
    mesin = models.CharField(max_length=10, blank=True, null=True)
    idasal = models.BigIntegerField(blank=True, null=True)
    tgltarik = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TJatwalSc'


class Tjatwalsc2(models.Model):
    idnya = models.BigAutoField(primary_key=True)
    keynya = models.CharField(db_column='KeyNya', max_length=100)  # Field name made lowercase.
    codenya = models.CharField(db_column='CodeNya', max_length=10)  # Field name made lowercase.
    thicknya = models.CharField(db_column='Thicknya', max_length=10)  # Field name made lowercase.
    widthnya = models.CharField(db_column='Widthnya', max_length=10)  # Field name made lowercase.
    lengthnya = models.CharField(db_column='Lengthnya', max_length=10)  # Field name made lowercase.
    qtynya = models.CharField(db_column='Qtynya', max_length=10)  # Field name made lowercase.
    fromnya = models.CharField(db_column='FromNya', max_length=10)  # Field name made lowercase.
    tonya = models.CharField(db_column='Tonya', max_length=10)  # Field name made lowercase.
    minnya = models.CharField(db_column='Minnya', max_length=10)  # Field name made lowercase.
    weightnya = models.CharField(db_column='Weightnya', max_length=10)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    waktuupload = models.CharField(db_column='waktuUpload', max_length=20)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    stjatwal = models.CharField(max_length=1)
    stuser = models.CharField(db_column='StUser', max_length=20, blank=True, null=True)  # Field name made lowercase.
    remil = models.CharField(db_column='Remil', max_length=1, blank=True, null=True)  # Field name made lowercase.
    selesai = models.CharField(db_column='Selesai', max_length=10, blank=True, null=True)  # Field name made lowercase.
    untuk = models.CharField(max_length=30, blank=True, null=True)
    mesin = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TJatwalSc2'


class TjatwalscHist2(models.Model):
    idnya = models.BigIntegerField()
    keynya = models.CharField(db_column='KeyNya', max_length=75)  # Field name made lowercase.
    codenya = models.CharField(db_column='CodeNya', max_length=5)  # Field name made lowercase.
    thicknya = models.CharField(db_column='Thicknya', max_length=10)  # Field name made lowercase.
    widthnya = models.CharField(db_column='Widthnya', max_length=10)  # Field name made lowercase.
    lengthnya = models.CharField(db_column='Lengthnya', max_length=10)  # Field name made lowercase.
    qtynya = models.CharField(db_column='Qtynya', max_length=10)  # Field name made lowercase.
    fromnya = models.CharField(db_column='FromNya', max_length=10)  # Field name made lowercase.
    tonya = models.CharField(db_column='Tonya', max_length=10)  # Field name made lowercase.
    minnya = models.CharField(db_column='Minnya', max_length=10)  # Field name made lowercase.
    weightnya = models.CharField(db_column='Weightnya', max_length=10)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    waktuupload = models.CharField(db_column='waktuUpload', max_length=20)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    stjatwal = models.CharField(max_length=1)
    stuser = models.CharField(db_column='StUser', max_length=20, blank=True, null=True)  # Field name made lowercase.
    remil = models.CharField(db_column='Remil', max_length=1, blank=True, null=True)  # Field name made lowercase.
    selesai = models.CharField(db_column='Selesai', max_length=10, blank=True, null=True)  # Field name made lowercase.
    untuk = models.CharField(max_length=30, blank=True, null=True)
    mesin = models.CharField(max_length=10, blank=True, null=True)
    idasal = models.BigIntegerField(blank=True, null=True)
    tgltarik = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TJatwalSc_hist2'


class TjatwalscHisx(models.Model):
    idnya = models.CharField(max_length=20)
    keynya = models.CharField(db_column='KeyNya', max_length=75)  # Field name made lowercase.
    codenya = models.CharField(db_column='CodeNya', max_length=5)  # Field name made lowercase.
    thicknya = models.CharField(db_column='Thicknya', max_length=10)  # Field name made lowercase.
    widthnya = models.CharField(db_column='Widthnya', max_length=10)  # Field name made lowercase.
    lengthnya = models.CharField(db_column='Lengthnya', max_length=10)  # Field name made lowercase.
    qtynya = models.CharField(db_column='Qtynya', max_length=10)  # Field name made lowercase.
    fromnya = models.CharField(db_column='FromNya', max_length=10)  # Field name made lowercase.
    tonya = models.CharField(db_column='Tonya', max_length=10)  # Field name made lowercase.
    minnya = models.CharField(db_column='Minnya', max_length=10)  # Field name made lowercase.
    weightnya = models.CharField(db_column='Weightnya', max_length=10)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    waktuupload = models.CharField(db_column='waktuUpload', max_length=20)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    stjatwal = models.CharField(max_length=1)
    stuser = models.CharField(db_column='StUser', max_length=20, blank=True, null=True)  # Field name made lowercase.
    remil = models.CharField(db_column='Remil', max_length=1, blank=True, null=True)  # Field name made lowercase.
    selesai = models.CharField(db_column='Selesai', max_length=10, blank=True, null=True)  # Field name made lowercase.
    untuk = models.CharField(max_length=30, blank=True, null=True)
    mesin = models.CharField(max_length=10, blank=True, null=True)
    keterangan = models.CharField(max_length=30, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TJatwalSc_hisx'


class TAdjustment(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ID')  # Field name made lowercase.
    t_date = models.DateTimeField(db_column='T_DATE', blank=True, null=True)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='KODE_BARANG', max_length=20, blank=True, null=True)  # Field name made lowercase.
    qty = models.DecimalField(db_column='QTY', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    amt = models.DecimalField(db_column='AMT', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    update_timestamp = models.DateTimeField(db_column='UPDATE_TIMESTAMP', blank=True, null=True)  # Field name made lowercase.
    update_user = models.CharField(db_column='UPDATE_USER', max_length=20, blank=True, null=True)  # Field name made lowercase.
    update_status = models.CharField(db_column='UPDATE_STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_ADJUSTMENT'


class TAdjustmentMixing(models.Model):
    id = models.AutoField(primary_key=True)
    kd_mixing = models.CharField(max_length=50, blank=True, null=True)
    qtyasli = models.DecimalField(db_column='qtyAsli', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qtybaru = models.DecimalField(db_column='qtyBaru', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    catatan = models.TextField(blank=True, null=True)  # This field type is a guess.
    tgl_insert = models.DateTimeField(blank=True, null=True)
    pengguna = models.CharField(max_length=20, blank=True, null=True)
    user_edit = models.CharField(max_length=20, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_ADJUSTMENT_MIXING'


class TActualInp(models.Model):
    code = models.CharField(db_column='Code', max_length=255, blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    th = models.FloatField(blank=True, null=True)
    bln = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Actual_Inp'


class TAdjutmenWd(models.Model):
    itemno = models.CharField(max_length=35, blank=True, null=True)
    us = models.DecimalField(db_column='US', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    rp = models.DecimalField(db_column='RP', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qty = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    th = models.CharField(max_length=4, blank=True, null=True)
    bln = models.CharField(max_length=2, blank=True, null=True)
    rdp = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'T_Adjutmen_WD'


class TAjusmen(models.Model):
    barcodesw = models.CharField(db_column='BarcodeSw', max_length=20)  # Field name made lowercase.
    qtyasli = models.CharField(db_column='QtyAsli', max_length=20)  # Field name made lowercase.
    qtybaru = models.CharField(db_column='QtyBaru', max_length=20)  # Field name made lowercase.
    kdbarang = models.CharField(max_length=20)
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    barcodeasli = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Ajusmen'


class TBb2Sem(models.Model):
    a = models.CharField(db_column='A', max_length=150, blank=True, null=True)  # Field name made lowercase.
    b = models.CharField(db_column='B', max_length=150, blank=True, null=True)  # Field name made lowercase.
    c = models.CharField(db_column='C', max_length=150, blank=True, null=True)  # Field name made lowercase.
    d = models.CharField(db_column='D', max_length=150, blank=True, null=True)  # Field name made lowercase.
    e = models.CharField(db_column='E', max_length=150, blank=True, null=True)  # Field name made lowercase.
    f = models.CharField(db_column='F', max_length=150, blank=True, null=True)  # Field name made lowercase.
    g = models.CharField(db_column='G', max_length=150, blank=True, null=True)  # Field name made lowercase.
    h = models.CharField(db_column='H', max_length=150, blank=True, null=True)  # Field name made lowercase.
    i = models.CharField(db_column='I', max_length=150, blank=True, null=True)  # Field name made lowercase.
    j = models.CharField(db_column='J', max_length=150, blank=True, null=True)  # Field name made lowercase.
    k = models.CharField(db_column='K', max_length=150, blank=True, null=True)  # Field name made lowercase.
    l = models.CharField(db_column='L', max_length=150, blank=True, null=True)  # Field name made lowercase.
    m = models.CharField(db_column='M', max_length=150, blank=True, null=True)  # Field name made lowercase.
    n = models.CharField(db_column='N', max_length=150, blank=True, null=True)  # Field name made lowercase.
    o = models.CharField(db_column='O', max_length=150, blank=True, null=True)  # Field name made lowercase.
    p = models.CharField(db_column='P', max_length=150, blank=True, null=True)  # Field name made lowercase.
    q = models.CharField(db_column='Q', max_length=150, blank=True, null=True)  # Field name made lowercase.
    r = models.CharField(db_column='R', max_length=150, blank=True, null=True)  # Field name made lowercase.
    s = models.CharField(db_column='S', max_length=150, blank=True, null=True)  # Field name made lowercase.
    t = models.CharField(db_column='T', max_length=150, blank=True, null=True)  # Field name made lowercase.
    u = models.CharField(db_column='U', max_length=150, blank=True, null=True)  # Field name made lowercase.
    v = models.CharField(db_column='V', max_length=150, blank=True, null=True)  # Field name made lowercase.
    w = models.CharField(db_column='W', max_length=150, blank=True, null=True)  # Field name made lowercase.
    x = models.CharField(db_column='X', max_length=150, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_BB2_Sem'


class TBarangMasukD(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='Kode_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    jumlah_barang = models.FloatField(db_column='Jumlah_Barang')  # Field name made lowercase.
    tanggal_pengiriman = models.DateTimeField(db_column='Tanggal_Pengiriman', blank=True, null=True)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglhabis = models.CharField(db_column='TglHabis', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tglhabisasli = models.CharField(db_column='TglHabisAsli', max_length=10, blank=True, null=True)  # Field name made lowercase.
    hold = models.CharField(max_length=1, blank=True, null=True)
    sign = models.CharField(max_length=10, blank=True, null=True)
    soa = models.CharField(db_column='SOA', max_length=1, blank=True, null=True)  # Field name made lowercase.
    insp = models.CharField(max_length=1, blank=True, null=True)
    ppi = models.CharField(max_length=1, blank=True, null=True)
    prioritas = models.CharField(db_column='Prioritas', max_length=1, blank=True, null=True)  # Field name made lowercase.
    no_lot = models.CharField(db_column='No_lot', max_length=20, blank=True, null=True)  # Field name made lowercase.
    lot_sup = models.CharField(db_column='Lot_sup', max_length=15)  # Field name made lowercase.
    barcode = models.CharField(max_length=20)
    diambil = models.CharField(max_length=1, blank=True, null=True)
    very = models.CharField(db_column='Very', max_length=1)  # Field name made lowercase.
    sa = models.CharField(db_column='Sa', max_length=1, blank=True, null=True)  # Field name made lowercase.
    tglvery = models.CharField(db_column='TglVery', max_length=10)  # Field name made lowercase.
    tglsa = models.CharField(db_column='TglSa', max_length=10, blank=True, null=True)  # Field name made lowercase.
    disposisi = models.CharField(max_length=1, blank=True, null=True)
    nosa = models.CharField(db_column='noSA', max_length=20, blank=True, null=True)  # Field name made lowercase.
    notesa = models.CharField(db_column='NoteSa', max_length=50, blank=True, null=True)  # Field name made lowercase.
    urut = models.FloatField(blank=True, null=True)
    kgasli = models.FloatField(db_column='KgAsli', blank=True, null=True)  # Field name made lowercase.
    tglproduksi = models.CharField(db_column='Tglproduksi', max_length=10, blank=True, null=True)  # Field name made lowercase.
    po = models.CharField(db_column='Po', max_length=15, blank=True, null=True)  # Field name made lowercase.
    pelanggan = models.CharField(db_column='Pelanggan', max_length=15, blank=True, null=True)  # Field name made lowercase.
    noaju = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Barang_Masuk_D'


class TBarangMasukDWip(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='Kode_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    lot_lama = models.CharField(db_column='Lot_Lama', max_length=20)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty')  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.
    kode_barang_wip = models.CharField(db_column='Kode_Barang_WIP', max_length=35, blank=True, null=True)  # Field name made lowercase.
    lot_wip = models.CharField(db_column='Lot_WIP', max_length=20)  # Field name made lowercase.
    qty_wip = models.FloatField(db_column='Qty_WIP')  # Field name made lowercase.
    barcode_wip = models.CharField(db_column='Barcode_WIP', max_length=20)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    barcoderm = models.CharField(db_column='BarcodeRM', max_length=15, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Barang_Masuk_D_WIP'


class TBarangMasukMilling(models.Model):
    no_keluar = models.CharField(db_column='No_Keluar', max_length=15)  # Field name made lowercase.
    konfirmasi = models.CharField(max_length=1)
    nopegs = models.CharField(db_column='NoPegS', max_length=15)  # Field name made lowercase.
    nmpegs = models.CharField(db_column='NmPegS', max_length=300, blank=True, null=True)  # Field name made lowercase.
    nopegd = models.CharField(db_column='NoPegD', max_length=15)  # Field name made lowercase.
    nmpegd = models.CharField(db_column='NmPegD', max_length=300, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    catatan = models.CharField(db_column='Catatan', max_length=300, blank=True, null=True)  # Field name made lowercase.
    nopeg1 = models.CharField(db_column='NoPeg1', max_length=10, blank=True, null=True)  # Field name made lowercase.
    nmpeg1 = models.CharField(db_column='NmPeg1', max_length=100, blank=True, null=True)  # Field name made lowercase.
    nopeg2 = models.CharField(db_column='NoPeg2', max_length=10, blank=True, null=True)  # Field name made lowercase.
    nmpeg2 = models.CharField(db_column='NmPeg2', max_length=100, blank=True, null=True)  # Field name made lowercase.
    untukmilling = models.CharField(db_column='UntukMilling', max_length=2, blank=True, null=True)  # Field name made lowercase.
    bagian = models.CharField(db_column='Bagian', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Barang_Masuk_Milling'


class TBarangMasukMillingD(models.Model):
    no_keluar = models.CharField(db_column='No_Keluar', max_length=15)  # Field name made lowercase.
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kd_lot = models.CharField(db_column='Kd_lot', max_length=10)  # Field name made lowercase.
    kd_barang = models.CharField(max_length=35, blank=True, null=True)
    kd_barang_baru = models.CharField(db_column='kd_barang_Baru', max_length=15)  # Field name made lowercase.
    jlm = models.FloatField(db_column='JLM', blank=True, null=True)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='Tglmasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='UNIT', max_length=20)  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.
    bar = models.CharField(db_column='Bar', max_length=10, blank=True, null=True)  # Field name made lowercase.
    asalbrg = models.CharField(db_column='Asalbrg', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Barang_Masuk_Milling_D'


class TBarangMasukMillingD2(models.Model):
    no_keluar = models.CharField(db_column='No_Keluar', max_length=15)  # Field name made lowercase.
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kd_lot = models.CharField(db_column='Kd_lot', max_length=10)  # Field name made lowercase.
    kd_barang = models.CharField(max_length=10)
    kd_barang_baru = models.CharField(db_column='kd_barang_Baru', max_length=15)  # Field name made lowercase.
    jlm = models.FloatField(db_column='JLM', blank=True, null=True)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='Tglmasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='UNIT', max_length=20)  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.
    bar = models.CharField(db_column='Bar', max_length=10, blank=True, null=True)  # Field name made lowercase.
    asalbrg = models.CharField(db_column='Asalbrg', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Barang_Masuk_Milling_d_2'


class TBarangMasukSelainMilling(models.Model):
    no_keluar = models.CharField(db_column='No_Keluar', max_length=15)  # Field name made lowercase.
    konfirmasi = models.CharField(max_length=1)
    nopegs = models.CharField(db_column='NoPegS', max_length=15)  # Field name made lowercase.
    nmpegs = models.CharField(db_column='NmPegS', max_length=300, blank=True, null=True)  # Field name made lowercase.
    nopegd = models.CharField(db_column='NoPegD', max_length=15)  # Field name made lowercase.
    nmpegd = models.CharField(db_column='NmPegD', max_length=300, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    catatan = models.CharField(db_column='Catatan', max_length=300, blank=True, null=True)  # Field name made lowercase.
    nopeg1 = models.CharField(db_column='NoPeg1', max_length=10, blank=True, null=True)  # Field name made lowercase.
    nmpeg1 = models.CharField(db_column='NmPeg1', max_length=100, blank=True, null=True)  # Field name made lowercase.
    nopeg2 = models.CharField(db_column='NoPeg2', max_length=10, blank=True, null=True)  # Field name made lowercase.
    nmpeg2 = models.CharField(db_column='NmPeg2', max_length=100, blank=True, null=True)  # Field name made lowercase.
    untukmilling = models.CharField(db_column='UntukMilling', max_length=2, blank=True, null=True)  # Field name made lowercase.
    bagian = models.CharField(db_column='Bagian', max_length=30, blank=True, null=True)  # Field name made lowercase.
    kodebagian = models.CharField(db_column='KodeBagian', max_length=15, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Barang_Masuk_Selain_Milling'


class TBarangMasukSelainMillingD(models.Model):
    no_keluar = models.CharField(db_column='No_Keluar', max_length=15)  # Field name made lowercase.
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kd_lot = models.CharField(db_column='Kd_lot', max_length=10)  # Field name made lowercase.
    kd_barang = models.CharField(max_length=35, blank=True, null=True)
    kd_barang_baru = models.CharField(db_column='kd_barang_Baru', max_length=35, blank=True, null=True)  # Field name made lowercase.
    jlm = models.FloatField(db_column='JLM', blank=True, null=True)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='Tglmasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='UNIT', max_length=20)  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.
    bar = models.CharField(db_column='Bar', max_length=10, blank=True, null=True)  # Field name made lowercase.
    asalbrg = models.CharField(db_column='Asalbrg', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Barang_Masuk_Selain_Milling_D'


class TBarangPemusnahanD(models.Model):
    no_pemushana = models.CharField(db_column='No_pemushana', max_length=15)  # Field name made lowercase.
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kd_lot = models.CharField(db_column='Kd_Lot', max_length=10)  # Field name made lowercase.
    kd_barang = models.CharField(db_column='KD_BARANG', max_length=10)  # Field name made lowercase.
    kd_barang_baru = models.CharField(db_column='Kd_Barang_Baru', max_length=15)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    jlm = models.FloatField(db_column='JLM')  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='Unit', max_length=10)  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.
    lot_sup = models.CharField(max_length=20)
    tempat = models.CharField(db_column='Tempat', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Barang_Pemusnahan_D'


class TBarangProduksi(models.Model):
    no_produksi = models.CharField(db_column='No_Produksi', max_length=200)  # Field name made lowercase.
    jenis_resep = models.CharField(db_column='Jenis_Resep', max_length=150)  # Field name made lowercase.
    usernya = models.CharField(max_length=100)
    status = models.CharField(max_length=1)
    tglmasuk = models.CharField(max_length=150)
    tgledit = models.CharField(max_length=100, blank=True, null=True)
    pc = models.CharField(db_column='PC', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Barang_Produksi'


class TBarangProduksiD(models.Model):
    no_produksi = models.CharField(db_column='No_Produksi', max_length=20)  # Field name made lowercase.
    no_keluar = models.CharField(db_column='No_Keluar', max_length=15)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='Kode_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=1)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=15)  # Field name made lowercase.
    tglkeluar = models.CharField(db_column='TglKeluar', max_length=10, blank=True, null=True)  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.
    jlmresep = models.CharField(max_length=10, blank=True, null=True)
    barangdua = models.CharField(max_length=20, blank=True, null=True)
    barcodecampuran = models.CharField(db_column='BarcodeCampuran', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kdbrgcampuran = models.CharField(db_column='KdBrgCampuran', max_length=35, blank=True, null=True)  # Field name made lowercase.
    waktu = models.CharField(max_length=20, blank=True, null=True)
    namarsp = models.CharField(db_column='NamaRsp', max_length=100, blank=True, null=True)  # Field name made lowercase.
    asal = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Barang_Produksi_D'


class TBarangMasukQty(models.Model):
    barcode = models.CharField(max_length=20)
    qtynya = models.CharField(db_column='Qtynya', max_length=10)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Barang_masuk_Qty'


class TCalender1(models.Model):
    kd_calender = models.CharField(db_column='kd_Calender', max_length=30, blank=True, null=True)  # Field name made lowercase.
    kd_mixing = models.CharField(db_column='kd_Mixing', max_length=30, blank=True, null=True)  # Field name made lowercase.
    item = models.CharField(db_column='Item', max_length=30, blank=True, null=True)  # Field name made lowercase.
    qtynya = models.CharField(max_length=30, blank=True, null=True)
    usernya = models.CharField(db_column='Usernya', max_length=25, blank=True, null=True)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jamnya = models.CharField(max_length=30, blank=True, null=True)
    stcal = models.CharField(max_length=20, blank=True, null=True)
    qtytot = models.CharField(max_length=30, blank=True, null=True)
    roolnya = models.CharField(db_column='RoolNya', max_length=30, blank=True, null=True)  # Field name made lowercase.
    nokaret = models.CharField(max_length=30, blank=True, null=True)
    totroll = models.CharField(db_column='TotRoll', max_length=30, blank=True, null=True)  # Field name made lowercase.
    panjang = models.CharField(db_column='Panjang', max_length=30, blank=True, null=True)  # Field name made lowercase.
    tglmixing = models.CharField(db_column='TglMixing', max_length=20, blank=True, null=True)  # Field name made lowercase.
    bacthmix = models.CharField(db_column='BacthMix', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rakno = models.CharField(db_column='RakNo', max_length=30, blank=True, null=True)  # Field name made lowercase.
    exp = models.CharField(max_length=20, blank=True, null=True)
    idjatwal = models.BigIntegerField(blank=True, null=True)
    terpakai = models.CharField(max_length=15, blank=True, null=True)
    mesin = models.CharField(max_length=50, blank=True, null=True)
    stdijatwal = models.CharField(max_length=5, blank=True, null=True)
    dis = models.CharField(max_length=50, blank=True, null=True)
    usere = models.CharField(max_length=30, blank=True, null=True)
    lebar = models.CharField(max_length=20, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Calender1'


class TCalenderK(models.Model):
    kd_calender_k = models.CharField(db_column='KD_Calender_K', max_length=25)  # Field name made lowercase.
    kdcalender = models.CharField(db_column='KDCalender', max_length=25)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    tglmasuk = models.CharField(max_length=30)
    useredit = models.CharField(max_length=20, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    statusnya = models.CharField(max_length=1)
    panjang = models.CharField(max_length=15, blank=True, null=True)
    rak = models.CharField(db_column='Rak', max_length=15, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Calender_K'


class TCekQtyTimbangHonda(models.Model):
    nourut = models.BigAutoField(primary_key=True, db_column='NoUrut')  # Field name made lowercase.
    kdtimbang = models.CharField(max_length=20, blank=True, null=True)
    kdtimbangpengganti = models.CharField(db_column='kdtimbangPengganti', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kdresep = models.CharField(db_column='kdResep', max_length=20, blank=True, null=True)  # Field name made lowercase.
    groupresep = models.CharField(db_column='GroupResep', max_length=5, blank=True, null=True)  # Field name made lowercase.
    totbacth = models.CharField(db_column='TotBacth', max_length=3, blank=True, null=True)  # Field name made lowercase.
    bacth = models.CharField(db_column='Bacth', max_length=3, blank=True, null=True)  # Field name made lowercase.
    qtysys = models.DecimalField(db_column='QtySys', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qtyakhir = models.DecimalField(db_column='QtyAkhir', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    mesin = models.CharField(max_length=5, blank=True, null=True)
    timbangulang = models.CharField(max_length=1, blank=True, null=True)
    statusnya = models.CharField(max_length=1, blank=True, null=True)
    idjatwal = models.BigIntegerField(blank=True, null=True)
    usernya = models.CharField(max_length=20, blank=True, null=True)
    tglmasuk = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=50, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Cek_Qty_Timbang_Honda'


class TDetailWip(models.Model):
    kdmasuk = models.CharField(db_column='kdMasuk', max_length=15)  # Field name made lowercase.
    kdbarang = models.CharField(max_length=20)
    statusnya = models.CharField(max_length=1)
    usernya = models.CharField(max_length=15)
    tglmasuk = models.CharField(max_length=10)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=15, blank=True, null=True)
    barcode = models.CharField(max_length=20)
    berat1 = models.CharField(max_length=9, blank=True, null=True)
    berat2 = models.CharField(max_length=9, blank=True, null=True)
    berat3 = models.CharField(max_length=9, blank=True, null=True)
    berat4 = models.CharField(max_length=9, blank=True, null=True)
    berat5 = models.CharField(max_length=9, blank=True, null=True)
    berat6 = models.CharField(max_length=9, blank=True, null=True)
    berat7 = models.CharField(max_length=9, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Detail_WIP'


class TDrayer(models.Model):
    iddrayer = models.BigAutoField(primary_key=True)
    kddrayer = models.CharField(unique=True, max_length=200)
    tgldrayer = models.DateTimeField()
    idjadwal = models.CharField(max_length=200)
    qtysc = models.CharField(max_length=50)
    dc_db_length = models.CharField(db_column='DC_DB_Length', max_length=50)  # Field name made lowercase.
    dc_db_weight = models.CharField(db_column='DC_DB_Weight', max_length=50)  # Field name made lowercase.
    dc_db_temp = models.CharField(db_column='DC_DB_Temp', max_length=50)  # Field name made lowercase.
    dc_af_length = models.CharField(db_column='DC_AF_Length', max_length=50)  # Field name made lowercase.
    dc_af_weight = models.CharField(db_column='DC_AF_Weight', max_length=50)  # Field name made lowercase.
    dc_af_temp = models.CharField(db_column='DC_AF_Temp', max_length=50)  # Field name made lowercase.
    dtemp1 = models.CharField(db_column='DTemp1', max_length=50)  # Field name made lowercase.
    dtemp2 = models.CharField(db_column='DTemp2', max_length=50)  # Field name made lowercase.
    dtemp3 = models.CharField(db_column='DTemp3', max_length=50)  # Field name made lowercase.
    dtemp4 = models.CharField(db_column='DTemp4', max_length=50)  # Field name made lowercase.
    dtemp5 = models.CharField(db_column='Dtemp5', max_length=50)  # Field name made lowercase.
    ritem = models.CharField(db_column='RItem', max_length=200)  # Field name made lowercase.
    r_act_lenght = models.CharField(db_column='R_act_Lenght', max_length=50)  # Field name made lowercase.
    r_act_weight = models.CharField(db_column='R_act_Weight', max_length=50)  # Field name made lowercase.
    tglin = models.DateTimeField()
    userin = models.CharField(max_length=200)
    statusnya = models.CharField(max_length=2)
    tgledit = models.DateTimeField(blank=True, null=True)
    useredit = models.CharField(max_length=200, blank=True, null=True)
    ch = models.CharField(max_length=1, blank=True, null=True)
    roll = models.CharField(max_length=200, blank=True, null=True)
    itemdesc = models.CharField(max_length=500)
    terpakai = models.CharField(max_length=1)
    resepdrayer = models.CharField(db_column='ResepDrayer', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Drayer'


class TDrayer1(models.Model):
    iddrayer = models.BigAutoField(primary_key=True)
    kddrayer = models.CharField(max_length=200)
    tgldrayer = models.DateTimeField()
    idjadwal = models.CharField(max_length=200)
    qtysc = models.CharField(max_length=50)
    dc_db_length = models.CharField(db_column='DC_DB_Length', max_length=50)  # Field name made lowercase.
    dc_db_weight = models.CharField(db_column='DC_DB_Weight', max_length=50)  # Field name made lowercase.
    dc_db_temp = models.CharField(db_column='DC_DB_Temp', max_length=50)  # Field name made lowercase.
    dc_af_length = models.CharField(db_column='DC_AF_Length', max_length=50)  # Field name made lowercase.
    dc_af_weight = models.CharField(db_column='DC_AF_Weight', max_length=50)  # Field name made lowercase.
    dc_af_temp = models.CharField(db_column='DC_AF_Temp', max_length=50)  # Field name made lowercase.
    dtemp1 = models.CharField(db_column='DTemp1', max_length=50)  # Field name made lowercase.
    dtemp2 = models.CharField(db_column='DTemp2', max_length=50)  # Field name made lowercase.
    dtemp3 = models.CharField(db_column='DTemp3', max_length=50)  # Field name made lowercase.
    dtemp4 = models.CharField(db_column='DTemp4', max_length=50)  # Field name made lowercase.
    dtemp5 = models.CharField(db_column='Dtemp5', max_length=50)  # Field name made lowercase.
    ritem = models.CharField(db_column='RItem', max_length=200)  # Field name made lowercase.
    r_act_lenght = models.CharField(db_column='R_act_Lenght', max_length=50)  # Field name made lowercase.
    r_act_weight = models.CharField(db_column='R_act_Weight', max_length=50)  # Field name made lowercase.
    tglin = models.DateTimeField()
    userin = models.CharField(max_length=200)
    statusnya = models.CharField(max_length=2)
    tgledit = models.DateTimeField(blank=True, null=True)
    useredit = models.CharField(max_length=200, blank=True, null=True)
    ch = models.CharField(max_length=1, blank=True, null=True)
    roll = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Drayer1'


class TDrayerD(models.Model):
    iddrayer = models.CharField(max_length=200)
    kddrayer = models.CharField(max_length=200)
    barcode_fabric = models.CharField(db_column='Barcode_Fabric', max_length=200)  # Field name made lowercase.
    lot = models.CharField(max_length=200)
    act_weight = models.CharField(db_column='Act_weight', max_length=50)  # Field name made lowercase.
    act_lenght = models.CharField(db_column='Act_Lenght', max_length=50)  # Field name made lowercase.
    sumber = models.CharField(db_column='Sumber', max_length=200)  # Field name made lowercase.
    tglin = models.DateTimeField()
    userin = models.CharField(max_length=200)
    statusnya = models.CharField(max_length=2)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Drayer_D'


class TDrayerD1(models.Model):
    iddrayer = models.CharField(max_length=200)
    kddrayer = models.CharField(max_length=200)
    barcode_fabric = models.CharField(db_column='Barcode_Fabric', max_length=200)  # Field name made lowercase.
    lot = models.CharField(max_length=200)
    act_weight = models.CharField(db_column='Act_weight', max_length=50)  # Field name made lowercase.
    act_lenght = models.CharField(db_column='Act_Lenght', max_length=50)  # Field name made lowercase.
    sumber = models.CharField(db_column='Sumber', max_length=200)  # Field name made lowercase.
    tglin = models.DateTimeField()
    userin = models.CharField(max_length=200)
    statusnya = models.CharField(max_length=2)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Drayer_D1'


class TExp(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=30)  # Field name made lowercase.
    kd_barang = models.CharField(db_column='Kd_barang', max_length=20)  # Field name made lowercase.
    lot_sup = models.CharField(db_column='Lot_Sup', max_length=20)  # Field name made lowercase.
    tanggalawal = models.CharField(db_column='TanggalAwal', max_length=10)  # Field name made lowercase.
    tanggal1 = models.CharField(db_column='Tanggal1', max_length=10)  # Field name made lowercase.
    tanggal2 = models.CharField(db_column='Tanggal2', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tanggal3 = models.CharField(db_column='Tanggal3', max_length=10, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Exp'


class TFirstBalance(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='KODE_BARANG', max_length=20, blank=True, null=True)  # Field name made lowercase.
    in_qty = models.DecimalField(db_column='IN_QTY', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_qty = models.DecimalField(db_column='OUT_QTY', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_amt = models.DecimalField(db_column='IN_AMT', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_amt = models.DecimalField(db_column='OUT_AMT', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    update_timestamp = models.DateTimeField(db_column='UPDATE_TIMESTAMP', blank=True, null=True)  # Field name made lowercase.
    update_user = models.CharField(db_column='UPDATE_USER', max_length=50, blank=True, null=True)  # Field name made lowercase.
    update_status = models.CharField(db_column='UPDATE_STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_FIRST_BALANCE'


class TFotoRemil(models.Model):
    idfoto = models.CharField(db_column='Idfoto', max_length=20)  # Field name made lowercase.
    idremil = models.CharField(max_length=30)
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    terpakai = models.CharField(max_length=1)
    bagian = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'T_Foto_Remil'


class THistBarangMasuk2(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20)  # Field name made lowercase.
    no_nota_supp = models.CharField(db_column='No_Nota_Supp', max_length=18)  # Field name made lowercase.
    tanggal_pengiriman = models.DateTimeField(db_column='Tanggal_Pengiriman')  # Field name made lowercase.
    pengirim = models.CharField(db_column='Pengirim', max_length=50)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    konfirmasi = models.CharField(db_column='Konfirmasi', max_length=1)  # Field name made lowercase.
    tglperiksa = models.CharField(db_column='TglPeriksa', max_length=10, blank=True, null=True)  # Field name made lowercase.
    no_surat_jalan = models.CharField(db_column='No_Surat_Jalan', max_length=30, blank=True, null=True)  # Field name made lowercase.
    keterangan = models.CharField(db_column='Keterangan', max_length=100, blank=True, null=True)  # Field name made lowercase.
    penerima = models.CharField(db_column='Penerima', max_length=20, blank=True, null=True)  # Field name made lowercase.
    mengetahui = models.CharField(db_column='Mengetahui', max_length=20, blank=True, null=True)  # Field name made lowercase.
    disetujui = models.CharField(db_column='Disetujui', max_length=20, blank=True, null=True)  # Field name made lowercase.
    qc = models.CharField(db_column='QC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tglproduksi = models.CharField(db_column='Tglproduksi', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_Masuk_2'


class THistBarangMasuk2Lama1(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20)  # Field name made lowercase.
    no_nota_supp = models.CharField(db_column='No_Nota_Supp', max_length=18)  # Field name made lowercase.
    tanggal_pengiriman = models.DateTimeField(db_column='Tanggal_Pengiriman')  # Field name made lowercase.
    pengirim = models.CharField(db_column='Pengirim', max_length=50)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    konfirmasi = models.CharField(db_column='Konfirmasi', max_length=1)  # Field name made lowercase.
    tglperiksa = models.CharField(db_column='TglPeriksa', max_length=10, blank=True, null=True)  # Field name made lowercase.
    no_surat_jalan = models.CharField(db_column='No_Surat_Jalan', max_length=30, blank=True, null=True)  # Field name made lowercase.
    keterangan = models.CharField(db_column='Keterangan', max_length=100, blank=True, null=True)  # Field name made lowercase.
    penerima = models.CharField(db_column='Penerima', max_length=20, blank=True, null=True)  # Field name made lowercase.
    mengetahui = models.CharField(db_column='Mengetahui', max_length=20, blank=True, null=True)  # Field name made lowercase.
    disetujui = models.CharField(db_column='Disetujui', max_length=20, blank=True, null=True)  # Field name made lowercase.
    qc = models.CharField(db_column='QC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tglproduksi = models.CharField(db_column='Tglproduksi', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_Masuk_2_lama1'


class THistBarangMasukD(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='Kode_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    jumlah_barang = models.FloatField(db_column='Jumlah_Barang')  # Field name made lowercase.
    tanggal_pengiriman = models.DateTimeField(db_column='Tanggal_Pengiriman', blank=True, null=True)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglhabis = models.CharField(db_column='TglHabis', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tglhabisasli = models.CharField(db_column='TglHabisAsli', max_length=10, blank=True, null=True)  # Field name made lowercase.
    hold = models.CharField(max_length=1, blank=True, null=True)
    sign = models.CharField(max_length=10, blank=True, null=True)
    soa = models.CharField(db_column='SOA', max_length=1, blank=True, null=True)  # Field name made lowercase.
    insp = models.CharField(max_length=1, blank=True, null=True)
    ppi = models.CharField(max_length=1, blank=True, null=True)
    prioritas = models.CharField(db_column='Prioritas', max_length=1, blank=True, null=True)  # Field name made lowercase.
    no_lot = models.CharField(db_column='No_lot', max_length=20, blank=True, null=True)  # Field name made lowercase.
    lot_sup = models.CharField(db_column='Lot_sup', max_length=15)  # Field name made lowercase.
    barcode = models.CharField(max_length=20)
    diambil = models.CharField(max_length=1, blank=True, null=True)
    very = models.CharField(db_column='Very', max_length=1)  # Field name made lowercase.
    sa = models.CharField(db_column='Sa', max_length=1, blank=True, null=True)  # Field name made lowercase.
    tglvery = models.CharField(db_column='TglVery', max_length=10)  # Field name made lowercase.
    tglsa = models.CharField(db_column='TglSa', max_length=10, blank=True, null=True)  # Field name made lowercase.
    disposisi = models.CharField(max_length=1, blank=True, null=True)
    nosa = models.CharField(db_column='noSA', max_length=20, blank=True, null=True)  # Field name made lowercase.
    notesa = models.CharField(db_column='NoteSa', max_length=50, blank=True, null=True)  # Field name made lowercase.
    urut = models.FloatField(blank=True, null=True)
    kgasli = models.FloatField(db_column='KgAsli', blank=True, null=True)  # Field name made lowercase.
    tglproduksi = models.CharField(db_column='Tglproduksi', max_length=10, blank=True, null=True)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20, blank=True, null=True)  # Field name made lowercase.
    po = models.CharField(db_column='Po', max_length=15, blank=True, null=True)  # Field name made lowercase.
    pelanggan = models.CharField(db_column='Pelanggan', max_length=15, blank=True, null=True)  # Field name made lowercase.
    noaju = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_Masuk_D'


class THistBarangMasukDWip(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='Kode_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    lot_lama = models.CharField(db_column='Lot_Lama', max_length=20)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty')  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.
    kode_barang_wip = models.CharField(db_column='Kode_Barang_WIP', max_length=35, blank=True, null=True)  # Field name made lowercase.
    lot_wip = models.CharField(db_column='Lot_WIP', max_length=20)  # Field name made lowercase.
    qty_wip = models.FloatField(db_column='Qty_WIP')  # Field name made lowercase.
    barcode_wip = models.CharField(db_column='Barcode_WIP', max_length=20)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    barcoderm = models.CharField(db_column='BarcodeRM', max_length=15, blank=True, null=True)  # Field name made lowercase.
    lot_sup = models.CharField(db_column='Lot_sup', max_length=15, blank=True, null=True)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_Masuk_D_WIP'


class THistBarangMasukDWipLama1(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='Kode_Barang', max_length=20)  # Field name made lowercase.
    lot_lama = models.CharField(db_column='Lot_Lama', max_length=20)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty')  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.
    kode_barang_wip = models.CharField(db_column='Kode_Barang_WIP', max_length=35, blank=True, null=True)  # Field name made lowercase.
    lot_wip = models.CharField(db_column='Lot_WIP', max_length=20)  # Field name made lowercase.
    qty_wip = models.FloatField(db_column='Qty_WIP')  # Field name made lowercase.
    barcode_wip = models.CharField(db_column='Barcode_WIP', max_length=20)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    barcoderm = models.CharField(db_column='BarcodeRM', max_length=15, blank=True, null=True)  # Field name made lowercase.
    lot_sup = models.CharField(db_column='Lot_sup', max_length=15, blank=True, null=True)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_Masuk_D_WIP_lama1'


class THistBarangMasukDLama1(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='Kode_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    jumlah_barang = models.FloatField(db_column='Jumlah_Barang')  # Field name made lowercase.
    tanggal_pengiriman = models.DateTimeField(db_column='Tanggal_Pengiriman', blank=True, null=True)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglhabis = models.CharField(db_column='TglHabis', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tglhabisasli = models.CharField(db_column='TglHabisAsli', max_length=10, blank=True, null=True)  # Field name made lowercase.
    hold = models.CharField(max_length=1, blank=True, null=True)
    sign = models.CharField(max_length=10, blank=True, null=True)
    soa = models.CharField(db_column='SOA', max_length=1, blank=True, null=True)  # Field name made lowercase.
    insp = models.CharField(max_length=1, blank=True, null=True)
    ppi = models.CharField(max_length=1, blank=True, null=True)
    prioritas = models.CharField(db_column='Prioritas', max_length=1, blank=True, null=True)  # Field name made lowercase.
    no_lot = models.CharField(db_column='No_lot', max_length=20, blank=True, null=True)  # Field name made lowercase.
    lot_sup = models.CharField(db_column='Lot_sup', max_length=15)  # Field name made lowercase.
    barcode = models.CharField(max_length=20)
    diambil = models.CharField(max_length=1, blank=True, null=True)
    very = models.CharField(db_column='Very', max_length=1)  # Field name made lowercase.
    sa = models.CharField(db_column='Sa', max_length=1, blank=True, null=True)  # Field name made lowercase.
    tglvery = models.CharField(db_column='TglVery', max_length=10)  # Field name made lowercase.
    tglsa = models.CharField(db_column='TglSa', max_length=10, blank=True, null=True)  # Field name made lowercase.
    disposisi = models.CharField(max_length=1, blank=True, null=True)
    nosa = models.CharField(db_column='noSA', max_length=20, blank=True, null=True)  # Field name made lowercase.
    notesa = models.CharField(db_column='NoteSa', max_length=50, blank=True, null=True)  # Field name made lowercase.
    urut = models.FloatField(blank=True, null=True)
    kgasli = models.FloatField(db_column='KgAsli', blank=True, null=True)  # Field name made lowercase.
    tglproduksi = models.CharField(db_column='Tglproduksi', max_length=10, blank=True, null=True)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20, blank=True, null=True)  # Field name made lowercase.
    po = models.CharField(db_column='Po', max_length=15, blank=True, null=True)  # Field name made lowercase.
    pelanggan = models.CharField(db_column='Pelanggan', max_length=15, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_Masuk_D_lama1'


class THistBarangMasukMillingD(models.Model):
    no_keluar = models.CharField(db_column='No_Keluar', max_length=15)  # Field name made lowercase.
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kd_lot = models.CharField(db_column='Kd_lot', max_length=10)  # Field name made lowercase.
    kd_barang = models.CharField(max_length=35, blank=True, null=True)
    kd_barang_baru = models.CharField(db_column='kd_barang_Baru', max_length=15)  # Field name made lowercase.
    jlm = models.FloatField(db_column='JLM', blank=True, null=True)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='Tglmasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='UNIT', max_length=20)  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.
    bar = models.CharField(db_column='Bar', max_length=10, blank=True, null=True)  # Field name made lowercase.
    asalbrg = models.CharField(db_column='Asalbrg', max_length=1, blank=True, null=True)  # Field name made lowercase.
    lot_sup = models.CharField(db_column='Lot_sup', max_length=15, blank=True, null=True)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_Masuk_Milling_D'


class THistBarangMasukMillingDLama1(models.Model):
    no_keluar = models.CharField(db_column='No_Keluar', max_length=15)  # Field name made lowercase.
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kd_lot = models.CharField(db_column='Kd_lot', max_length=10)  # Field name made lowercase.
    kd_barang = models.CharField(max_length=35, blank=True, null=True)
    kd_barang_baru = models.CharField(db_column='kd_barang_Baru', max_length=15)  # Field name made lowercase.
    jlm = models.FloatField(db_column='JLM', blank=True, null=True)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='Tglmasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='UNIT', max_length=20)  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.
    bar = models.CharField(db_column='Bar', max_length=10, blank=True, null=True)  # Field name made lowercase.
    asalbrg = models.CharField(db_column='Asalbrg', max_length=1, blank=True, null=True)  # Field name made lowercase.
    lot_sup = models.CharField(db_column='Lot_sup', max_length=15, blank=True, null=True)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_Masuk_Milling_D_lama1'


class THistBarangMasukSelainMillingD(models.Model):
    no_keluar = models.CharField(db_column='No_Keluar', max_length=15)  # Field name made lowercase.
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kd_lot = models.CharField(db_column='Kd_lot', max_length=10)  # Field name made lowercase.
    kd_barang = models.CharField(max_length=35, blank=True, null=True)
    kd_barang_baru = models.CharField(db_column='kd_barang_Baru', max_length=35, blank=True, null=True)  # Field name made lowercase.
    jlm = models.FloatField(db_column='JLM', blank=True, null=True)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='Tglmasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='UNIT', max_length=20)  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.
    bar = models.CharField(db_column='Bar', max_length=10, blank=True, null=True)  # Field name made lowercase.
    asalbrg = models.CharField(db_column='Asalbrg', max_length=1, blank=True, null=True)  # Field name made lowercase.
    lot_sup = models.CharField(db_column='Lot_sup', max_length=15, blank=True, null=True)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_Masuk_Selain_Milling_D'


class THistBarangMasukSelainMillingDLama1(models.Model):
    no_keluar = models.CharField(db_column='No_Keluar', max_length=15)  # Field name made lowercase.
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kd_lot = models.CharField(db_column='Kd_lot', max_length=10)  # Field name made lowercase.
    kd_barang = models.CharField(max_length=35, blank=True, null=True)
    kd_barang_baru = models.CharField(db_column='kd_barang_Baru', max_length=35, blank=True, null=True)  # Field name made lowercase.
    jlm = models.FloatField(db_column='JLM', blank=True, null=True)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='Tglmasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='UNIT', max_length=20)  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.
    bar = models.CharField(db_column='Bar', max_length=10, blank=True, null=True)  # Field name made lowercase.
    asalbrg = models.CharField(db_column='Asalbrg', max_length=1, blank=True, null=True)  # Field name made lowercase.
    lot_sup = models.CharField(db_column='Lot_sup', max_length=15, blank=True, null=True)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_Masuk_Selain_Milling_D_lama1'


class THistBarangProduksi(models.Model):
    no_produksi = models.CharField(db_column='No_Produksi', max_length=200)  # Field name made lowercase.
    jenis_resep = models.CharField(db_column='Jenis_Resep', max_length=150)  # Field name made lowercase.
    usernya = models.CharField(max_length=100)
    status = models.CharField(max_length=1)
    tglmasuk = models.CharField(max_length=150)
    tgledit = models.CharField(max_length=100, blank=True, null=True)
    pc = models.CharField(db_column='PC', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_Produksi'


class THistBarangProduksiD(models.Model):
    no_produksi = models.CharField(db_column='No_Produksi', max_length=20)  # Field name made lowercase.
    no_keluar = models.CharField(db_column='No_Keluar', max_length=15)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='Kode_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=1)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=15)  # Field name made lowercase.
    tglkeluar = models.CharField(db_column='TglKeluar', max_length=10, blank=True, null=True)  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.
    jlmresep = models.CharField(max_length=10, blank=True, null=True)
    barangdua = models.CharField(max_length=20, blank=True, null=True)
    barcodecampuran = models.CharField(db_column='BarcodeCampuran', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kdbrgcampuran = models.CharField(db_column='KdBrgCampuran', max_length=35, blank=True, null=True)  # Field name made lowercase.
    waktu = models.CharField(max_length=20, blank=True, null=True)
    namarsp = models.CharField(db_column='NamaRsp', max_length=100, blank=True, null=True)  # Field name made lowercase.
    lot_sup = models.CharField(max_length=100, blank=True, null=True)
    kode_sup = models.CharField(max_length=100, blank=True, null=True)
    asal = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_Produksi_D'


class THistBarangProduksiDLama1Hapus(models.Model):
    no_produksi = models.CharField(db_column='No_Produksi', max_length=20)  # Field name made lowercase.
    no_keluar = models.CharField(db_column='No_Keluar', max_length=15)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='Kode_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=1)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=15)  # Field name made lowercase.
    tglkeluar = models.CharField(db_column='TglKeluar', max_length=10, blank=True, null=True)  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.
    jlmresep = models.CharField(max_length=10, blank=True, null=True)
    barangdua = models.CharField(max_length=20, blank=True, null=True)
    barcodecampuran = models.CharField(db_column='BarcodeCampuran', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kdbrgcampuran = models.CharField(db_column='KdBrgCampuran', max_length=35, blank=True, null=True)  # Field name made lowercase.
    waktu = models.CharField(max_length=20, blank=True, null=True)
    namarsp = models.CharField(db_column='NamaRsp', max_length=100, blank=True, null=True)  # Field name made lowercase.
    lot_sup = models.CharField(max_length=100, blank=True, null=True)
    kode_sup = models.CharField(max_length=100, blank=True, null=True)
    asal = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_Produksi_D_lama1_hapus'


class THistBarangProduksiLama1Hapus(models.Model):
    no_produksi = models.CharField(db_column='No_Produksi', max_length=200)  # Field name made lowercase.
    jenis_resep = models.CharField(db_column='Jenis_Resep', max_length=150)  # Field name made lowercase.
    usernya = models.CharField(max_length=100)
    status = models.CharField(max_length=1)
    tglmasuk = models.CharField(max_length=150)
    tgledit = models.CharField(max_length=100, blank=True, null=True)
    pc = models.CharField(db_column='PC', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_Produksi_lama1_hapus'


class THistBarangMasuk(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20)  # Field name made lowercase.
    no_nota_supp = models.CharField(db_column='No_Nota_Supp', max_length=18)  # Field name made lowercase.
    tanggal_pengiriman = models.DateTimeField(db_column='Tanggal_Pengiriman')  # Field name made lowercase.
    pengirim = models.CharField(db_column='Pengirim', max_length=50)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    konfirmasi = models.CharField(db_column='Konfirmasi', max_length=1)  # Field name made lowercase.
    tglperiksa = models.CharField(db_column='TglPeriksa', max_length=10, blank=True, null=True)  # Field name made lowercase.
    no_surat_jalan = models.CharField(db_column='No_Surat_Jalan', max_length=30, blank=True, null=True)  # Field name made lowercase.
    keterangan = models.CharField(db_column='Keterangan', max_length=100, blank=True, null=True)  # Field name made lowercase.
    penerima = models.CharField(db_column='Penerima', max_length=20, blank=True, null=True)  # Field name made lowercase.
    mengetahui = models.CharField(db_column='Mengetahui', max_length=20, blank=True, null=True)  # Field name made lowercase.
    disetujui = models.CharField(db_column='Disetujui', max_length=20, blank=True, null=True)  # Field name made lowercase.
    qc = models.CharField(db_column='QC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tglproduksi = models.CharField(db_column='Tglproduksi', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_masuk'


class THistBarangMasukLama1(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20)  # Field name made lowercase.
    no_nota_supp = models.CharField(db_column='No_Nota_Supp', max_length=18)  # Field name made lowercase.
    tanggal_pengiriman = models.DateTimeField(db_column='Tanggal_Pengiriman')  # Field name made lowercase.
    pengirim = models.CharField(db_column='Pengirim', max_length=50)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    konfirmasi = models.CharField(db_column='Konfirmasi', max_length=1)  # Field name made lowercase.
    tglperiksa = models.CharField(db_column='TglPeriksa', max_length=10, blank=True, null=True)  # Field name made lowercase.
    no_surat_jalan = models.CharField(db_column='No_Surat_Jalan', max_length=30, blank=True, null=True)  # Field name made lowercase.
    keterangan = models.CharField(db_column='Keterangan', max_length=100, blank=True, null=True)  # Field name made lowercase.
    penerima = models.CharField(db_column='Penerima', max_length=20, blank=True, null=True)  # Field name made lowercase.
    mengetahui = models.CharField(db_column='Mengetahui', max_length=20, blank=True, null=True)  # Field name made lowercase.
    disetujui = models.CharField(db_column='Disetujui', max_length=20, blank=True, null=True)  # Field name made lowercase.
    qc = models.CharField(db_column='QC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tglproduksi = models.CharField(db_column='Tglproduksi', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Barang_masuk_lama1'


class THistLotKeluar(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    no_keluar = models.CharField(db_column='No_Keluar', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kd_barang = models.CharField(db_column='Kd_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    kd_lot = models.CharField(db_column='Kd_Lot', max_length=150)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=100)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=100, blank=True, null=True)  # Field name made lowercase.
    barcode = models.CharField(max_length=200, blank=True, null=True)
    lot_sup = models.CharField(db_column='Lot_sup', max_length=15, blank=True, null=True)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Lot_Keluar'


class THistLotKeluarLama1Hapus(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    no_keluar = models.CharField(db_column='No_Keluar', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kd_barang = models.CharField(db_column='Kd_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    kd_lot = models.CharField(db_column='Kd_Lot', max_length=150)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=100)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=100, blank=True, null=True)  # Field name made lowercase.
    barcode = models.CharField(max_length=200, blank=True, null=True)
    lot_sup = models.CharField(db_column='Lot_sup', max_length=15, blank=True, null=True)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Lot_Keluar_lama1_hapus'


class THistLotMasuk(models.Model):
    kdlot = models.CharField(max_length=10)
    no_transaksi = models.CharField(max_length=15, blank=True, null=True)
    kode_barang = models.CharField(db_column='kode_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    jenis_barang = models.CharField(max_length=15, blank=True, null=True)
    jumlah = models.FloatField(blank=True, null=True)
    usernya = models.CharField(db_column='Usernya', max_length=20, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(max_length=1, blank=True, null=True)
    tglmasuk = models.CharField(max_length=10, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    barcode = models.CharField(max_length=20, blank=True, null=True)
    lot_sup = models.CharField(db_column='Lot_sup', max_length=15, blank=True, null=True)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Lot_Masuk'


class THistLotMasukLama1(models.Model):
    kdlot = models.CharField(max_length=10)
    no_transaksi = models.CharField(max_length=15, blank=True, null=True)
    kode_barang = models.CharField(db_column='kode_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    jenis_barang = models.CharField(max_length=15, blank=True, null=True)
    jumlah = models.FloatField(blank=True, null=True)
    usernya = models.CharField(db_column='Usernya', max_length=20, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(max_length=1, blank=True, null=True)
    tglmasuk = models.CharField(max_length=10, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    barcode = models.CharField(max_length=20, blank=True, null=True)
    lot_sup = models.CharField(db_column='Lot_sup', max_length=15, blank=True, null=True)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_Lot_Masuk_lama1'


class THistPrintProduksi(models.Model):
    idnya = models.BigAutoField(primary_key=True, db_column='IdNya')  # Field name made lowercase.
    kdtimbang = models.CharField(max_length=20, blank=True, null=True)
    kdresep = models.CharField(max_length=20, blank=True, null=True)
    nmresep = models.CharField(max_length=50, blank=True, null=True)
    totalbatch = models.CharField(max_length=10, blank=True, null=True)
    batch = models.CharField(max_length=10, blank=True, null=True)
    tglcompounding = models.CharField(max_length=30, blank=True, null=True)
    usernya = models.CharField(max_length=20, blank=True, null=True)
    itemgroup = models.CharField(max_length=10, blank=True, null=True)
    kdbarang = models.CharField(max_length=35, blank=True, null=True)
    qtybarang = models.CharField(max_length=10, blank=True, null=True)
    stdqty = models.CharField(max_length=10, blank=True, null=True)
    statusnya = models.CharField(max_length=1)
    waktu = models.CharField(max_length=20, blank=True, null=True)
    nourut = models.CharField(db_column='NoUrut', max_length=2, blank=True, null=True)  # Field name made lowercase.
    terpakai = models.CharField(max_length=10, blank=True, null=True)
    proses = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'T_Hist_Print_Produksi'


class THistPrintProduksiLama1Hapus(models.Model):
    idnya = models.BigAutoField(primary_key=True, db_column='IdNya')  # Field name made lowercase.
    kdtimbang = models.CharField(max_length=20, blank=True, null=True)
    kdresep = models.CharField(max_length=20, blank=True, null=True)
    nmresep = models.CharField(max_length=50, blank=True, null=True)
    totalbatch = models.CharField(max_length=10, blank=True, null=True)
    batch = models.CharField(max_length=10, blank=True, null=True)
    tglcompounding = models.CharField(max_length=30, blank=True, null=True)
    usernya = models.CharField(max_length=20, blank=True, null=True)
    itemgroup = models.CharField(max_length=10, blank=True, null=True)
    kdbarang = models.CharField(max_length=35, blank=True, null=True)
    qtybarang = models.CharField(max_length=10, blank=True, null=True)
    stdqty = models.CharField(max_length=10, blank=True, null=True)
    statusnya = models.CharField(max_length=1)
    waktu = models.CharField(max_length=20, blank=True, null=True)
    nourut = models.CharField(db_column='NoUrut', max_length=2, blank=True, null=True)  # Field name made lowercase.
    terpakai = models.CharField(max_length=10, blank=True, null=True)
    proses = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'T_Hist_Print_Produksi_lama1_hapus'


class THistRemil(models.Model):
    resep = models.CharField(db_column='Resep', max_length=30)  # Field name made lowercase.
    tglpro = models.CharField(db_column='TglPro', max_length=10)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty')  # Field name made lowercase.
    tglmasuk = models.CharField(max_length=10)
    usernya = models.CharField(max_length=20)
    kdremil = models.CharField(max_length=30)
    tglexp = models.CharField(max_length=10, blank=True, null=True)
    seksi = models.CharField(db_column='Seksi', max_length=100, blank=True, null=True)  # Field name made lowercase.
    tglcal = models.CharField(db_column='tglCal', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tglremil = models.CharField(max_length=10, blank=True, null=True)
    kdcalender = models.CharField(db_column='kdCalender', max_length=30, blank=True, null=True)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    terpakai = models.CharField(db_column='Terpakai', max_length=1, blank=True, null=True)  # Field name made lowercase.
    subsek = models.CharField(max_length=20, blank=True, null=True)
    shift = models.CharField(max_length=10, blank=True, null=True)
    user_edit = models.CharField(max_length=50, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    sebabremil = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Hist_Remil'


class THistRemilLama1Hapus(models.Model):
    resep = models.CharField(db_column='Resep', max_length=30)  # Field name made lowercase.
    tglpro = models.CharField(db_column='TglPro', max_length=10)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty')  # Field name made lowercase.
    tglmasuk = models.CharField(max_length=10)
    usernya = models.CharField(max_length=20)
    kdremil = models.CharField(max_length=30)
    tglexp = models.CharField(max_length=10, blank=True, null=True)
    seksi = models.CharField(db_column='Seksi', max_length=100, blank=True, null=True)  # Field name made lowercase.
    tglcal = models.CharField(db_column='tglCal', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tglremil = models.CharField(max_length=10, blank=True, null=True)
    kdcalender = models.CharField(db_column='kdCalender', max_length=30, blank=True, null=True)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    terpakai = models.CharField(db_column='Terpakai', max_length=1, blank=True, null=True)  # Field name made lowercase.
    subsek = models.CharField(max_length=20, blank=True, null=True)
    shift = models.CharField(max_length=10, blank=True, null=True)
    user_edit = models.CharField(max_length=50, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Hist_Remil_lama1_hapus'


class THistMixing(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column='Id')  # Field name made lowercase.
    kd_mixing = models.CharField(db_column='Kd_Mixing', max_length=20)  # Field name made lowercase.
    kd_resep = models.CharField(db_column='kd_Resep', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item = models.CharField(db_column='Item', max_length=20)  # Field name made lowercase.
    qty = models.CharField(db_column='Qty', max_length=20)  # Field name made lowercase.
    kdweihing = models.CharField(db_column='KdWeihing', max_length=20)  # Field name made lowercase.
    operator = models.CharField(db_column='Operator', max_length=20)  # Field name made lowercase.
    tglmixing = models.CharField(db_column='tglMixing', max_length=20)  # Field name made lowercase.
    waktu = models.CharField(max_length=20, blank=True, null=True)
    tglmasuk = models.CharField(db_column='Tglmasuk', max_length=10)  # Field name made lowercase.
    usernya = models.CharField(max_length=20)
    statusnya = models.CharField(max_length=1)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=20, blank=True, null=True)
    mesin = models.CharField(db_column='Mesin', max_length=10, blank=True, null=True)  # Field name made lowercase.
    batch = models.CharField(db_column='Batch', max_length=10, blank=True, null=True)  # Field name made lowercase.
    proses = models.CharField(max_length=1)
    hold = models.CharField(db_column='Hold', max_length=1, blank=True, null=True)  # Field name made lowercase.
    tglqc = models.CharField(max_length=10, blank=True, null=True)
    tglhold = models.CharField(max_length=10, blank=True, null=True)
    bacttot = models.DecimalField(db_column='BactTot', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qtot = models.DecimalField(db_column='Qtot', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    tglexp = models.CharField(max_length=10, blank=True, null=True)
    idjatwal = models.CharField(max_length=8, blank=True, null=True)
    idprint = models.CharField(max_length=20, blank=True, null=True)
    lewat = models.CharField(max_length=1)
    usrtimbang = models.CharField(db_column='UsrTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jamtimbang = models.CharField(db_column='JamTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tgltimbang = models.CharField(db_column='TglTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    userqc = models.CharField(db_column='UserQC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    terpakai = models.CharField(max_length=1)
    jenis = models.CharField(max_length=20, blank=True, null=True)
    qty_adjusment = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    chamtemp = models.CharField(db_column='ChamTemp', max_length=9, blank=True, null=True)  # Field name made lowercase.
    tempwaterin = models.CharField(db_column='TempWaterIN', max_length=9, blank=True, null=True)  # Field name made lowercase.
    fwpressure = models.CharField(db_column='FWPressure', max_length=9, blank=True, null=True)  # Field name made lowercase.
    watflowrate = models.CharField(db_column='WatFlowRate', max_length=9, blank=True, null=True)  # Field name made lowercase.
    palet = models.CharField(db_column='Palet', max_length=9, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Hist_mixing'


class THistMixingLama1Hapus(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column='Id')  # Field name made lowercase.
    kd_mixing = models.CharField(db_column='Kd_Mixing', max_length=20)  # Field name made lowercase.
    kd_resep = models.CharField(db_column='kd_Resep', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item = models.CharField(db_column='Item', max_length=20)  # Field name made lowercase.
    qty = models.CharField(db_column='Qty', max_length=20)  # Field name made lowercase.
    kdweihing = models.CharField(db_column='KdWeihing', max_length=20)  # Field name made lowercase.
    operator = models.CharField(db_column='Operator', max_length=20)  # Field name made lowercase.
    tglmixing = models.CharField(db_column='tglMixing', max_length=20)  # Field name made lowercase.
    waktu = models.CharField(max_length=20, blank=True, null=True)
    tglmasuk = models.CharField(db_column='Tglmasuk', max_length=10)  # Field name made lowercase.
    usernya = models.CharField(max_length=20)
    statusnya = models.CharField(max_length=1)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=20, blank=True, null=True)
    mesin = models.CharField(db_column='Mesin', max_length=10, blank=True, null=True)  # Field name made lowercase.
    batch = models.CharField(db_column='Batch', max_length=10, blank=True, null=True)  # Field name made lowercase.
    proses = models.CharField(max_length=1)
    hold = models.CharField(db_column='Hold', max_length=1, blank=True, null=True)  # Field name made lowercase.
    tglqc = models.CharField(max_length=10, blank=True, null=True)
    tglhold = models.CharField(max_length=10, blank=True, null=True)
    bacttot = models.DecimalField(db_column='BactTot', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qtot = models.DecimalField(db_column='Qtot', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    tglexp = models.CharField(max_length=10, blank=True, null=True)
    idjatwal = models.CharField(max_length=8, blank=True, null=True)
    idprint = models.CharField(max_length=20, blank=True, null=True)
    lewat = models.CharField(max_length=1)
    usrtimbang = models.CharField(db_column='UsrTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jamtimbang = models.CharField(db_column='JamTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tgltimbang = models.CharField(db_column='TglTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    userqc = models.CharField(db_column='UserQC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    terpakai = models.CharField(max_length=1)
    jenis = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Hist_mixing_lama1_hapus'


class TJatwal(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='Id')  # Field name made lowercase.
    kdjatwal = models.CharField(db_column='KdJatwal', max_length=200)  # Field name made lowercase.
    mesin = models.CharField(db_column='Mesin', max_length=100)  # Field name made lowercase.
    tglproduksi = models.CharField(max_length=100)
    waktuupload = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=10)
    usernya = models.CharField(max_length=100, blank=True, null=True)
    proses = models.CharField(db_column='Proses', max_length=10)  # Field name made lowercase.
    kdmixing = models.CharField(db_column='kdMixing', max_length=200)  # Field name made lowercase.
    bacth = models.CharField(max_length=20, blank=True, null=True)
    bacthselesai = models.CharField(max_length=20)
    waktuupdate = models.CharField(max_length=100, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=20, blank=True, null=True)
    stjatwal = models.CharField(max_length=1)
    stuser = models.CharField(max_length=20, blank=True, null=True)
    nourut = models.CharField(db_column='noUrut', max_length=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Jatwal'


class TKanbanD(models.Model):
    no_keluar = models.CharField(db_column='No_Keluar', max_length=15)  # Field name made lowercase.
    kanban = models.CharField(db_column='Kanban', max_length=20)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Kanban_D'


class TLogBalanceWeeklyHapus(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ID')  # Field name made lowercase.
    id_log = models.IntegerField(db_column='ID_LOG', blank=True, null=True)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='KODE_BARANG', max_length=20, blank=True, null=True)  # Field name made lowercase.
    balance = models.DecimalField(db_column='BALANCE', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_LOG_BALANCE_WEEKLY_hapus'


class TLogGetDataSbscHapus(models.Model):
    id = models.DecimalField(primary_key=True, db_column='ID', max_digits=10, decimal_places=0)  # Field name made lowercase.
    no_transaksi = models.CharField(db_column='NO_TRANSAKSI', max_length=50, blank=True, null=True)  # Field name made lowercase.
    no_po = models.CharField(db_column='NO_PO', max_length=15, blank=True, null=True)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='KODE_SUP', max_length=50, blank=True, null=True)  # Field name made lowercase.
    tglmasuk = models.DateTimeField(db_column='TGLMASUK', blank=True, null=True)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='KODE_BARANG', max_length=50, blank=True, null=True)  # Field name made lowercase.
    t_code = models.CharField(db_column='T_CODE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    update_timestamp = models.DateTimeField(db_column='UPDATE_TIMESTAMP', blank=True, null=True)  # Field name made lowercase.
    update_user = models.CharField(db_column='UPDATE_USER', max_length=20, blank=True, null=True)  # Field name made lowercase.
    update_status = models.CharField(db_column='UPDATE_STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_LOG_GET_DATA_SBSC_hapus'


class TLogRptDMtrWeeklyHapus(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ID')  # Field name made lowercase.
    transact_year = models.IntegerField(db_column='TRANSACT_YEAR', blank=True, null=True)  # Field name made lowercase.
    transact_month = models.IntegerField(db_column='TRANSACT_MONTH', blank=True, null=True)  # Field name made lowercase.
    transact_week = models.IntegerField(db_column='TRANSACT_WEEK', blank=True, null=True)  # Field name made lowercase.
    start_date = models.DateTimeField(db_column='START_DATE', blank=True, null=True)  # Field name made lowercase.
    end_date = models.DateTimeField(db_column='END_DATE', blank=True, null=True)  # Field name made lowercase.
    update_timestamp = models.DateTimeField(db_column='UPDATE_TIMESTAMP', blank=True, null=True)  # Field name made lowercase.
    update_user = models.CharField(db_column='UPDATE_USER', max_length=50, blank=True, null=True)  # Field name made lowercase.
    update_status = models.CharField(db_column='UPDATE_STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_LOG_RPT_D_MTR_WEEKLY_hapus'


class TLaporanMixing(models.Model):
    idnya = models.CharField(max_length=200, blank=True, null=True)
    kd_mixing = models.CharField(max_length=200, blank=True, null=True)
    kd_resep = models.CharField(max_length=200, blank=True, null=True)
    item = models.CharField(max_length=200, blank=True, null=True)
    qty_dimix = models.CharField(max_length=200, blank=True, null=True)
    kdweihing = models.CharField(max_length=200, blank=True, null=True)
    operator = models.CharField(max_length=200, blank=True, null=True)
    tglmixing = models.CharField(max_length=200, blank=True, null=True)
    waktu = models.CharField(max_length=200, blank=True, null=True)
    tglmasuk = models.CharField(max_length=200, blank=True, null=True)
    usernya = models.CharField(max_length=200, blank=True, null=True)
    statusnya = models.CharField(max_length=200, blank=True, null=True)
    tgledit = models.CharField(max_length=200, blank=True, null=True)
    useredit = models.CharField(max_length=200, blank=True, null=True)
    mesin = models.CharField(max_length=200, blank=True, null=True)
    batch = models.CharField(max_length=200, blank=True, null=True)
    proses = models.CharField(max_length=200, blank=True, null=True)
    hold = models.CharField(max_length=200, blank=True, null=True)
    tglqc = models.CharField(max_length=200, blank=True, null=True)
    tglhold = models.CharField(max_length=200, blank=True, null=True)
    bacttot = models.CharField(db_column='Bacttot', max_length=200, blank=True, null=True)  # Field name made lowercase.
    qtot = models.CharField(max_length=200, blank=True, null=True)
    tglexp = models.CharField(max_length=200, blank=True, null=True)
    idjatwal = models.CharField(max_length=200, blank=True, null=True)
    idprint = models.CharField(max_length=200, blank=True, null=True)
    lewat = models.CharField(max_length=200, blank=True, null=True)
    usertimbang = models.CharField(max_length=200, blank=True, null=True)
    jamtimbang = models.CharField(db_column='Jamtimbang', max_length=200, blank=True, null=True)  # Field name made lowercase.
    tgltimbang = models.CharField(max_length=200, blank=True, null=True)
    userqc = models.CharField(max_length=200, blank=True, null=True)
    kdresepp = models.CharField(max_length=200, blank=True, null=True)
    kdtimbangg = models.CharField(max_length=200, blank=True, null=True)
    namaresep = models.CharField(max_length=200, blank=True, null=True)
    itemgroup = models.CharField(max_length=200, blank=True, null=True)
    kdbarangnn = models.CharField(max_length=200, blank=True, null=True)
    batchh = models.CharField(max_length=200, blank=True, null=True)
    tglcompounding = models.CharField(max_length=200, blank=True, null=True)
    userwh = models.CharField(max_length=200, blank=True, null=True)
    itemgroupx = models.CharField(max_length=200, blank=True, null=True)
    jamtimbangx = models.CharField(db_column='Jamtimbangx', max_length=200, blank=True, null=True)  # Field name made lowercase.
    kode = models.CharField(max_length=200, blank=True, null=True)
    nama = models.CharField(max_length=200, blank=True, null=True)
    qtykalonol = models.CharField(max_length=200, blank=True, null=True)
    c = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Laporan_mixing'


class TLotKeluar(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    no_keluar = models.CharField(db_column='No_Keluar', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kd_barang = models.CharField(db_column='Kd_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    kd_lot = models.CharField(db_column='Kd_Lot', max_length=150)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=100)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=100, blank=True, null=True)  # Field name made lowercase.
    barcode = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Lot_Keluar'


class TLotMasuk(models.Model):
    kdlot = models.CharField(max_length=10)
    no_transaksi = models.CharField(max_length=15, blank=True, null=True)
    kode_barang = models.CharField(db_column='kode_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    jenis_barang = models.CharField(max_length=15, blank=True, null=True)
    jumlah = models.FloatField(blank=True, null=True)
    usernya = models.CharField(db_column='Usernya', max_length=20, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(max_length=1, blank=True, null=True)
    tglmasuk = models.CharField(max_length=10, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    barcode = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Lot_Masuk'


class TLotMasuk2(models.Model):
    kdlot = models.CharField(max_length=10)
    no_transaksi = models.CharField(max_length=15, blank=True, null=True)
    kode_barang = models.CharField(db_column='kode_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    jenis_barang = models.CharField(max_length=15, blank=True, null=True)
    jumlah = models.FloatField(blank=True, null=True)
    usernya = models.CharField(db_column='Usernya', max_length=20, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(max_length=1, blank=True, null=True)
    tglmasuk = models.CharField(max_length=10, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    barcode = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Lot_Masuk_2'


class TLotKeluar2(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    no_keluar = models.CharField(db_column='No_Keluar', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kd_barang = models.CharField(db_column='Kd_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    kd_lot = models.CharField(db_column='Kd_Lot', max_length=150)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=100)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=100, blank=True, null=True)  # Field name made lowercase.
    barcode = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Lot_keluar_2'


class TMinggu(models.Model):
    minggu = models.AutoField(primary_key=True)
    statusnya = models.CharField(max_length=1)
    rdp = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'T_Minggu'


class TMixing(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='Id')  # Field name made lowercase.
    kd_mixing = models.CharField(db_column='Kd_Mixing', max_length=20)  # Field name made lowercase.
    kd_resep = models.CharField(db_column='kd_Resep', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item = models.CharField(db_column='Item', max_length=20)  # Field name made lowercase.
    qty = models.CharField(db_column='Qty', max_length=20)  # Field name made lowercase.
    kdweihing = models.CharField(db_column='KdWeihing', max_length=20)  # Field name made lowercase.
    operator = models.CharField(db_column='Operator', max_length=20)  # Field name made lowercase.
    tglmixing = models.CharField(db_column='tglMixing', max_length=20)  # Field name made lowercase.
    waktu = models.CharField(max_length=20, blank=True, null=True)
    tglmasuk = models.CharField(db_column='Tglmasuk', max_length=10)  # Field name made lowercase.
    usernya = models.CharField(max_length=20)
    statusnya = models.CharField(max_length=1)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=20, blank=True, null=True)
    mesin = models.CharField(db_column='Mesin', max_length=10, blank=True, null=True)  # Field name made lowercase.
    batch = models.CharField(db_column='Batch', max_length=10, blank=True, null=True)  # Field name made lowercase.
    proses = models.CharField(max_length=1)
    hold = models.CharField(db_column='Hold', max_length=1, blank=True, null=True)  # Field name made lowercase.
    tglqc = models.CharField(max_length=10, blank=True, null=True)
    tglhold = models.CharField(max_length=10, blank=True, null=True)
    bacttot = models.DecimalField(db_column='BactTot', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qtot = models.DecimalField(db_column='Qtot', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    tglexp = models.CharField(max_length=10, blank=True, null=True)
    idjatwal = models.CharField(max_length=8, blank=True, null=True)
    idprint = models.CharField(max_length=20, blank=True, null=True)
    lewat = models.CharField(max_length=1)
    usrtimbang = models.CharField(db_column='UsrTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jamtimbang = models.CharField(db_column='JamTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tgltimbang = models.CharField(db_column='TglTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    userqc = models.CharField(db_column='UserQC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    terpakai = models.CharField(max_length=1)
    jenis = models.CharField(max_length=20, blank=True, null=True)
    qty_adjusment = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    chamtemp = models.CharField(db_column='ChamTemp', max_length=9)  # Field name made lowercase.
    tempwaterin = models.CharField(db_column='TempWaterIN', max_length=9)  # Field name made lowercase.
    fwpressure = models.CharField(db_column='FWPressure', max_length=9)  # Field name made lowercase.
    watflowrate = models.CharField(db_column='WatFlowRate', max_length=9)  # Field name made lowercase.
    palet = models.CharField(db_column='Palet', max_length=9)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Mixing'


class TMixingKd2(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='Id')  # Field name made lowercase.
    kd_mixing = models.CharField(db_column='Kd_Mixing', max_length=20)  # Field name made lowercase.
    kd_resep = models.CharField(db_column='kd_Resep', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item = models.CharField(db_column='Item', max_length=20)  # Field name made lowercase.
    qty = models.CharField(db_column='Qty', max_length=20)  # Field name made lowercase.
    kdweihing = models.CharField(db_column='KdWeihing', max_length=20)  # Field name made lowercase.
    operator = models.CharField(db_column='Operator', max_length=20)  # Field name made lowercase.
    tglmixing = models.CharField(db_column='tglMixing', max_length=20)  # Field name made lowercase.
    waktu = models.CharField(max_length=20, blank=True, null=True)
    tglmasuk = models.CharField(db_column='Tglmasuk', max_length=10)  # Field name made lowercase.
    usernya = models.CharField(max_length=20)
    statusnya = models.CharField(max_length=1)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=20, blank=True, null=True)
    mesin = models.CharField(db_column='Mesin', max_length=10, blank=True, null=True)  # Field name made lowercase.
    batch = models.CharField(db_column='Batch', max_length=10, blank=True, null=True)  # Field name made lowercase.
    proses = models.CharField(max_length=1)
    hold = models.CharField(db_column='Hold', max_length=1, blank=True, null=True)  # Field name made lowercase.
    tglqc = models.CharField(max_length=10, blank=True, null=True)
    tglhold = models.CharField(max_length=10, blank=True, null=True)
    bacttot = models.DecimalField(db_column='BactTot', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qtot = models.DecimalField(db_column='Qtot', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    tglexp = models.CharField(max_length=10, blank=True, null=True)
    idjatwal = models.CharField(max_length=8, blank=True, null=True)
    idprint = models.CharField(max_length=20, blank=True, null=True)
    lewat = models.CharField(max_length=1)
    usrtimbang = models.CharField(db_column='UsrTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jamtimbang = models.CharField(db_column='JamTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tgltimbang = models.CharField(db_column='TglTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    userqc = models.CharField(db_column='UserQC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    terpakai = models.CharField(max_length=1)
    jenis = models.CharField(max_length=20, blank=True, null=True)
    qty_adjusment = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Mixing_kd2'


class TMixingKd2Hist(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='Id')  # Field name made lowercase.
    kd_mixing = models.CharField(db_column='Kd_Mixing', max_length=20)  # Field name made lowercase.
    kd_resep = models.CharField(db_column='kd_Resep', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item = models.CharField(db_column='Item', max_length=20)  # Field name made lowercase.
    qty = models.CharField(db_column='Qty', max_length=20)  # Field name made lowercase.
    kdweihing = models.CharField(db_column='KdWeihing', max_length=20)  # Field name made lowercase.
    operator = models.CharField(db_column='Operator', max_length=20)  # Field name made lowercase.
    tglmixing = models.CharField(db_column='tglMixing', max_length=20)  # Field name made lowercase.
    waktu = models.CharField(max_length=20, blank=True, null=True)
    tglmasuk = models.CharField(db_column='Tglmasuk', max_length=10)  # Field name made lowercase.
    usernya = models.CharField(max_length=20)
    statusnya = models.CharField(max_length=1)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=20, blank=True, null=True)
    mesin = models.CharField(db_column='Mesin', max_length=10, blank=True, null=True)  # Field name made lowercase.
    batch = models.CharField(db_column='Batch', max_length=10, blank=True, null=True)  # Field name made lowercase.
    proses = models.CharField(max_length=1)
    hold = models.CharField(db_column='Hold', max_length=1, blank=True, null=True)  # Field name made lowercase.
    tglqc = models.CharField(max_length=10, blank=True, null=True)
    tglhold = models.CharField(max_length=10, blank=True, null=True)
    bacttot = models.DecimalField(db_column='BactTot', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qtot = models.DecimalField(db_column='Qtot', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    tglexp = models.CharField(max_length=10, blank=True, null=True)
    idjatwal = models.CharField(max_length=8, blank=True, null=True)
    idprint = models.CharField(max_length=20, blank=True, null=True)
    lewat = models.CharField(max_length=1)
    usrtimbang = models.CharField(db_column='UsrTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jamtimbang = models.CharField(db_column='JamTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tgltimbang = models.CharField(db_column='TglTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    userqc = models.CharField(db_column='UserQC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    terpakai = models.CharField(max_length=1)
    jenis = models.CharField(max_length=20, blank=True, null=True)
    qty_adjusment = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Mixing_kd2_hist'


class TPo(models.Model):
    ponumber = models.CharField(db_column='PoNumber', max_length=20)  # Field name made lowercase.
    podate = models.CharField(db_column='PODate', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kd_supplier = models.CharField(db_column='Kd_Supplier', max_length=20)  # Field name made lowercase.
    kd_barang = models.CharField(max_length=15)
    qty_in = models.DecimalField(db_column='Qty_in', max_digits=18, decimal_places=0)  # Field name made lowercase.
    qty_out = models.DecimalField(db_column='Qty_Out', max_digits=18, decimal_places=0)  # Field name made lowercase.
    amount_in = models.DecimalField(db_column='Amount_in', max_digits=18, decimal_places=0)  # Field name made lowercase.
    amount_out = models.DecimalField(db_column='Amount_Out', max_digits=18, decimal_places=0)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglin = models.DateTimeField(db_column='TglIn')  # Field name made lowercase.
    user_in = models.CharField(db_column='User_in', max_length=20)  # Field name made lowercase.
    user_edit = models.CharField(db_column='User_Edit', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tgledit = models.DateTimeField(db_column='TglEdit', blank=True, null=True)  # Field name made lowercase.
    selesai = models.CharField(db_column='Selesai', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_PO'


class TPoLog(models.Model):
    ponumber = models.CharField(db_column='PoNumber', max_length=20)  # Field name made lowercase.
    podate = models.CharField(db_column='PODate', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kd_supplier = models.CharField(db_column='Kd_Supplier', max_length=20)  # Field name made lowercase.
    kd_barang = models.CharField(max_length=15)
    qty_in = models.DecimalField(db_column='Qty_in', max_digits=18, decimal_places=0)  # Field name made lowercase.
    qty_out = models.DecimalField(db_column='Qty_Out', max_digits=18, decimal_places=0)  # Field name made lowercase.
    amount_in = models.DecimalField(db_column='Amount_in', max_digits=18, decimal_places=0)  # Field name made lowercase.
    amount_out = models.DecimalField(db_column='Amount_Out', max_digits=18, decimal_places=0)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    tglin = models.DateTimeField(db_column='TglIn')  # Field name made lowercase.
    user_in = models.CharField(db_column='User_in', max_length=20)  # Field name made lowercase.
    user_edit = models.CharField(db_column='User_Edit', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tgledit = models.DateTimeField(db_column='TglEdit', blank=True, null=True)  # Field name made lowercase.
    selesai = models.CharField(db_column='Selesai', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_PO_log'


class TPidandahPallet(models.Model):
    pallet_l = models.CharField(db_column='Pallet_L', max_length=5)  # Field name made lowercase.
    pallet_b = models.CharField(db_column='Pallet_B', max_length=5)  # Field name made lowercase.
    qty = models.FloatField()
    usernya = models.CharField(max_length=50)
    tglmasuk = models.CharField(max_length=10)
    status = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'T_Pidandah_pallet'


class TPrintBarcode(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=30)  # Field name made lowercase.
    lot_sup = models.CharField(db_column='Lot_sup', max_length=30)  # Field name made lowercase.
    barcode = models.CharField(max_length=30)
    nama = models.CharField(max_length=35, blank=True, null=True)
    nmsup = models.CharField(db_column='NmSup', max_length=100, blank=True, null=True)  # Field name made lowercase.
    suratjalan = models.CharField(db_column='SuratJalan', max_length=30, blank=True, null=True)  # Field name made lowercase.
    barcode_asli = models.CharField(db_column='Barcode_Asli', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Print_Barcode'


class TQr(models.Model):
    id = models.TextField(primary_key=True)
    produk = models.TextField(blank=True, null=True)
    qrc = models.TextField(db_column='QrC', blank=True, null=True)  # Field name made lowercase.
    qr = models.BinaryField(db_column='QR', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_QR'


class TRmtBox(models.Model):
    no = models.CharField(db_column='No', max_length=2)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_RMT_Box'


class TRptActualCostHapus(models.Model):
    id = models.AutoField(primary_key=True,db_column='ID')  # Field name made lowercase.
    kd_barang = models.CharField(db_column='KD_BARANG', max_length=20, blank=True, null=True)  # Field name made lowercase.
    t_date = models.DateTimeField(db_column='T_DATE', blank=True, null=True)  # Field name made lowercase.
    update_timestamp = models.DateTimeField(db_column='UPDATE_TIMESTAMP', blank=True, null=True)  # Field name made lowercase.
    update_user = models.CharField(db_column='UPDATE_USER', max_length=20, blank=True, null=True)  # Field name made lowercase.
    update_status = models.CharField(db_column='UPDATE_STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.
    amt_1 = models.DecimalField(db_column='AMT_1', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    qty_1 = models.DecimalField(db_column='QTY_1', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    amt_2 = models.DecimalField(db_column='AMT_2', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    qty_2 = models.DecimalField(db_column='QTY_2', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    amt_3 = models.DecimalField(db_column='AMT_3', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    qty_3 = models.DecimalField(db_column='QTY_3', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    amt_4 = models.DecimalField(db_column='AMT_4', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    qty_4 = models.DecimalField(db_column='QTY_4', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    amt_5 = models.DecimalField(db_column='AMT_5', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    qty_5 = models.DecimalField(db_column='QTY_5', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_RPT_ACTUAL_COST_hapus'


class TRptComparesHapus(models.Model):
    id = models.AutoField(primary_key=True,db_column='ID')  # Field name made lowercase.
    t_date = models.DateTimeField(db_column='T_DATE', blank=True, null=True)  # Field name made lowercase.
    kd_barang = models.CharField(db_column='KD_BARANG', max_length=20, blank=True, null=True)  # Field name made lowercase.
    end_bal = models.DecimalField(db_column='END_BAL', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    take_seiwa = models.DecimalField(db_column='TAKE_SEIWA', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    take_ttlc = models.DecimalField(db_column='TAKE_TTLC', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    diff = models.DecimalField(db_column='DIFF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    update_time = models.DateTimeField(db_column='UPDATE_TIME', blank=True, null=True)  # Field name made lowercase.
    update_user = models.CharField(db_column='UPDATE_USER', max_length=20, blank=True, null=True)  # Field name made lowercase.
    update_status = models.CharField(db_column='UPDATE_STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_RPT_COMPARES_hapus'


class TRptDirectMtrWeeklyHapus(models.Model):
    id = models.AutoField(primary_key=True,db_column='ID')  # Field name made lowercase.
    kode_barang = models.CharField(db_column='KODE_BARANG', max_length=20, blank=True, null=True)  # Field name made lowercase.
    nama_barang = models.CharField(db_column='NAMA_BARANG', max_length=50, blank=True, null=True)  # Field name made lowercase.
    jenis_barang = models.CharField(db_column='JENIS_BARANG', max_length=50, blank=True, null=True)  # Field name made lowercase.
    transact_year = models.IntegerField(db_column='TRANSACT_YEAR', blank=True, null=True)  # Field name made lowercase.
    transact_month = models.IntegerField(db_column='TRANSACT_MONTH', blank=True, null=True)  # Field name made lowercase.
    update_timestamp = models.DateTimeField(db_column='UPDATE_TIMESTAMP', blank=True, null=True)  # Field name made lowercase.
    update_user = models.CharField(db_column='UPDATE_USER', max_length=50, blank=True, null=True)  # Field name made lowercase.
    update_status = models.CharField(db_column='UPDATE_STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.
    in_1 = models.DecimalField(db_column='IN_1', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_1 = models.DecimalField(db_column='OUT_1', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_2 = models.DecimalField(db_column='IN_2', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_2 = models.DecimalField(db_column='OUT_2', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_3 = models.DecimalField(db_column='IN_3', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_3 = models.DecimalField(db_column='OUT_3', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_4 = models.DecimalField(db_column='IN_4', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_4 = models.DecimalField(db_column='OUT_4', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_5 = models.DecimalField(db_column='IN_5', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_5 = models.DecimalField(db_column='OUT_5', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_6 = models.DecimalField(db_column='IN_6', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_6 = models.DecimalField(db_column='OUT_6', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_7 = models.DecimalField(db_column='IN_7', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_7 = models.DecimalField(db_column='OUT_7', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_8 = models.DecimalField(db_column='IN_8', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_8 = models.DecimalField(db_column='OUT_8', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_9 = models.DecimalField(db_column='IN_9', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_9 = models.DecimalField(db_column='OUT_9', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_10 = models.DecimalField(db_column='IN_10', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_10 = models.DecimalField(db_column='OUT_10', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_11 = models.DecimalField(db_column='IN_11', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_11 = models.DecimalField(db_column='OUT_11', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_12 = models.DecimalField(db_column='IN_12', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_12 = models.DecimalField(db_column='OUT_12', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_13 = models.DecimalField(db_column='IN_13', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_13 = models.DecimalField(db_column='OUT_13', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_14 = models.DecimalField(db_column='IN_14', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_14 = models.DecimalField(db_column='OUT_14', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_15 = models.DecimalField(db_column='IN_15', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_15 = models.DecimalField(db_column='OUT_15', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_16 = models.DecimalField(db_column='IN_16', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_16 = models.DecimalField(db_column='OUT_16', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_17 = models.DecimalField(db_column='IN_17', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_17 = models.DecimalField(db_column='OUT_17', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_18 = models.DecimalField(db_column='IN_18', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_18 = models.DecimalField(db_column='OUT_18', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_19 = models.DecimalField(db_column='IN_19', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_19 = models.DecimalField(db_column='OUT_19', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_20 = models.DecimalField(db_column='IN_20', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_20 = models.DecimalField(db_column='OUT_20', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_21 = models.DecimalField(db_column='IN_21', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_21 = models.DecimalField(db_column='OUT_21', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_22 = models.DecimalField(db_column='IN_22', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_22 = models.DecimalField(db_column='OUT_22', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_23 = models.DecimalField(db_column='IN_23', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_23 = models.DecimalField(db_column='OUT_23', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_24 = models.DecimalField(db_column='IN_24', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_24 = models.DecimalField(db_column='OUT_24', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_25 = models.DecimalField(db_column='IN_25', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_25 = models.DecimalField(db_column='OUT_25', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_26 = models.DecimalField(db_column='IN_26', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_26 = models.DecimalField(db_column='OUT_26', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_27 = models.DecimalField(db_column='IN_27', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_27 = models.DecimalField(db_column='OUT_27', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_28 = models.DecimalField(db_column='IN_28', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_28 = models.DecimalField(db_column='OUT_28', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_29 = models.DecimalField(db_column='IN_29', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_29 = models.DecimalField(db_column='OUT_29', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_30 = models.DecimalField(db_column='IN_30', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_30 = models.DecimalField(db_column='OUT_30', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_31 = models.DecimalField(db_column='IN_31', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_31 = models.DecimalField(db_column='OUT_31', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_RPT_DIRECT_MTR_WEEKLY_hapus'


class TRptMonthlyHapus(models.Model):
    id = models.AutoField(primary_key=True,db_column='ID')  # Field name made lowercase.
    kd_barang = models.CharField(db_column='KD_BARANG', max_length=20, blank=True, null=True)  # Field name made lowercase.
    t_date = models.DateTimeField(db_column='T_DATE', blank=True, null=True)  # Field name made lowercase.
    update_timestamp = models.DateTimeField(db_column='UPDATE_TIMESTAMP', blank=True, null=True)  # Field name made lowercase.
    update_user = models.CharField(db_column='UPDATE_USER', max_length=20, blank=True, null=True)  # Field name made lowercase.
    update_status = models.CharField(db_column='UPDATE_STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.
    in_1 = models.DecimalField(db_column='IN_1', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_1 = models.DecimalField(db_column='OUT_1', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_2 = models.DecimalField(db_column='IN_2', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_2 = models.DecimalField(db_column='OUT_2', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_3 = models.DecimalField(db_column='IN_3', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_3 = models.DecimalField(db_column='OUT_3', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_4 = models.DecimalField(db_column='IN_4', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_4 = models.DecimalField(db_column='OUT_4', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_5 = models.DecimalField(db_column='IN_5', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_5 = models.DecimalField(db_column='OUT_5', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    adj = models.DecimalField(db_column='ADJ', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_RPT_MONTHLY_hapus'


class TRptVarianceHapus(models.Model):
    id = models.AutoField(primary_key=True,db_column='ID')  # Field name made lowercase.
    kd_barang = models.CharField(db_column='KD_BARANG', max_length=20, blank=True, null=True)  # Field name made lowercase.
    t_date = models.DateTimeField(db_column='T_DATE', blank=True, null=True)  # Field name made lowercase.
    open_bal = models.DecimalField(db_column='OPEN_BAL', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    inc_actual = models.DecimalField(db_column='INC_ACTUAL', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    inc_std_cost = models.DecimalField(db_column='INC_STD_COST', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    inc_var = models.DecimalField(db_column='INC_VAR', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    out_std = models.DecimalField(db_column='OUT_STD', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    adj_cost = models.DecimalField(db_column='ADJ_COST', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    end_bal = models.DecimalField(db_column='END_BAL', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='REMARKS', max_length=50, blank=True, null=True)  # Field name made lowercase.
    update_time = models.DateTimeField(db_column='UPDATE_TIME', blank=True, null=True)  # Field name made lowercase.
    update_user = models.CharField(db_column='UPDATE_USER', max_length=50, blank=True, null=True)  # Field name made lowercase.
    update_status = models.CharField(db_column='UPDATE_STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_RPT_VARIANCE_hapus'


class TSumDailyMtr(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID')  # Field name made lowercase.
    kode = models.CharField(db_column='KODE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    transact_date = models.DateTimeField(db_column='TRANSACT_DATE', blank=True, null=True)  # Field name made lowercase.
    week_num = models.IntegerField(db_column='WEEK_NUM', blank=True, null=True)  # Field name made lowercase.
    sum_daily = models.DecimalField(db_column='SUM_DAILY', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    update_timestamp = models.DateTimeField(db_column='UPDATE_TIMESTAMP', blank=True, null=True)  # Field name made lowercase.
    update_user = models.CharField(db_column='UPDATE_USER', max_length=50, blank=True, null=True)  # Field name made lowercase.
    update_status = models.CharField(db_column='UPDATE_STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_SUM_DAILY_MTR'


class TSemProduksi(models.Model):
    mesin = models.CharField(max_length=10, blank=True, null=True)
    groupnya = models.CharField(max_length=3, blank=True, null=True)
    resep = models.CharField(max_length=15, blank=True, null=True)
    bacth = models.CharField(max_length=10, blank=True, null=True)
    barcodeasli1 = models.CharField(max_length=120, blank=True, null=True)
    barcodeasli2 = models.CharField(max_length=120, blank=True, null=True)
    qty1 = models.CharField(max_length=10, blank=True, null=True)
    qty2 = models.CharField(max_length=10, blank=True, null=True)
    totbacth = models.CharField(db_column='Totbacth', max_length=15, blank=True, null=True)  # Field name made lowercase.
    nourut = models.CharField(db_column='noUrut', max_length=10, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(max_length=10, blank=True, null=True)
    nmresep = models.CharField(max_length=115, blank=True, null=True)
    tgl = models.CharField(max_length=10, blank=True, null=True)
    waktu = models.CharField(max_length=10, blank=True, null=True)
    kdbarangutama = models.CharField(max_length=10, blank=True, null=True)
    qtystd = models.CharField(max_length=10, blank=True, null=True)
    putaran = models.CharField(max_length=10, blank=True, null=True)
    printnya = models.CharField(max_length=1, blank=True, null=True)
    bpb = models.CharField(max_length=20, blank=True, null=True)
    brg2 = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_Sem_produksi'


class TStocktakeA(models.Model):
    kodebarang = models.CharField(db_column='Kodebarang', max_length=10)  # Field name made lowercase.
    th = models.CharField(max_length=4)
    bln = models.CharField(max_length=2)
    seiwa = models.DecimalField(max_digits=19, decimal_places=4)
    ttlc = models.DecimalField(max_digits=19, decimal_places=4)
    tglmasuk = models.CharField(max_length=10)
    usernya = models.CharField(max_length=20)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=20, blank=True, null=True)
    statusnya = models.CharField(max_length=1)
    rdp = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'T_Stocktake_A'


class TTerusTimbang(models.Model):
    mesin = models.CharField(max_length=10)
    groupnya = models.CharField(max_length=10)
    resepnya = models.CharField(max_length=20)
    batch = models.CharField(db_column='Batch', max_length=10)  # Field name made lowercase.
    totbatch = models.CharField(db_column='Totbatch', max_length=10)  # Field name made lowercase.
    gridrow = models.CharField(db_column='Gridrow', max_length=10)  # Field name made lowercase.
    totbatchsambung = models.CharField(db_column='TotbatchSambung', max_length=10)  # Field name made lowercase.
    putaran = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'T_Terus_Timbang'


class TAfterS(models.Model):
    kdmix = models.CharField(max_length=20)
    qty = models.DecimalField(max_digits=19, decimal_places=4)

    class Meta:
        managed = False
        db_table = 'T_after_S'


class THisBarcodeRm(models.Model):
    barcoderm = models.CharField(db_column='barcodeRM', max_length=50)  # Field name made lowercase.
    barcodeasli = models.CharField(max_length=100)
    tanggal = models.DateTimeField()
    usernya = models.CharField(max_length=50)
    qty = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'T_his_Barcode_RM'


class THisBarcodeRmLama1(models.Model):
    barcoderm = models.CharField(db_column='barcodeRM', max_length=50)  # Field name made lowercase.
    barcodeasli = models.CharField(max_length=100)
    tanggal = models.DateTimeField()
    usernya = models.CharField(max_length=50)
    qty = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'T_his_Barcode_RM_lama1'


class THisJatwalsc(models.Model):
    idnya = models.BigAutoField(primary_key=True)
    keynya = models.CharField(db_column='KeyNya', max_length=75)  # Field name made lowercase.
    codenya = models.CharField(db_column='CodeNya', max_length=5)  # Field name made lowercase.
    thicknya = models.CharField(db_column='Thicknya', max_length=10)  # Field name made lowercase.
    widthnya = models.CharField(db_column='Widthnya', max_length=10)  # Field name made lowercase.
    lengthnya = models.CharField(db_column='Lengthnya', max_length=10)  # Field name made lowercase.
    qtynya = models.CharField(db_column='Qtynya', max_length=10)  # Field name made lowercase.
    fromnya = models.CharField(db_column='FromNya', max_length=10)  # Field name made lowercase.
    tonya = models.CharField(db_column='Tonya', max_length=10)  # Field name made lowercase.
    minnya = models.CharField(db_column='Minnya', max_length=10)  # Field name made lowercase.
    weightnya = models.CharField(db_column='Weightnya', max_length=10)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    waktuupload = models.CharField(db_column='waktuUpload', max_length=20)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=20)  # Field name made lowercase.
    stjatwal = models.CharField(max_length=1)
    stuser = models.CharField(db_column='StUser', max_length=20, blank=True, null=True)  # Field name made lowercase.
    remil = models.CharField(db_column='Remil', max_length=1, blank=True, null=True)  # Field name made lowercase.
    selesai = models.CharField(db_column='Selesai', max_length=10, blank=True, null=True)  # Field name made lowercase.
    untuk = models.CharField(max_length=30, blank=True, null=True)
    mesin = models.CharField(max_length=10, blank=True, null=True)
    idasal = models.BigIntegerField(blank=True, null=True)
    tgltarik = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_his_JatwalSc'


class THistBarangProduksiDAudit(models.Model):
    no_produksi = models.CharField(db_column='No_Produksi', max_length=20)  # Field name made lowercase.
    no_keluar = models.CharField(db_column='No_Keluar', max_length=15)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='Kode_Barang', max_length=35, blank=True, null=True)  # Field name made lowercase.
    jumlah = models.FloatField(db_column='Jumlah')  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=1)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=15)  # Field name made lowercase.
    tglkeluar = models.CharField(db_column='TglKeluar', max_length=10, blank=True, null=True)  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.
    jlmresep = models.CharField(max_length=10, blank=True, null=True)
    barangdua = models.CharField(max_length=20, blank=True, null=True)
    barcodecampuran = models.CharField(db_column='BarcodeCampuran', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kdbrgcampuran = models.CharField(db_column='KdBrgCampuran', max_length=35, blank=True, null=True)  # Field name made lowercase.
    waktu = models.CharField(max_length=20, blank=True, null=True)
    namarsp = models.CharField(db_column='NamaRsp', max_length=100, blank=True, null=True)  # Field name made lowercase.
    lot_sup = models.CharField(max_length=100, blank=True, null=True)
    kode_sup = models.CharField(max_length=100, blank=True, null=True)
    asal = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_hist_Barang_Produksi_D_audit'


class TPrintProduksi(models.Model):
    idnya = models.BigAutoField(primary_key=True, db_column='IdNya')  # Field name made lowercase.
    kdtimbang = models.CharField(max_length=20, blank=True, null=True)
    kdresep = models.CharField(max_length=20, blank=True, null=True)
    nmresep = models.CharField(max_length=50, blank=True, null=True)
    totalbatch = models.CharField(max_length=10, blank=True, null=True)
    batch = models.CharField(max_length=10, blank=True, null=True)
    tglcompounding = models.CharField(max_length=30, blank=True, null=True)
    usernya = models.CharField(max_length=20, blank=True, null=True)
    itemgroup = models.CharField(max_length=10, blank=True, null=True)
    kdbarang = models.CharField(max_length=35, blank=True, null=True)
    qtybarang = models.CharField(max_length=10, blank=True, null=True)
    stdqty = models.CharField(max_length=10, blank=True, null=True)
    statusnya = models.CharField(max_length=1)
    waktu = models.CharField(max_length=20, blank=True, null=True)
    nourut = models.CharField(db_column='NoUrut', max_length=2, blank=True, null=True)  # Field name made lowercase.
    terpakai = models.CharField(max_length=10, blank=True, null=True)
    proses = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'T_print_produksi'


class Tabletutup(models.Model):
    no = models.CharField(max_length=10, blank=True, null=True)
    kodebarang = models.CharField(max_length=200, blank=True, null=True)
    nama = models.CharField(max_length=200, blank=True, null=True)
    us = models.CharField(max_length=100, blank=True, null=True)
    rp = models.CharField(max_length=100, blank=True, null=True)
    qty = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Tabletutup'


class ZTesTriger(models.Model):
    idd = models.CharField(max_length=50, blank=True, null=True)
    nama = models.CharField(max_length=50, blank=True, null=True)
    kkk = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Z_tes_triger'


class Aatiga(models.Model):
    f1 = models.CharField(db_column='F1', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'aatiga'


class Dtproperties(models.Model):
    objectid = models.IntegerField(blank=True, null=True)
    property = models.CharField(max_length=64)
    value = models.CharField(max_length=255, blank=True, null=True)
    uvalue = models.CharField(max_length=255, blank=True, null=True)
    lvalue = models.BinaryField(blank=True, null=True)
    version = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'dtproperties'
        unique_together = (('id', 'property'),)


class ExpSbsc(models.Model):
    kdresep = models.CharField(max_length=255, blank=True, null=True)
    nama_resep = models.CharField(db_column='nama resep', max_length=255, blank=True, null=True)  # Field renamed to remove unsuitable characters.
    hari_exp = models.FloatField(db_column='hari EXP', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'exp_SBSC'


class ExpSbsm(models.Model):
    kdresep = models.CharField(max_length=255, blank=True, null=True)
    nama_resep = models.CharField(db_column='nama resep', max_length=255, blank=True, null=True)  # Field renamed to remove unsuitable characters.
    hari_exp = models.FloatField(db_column='hari EXP', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'exp_SBSM'


class Expmix(models.Model):
    kdresep = models.CharField(max_length=255, blank=True, null=True)
    namaresep = models.CharField(max_length=255, blank=True, null=True)
    exp = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'expmix'


class HistTabelTutupbuku(models.Model):
    kode_barang = models.CharField(max_length=50)
    tahun = models.CharField(max_length=4, blank=True, null=True)
    bulan = models.CharField(max_length=2, blank=True, null=True)
    qty = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    stock_rp = models.DecimalField(db_column='Stock_rp', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    stock_us = models.DecimalField(db_column='Stock_Us', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    rate = models.DecimalField(db_column='Rate', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(max_length=30, blank=True, null=True)
    tgl_tutup = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    useredit = models.CharField(max_length=30, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    kode_gudang = models.CharField(max_length=10, blank=True, null=True)
    amount = models.DecimalField(db_column='Amount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qty_ak = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hist_tabel_tutupbuku'


class MBarcode(models.Model):
    barcode = models.CharField(db_column='BARCODE', max_length=10)  # Field name made lowercase.
    terpakai = models.CharField(db_column='TERPAKAI', max_length=1)  # Field name made lowercase.
    barcodeasli = models.CharField(db_column='BARCODEASLI', max_length=20, blank=True, null=True)  # Field name made lowercase.
    no_transaksi = models.CharField(db_column='NO_TRANSAKSI', max_length=20, blank=True, null=True)  # Field name made lowercase.
    no_keluar = models.CharField(db_column='No_Keluar', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kd_barang = models.CharField(max_length=35, blank=True, null=True)
    no_lot = models.CharField(db_column='No_Lot', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jlmbarang = models.DecimalField(max_digits=19, decimal_places=4)
    wip = models.CharField(db_column='WIP', max_length=1, blank=True, null=True)  # Field name made lowercase.
    qrc = models.BinaryField(db_column='QrC', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'm_barcode'


class MBarcode2018(models.Model):
    barcode = models.CharField(db_column='BARCODE', max_length=10)  # Field name made lowercase.
    terpakai = models.CharField(db_column='TERPAKAI', max_length=1)  # Field name made lowercase.
    barcodeasli = models.CharField(db_column='BARCODEASLI', max_length=20, blank=True, null=True)  # Field name made lowercase.
    no_transaksi = models.CharField(db_column='NO_TRANSAKSI', max_length=20, blank=True, null=True)  # Field name made lowercase.
    no_keluar = models.CharField(db_column='No_Keluar', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kd_barang = models.CharField(max_length=35, blank=True, null=True)
    no_lot = models.CharField(db_column='No_Lot', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jlmbarang = models.DecimalField(max_digits=19, decimal_places=4)
    wip = models.CharField(db_column='WIP', max_length=1, blank=True, null=True)  # Field name made lowercase.
    qrc = models.BinaryField(db_column='QrC', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'm_barcode2018'


class MBarcode2019(models.Model):
    barcode = models.CharField(db_column='BARCODE', max_length=10)  # Field name made lowercase.
    terpakai = models.CharField(db_column='TERPAKAI', max_length=1)  # Field name made lowercase.
    barcodeasli = models.CharField(db_column='BARCODEASLI', max_length=20, blank=True, null=True)  # Field name made lowercase.
    no_transaksi = models.CharField(db_column='NO_TRANSAKSI', max_length=20, blank=True, null=True)  # Field name made lowercase.
    no_keluar = models.CharField(db_column='No_Keluar', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kd_barang = models.CharField(max_length=35, blank=True, null=True)
    no_lot = models.CharField(db_column='No_Lot', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jlmbarang = models.DecimalField(max_digits=19, decimal_places=4)
    wip = models.CharField(db_column='WIP', max_length=1, blank=True, null=True)  # Field name made lowercase.
    qrc = models.BinaryField(db_column='QrC', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'm_barcode2019'


class MResepC(models.Model):
    itemno = models.CharField(max_length=255, blank=True, null=True)
    cn1 = models.CharField(max_length=255, blank=True, null=True)
    cq1 = models.FloatField(blank=True, null=True)
    cn2 = models.CharField(max_length=255, blank=True, null=True)
    c2q = models.FloatField(blank=True, null=True)
    cn3 = models.CharField(max_length=255, blank=True, null=True)
    cq3 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'm_resep_C'


class MResepRmt(models.Model):
    no_karet = models.CharField(db_column='No_karet', max_length=20)  # Field name made lowercase.
    berat_max = models.DecimalField(db_column='Berat_Max', max_digits=19, decimal_places=4)  # Field name made lowercase.
    tglmasuk = models.CharField(max_length=10)
    usernya = models.CharField(max_length=20)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'm_resep_RMT'


class MResepBackup(models.Model):
    kdresep = models.CharField(db_column='KdResep', max_length=15, blank=True, null=True)  # Field name made lowercase.
    namaresep = models.CharField(db_column='NamaResep', max_length=30, blank=True, null=True)  # Field name made lowercase.
    kdbarang = models.CharField(db_column='KdBarang', max_length=15, blank=True, null=True)  # Field name made lowercase.
    kdbarangcadangan = models.CharField(db_column='KdBarangCadangan', max_length=15, blank=True, null=True)  # Field name made lowercase.
    nourut = models.FloatField(db_column='NoUrut', blank=True, null=True)  # Field name made lowercase.
    jumlahbarang = models.FloatField(db_column='JumlahBarang', blank=True, null=True)  # Field name made lowercase.
    lebih = models.FloatField(blank=True, null=True)
    kurang = models.FloatField(blank=True, null=True)
    status = models.CharField(db_column='Status', max_length=1, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(max_length=20, blank=True, null=True)
    tglmasuk = models.CharField(max_length=10, blank=True, null=True)
    tgledit = models.CharField(max_length=19, blank=True, null=True)
    groupresep = models.CharField(db_column='GroupResep', max_length=3, blank=True, null=True)  # Field name made lowercase.
    resep = models.CharField(db_column='Resep', max_length=20, blank=True, null=True)  # Field name made lowercase.
    fase = models.CharField(db_column='Fase', max_length=20, blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rb = models.CharField(db_column='RB', max_length=1, blank=True, null=True)  # Field name made lowercase.
    timbang = models.CharField(db_column='Timbang', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'm_resep_backup'


class MResepCalender2(models.Model):
    rubber = models.CharField(max_length=50, blank=True, null=True)
    thickness = models.FloatField(db_column='Thickness', blank=True, null=True)  # Field name made lowercase.
    width = models.FloatField(db_column='Width', blank=True, null=True)  # Field name made lowercase.
    sheecut = models.CharField(db_column='Sheecut', max_length=255, blank=True, null=True)  # Field name made lowercase.
    keynya = models.CharField(max_length=255, blank=True, null=True)
    itemno = models.CharField(max_length=255, blank=True, null=True)
    desc = models.CharField(max_length=255, blank=True, null=True)
    batch_size_length = models.CharField(db_column='Batch Size length', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    batch_size_unit = models.CharField(db_column='Batch Size unit', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_item_1 = models.CharField(db_column='Child Item 1', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_quantity_1 = models.FloatField(db_column='Child Quantity 1', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_item_2 = models.CharField(db_column='Child Item 2', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_quantity_2 = models.FloatField(db_column='Child Quantity 2', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_item_3 = models.CharField(db_column='Child Item 3', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_quantity_3 = models.FloatField(db_column='Child Quantity 3', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_item_4 = models.CharField(db_column='Child Item 4', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_quantity_4 = models.FloatField(db_column='Child Quantity 4', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_item_5 = models.CharField(db_column='Child Item 5', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    child_quantity_5 = models.FloatField(db_column='Child Quantity 5', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    statusnya = models.CharField(max_length=255, blank=True, null=True)
    exp = models.FloatField(db_column='Exp', blank=True, null=True)  # Field name made lowercase.
    sg = models.CharField(db_column='SG', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fc1 = models.CharField(max_length=1, blank=True, null=True)
    fc2 = models.CharField(max_length=1, blank=True, null=True)
    fc3 = models.CharField(max_length=1, blank=True, null=True)
    fc4 = models.CharField(max_length=1, blank=True, null=True)
    fc5 = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'm_resep_calender2'


class MResepOilAktif(models.Model):
    f1 = models.CharField(db_column='F1', max_length=255, blank=True, null=True)  # Field name made lowercase.
    f2 = models.CharField(db_column='F2', max_length=255, blank=True, null=True)  # Field name made lowercase.
    f3 = models.CharField(db_column='F3', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'm_resep_oil_aktif'


class MResepScrap(models.Model):
    seksi = models.CharField(max_length=20)
    kdresep = models.CharField(max_length=100)
    berat_box = models.DecimalField(db_column='Berat_Box', max_digits=19, decimal_places=4)  # Field name made lowercase.
    expr = models.CharField(max_length=2, blank=True, null=True)
    usernya = models.CharField(max_length=50, blank=True, null=True)
    tglmasuk = models.CharField(max_length=10, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'm_resep_scrap'


class MasterSubsection(models.Model):
    kode = models.CharField(max_length=12)
    seksi = models.CharField(max_length=5, blank=True, null=True)
    subsek = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'master_subsection'


class ResepMixingAktif(models.Model):
    kode = models.CharField(max_length=255, blank=True, null=True)
    aktif = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'resep_mixing_aktif'


class Roles(models.Model):
    id = models.BigIntegerField(primary_key=True, blank=True)
    nama_modul = models.CharField(max_length=255, blank=True, null=True)
    parent_modul = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    created_user = models.CharField(max_length=255, blank=True, null=True)
    updated_user = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roles'


class TBlockKonfirmasi(models.Model):
    usernya = models.CharField(max_length=10)
    tanggalnya = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 't_Block_Konfirmasi'


class TCalenderx(models.Model):
    kd_calender = models.CharField(db_column='kd_Calender', max_length=30, blank=True, null=True)  # Field name made lowercase.
    kd_mixing = models.CharField(db_column='kd_Mixing', max_length=30, blank=True, null=True)  # Field name made lowercase.
    item = models.CharField(db_column='Item', max_length=30, blank=True, null=True)  # Field name made lowercase.
    qtynya = models.CharField(max_length=30, blank=True, null=True)
    usernya = models.CharField(db_column='Usernya', max_length=25, blank=True, null=True)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jamnya = models.CharField(max_length=30, blank=True, null=True)
    stcal = models.CharField(max_length=20, blank=True, null=True)
    qtytot = models.CharField(max_length=30, blank=True, null=True)
    roolnya = models.CharField(db_column='RoolNya', max_length=30, blank=True, null=True)  # Field name made lowercase.
    nokaret = models.CharField(max_length=255, blank=True, null=True)
    totroll = models.CharField(db_column='TotRoll', max_length=30, blank=True, null=True)  # Field name made lowercase.
    panjang = models.CharField(db_column='Panjang', max_length=30, blank=True, null=True)  # Field name made lowercase.
    tglmixing = models.CharField(db_column='TglMixing', max_length=20, blank=True, null=True)  # Field name made lowercase.
    bacthmix = models.CharField(db_column='BacthMix', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rakno = models.CharField(db_column='RakNo', max_length=30, blank=True, null=True)  # Field name made lowercase.
    exp = models.CharField(max_length=20, blank=True, null=True)
    idjatwal = models.BigIntegerField(blank=True, null=True)
    terpakai = models.CharField(max_length=15, blank=True, null=True)
    mesin = models.CharField(max_length=50, blank=True, null=True)
    stdijatwal = models.CharField(max_length=5, blank=True, null=True)
    dis = models.CharField(max_length=50, blank=True, null=True)
    usere = models.CharField(max_length=30, blank=True, null=True)
    lebar = models.CharField(max_length=20, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    qcpas = models.CharField(db_column='QcPas', max_length=1)  # Field name made lowercase.
    hlodnya = models.CharField(max_length=1)
    qcuser = models.CharField(db_column='QCuser', max_length=10, blank=True, null=True)  # Field name made lowercase.
    qctgl = models.CharField(db_column='Qctgl', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_Calenderx'


class THistMixingPisah(models.Model):
    idpisah = models.BigAutoField(primary_key=True)
    idmixing = models.CharField(max_length=20)
    qtyp = models.DecimalField(max_digits=19, decimal_places=4)
    terpakai = models.CharField(max_length=1)
    usernyax = models.CharField(max_length=10, blank=True, null=True)
    tgl = models.DateTimeField(blank=True, null=True)
    qtyajusment = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_Hist_mixing_pisah'


class TRmt(models.Model):
    resep = models.CharField(db_column='Resep', max_length=10)  # Field name made lowercase.
    tglpro = models.CharField(db_column='TglPro', max_length=10)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty')  # Field name made lowercase.
    tglmasuk = models.CharField(max_length=10)
    usernya = models.CharField(max_length=20)
    kdrmt = models.CharField(db_column='kdRMT', max_length=20)  # Field name made lowercase.
    tglexp = models.CharField(max_length=10, blank=True, null=True)
    seksi = models.CharField(db_column='Seksi', max_length=100, blank=True, null=True)  # Field name made lowercase.
    tglcal = models.CharField(db_column='tglCal', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tglremil = models.CharField(max_length=10, blank=True, null=True)
    kdcalender = models.CharField(db_column='kdCalender', max_length=20, blank=True, null=True)  # Field name made lowercase.
    statusnya = models.CharField(max_length=1)
    terpakai = models.CharField(max_length=1)
    box = models.CharField(max_length=2, blank=True, null=True)
    lot = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_RMT'


class TBarangMasuk(models.Model):
    no_transaksi = models.CharField(db_column='No_Transaksi', max_length=15)  # Field name made lowercase.
    kode_sup = models.CharField(db_column='Kode_Sup', max_length=20)  # Field name made lowercase.
    no_nota_supp = models.CharField(db_column='No_Nota_Supp', max_length=18)  # Field name made lowercase.
    tanggal_pengiriman = models.DateTimeField(db_column='Tanggal_Pengiriman')  # Field name made lowercase.
    pengirim = models.CharField(db_column='Pengirim', max_length=50)  # Field name made lowercase.
    tglmasuk = models.CharField(db_column='TglMasuk', max_length=10)  # Field name made lowercase.
    tgledit = models.CharField(db_column='TglEdit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(db_column='Usernya', max_length=10)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    konfirmasi = models.CharField(db_column='Konfirmasi', max_length=1)  # Field name made lowercase.
    tglperiksa = models.CharField(db_column='TglPeriksa', max_length=10, blank=True, null=True)  # Field name made lowercase.
    no_surat_jalan = models.CharField(db_column='No_Surat_Jalan', max_length=30, blank=True, null=True)  # Field name made lowercase.
    keterangan = models.CharField(db_column='Keterangan', max_length=100, blank=True, null=True)  # Field name made lowercase.
    penerima = models.CharField(db_column='Penerima', max_length=20, blank=True, null=True)  # Field name made lowercase.
    mengetahui = models.CharField(db_column='Mengetahui', max_length=20, blank=True, null=True)  # Field name made lowercase.
    disetujui = models.CharField(db_column='Disetujui', max_length=20, blank=True, null=True)  # Field name made lowercase.
    qc = models.CharField(db_column='QC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tglproduksi = models.CharField(db_column='Tglproduksi', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_barang_masuk'


class TBarcodeRmCl(models.Model):
    barcode = models.CharField(db_column='BARCODE', max_length=10)  # Field name made lowercase.
    terpakai = models.CharField(db_column='TERPAKAI', max_length=1)  # Field name made lowercase.
    barcodeasli = models.CharField(db_column='BARCODEASLI', max_length=20, blank=True, null=True)  # Field name made lowercase.
    no_transaksi = models.CharField(db_column='NO_TRANSAKSI', max_length=20, blank=True, null=True)  # Field name made lowercase.
    no_keluar = models.CharField(db_column='No_Keluar', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kd_barang = models.CharField(max_length=20, blank=True, null=True)
    no_lot = models.CharField(db_column='No_Lot', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jlmbarang = models.DecimalField(max_digits=19, decimal_places=4)
    wip = models.CharField(db_column='WIP', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_barcode_rm_cl'


class TCalender(models.Model):
    kd_calender = models.CharField(db_column='kd_Calender', max_length=40, blank=True, null=True)  # Field name made lowercase.
    kd_mixing = models.TextField(db_column='kd_Mixing', blank=True, null=True)  # Field name made lowercase.
    item = models.TextField(db_column='Item', blank=True, null=True)  # Field name made lowercase.
    qtynya = models.TextField(blank=True, null=True)
    usernya = models.TextField(db_column='Usernya', blank=True, null=True)  # Field name made lowercase.
    statusnya = models.TextField(db_column='Statusnya', blank=True, null=True)  # Field name made lowercase.
    jamnya = models.TextField(blank=True, null=True)
    stcal = models.TextField(blank=True, null=True)
    qtytot = models.TextField(blank=True, null=True)
    roolnya = models.TextField(db_column='RoolNya', blank=True, null=True)  # Field name made lowercase.
    nokaret = models.TextField(blank=True, null=True)
    totroll = models.TextField(db_column='TotRoll', blank=True, null=True)  # Field name made lowercase.
    panjang = models.TextField(db_column='Panjang', blank=True, null=True)  # Field name made lowercase.
    tglmixing = models.TextField(db_column='TglMixing', blank=True, null=True)  # Field name made lowercase.
    bacthmix = models.TextField(db_column='BacthMix', blank=True, null=True)  # Field name made lowercase.
    rakno = models.TextField(db_column='RakNo', blank=True, null=True)  # Field name made lowercase.
    exp = models.TextField(blank=True, null=True)
    idjatwal = models.BigIntegerField(blank=True, null=True)
    terpakai = models.TextField(blank=True, null=True)
    mesin = models.TextField(blank=True, null=True)
    stdijatwal = models.TextField(blank=True, null=True)
    dis = models.TextField(blank=True, null=True)
    usere = models.TextField(blank=True, null=True)
    lebar = models.TextField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    qcpas = models.CharField(db_column='QcPas', max_length=1)  # Field name made lowercase.
    hlodnya = models.CharField(max_length=1)
    qcuser = models.TextField(db_column='QCuser', blank=True, null=True)  # Field name made lowercase.
    qctgl = models.TextField(db_column='Qctgl', blank=True, null=True)  # Field name made lowercase.
    tgljam = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_calender'


class TCalenderL(models.Model):
    link = models.TextField(blank=True, null=True)
    karet = models.TextField(blank=True, null=True)
    remil1 = models.TextField(blank=True, null=True)
    remil2 = models.TextField(blank=True, null=True)
    roll1 = models.TextField(blank=True, null=True)
    roll2 = models.TextField(blank=True, null=True)
    tglin = models.DateTimeField(blank=True, null=True)
    usernya = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_calender_L'


class TCalenderM(models.Model):
    karet = models.TextField(blank=True, null=True)
    kdcal = models.TextField(blank=True, null=True)
    barcode = models.TextField(blank=True, null=True)
    qty = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    tglin = models.DateTimeField(blank=True, null=True)
    usernya = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_calender_M'


class TCalenderSatuS(models.Model):
    kd_calender = models.CharField(db_column='kd_Calender', max_length=30, blank=True, null=True)  # Field name made lowercase.
    kd_mixing = models.CharField(db_column='kd_Mixing', max_length=30, blank=True, null=True)  # Field name made lowercase.
    item = models.CharField(db_column='Item', max_length=30, blank=True, null=True)  # Field name made lowercase.
    qtynya = models.CharField(max_length=30, blank=True, null=True)
    usernya = models.CharField(db_column='Usernya', max_length=25, blank=True, null=True)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jamnya = models.CharField(max_length=30, blank=True, null=True)
    stcal = models.CharField(max_length=20, blank=True, null=True)
    qtytot = models.CharField(max_length=30, blank=True, null=True)
    roolnya = models.CharField(db_column='RoolNya', max_length=30, blank=True, null=True)  # Field name made lowercase.
    nokaret = models.CharField(max_length=255, blank=True, null=True)
    totroll = models.CharField(db_column='TotRoll', max_length=30, blank=True, null=True)  # Field name made lowercase.
    panjang = models.CharField(db_column='Panjang', max_length=30, blank=True, null=True)  # Field name made lowercase.
    tglmixing = models.CharField(db_column='TglMixing', max_length=20, blank=True, null=True)  # Field name made lowercase.
    bacthmix = models.CharField(db_column='BacthMix', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rakno = models.CharField(db_column='RakNo', max_length=30, blank=True, null=True)  # Field name made lowercase.
    exp = models.CharField(max_length=20, blank=True, null=True)
    idjatwal = models.BigIntegerField(blank=True, null=True)
    terpakai = models.CharField(max_length=15, blank=True, null=True)
    mesin = models.CharField(max_length=50, blank=True, null=True)
    stdijatwal = models.CharField(max_length=5, blank=True, null=True)
    dis = models.CharField(max_length=50, blank=True, null=True)
    usere = models.CharField(max_length=30, blank=True, null=True)
    lebar = models.CharField(max_length=20, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    qcpas = models.CharField(db_column='QcPas', max_length=1)  # Field name made lowercase.
    hlodnya = models.CharField(max_length=1)
    qcuser = models.CharField(db_column='QCuser', max_length=10, blank=True, null=True)  # Field name made lowercase.
    qctgl = models.CharField(db_column='Qctgl', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_calender_Satu_s'


class TCalenderD(models.Model):
    kd_calender = models.CharField(max_length=20, blank=True, null=True)
    kd_mixing = models.CharField(max_length=20, blank=True, null=True)
    panjang = models.CharField(max_length=20, blank=True, null=True)
    lebar = models.CharField(max_length=20, blank=True, null=True)
    lebar2 = models.CharField(max_length=50, blank=True, null=True)
    lebar3 = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_calender_d'


class TDirectMaterialDaily(models.Model):
    entry_id = models.IntegerField(primary_key=True, db_column='ENTRY_ID')  # Field name made lowercase.
    kode_barang = models.CharField(db_column='KODE_BARANG', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kode_supplier = models.CharField(db_column='KODE_SUPPLIER', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kode_gudang = models.CharField(db_column='KODE_GUDANG', max_length=5, blank=True, null=True)  # Field name made lowercase.
    transact_date = models.DateTimeField(db_column='TRANSACT_DATE', blank=True, null=True)  # Field name made lowercase.
    week_num = models.IntegerField(db_column='WEEK_NUM', blank=True, null=True)  # Field name made lowercase.
    no_surat_jalan = models.CharField(db_column='NO_SURAT_JALAN', max_length=20, blank=True, null=True)  # Field name made lowercase.
    no_po = models.CharField(db_column='NO_PO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    invoice_no = models.CharField(db_column='INVOICE_NO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    bc_no = models.CharField(db_column='BC_NO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    in_qty = models.DecimalField(db_column='IN_QTY', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_qty = models.DecimalField(db_column='OUT_QTY', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    in_amount = models.DecimalField(db_column='IN_AMOUNT', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    out_amount = models.DecimalField(db_column='OUT_AMOUNT', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    check_status = models.IntegerField(db_column='CHECK_STATUS', blank=True, null=True)  # Field name made lowercase.
    update_timestamp = models.DateTimeField(db_column='UPDATE_TIMESTAMP', blank=True, null=True)  # Field name made lowercase.
    update_user = models.CharField(db_column='UPDATE_USER', max_length=50, blank=True, null=True)  # Field name made lowercase.
    update_status = models.CharField(db_column='UPDATE_STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.
    fakturno = models.CharField(max_length=20, blank=True, null=True)
    poasli = models.CharField(db_column='POAsli', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_direct_material_daily'


class THistCalender(models.Model):
    kd_calender = models.CharField(db_column='kd_Calender', max_length=30, blank=True, null=True)  # Field name made lowercase.
    kd_mixing = models.CharField(db_column='kd_Mixing', max_length=30, blank=True, null=True)  # Field name made lowercase.
    item = models.CharField(db_column='Item', max_length=30, blank=True, null=True)  # Field name made lowercase.
    qtynya = models.CharField(max_length=30, blank=True, null=True)
    usernya = models.CharField(db_column='Usernya', max_length=25, blank=True, null=True)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jamnya = models.CharField(max_length=30, blank=True, null=True)
    stcal = models.CharField(max_length=20, blank=True, null=True)
    qtytot = models.CharField(max_length=30, blank=True, null=True)
    roolnya = models.CharField(db_column='RoolNya', max_length=30, blank=True, null=True)  # Field name made lowercase.
    nokaret = models.CharField(max_length=255, blank=True, null=True)
    totroll = models.CharField(db_column='TotRoll', max_length=30, blank=True, null=True)  # Field name made lowercase.
    panjang = models.CharField(db_column='Panjang', max_length=30, blank=True, null=True)  # Field name made lowercase.
    tglmixing = models.CharField(db_column='TglMixing', max_length=20, blank=True, null=True)  # Field name made lowercase.
    bacthmix = models.CharField(db_column='BacthMix', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rakno = models.CharField(db_column='RakNo', max_length=30, blank=True, null=True)  # Field name made lowercase.
    exp = models.CharField(max_length=20, blank=True, null=True)
    idjatwal = models.BigIntegerField(blank=True, null=True)
    terpakai = models.CharField(max_length=15, blank=True, null=True)
    mesin = models.CharField(max_length=50, blank=True, null=True)
    stdijatwal = models.CharField(max_length=5, blank=True, null=True)
    dis = models.CharField(max_length=50, blank=True, null=True)
    usere = models.CharField(max_length=30, blank=True, null=True)
    lebar = models.CharField(max_length=20, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    qcpas = models.CharField(db_column='QcPas', max_length=1)  # Field name made lowercase.
    hlodnya = models.CharField(max_length=1)
    qcuser = models.CharField(db_column='QCuser', max_length=10, blank=True, null=True)  # Field name made lowercase.
    qctgl = models.CharField(db_column='Qctgl', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tgljam = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_hist_calender'


class THistCalenderLama1Hapus(models.Model):
    kd_calender = models.CharField(db_column='kd_Calender', max_length=30, blank=True, null=True)  # Field name made lowercase.
    kd_mixing = models.CharField(db_column='kd_Mixing', max_length=30, blank=True, null=True)  # Field name made lowercase.
    item = models.CharField(db_column='Item', max_length=30, blank=True, null=True)  # Field name made lowercase.
    qtynya = models.CharField(max_length=30, blank=True, null=True)
    usernya = models.CharField(db_column='Usernya', max_length=25, blank=True, null=True)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jamnya = models.CharField(max_length=30, blank=True, null=True)
    stcal = models.CharField(max_length=20, blank=True, null=True)
    qtytot = models.CharField(max_length=30, blank=True, null=True)
    roolnya = models.CharField(db_column='RoolNya', max_length=30, blank=True, null=True)  # Field name made lowercase.
    nokaret = models.CharField(max_length=255, blank=True, null=True)
    totroll = models.CharField(db_column='TotRoll', max_length=30, blank=True, null=True)  # Field name made lowercase.
    panjang = models.CharField(db_column='Panjang', max_length=30, blank=True, null=True)  # Field name made lowercase.
    tglmixing = models.CharField(db_column='TglMixing', max_length=20, blank=True, null=True)  # Field name made lowercase.
    bacthmix = models.CharField(db_column='BacthMix', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rakno = models.CharField(db_column='RakNo', max_length=30, blank=True, null=True)  # Field name made lowercase.
    exp = models.CharField(max_length=20, blank=True, null=True)
    idjatwal = models.BigIntegerField(blank=True, null=True)
    terpakai = models.CharField(max_length=15, blank=True, null=True)
    mesin = models.CharField(max_length=50, blank=True, null=True)
    stdijatwal = models.CharField(max_length=5, blank=True, null=True)
    dis = models.CharField(max_length=50, blank=True, null=True)
    usere = models.CharField(max_length=30, blank=True, null=True)
    lebar = models.CharField(max_length=20, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    qcpas = models.CharField(db_column='QcPas', max_length=1)  # Field name made lowercase.
    hlodnya = models.CharField(max_length=1)
    qcuser = models.CharField(db_column='QCuser', max_length=10, blank=True, null=True)  # Field name made lowercase.
    qctgl = models.CharField(db_column='Qctgl', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_hist_calender_lama1_hapus'


class THistJatwal(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='Id')  # Field name made lowercase.
    kdjatwal = models.CharField(db_column='KdJatwal', max_length=200)  # Field name made lowercase.
    mesin = models.CharField(db_column='Mesin', max_length=100)  # Field name made lowercase.
    tglproduksi = models.CharField(max_length=100)
    waktuupload = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=10)
    usernya = models.CharField(max_length=100, blank=True, null=True)
    proses = models.CharField(db_column='Proses', max_length=10)  # Field name made lowercase.
    kdmixing = models.CharField(db_column='kdMixing', max_length=200)  # Field name made lowercase.
    bacth = models.CharField(max_length=20, blank=True, null=True)
    bacthselesai = models.CharField(max_length=20)
    waktuupdate = models.CharField(max_length=100, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=20, blank=True, null=True)
    stjatwal = models.CharField(max_length=1)
    stuser = models.CharField(max_length=20, blank=True, null=True)
    nourut = models.CharField(db_column='noUrut', max_length=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_hist_jatwal'


class THitJatwal(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='Id')  # Field name made lowercase.
    kdjatwal = models.CharField(db_column='KdJatwal', max_length=200)  # Field name made lowercase.
    mesin = models.CharField(db_column='Mesin', max_length=100)  # Field name made lowercase.
    tglproduksi = models.CharField(max_length=100)
    waktuupload = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=10)
    usernya = models.CharField(max_length=100, blank=True, null=True)
    proses = models.CharField(db_column='Proses', max_length=10)  # Field name made lowercase.
    kdmixing = models.CharField(db_column='kdMixing', max_length=200)  # Field name made lowercase.
    bacth = models.CharField(max_length=20, blank=True, null=True)
    bacthselesai = models.CharField(max_length=20)
    waktuupdate = models.CharField(max_length=100, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=20, blank=True, null=True)
    stjatwal = models.CharField(max_length=1)
    stuser = models.CharField(max_length=20, blank=True, null=True)
    nourut = models.CharField(db_column='noUrut', max_length=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_hit_Jatwal'


class THitJatwalWeihing(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='Id')  # Field name made lowercase.
    kdjatwal = models.CharField(db_column='KdJatwal', max_length=200)  # Field name made lowercase.
    mesin = models.CharField(db_column='Mesin', max_length=100)  # Field name made lowercase.
    tglproduksi = models.CharField(max_length=100)
    waktuupload = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=10)
    usernya = models.CharField(max_length=100, blank=True, null=True)
    proses = models.CharField(db_column='Proses', max_length=10)  # Field name made lowercase.
    kdmixing = models.CharField(db_column='kdMixing', max_length=200)  # Field name made lowercase.
    bacth = models.CharField(max_length=20, blank=True, null=True)
    bacthselesai = models.CharField(max_length=20)
    waktuupdate = models.CharField(max_length=100, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=20, blank=True, null=True)
    stjatwal = models.CharField(max_length=1)
    stuser = models.CharField(max_length=20, blank=True, null=True)
    nourut = models.CharField(db_column='noUrut', max_length=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_hit_jatwal_Weihing'


class TImportBarcode(models.Model):
    barcode = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 't_import_Barcode'


class TJatwalWeihing(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='Id')  # Field name made lowercase.
    kdjatwal = models.CharField(db_column='KdJatwal', max_length=200)  # Field name made lowercase.
    mesin = models.CharField(db_column='Mesin', max_length=100)  # Field name made lowercase.
    tglproduksi = models.CharField(max_length=100)
    waktuupload = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=10)
    usernya = models.CharField(max_length=100, blank=True, null=True)
    proses = models.CharField(db_column='Proses', max_length=10)  # Field name made lowercase.
    kdmixing = models.CharField(db_column='kdMixing', max_length=200)  # Field name made lowercase.
    bacth = models.CharField(max_length=20, blank=True, null=True)
    bacthselesai = models.CharField(max_length=20)
    waktuupdate = models.CharField(max_length=100, blank=True, null=True)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=20, blank=True, null=True)
    stjatwal = models.CharField(max_length=1)
    stuser = models.CharField(max_length=20, blank=True, null=True)
    nourut = models.CharField(db_column='noUrut', max_length=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_jatwal_Weihing'


class TLangkahBb2(models.Model):
    mesin = models.CharField(max_length=50, blank=True, null=True)
    kdresep = models.CharField(max_length=50, blank=True, null=True)
    idjadwal = models.CharField(max_length=50, blank=True, null=True)
    langkah = models.CharField(max_length=50, blank=True, null=True)
    bacth = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_langkah_BB2'


class TMixingHistHapus(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='Id')  # Field name made lowercase.
    kd_mixing = models.CharField(db_column='Kd_Mixing', max_length=20)  # Field name made lowercase.
    kd_resep = models.CharField(db_column='kd_Resep', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item = models.CharField(db_column='Item', max_length=20)  # Field name made lowercase.
    qty = models.CharField(db_column='Qty', max_length=20)  # Field name made lowercase.
    kdweihing = models.CharField(db_column='KdWeihing', max_length=20)  # Field name made lowercase.
    operator = models.CharField(db_column='Operator', max_length=20)  # Field name made lowercase.
    tglmixing = models.CharField(db_column='tglMixing', max_length=20)  # Field name made lowercase.
    waktu = models.CharField(max_length=20, blank=True, null=True)
    tglmasuk = models.CharField(db_column='Tglmasuk', max_length=10)  # Field name made lowercase.
    usernya = models.CharField(max_length=20)
    statusnya = models.CharField(max_length=1)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=20, blank=True, null=True)
    mesin = models.CharField(db_column='Mesin', max_length=10, blank=True, null=True)  # Field name made lowercase.
    batch = models.CharField(db_column='Batch', max_length=10, blank=True, null=True)  # Field name made lowercase.
    proses = models.CharField(max_length=1)
    hold = models.CharField(db_column='Hold', max_length=1, blank=True, null=True)  # Field name made lowercase.
    tglqc = models.CharField(max_length=10, blank=True, null=True)
    tglhold = models.CharField(max_length=10, blank=True, null=True)
    bacttot = models.DecimalField(db_column='BactTot', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qtot = models.DecimalField(db_column='Qtot', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    tglexp = models.CharField(max_length=10, blank=True, null=True)
    idjatwal = models.CharField(max_length=8, blank=True, null=True)
    idprint = models.CharField(max_length=20, blank=True, null=True)
    lewat = models.CharField(max_length=1)
    usrtimbang = models.CharField(db_column='UsrTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jamtimbang = models.CharField(db_column='JamTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tgltimbang = models.CharField(db_column='TglTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    userqc = models.CharField(db_column='UserQC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    terpakai = models.CharField(max_length=1)
    jenis = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_mixing_hist_hapus'


class TMixingPisah(models.Model):
    idpisah = models.BigAutoField(primary_key=True)
    idmixing = models.CharField(max_length=20)
    qtyp = models.DecimalField(max_digits=19, decimal_places=4)
    terpakai = models.CharField(max_length=1)
    usernyax = models.CharField(max_length=10, blank=True, null=True)
    tgl = models.DateTimeField(blank=True, null=True)
    qtyajusment = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_mixing_pisah'


class TMixngWdddHapus(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='Id')  # Field name made lowercase.
    kd_mixing = models.CharField(db_column='Kd_Mixing', max_length=20)  # Field name made lowercase.
    kd_resep = models.CharField(db_column='kd_Resep', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item = models.CharField(db_column='Item', max_length=20)  # Field name made lowercase.
    qty = models.CharField(db_column='Qty', max_length=20)  # Field name made lowercase.
    kdweihing = models.CharField(db_column='KdWeihing', max_length=20)  # Field name made lowercase.
    operator = models.CharField(db_column='Operator', max_length=20)  # Field name made lowercase.
    tglmixing = models.CharField(db_column='tglMixing', max_length=20)  # Field name made lowercase.
    waktu = models.CharField(max_length=20, blank=True, null=True)
    tglmasuk = models.CharField(db_column='Tglmasuk', max_length=10)  # Field name made lowercase.
    usernya = models.CharField(max_length=20)
    statusnya = models.CharField(max_length=1)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=20, blank=True, null=True)
    mesin = models.CharField(db_column='Mesin', max_length=10, blank=True, null=True)  # Field name made lowercase.
    batch = models.CharField(db_column='Batch', max_length=10, blank=True, null=True)  # Field name made lowercase.
    proses = models.CharField(max_length=1)
    hold = models.CharField(db_column='Hold', max_length=1, blank=True, null=True)  # Field name made lowercase.
    tglqc = models.CharField(max_length=10, blank=True, null=True)
    tglhold = models.CharField(max_length=10, blank=True, null=True)
    bacttot = models.DecimalField(db_column='BactTot', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qtot = models.DecimalField(db_column='Qtot', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    tglexp = models.CharField(max_length=10, blank=True, null=True)
    idjatwal = models.CharField(max_length=8, blank=True, null=True)
    idprint = models.CharField(max_length=20, blank=True, null=True)
    lewat = models.CharField(max_length=1)
    usrtimbang = models.CharField(db_column='UsrTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    jamtimbang = models.CharField(db_column='JamTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tgltimbang = models.CharField(db_column='TglTimbang', max_length=20, blank=True, null=True)  # Field name made lowercase.
    userqc = models.CharField(db_column='UserQC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    terpakai = models.CharField(max_length=1)
    jenis = models.CharField(max_length=20, blank=True, null=True)
    qty_adjusment = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    chamtemp = models.CharField(db_column='ChamTemp', max_length=9, blank=True, null=True)  # Field name made lowercase.
    tempwaterin = models.CharField(db_column='TempWaterIN', max_length=9, blank=True, null=True)  # Field name made lowercase.
    fwpressure = models.CharField(db_column='FWPressure', max_length=9, blank=True, null=True)  # Field name made lowercase.
    watflowrate = models.CharField(db_column='WatFlowRate', max_length=9, blank=True, null=True)  # Field name made lowercase.
    palet = models.CharField(db_column='Palet', max_length=9, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_mixng_wddd_hapus'


class TRemil(models.Model):
    resep = models.CharField(db_column='Resep', max_length=30)  # Field name made lowercase.
    tglpro = models.CharField(db_column='TglPro', max_length=10)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty')  # Field name made lowercase.
    tglmasuk = models.CharField(max_length=100, blank=True, null=True)
    usernya = models.CharField(max_length=20)
    kdremil = models.CharField(max_length=30)
    tglexp = models.CharField(max_length=10, blank=True, null=True)
    seksi = models.CharField(db_column='Seksi', max_length=100, blank=True, null=True)  # Field name made lowercase.
    tglcal = models.CharField(db_column='tglCal', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tglremil = models.CharField(max_length=100, blank=True, null=True)
    kdcalender = models.CharField(db_column='kdCalender', max_length=30, blank=True, null=True)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    terpakai = models.CharField(db_column='Terpakai', max_length=1, blank=True, null=True)  # Field name made lowercase.
    subsek = models.CharField(max_length=20, blank=True, null=True)
    shift = models.CharField(max_length=10, blank=True, null=True)
    user_edit = models.CharField(max_length=50, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    sebabremil = models.CharField(db_column='Sebabremil', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_remil'


class TScrap(models.Model):
    resep = models.CharField(db_column='Resep', max_length=30)  # Field name made lowercase.
    tglpro = models.CharField(db_column='TglPro', max_length=10)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty')  # Field name made lowercase.
    tglmasuk = models.DateTimeField(blank=True, null=True)
    usernya = models.CharField(max_length=20)
    kdscrap = models.CharField(max_length=30)
    tglexp = models.CharField(max_length=10, blank=True, null=True)
    seksi = models.CharField(db_column='Seksi', max_length=100, blank=True, null=True)  # Field name made lowercase.
    tglcal = models.CharField(db_column='tglCal', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tglscrap = models.CharField(max_length=10, blank=True, null=True)
    kdcalender = models.CharField(db_column='kdCalender', max_length=30, blank=True, null=True)  # Field name made lowercase.
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.
    terpakai = models.CharField(db_column='Terpakai', max_length=1, blank=True, null=True)  # Field name made lowercase.
    subsek = models.CharField(max_length=20, blank=True, null=True)
    shift = models.CharField(max_length=10, blank=True, null=True)
    user_edit = models.CharField(max_length=50, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    jenis = models.CharField(db_column='Jenis', max_length=100, blank=True, null=True)  # Field name made lowercase.
    nokar = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_scrap'


class TSisaCalender(models.Model):
    kdmixing = models.CharField(max_length=20)
    qtynya = models.CharField(max_length=9)
    tglin = models.DateTimeField()
    usernya = models.CharField(max_length=20)
    statusnya = models.CharField(max_length=1)
    useredit = models.CharField(max_length=20, blank=True, null=True)
    tgledit = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_sisa_calender'


class TStockMixingClear(models.Model):
    barcode = models.CharField(max_length=255)
    usernya = models.CharField(max_length=255)
    tgl = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 't_stock_mixing_clear'


class Tabel20(models.Model):
    kodebrg = models.CharField(db_column='Kodebrg', max_length=15)  # Field name made lowercase.
    th = models.CharField(max_length=4)
    bln = models.CharField(max_length=2)
    qty20 = models.DecimalField(max_digits=19, decimal_places=4)
    rdp = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'tabel_20'


class TabelPemasukan(models.Model):
    id_pemasukan = models.CharField(max_length=50, primary_key = True)
    no_bbm = models.CharField(max_length=30, blank=True, null=True)
    no_po = models.CharField(max_length=150, blank=True, null=True)
    no_faktur = models.CharField(max_length=150, blank=True, null=True)
    no_bc = models.CharField(max_length=150, blank=True, null=True)
    kode_gudang = models.CharField(max_length=30, blank=True, null=True)
    kode_barang = models.CharField(max_length=200, blank=True, null=True)
    kode_supplier = models.CharField(max_length=30, blank=True, null=True)
    qty = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    rp_us = models.CharField(max_length=2, blank=True, null=True)
    nilai_rp = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    nilai_usd = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    rate = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    konfirmasi = models.CharField(max_length=1, blank=True, null=True)
    minggu = models.IntegerField(blank=True, null=True)
    tgl_masuk = models.DateTimeField(blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    usernya = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    useredit = models.CharField(max_length=30, blank=True, null=True)
    hari = models.IntegerField(blank=True, null=True)
    invoice = models.CharField(max_length=150, blank=True, null=True)
    docpa = models.CharField(db_column='DocPa', max_length=150, blank=True, null=True)  # Field name made lowercase.
    tgldocpa = models.CharField(db_column='TglDocPa', max_length=25, blank=True, null=True)  # Field name made lowercase.
    kdhs = models.CharField(db_column='KdHS', max_length=30, blank=True, null=True)  # Field name made lowercase.
    kdjenisdoc = models.CharField(db_column='KdJenisDoc', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tglinvoice = models.CharField(db_column='TglInvoice', max_length=20, blank=True, null=True)  # Field name made lowercase.
    bl = models.CharField(db_column='BL', max_length=50, blank=True, null=True)  # Field name made lowercase.
    tglbl = models.CharField(db_column='TglBL', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cif = models.CharField(db_column='Cif', max_length=20)  # Field name made lowercase.
    bmm = models.CharField(db_column='BMM', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cukairate = models.CharField(db_column='CukaiRate', max_length=10)  # Field name made lowercase.
    pnbp = models.CharField(db_column='PnBp', max_length=50)  # Field name made lowercase.
    qtytot = models.CharField(max_length=20)
    nosj = models.CharField(max_length=50, blank=True, null=True)
    tgl_sj = models.DateTimeField(blank=True, null=True)
    kemasan = models.CharField(max_length=25, blank=True, null=True)
    jml_kemasan = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    berat_kotor = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    berat_bersih = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    volume = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    hrg_serah = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    tgl_po = models.DateTimeField(blank=True, null=True)
    jenis_kenda = models.CharField(max_length=50, blank=True, null=True)
    no_plat = models.CharField(max_length=10, blank=True, null=True)
    unit = models.CharField(max_length=25, blank=True, null=True)
    kodeedit = models.CharField(max_length=50, blank=True, null=True)
    jbar = models.CharField(max_length=1, blank=True, null=True)
    rdp = models.CharField(max_length=1)
    td = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tabel_pemasukan'


class TabelPengeluaran(models.Model):
    id_pengeluaran = models.CharField(max_length=20)
    no_bpb = models.CharField(max_length=30, blank=True, null=True)
    tgl_keluar = models.DateTimeField(blank=True, null=True)
    kode_barang = models.CharField(max_length=50, blank=True, null=True)
    qty = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    rp_us = models.CharField(max_length=2, blank=True, null=True)
    nominal_rp = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    nominal_us = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    std_rp = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    std_us = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    rate = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    minggu = models.IntegerField(blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    usernya = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    useredit = models.CharField(max_length=30, blank=True, null=True)
    hari = models.IntegerField(blank=True, null=True)
    kode_gudang = models.CharField(max_length=10, blank=True, null=True)
    rdp = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'tabel_pengeluaran'


class TabelTutupBukuC(models.Model):
    kode_barang = models.CharField(max_length=50)
    tahun = models.CharField(max_length=4, blank=True, null=True)
    bulan = models.CharField(max_length=2, blank=True, null=True)
    qty = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    stock_rp = models.DecimalField(db_column='Stock_rp', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    stock_us = models.DecimalField(db_column='Stock_Us', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    rate = models.DecimalField(db_column='Rate', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(max_length=30, blank=True, null=True)
    tgl_tutup = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    useredit = models.CharField(max_length=30, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    kode_gudang = models.CharField(max_length=10, blank=True, null=True)
    amount = models.DecimalField(db_column='Amount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qty_ak = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tabel_tutup_buku_C'


class TabelTutupbuku(models.Model):
    kode_barang = models.CharField(max_length=50)
    tahun = models.CharField(max_length=4, blank=True, null=True)
    bulan = models.CharField(max_length=2, blank=True, null=True)
    qty = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    stock_rp = models.DecimalField(db_column='Stock_rp', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    stock_us = models.DecimalField(db_column='Stock_Us', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    rate = models.DecimalField(db_column='Rate', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(max_length=30, blank=True, null=True)
    tgl_tutup = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    useredit = models.CharField(max_length=30, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    kode_gudang = models.CharField(max_length=10, blank=True, null=True)
    amount = models.DecimalField(db_column='Amount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qty_ak = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    rdp = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'tabel_tutupbuku'


class TabelTutupbuku5(models.Model):
    kode_barang = models.CharField(max_length=255, blank=True, null=True)
    tahun = models.FloatField(blank=True, null=True)
    bulan = models.FloatField(blank=True, null=True)
    qty = models.CharField(max_length=255, blank=True, null=True)
    stock_rp = models.CharField(db_column='Stock_rp', max_length=255, blank=True, null=True)  # Field name made lowercase.
    stock_us = models.CharField(db_column='Stock_Us', max_length=255, blank=True, null=True)  # Field name made lowercase.
    rate = models.FloatField(db_column='Rate', blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(max_length=255, blank=True, null=True)
    tgl_tutup = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    useredit = models.CharField(max_length=255, blank=True, null=True)
    tgl_edit = models.CharField(max_length=255, blank=True, null=True)
    kode_gudang = models.FloatField(blank=True, null=True)
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    qty_ak = models.FloatField(blank=True, null=True)
    rdp = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tabel_tutupbuku5'


class TabelTutupbukuAsli(models.Model):
    kode_barang = models.CharField(max_length=50)
    tahun = models.CharField(max_length=4, blank=True, null=True)
    bulan = models.CharField(max_length=2, blank=True, null=True)
    qty = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    stock_rp = models.DecimalField(db_column='Stock_rp', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    stock_us = models.DecimalField(db_column='Stock_Us', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    rate = models.DecimalField(db_column='Rate', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    usernya = models.CharField(max_length=30, blank=True, null=True)
    tgl_tutup = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    useredit = models.CharField(max_length=30, blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    kode_gudang = models.CharField(max_length=10, blank=True, null=True)
    amount = models.DecimalField(db_column='Amount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qty_ak = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tabel_tutupbuku_asli'


class TblSisa(models.Model):
    id_mixing = models.CharField(max_length=20, blank=True, null=True)
    kd_calender = models.CharField(max_length=50, blank=True, null=True)
    qty = models.FloatField(blank=True, null=True)
    tgl = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_sisa'


class UpdateResep1(models.Model):
    kdresep = models.CharField(max_length=255, blank=True, null=True)
    resep = models.CharField(db_column='Resep', max_length=4, blank=True, null=True)  # Field name made lowercase.
    fase = models.CharField(max_length=3, blank=True, null=True)
    tet = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'update_resep1'


class UserModule(models.Model):
    status = models.CharField(db_column='STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.
    insdt = models.DateTimeField(blank=True, null=True)
    upddt = models.DateTimeField(blank=True, null=True)
    usrname = models.CharField(max_length=15, blank=True, null=True)
    mdlid = models.CharField(max_length=20, blank=True, null=True)
    untuk = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_module'


class ZTHistBarangProduksiDUpdtePl(models.Model):
    kdtimbang = models.CharField(max_length=20, blank=True, null=True)
    no_produksix = models.CharField(db_column='No_Produksix', max_length=200)  # Field name made lowercase.
    no_produksi = models.CharField(db_column='No_Produksi', max_length=20)  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'z_T_hist_Barang_Produksi_D_Updte_pl'

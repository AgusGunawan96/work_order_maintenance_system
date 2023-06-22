# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class BarangV(models.Model):
    kode_jenis = models.FloatField(blank=True, null=True)
    kode_barang = models.CharField(max_length=50, blank=True, null=True)
    nama_barang = models.TextField(blank=True, null=True)
    spesifikasi = models.CharField(max_length=100, blank=True, null=True)
    kode_departement = models.FloatField(db_column='kode_Departement', blank=True, null=True)  # Field name made lowercase.
    satuan = models.CharField(max_length=50, blank=True, null=True)
    satuan_lain = models.CharField(max_length=50, blank=True, null=True)
    konversi = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)
    keterangan = models.CharField(max_length=150, blank=True, null=True)
    kelas = models.CharField(max_length=1, blank=True, null=True)
    kode_bpcs = models.FloatField(blank=True, null=True)
    vendor_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'BARANG_V'


class Bolist(models.Model):
    p_r_no_field = models.CharField(db_column='P/R No#', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    p_o_no_field = models.FloatField(db_column='P/O No#', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    curency = models.CharField(db_column='Curency', max_length=255, blank=True, null=True)  # Field name made lowercase.
    field_field = models.FloatField(db_column='-', blank=True, null=True)  # Field renamed to remove unsuitable characters. Field renamed because it started with '_'. Field renamed because it ended with '_'.
    f5 = models.CharField(db_column='F5', max_length=255, blank=True, null=True)  # Field name made lowercase.
    commodity_code = models.CharField(db_column='Commodity Code', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    kode_barang = models.CharField(db_column='KODE BARANG', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    f8 = models.CharField(db_column='F8', max_length=255, blank=True, null=True)  # Field name made lowercase.
    item_description = models.CharField(db_column='Item Description', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    ordering_qty = models.FloatField(db_column='Ordering Qty', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    receiving_qty = models.FloatField(db_column='Receiving Qty', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    unit_price = models.FloatField(db_column='Unit Price', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    request_delivery_date = models.FloatField(db_column='Request_Delivery Date', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    remarks = models.CharField(db_column='Remarks', max_length=255, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=255, blank=True, null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='UNIT', max_length=255, blank=True, null=True)  # Field name made lowercase.
    unit2 = models.CharField(db_column='UNIT2', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BOLIST'


class Bolistyogi(models.Model):
    pr_no = models.CharField(db_column='PR_no', max_length=255, blank=True, null=True)  # Field name made lowercase.
    po_no = models.FloatField(db_column='PO_no', blank=True, null=True)  # Field name made lowercase.
    curency = models.CharField(db_column='Curency', max_length=255, blank=True, null=True)  # Field name made lowercase.
    field_field = models.FloatField(db_column='-', blank=True, null=True)  # Field renamed to remove unsuitable characters. Field renamed because it started with '_'. Field renamed because it ended with '_'.
    f5 = models.CharField(db_column='F5', max_length=255, blank=True, null=True)  # Field name made lowercase.
    commodity_code = models.CharField(db_column='Commodity_Code', max_length=255, blank=True, null=True)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='KODE_BARANG', max_length=255, blank=True, null=True)  # Field name made lowercase.
    item_description = models.CharField(db_column='Item_Description', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ordering_qty = models.FloatField(db_column='Ordering_Qty', blank=True, null=True)  # Field name made lowercase.
    receiving_qty = models.FloatField(db_column='Receiving_Qty', blank=True, null=True)  # Field name made lowercase.
    unit_price = models.FloatField(db_column='Unit_Price', blank=True, null=True)  # Field name made lowercase.
    f12 = models.CharField(db_column='F12', max_length=255, blank=True, null=True)  # Field name made lowercase.
    rdd = models.DateTimeField(db_column='RDD', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=255, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=255, blank=True, null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='UNIT', max_length=255, blank=True, null=True)  # Field name made lowercase.
    unit2 = models.CharField(db_column='UNIT2', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BOLISTYOGI'


class MPurposeOfPurchase(models.Model):
    transaction_efect = models.CharField(db_column='Transaction_Efect', max_length=5)  # Field name made lowercase.
    reson_code = models.CharField(db_column='Reson_Code', max_length=5)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=150)  # Field name made lowercase.
    cost_center = models.CharField(db_column='COST_CENTER', max_length=150)  # Field name made lowercase.
    statusnya = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'M_Purpose_Of_Purchase'


class MasterCustomer(models.Model):
    kdcustomer = models.CharField(db_column='kdCustomer', max_length=20)  # Field name made lowercase.
    nmperusahaan = models.CharField(db_column='NmPerusahaan', max_length=200)  # Field name made lowercase.
    alamat = models.TextField(db_column='Alamat', blank=True, null=True)  # Field name made lowercase.
    kota = models.TextField(db_column='Kota', blank=True, null=True)  # Field name made lowercase.
    negara = models.TextField(db_column='Negara', blank=True, null=True)  # Field name made lowercase.
    tel = models.CharField(db_column='Tel', max_length=50, blank=True, null=True)  # Field name made lowercase.
    fax = models.CharField(db_column='Fax', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pic = models.CharField(db_column='PIC', max_length=100, blank=True, null=True)  # Field name made lowercase.
    statusnya = models.CharField(max_length=1)
    tglmasuk = models.CharField(max_length=10)
    usernya = models.CharField(max_length=20)
    tgledit = models.CharField(max_length=10, blank=True, null=True)
    useredit = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Master_Customer'


class MasterGroupFaktur(models.Model):
    kode = models.TextField(db_column='Kode', blank=True, null=True)  # Field name made lowercase.
    ket = models.CharField(db_column='Ket', max_length=500)  # Field name made lowercase.
    faktur = models.CharField(db_column='Faktur', max_length=3)  # Field name made lowercase.
    tglin = models.DateTimeField()
    userin = models.CharField(max_length=200)
    tgledit = models.DateTimeField(blank=True, null=True)
    useredit = models.CharField(max_length=200, blank=True, null=True)
    statusnya = models.CharField(db_column='Statusnya', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Master_Group_Faktur'


class MasterUserakses(models.Model):
    kode_user = models.CharField(db_column='kode_User', max_length=50, blank=True, null=True)  # Field name made lowercase.
    akses = models.CharField(db_column='Akses', max_length=50, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(max_length=3, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Master_UserAkses'


class MasterAkses(models.Model):
    akses = models.CharField(db_column='Akses', max_length=50, blank=True, null=True)  # Field name made lowercase.
    hak = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Master_akses'


class Poyogi(models.Model):
    pr_no = models.CharField(db_column='PR_no', max_length=255, blank=True, null=True)  # Field name made lowercase.
    po_no = models.TextField(db_column='PO_no', blank=True, null=True)  # Field name made lowercase.
    curency = models.CharField(db_column='Curency', max_length=255, blank=True, null=True)  # Field name made lowercase.
    field_field = models.FloatField(db_column='-', blank=True, null=True)  # Field renamed to remove unsuitable characters. Field renamed because it started with '_'. Field renamed because it ended with '_'.
    f5 = models.CharField(db_column='F5', max_length=255, blank=True, null=True)  # Field name made lowercase.
    commodity_code = models.CharField(db_column='Commodity_Code', max_length=255, blank=True, null=True)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='KODE_BARANG', max_length=255, blank=True, null=True)  # Field name made lowercase.
    item_description = models.CharField(db_column='Item_Description', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ordering_qty = models.FloatField(db_column='Ordering_Qty', blank=True, null=True)  # Field name made lowercase.
    receiving_qty = models.FloatField(db_column='Receiving_Qty', blank=True, null=True)  # Field name made lowercase.
    unit_price = models.FloatField(db_column='Unit_Price', blank=True, null=True)  # Field name made lowercase.
    f12 = models.CharField(db_column='F12', max_length=255, blank=True, null=True)  # Field name made lowercase.
    rdd = models.DateTimeField(db_column='RDD', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=255, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=255, blank=True, null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='UNIT', max_length=255, blank=True, null=True)  # Field name made lowercase.
    unit2 = models.CharField(db_column='UNIT2', max_length=255, blank=True, null=True)  # Field name made lowercase.
    kdsup = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'POYOGI'


class Poyogi2(models.Model):
    pr_no = models.CharField(db_column='PR_no', max_length=255, blank=True, null=True)  # Field name made lowercase.
    po_no = models.FloatField(db_column='PO_no', blank=True, null=True)  # Field name made lowercase.
    curency = models.CharField(db_column='Curency', max_length=255, blank=True, null=True)  # Field name made lowercase.
    field_field = models.FloatField(db_column='-', blank=True, null=True)  # Field renamed to remove unsuitable characters. Field renamed because it started with '_'. Field renamed because it ended with '_'.
    f5 = models.CharField(db_column='F5', max_length=255, blank=True, null=True)  # Field name made lowercase.
    commodity_code = models.CharField(db_column='Commodity_Code', max_length=255, blank=True, null=True)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='KODE_BARANG', max_length=255, blank=True, null=True)  # Field name made lowercase.
    item_description = models.CharField(db_column='Item_Description', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ordering_qty = models.FloatField(db_column='Ordering_Qty', blank=True, null=True)  # Field name made lowercase.
    receiving_qty = models.FloatField(db_column='Receiving_Qty', blank=True, null=True)  # Field name made lowercase.
    unit_price = models.DecimalField(db_column='Unit_Price', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    f12 = models.CharField(db_column='F12', max_length=255, blank=True, null=True)  # Field name made lowercase.
    rdd = models.DateTimeField(db_column='RDD', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=255, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=255, blank=True, null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='UNIT', max_length=255, blank=True, null=True)  # Field name made lowercase.
    unit2 = models.CharField(db_column='UNIT2', max_length=255, blank=True, null=True)  # Field name made lowercase.
    vendor_code = models.FloatField(db_column='Vendor Code', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    vendor_code1 = models.CharField(db_column='Vendor_Code1', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'POYOGI2'


class TBbm(models.Model):
    po_no = models.CharField(max_length=110)
    tgl_masuk = models.DateTimeField()
    nobbm = models.CharField(db_column='NoBBM', max_length=13)  # Field name made lowercase.
    usernya = models.CharField(max_length=50)
    tgl_insert = models.DateTimeField()
    statusnya = models.CharField(max_length=1)
    userprintm = models.CharField(max_length=50, blank=True, null=True)
    pengirim = models.CharField(max_length=50, blank=True, null=True)
    penerima = models.CharField(max_length=50, blank=True, null=True)
    mengetahui = models.CharField(max_length=50, blank=True, null=True)
    disetujui = models.CharField(max_length=50, blank=True, null=True)
    nobpb = models.CharField(db_column='noBPB', max_length=13, blank=True, null=True)  # Field name made lowercase.
    tgl_keluar = models.DateTimeField(db_column='tgl_Keluar', blank=True, null=True)  # Field name made lowercase.
    userk = models.CharField(max_length=50, blank=True, null=True)
    pengirimk = models.CharField(max_length=50, blank=True, null=True)
    penerimak = models.CharField(max_length=50, blank=True, null=True)
    mengetahuik = models.CharField(max_length=50, blank=True, null=True)
    disetujuik = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_BBM'


class TDebitKreditNote(models.Model):
    noin = models.CharField(db_column='NoIn', max_length=500, blank=True, null=True)  # Field name made lowercase.
    nonya = models.CharField(db_column='NONya', max_length=20)  # Field name made lowercase.
    dork = models.CharField(db_column='DorK', max_length=1)  # Field name made lowercase.
    tgl = models.CharField(db_column='Tgl', max_length=10)  # Field name made lowercase.
    catatan = models.TextField(db_column='Catatan', blank=True, null=True)  # Field name made lowercase.
    perusahaan = models.TextField(db_column='Perusahaan')  # Field name made lowercase.
    barang = models.TextField(db_column='Barang')  # Field name made lowercase.
    qty = models.CharField(db_column='Qty', max_length=20)  # Field name made lowercase.
    matauang = models.CharField(db_column='MataUang', max_length=5)  # Field name made lowercase.
    rate = models.CharField(db_column='Rate', max_length=10)  # Field name made lowercase.
    hrgsatuanusd = models.CharField(db_column='HrgSatuanUSD', max_length=20)  # Field name made lowercase.
    hrgsatuanird = models.CharField(db_column='HrgSatuanIRD', max_length=20)  # Field name made lowercase.
    totalusd = models.CharField(db_column='TotalUSD', max_length=20)  # Field name made lowercase.
    totalidr = models.CharField(db_column='TotalIDR', max_length=20)  # Field name made lowercase.
    usernya = models.CharField(db_column='UserNya', max_length=20)  # Field name made lowercase.
    tglmasuk = models.DateTimeField(db_column='TglMasuk')  # Field name made lowercase.
    useredit = models.CharField(db_column='UserEdit', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tgledit = models.DateTimeField(db_column='TglEdit', blank=True, null=True)  # Field name made lowercase.
    statusnya = models.CharField(db_column='StatusNya', max_length=1)  # Field name made lowercase.
    app1 = models.CharField(db_column='App1', max_length=1, blank=True, null=True)  # Field name made lowercase.
    userapp1 = models.CharField(db_column='UserApp1', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tglapp1 = models.DateTimeField(db_column='TglApp1', blank=True, null=True)  # Field name made lowercase.
    app2 = models.CharField(db_column='App2', max_length=1, blank=True, null=True)  # Field name made lowercase.
    userapp2 = models.CharField(db_column='UserApp2', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tglapp2 = models.DateTimeField(db_column='TglApp2', blank=True, null=True)  # Field name made lowercase.
    app3 = models.CharField(db_column='App3', max_length=1, blank=True, null=True)  # Field name made lowercase.
    userapp3 = models.CharField(db_column='UserApp3', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tglapp3 = models.DateTimeField(db_column='TglApp3', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'T_Debit_Kredit_Note'


class TPo(models.Model):
    po_no = models.CharField(max_length=110, primary_key=True)
    po_date = models.DateTimeField(blank=True, null=True)
    kode_supplier = models.CharField(max_length=150, blank=True, null=True)
    eta_date = models.DateTimeField(blank=True, null=True)
    cur = models.CharField(max_length=130, blank=True, null=True)
    kode_barang = models.CharField(max_length=130, blank=True, null=True)
    kode_relasi = models.CharField(max_length=130, blank=True, null=True)
    qty = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    unit = models.CharField(max_length=125, blank=True, null=True)
    jenis_qty = models.CharField(max_length=11, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    total = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    note = models.CharField(max_length=1150, blank=True, null=True)
    status = models.CharField(max_length=11, blank=True, null=True)
    user_insert = models.CharField(max_length=125, blank=True, null=True)
    user_edit = models.CharField(max_length=125, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    j = models.CharField(max_length=11, blank=True, null=True)
    pr_no = models.CharField(db_column='PR_no', max_length=120, blank=True, null=True)  # Field name made lowercase.
    ship_via = models.CharField(max_length=1100, blank=True, null=True)
    qty2 = models.FloatField(blank=True, null=True)
    satlain = models.CharField(max_length=130, blank=True, null=True)
    co_rm = models.CharField(db_column='CO_RM', max_length=11, blank=True, null=True)  # Field name made lowercase.
    yg_co_rm = models.CharField(max_length=150, blank=True, null=True)
    tgl_co_rm = models.DateTimeField(db_column='tgl_CO_RM', blank=True, null=True)  # Field name made lowercase.
    co_adm = models.CharField(db_column='CO_ADM', max_length=11, blank=True, null=True)  # Field name made lowercase.
    yg_co_adm = models.CharField(max_length=150, blank=True, null=True)
    tgl_co_adm = models.DateTimeField(db_column='tgl_CO_ADM', blank=True, null=True)  # Field name made lowercase.
    co_as = models.CharField(db_column='CO_AS', max_length=11, blank=True, null=True)  # Field name made lowercase.
    yg_co_as = models.CharField(max_length=150, blank=True, null=True)
    tgl_co_as = models.DateTimeField(db_column='tgl_CO_AS', blank=True, null=True)  # Field name made lowercase.
    item_name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_PO'


class TPoLog(models.Model):
    po_no = models.CharField(max_length=110, blank=True, null=True)
    po_date = models.DateTimeField(blank=True, null=True)
    kode_supplier = models.CharField(max_length=150, blank=True, null=True)
    eta_date = models.DateTimeField(blank=True, null=True)
    cur = models.CharField(max_length=130, blank=True, null=True)
    kode_barang = models.CharField(max_length=130, blank=True, null=True)
    kode_relasi = models.CharField(max_length=130, blank=True, null=True)
    qty = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    unit = models.CharField(max_length=125, blank=True, null=True)
    jenis_qty = models.CharField(max_length=11, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    total = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    note = models.CharField(max_length=1150, blank=True, null=True)
    status = models.CharField(max_length=11, blank=True, null=True)
    user_insert = models.CharField(max_length=125, blank=True, null=True)
    user_edit = models.CharField(max_length=125, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    j = models.CharField(max_length=11, blank=True, null=True)
    pr_no = models.CharField(db_column='PR_no', max_length=120, blank=True, null=True)  # Field name made lowercase.
    ship_via = models.CharField(max_length=1100, blank=True, null=True)
    qty2 = models.FloatField(blank=True, null=True)
    satlain = models.CharField(max_length=130, blank=True, null=True)
    co_rm = models.CharField(db_column='CO_RM', max_length=11, blank=True, null=True)  # Field name made lowercase.
    yg_co_rm = models.CharField(max_length=150, blank=True, null=True)
    tgl_co_rm = models.DateTimeField(db_column='tgl_CO_RM', blank=True, null=True)  # Field name made lowercase.
    co_adm = models.CharField(db_column='CO_ADM', max_length=11, blank=True, null=True)  # Field name made lowercase.
    yg_co_adm = models.CharField(max_length=150, blank=True, null=True)
    tgl_co_adm = models.DateTimeField(db_column='tgl_CO_ADM', blank=True, null=True)  # Field name made lowercase.
    co_as = models.CharField(db_column='CO_AS', max_length=11, blank=True, null=True)  # Field name made lowercase.
    yg_co_as = models.CharField(max_length=150, blank=True, null=True)
    tgl_co_as = models.DateTimeField(db_column='tgl_CO_AS', blank=True, null=True)  # Field name made lowercase.
    item_name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'T_PO_log'


class TransKeluar(models.Model):
    kode_keluar = models.CharField(db_column='Kode_keluar', max_length=36, blank=True, null=True)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='Kode_barang', max_length=50, blank=True, null=True)  # Field name made lowercase.
    tgl_keluar = models.DateTimeField(blank=True, null=True)
    jumlah = models.FloatField(blank=True, null=True)
    satuan = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Trans_Keluar'


class TransMasuk(models.Model):
    kode_masuk = models.CharField(db_column='Kode_masuk', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='Kode_barang', max_length=200, blank=True, null=True)  # Field name made lowercase.
    tgl_masuk = models.DateTimeField(blank=True, null=True)
    qty = models.FloatField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    satuan = models.CharField(db_column='Satuan', max_length=50, blank=True, null=True)  # Field name made lowercase.
    qty2 = models.FloatField(blank=True, null=True)
    satlain = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    po_no = models.CharField(max_length=110, blank=True, null=True)
    pr_no = models.CharField(max_length=110, blank=True, null=True)
    jsat = models.CharField(max_length=1, blank=True, null=True)
    kode_supplier = models.CharField(max_length=50, blank=True, null=True)
    j = models.CharField(max_length=1, blank=True, null=True)
    harga_po = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    harga = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    item_name = models.CharField(max_length=200, blank=True, null=True)
    id_pemasukan = models.CharField(max_length=50, blank=True, null=True)
    nosj = models.CharField(max_length=150, blank=True, null=True)
    invoiceno = models.CharField(max_length=150, blank=True, null=True)
    do = models.CharField(max_length=150, blank=True, null=True)
    bc = models.CharField(max_length=2, blank=True, null=True)
    kodeedit = models.CharField(max_length=50, blank=True, null=True)
    tgl_invoice = models.DateTimeField(blank=True, null=True)
    tgl_sj = models.DateTimeField(blank=True, null=True)
    blawb = models.CharField(max_length=150, blank=True, null=True)
    vesel_flight = models.CharField(max_length=150, blank=True, null=True)
    freight = models.CharField(max_length=150, blank=True, null=True)
    forwarder = models.CharField(max_length=150, blank=True, null=True)
    bnpb = models.CharField(max_length=150, blank=True, null=True)
    imp = models.CharField(max_length=1, blank=True, null=True)
    rdp = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'Trans_Masuk'


class TransMasukLog(models.Model):
    kode_masuk = models.CharField(db_column='Kode_masuk', max_length=20, blank=True, null=True)  # Field name made lowercase.
    kode_barang = models.CharField(db_column='Kode_barang', max_length=200, blank=True, null=True)  # Field name made lowercase.
    tgl_masuk = models.DateTimeField(blank=True, null=True)
    qty = models.FloatField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    satuan = models.CharField(db_column='Satuan', max_length=50, blank=True, null=True)  # Field name made lowercase.
    qty2 = models.FloatField(blank=True, null=True)
    satlain = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    po_no = models.CharField(max_length=110, blank=True, null=True)
    pr_no = models.CharField(max_length=110, blank=True, null=True)
    jsat = models.CharField(max_length=1, blank=True, null=True)
    kode_supplier = models.CharField(max_length=50, blank=True, null=True)
    j = models.CharField(max_length=1, blank=True, null=True)
    harga_po = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    harga = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    item_name = models.CharField(max_length=200, blank=True, null=True)
    id_pemasukan = models.CharField(max_length=50, blank=True, null=True)
    nosj = models.CharField(max_length=150, blank=True, null=True)
    invoiceno = models.CharField(max_length=150, blank=True, null=True)
    do = models.CharField(max_length=150, blank=True, null=True)
    bc = models.CharField(max_length=2, blank=True, null=True)
    kodeedit = models.CharField(max_length=50, blank=True, null=True)
    tgl_invoice = models.DateTimeField(blank=True, null=True)
    tgl_sj = models.DateTimeField(blank=True, null=True)
    blawb = models.CharField(max_length=150, blank=True, null=True)
    vesel_flight = models.CharField(max_length=150, blank=True, null=True)
    freight = models.CharField(max_length=150, blank=True, null=True)
    forwarder = models.CharField(max_length=150, blank=True, null=True)
    bnpb = models.CharField(max_length=150, blank=True, null=True)
    imp = models.CharField(max_length=1, blank=True, null=True)
    rdp = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'Trans_Masuk_log'


class ImportSub(models.Model):
    material_code = models.CharField(db_column='Material_code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    part_no_mark = models.CharField(db_column='Part_no_mark', max_length=150, blank=True, null=True)  # Field name made lowercase.
    vendor_code = models.CharField(max_length=50, blank=True, null=True)
    material_name = models.CharField(max_length=250, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'import_sub'


class ImportVendor(models.Model):
    nol = models.CharField(max_length=50, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    alamat = models.CharField(db_column='ALAMAT', max_length=250, blank=True, null=True)  # Field name made lowercase.
    telephone = models.CharField(max_length=150, blank=True, null=True)
    fax = models.CharField(max_length=50, blank=True, null=True)
    contactperson = models.CharField(max_length=150, blank=True, null=True)
    purchasedmaterial = models.CharField(max_length=150, blank=True, null=True)
    vendorcode = models.CharField(db_column='Vendorcode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    groupe = models.CharField(db_column='Groupe', max_length=50, blank=True, null=True)  # Field name made lowercase.
    class_field = models.CharField(db_column='class', max_length=50, blank=True, null=True)  # Field renamed because it was a Python reserved word.
    termofpayment = models.CharField(max_length=50, blank=True, null=True)
    anualperformance = models.CharField(max_length=50, blank=True, null=True)
    qms = models.CharField(max_length=50, blank=True, null=True)
    ems = models.CharField(max_length=50, blank=True, null=True)
    auditresult = models.CharField(max_length=50, blank=True, null=True)
    grading = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'import_vendor'


class MasterBarang(models.Model):
    kode_jenis = models.FloatField(blank=True, null=True)
    kode_barang = models.TextField(blank=True, null=True)
    nama_barang = models.TextField(blank=True, null=True)
    spesifikasi = models.TextField(blank=True, null=True)
    kode_departement = models.FloatField(db_column='kode_Departement', blank=True, null=True)  # Field name made lowercase.
    satuan = models.CharField(max_length=50, blank=True, null=True)
    satuan_lain = models.CharField(max_length=50, blank=True, null=True)
    konversi = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)
    keterangan = models.CharField(max_length=150, blank=True, null=True)
    kelas = models.CharField(max_length=1, blank=True, null=True)
    kode_bpcs = models.FloatField(blank=True, null=True)
    vendor_code = models.CharField(max_length=50, blank=True, null=True)
    rdp = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'master_barang'


class MasterBpcs(models.Model):
    kode_bpcs = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    comodity_code = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(db_column='Description', max_length=100, blank=True, null=True)  # Field name made lowercase.
    account_number = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'master_bpcs'


class MasterCoo(models.Model):
    id = models.CharField(primary_key=True, max_length=50, blank=True)
    code = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    qty_total = models.CharField(max_length=100, blank=True, null=True)
    qty_act = models.CharField(max_length=100, blank=True, null=True)
    uom = models.CharField(max_length=100, blank=True, null=True)
    invoice_pts = models.CharField(max_length=100, blank=True, null=True)
    invoice_asli = models.CharField(max_length=100, blank=True, null=True)
    qty_inv = models.CharField(max_length=100, blank=True, null=True)
    price = models.CharField(max_length=100, blank=True, null=True)
    amount_act = models.CharField(max_length=100, blank=True, null=True)
    amount_po = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=50, blank=True, null=True)
    bc_code = models.CharField(max_length=100, blank=True, null=True)
    bc_date = models.CharField(max_length=100, blank=True, null=True)
    bm = models.CharField(max_length=100, blank=True, null=True)
    ppn = models.CharField(max_length=100, blank=True, null=True)
    pph = models.CharField(max_length=100, blank=True, null=True)
    tax = models.CharField(max_length=100, blank=True, null=True)
    coo_number = models.CharField(max_length=100, blank=True, null=True)
    remark = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'master_coo'


class MasterDepartement(models.Model):
    kode_departement = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    departement = models.CharField(db_column='Departement', max_length=50, blank=True, null=True)  # Field name made lowercase.
    keterangan = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    inisial = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'master_departement'


class MasterJenis(models.Model):
    kode_jenis = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    nama_jenis = models.CharField(max_length=50, blank=True, null=True)
    keterangan = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'master_jenis'


class MasterSatuan(models.Model):
    satuan = models.CharField(max_length=50, blank=True, null=True)
    keterangan = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'master_satuan'


class MasterSupplier(models.Model):
    kode_supplier = models.CharField(max_length=50, blank=True, null=True)
    nama_supplier = models.CharField(max_length=150, blank=True, null=True)
    alamat = models.CharField(max_length=250, blank=True, null=True)
    kota = models.CharField(max_length=50, blank=True, null=True)
    provinsi = models.CharField(max_length=50, blank=True, null=True)
    negara = models.CharField(max_length=50, blank=True, null=True)
    kodepos = models.CharField(max_length=50, blank=True, null=True)
    telepon = models.CharField(max_length=150, blank=True, null=True)
    fax = models.CharField(db_column='Fax', max_length=50, blank=True, null=True)  # Field name made lowercase.
    kontak = models.CharField(max_length=150, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    norek = models.CharField(max_length=50, blank=True, null=True)
    atasnama = models.CharField(max_length=50, blank=True, null=True)
    bank = models.CharField(max_length=50, blank=True, null=True)
    npwp = models.CharField(db_column='NPWP', max_length=50, blank=True, null=True)  # Field name made lowercase.
    keterangan = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)
    top_sup = models.CharField(max_length=50, blank=True, null=True)
    kode_2 = models.CharField(max_length=2, blank=True, null=True)
    rdp = models.CharField(db_column='RDP', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'master_supplier'


class MasterUser(models.Model):
    kode_user = models.CharField(max_length=50, blank=True, null=True)
    nama_user = models.CharField(max_length=100, blank=True, null=True)
    kode_departement = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    id_login = models.CharField(max_length=50, blank=True, null=True)
    kode_login = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    keterangan = models.CharField(db_column='Keterangan', max_length=150, blank=True, null=True)  # Field name made lowercase.
    ttd = models.BinaryField(blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'master_user'


class PrintParsial(models.Model):
    nopo = models.CharField(max_length=20, blank=True, null=True)
    po_date = models.CharField(max_length=50, blank=True, null=True)
    eta_date = models.CharField(max_length=50, blank=True, null=True)
    kode_barang = models.CharField(max_length=100, blank=True, null=True)
    nama_barang = models.TextField(blank=True, null=True)
    nama_supplier = models.CharField(max_length=100, blank=True, null=True)
    qty = models.CharField(max_length=50, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    qtyd = models.CharField(max_length=50, blank=True, null=True)
    qtym = models.CharField(max_length=50, blank=True, null=True)
    qtyr = models.CharField(db_column='qtyR', max_length=50, blank=True, null=True)  # Field name made lowercase.
    unit2 = models.CharField(max_length=50, blank=True, null=True)
    dlv_date = models.CharField(max_length=50, blank=True, null=True)
    eta_datee = models.CharField(max_length=50, blank=True, null=True)
    reture_date = models.CharField(max_length=50, blank=True, null=True)
    status_po = models.CharField(max_length=50, blank=True, null=True)
    neg_date = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'print_parsial'


class Submat(models.Model):
    item_no = models.CharField(db_column='Item_No', max_length=255, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=255, blank=True, null=True)  # Field name made lowercase.
    satuan = models.CharField(db_column='Satuan', max_length=255, blank=True, null=True)  # Field name made lowercase.
    bpcs = models.CharField(max_length=255, blank=True, null=True)
    f5 = models.CharField(db_column='F5', max_length=255, blank=True, null=True)  # Field name made lowercase.
    f6 = models.CharField(db_column='F6', max_length=255, blank=True, null=True)  # Field name made lowercase.
    f7 = models.CharField(db_column='F7', max_length=255, blank=True, null=True)  # Field name made lowercase.
    f8 = models.CharField(db_column='F8', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'submat'


class TCalenderL(models.Model):
    link = models.TextField(blank=True, null=True)
    karet = models.TextField(blank=True, null=True)
    remil1 = models.CharField(max_length=1, blank=True, null=True)
    remil2 = models.CharField(max_length=1, blank=True, null=True)
    roll1 = models.CharField(max_length=4, blank=True, null=True)
    roll2 = models.CharField(max_length=4, blank=True, null=True)
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


class TabelLimitHarga(models.Model):
    kode = models.CharField(db_column='Kode', max_length=200, blank=True, null=True)  # Field name made lowercase.
    ketjenisbarang = models.CharField(db_column='KetJenisBarang', max_length=200, blank=True, null=True)  # Field name made lowercase.
    matauang = models.CharField(max_length=10, blank=True, null=True)
    nominal = models.CharField(db_column='Nominal', max_length=100, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(max_length=1, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tabel_Limit_Harga'


class TabelLimitHargaApp(models.Model):
    nopo = models.CharField(db_column='Nopo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    statusnya = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tabel_Limit_Harga_App'


class TabelLimitDifisiApp(models.Model):
    nopr = models.CharField(db_column='Nopr', max_length=50, blank=True, null=True)  # Field name made lowercase.
    kodebarang = models.CharField(max_length=100, blank=True, null=True)
    statusnya = models.CharField(max_length=1, blank=True, null=True)
    tglapp = models.DateTimeField(db_column='tglApp', blank=True, null=True)  # Field name made lowercase.
    userapp = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tabel_Limit_difisi_App'


class TabelPr(models.Model):
    pr_no = models.CharField(db_column='PR_no', max_length=20, blank=True, null=True)  # Field name made lowercase.
    pr_date = models.DateTimeField(db_column='PR_date', blank=True, null=True)  # Field name made lowercase.
    sec_name = models.CharField(max_length=50, blank=True, null=True)
    empl_name = models.CharField(db_column='EMPL_name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    empl_no = models.CharField(max_length=50, blank=True, null=True)
    kode_barang = models.CharField(max_length=200, blank=True, null=True)
    qty = models.FloatField(blank=True, null=True)
    satuan = models.CharField(db_column='Satuan', max_length=50, blank=True, null=True)  # Field name made lowercase.
    qty2 = models.FloatField(blank=True, null=True)
    satlain = models.CharField(max_length=50, blank=True, null=True)
    expec_date = models.DateTimeField(blank=True, null=True)
    note = models.CharField(max_length=200, blank=True, null=True)
    kode_dept = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    ver = models.CharField(max_length=1, blank=True, null=True)
    tgl_ver = models.DateTimeField(blank=True, null=True)
    ver2 = models.CharField(max_length=1, blank=True, null=True)
    tgl_ver2 = models.DateTimeField(blank=True, null=True)
    ver3 = models.CharField(max_length=1, blank=True, null=True)
    tgl_ver3 = models.DateTimeField(blank=True, null=True)
    no_po = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)
    j = models.CharField(max_length=1, blank=True, null=True)
    yang_ver = models.CharField(max_length=25, blank=True, null=True)
    yang_ver2 = models.CharField(max_length=25, blank=True, null=True)
    yang_ver3 = models.CharField(max_length=25, blank=True, null=True)
    kode_relasi = models.CharField(max_length=20, blank=True, null=True)
    item_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tabel_PR'


class TabelDel(models.Model):
    kode_del = models.CharField(max_length=20, blank=True, null=True)
    kode_barang = models.CharField(max_length=50, blank=True, null=True)
    tgl_del = models.DateTimeField(blank=True, null=True)
    qty = models.FloatField(blank=True, null=True)
    satuan = models.CharField(max_length=30, blank=True, null=True)
    qty2 = models.FloatField(blank=True, null=True)
    satlain = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    user_insert = models.CharField(max_length=50, blank=True, null=True)
    user_edit = models.CharField(max_length=50, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    po_no = models.CharField(max_length=20, blank=True, null=True)
    pr_no = models.CharField(max_length=20, blank=True, null=True)
    jsat = models.CharField(max_length=1, blank=True, null=True)
    kode_supplier = models.CharField(max_length=50, blank=True, null=True)
    j = models.CharField(max_length=1, blank=True, null=True)
    item_name = models.TextField(blank=True, null=True)
    neg_date = models.DateTimeField(blank=True, null=True)
    tgl_jen = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tabel_del'


class TabelDispo(models.Model):
    id = models.BigAutoField(primary_key=True)
    po_no = models.CharField(max_length=110, blank=True, null=True)
    kode_barang = models.CharField(max_length=130, blank=True, null=True)
    item_name = models.CharField(max_length=200, blank=True, null=True)
    hrgsats = models.FloatField(blank=True, null=True)
    hrgtots = models.FloatField(blank=True, null=True)
    amounts = models.FloatField(blank=True, null=True)
    dissats = models.FloatField(blank=True, null=True)
    distots = models.FloatField(blank=True, null=True)
    disamounts = models.FloatField(blank=True, null=True)
    tglinsert = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tabel_dispo'


class TabelLogbook(models.Model):
    id_logbook = models.BigIntegerField(blank=True, null=True)
    invoice = models.CharField(max_length=50, blank=True, null=True)
    po_no = models.CharField(max_length=15, blank=True, null=True)
    kode_barang = models.CharField(max_length=100, blank=True, null=True)
    item_name = models.CharField(max_length=200, blank=True, null=True)
    etd = models.DateTimeField(blank=True, null=True)
    neg_date = models.DateTimeField(blank=True, null=True)
    disc = models.FloatField(blank=True, null=True)
    stat = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    qty = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tabel_logbook'


class TabelMatauang(models.Model):
    matauang = models.CharField(max_length=50, blank=True, null=True)
    keterangan = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tabel_matauang'


class TabelPemasukanLog(models.Model):
    id_pemasukan = models.CharField(max_length=50)
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
        db_table = 'tabel_pemasukan_log'


class TabelPrLog(models.Model):
    pr_no = models.CharField(db_column='PR_no', max_length=20, blank=True, null=True)  # Field name made lowercase.
    pr_date = models.DateTimeField(db_column='PR_date', blank=True, null=True)  # Field name made lowercase.
    sec_name = models.CharField(max_length=50, blank=True, null=True)
    empl_name = models.CharField(db_column='EMPL_name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    empl_no = models.CharField(max_length=50, blank=True, null=True)
    kode_barang = models.CharField(max_length=200, blank=True, null=True)
    qty = models.FloatField(blank=True, null=True)
    satuan = models.CharField(db_column='Satuan', max_length=50, blank=True, null=True)  # Field name made lowercase.
    qty2 = models.FloatField(blank=True, null=True)
    satlain = models.CharField(max_length=50, blank=True, null=True)
    expec_date = models.DateTimeField(blank=True, null=True)
    note = models.CharField(max_length=200, blank=True, null=True)
    kode_dept = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    ver = models.CharField(max_length=1, blank=True, null=True)
    tgl_ver = models.DateTimeField(blank=True, null=True)
    ver2 = models.CharField(max_length=1, blank=True, null=True)
    tgl_ver2 = models.DateTimeField(blank=True, null=True)
    ver3 = models.CharField(max_length=1, blank=True, null=True)
    tgl_ver3 = models.DateTimeField(blank=True, null=True)
    no_po = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    user_insert = models.CharField(max_length=25, blank=True, null=True)
    user_edit = models.CharField(max_length=25, blank=True, null=True)
    j = models.CharField(max_length=1, blank=True, null=True)
    yang_ver = models.CharField(max_length=25, blank=True, null=True)
    yang_ver2 = models.CharField(max_length=25, blank=True, null=True)
    yang_ver3 = models.CharField(max_length=25, blank=True, null=True)
    kode_relasi = models.CharField(max_length=20, blank=True, null=True)
    item_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tabel_pr_log'


class TabelRelasi(models.Model):
    kode_relasi = models.CharField(max_length=20, blank=True, null=True)
    kode_barang = models.CharField(max_length=15, blank=True, null=True)
    kode_2 = models.CharField(max_length=2, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    user_insert = models.CharField(max_length=35, blank=True, null=True)
    user_edit = models.CharField(max_length=35, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tabel_relasi'


class TabelRetur(models.Model):
    kode_retur = models.CharField(max_length=20, blank=True, null=True)
    tgl_retur = models.DateTimeField(blank=True, null=True)
    kode_masuk = models.CharField(max_length=20, blank=True, null=True)
    po_no = models.CharField(max_length=20, blank=True, null=True)
    kode_barang = models.CharField(max_length=50, blank=True, null=True)
    qty = models.FloatField(blank=True, null=True)
    satuan = models.CharField(max_length=30, blank=True, null=True)
    qty2 = models.FloatField(blank=True, null=True)
    satlain = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    user_insert = models.CharField(max_length=30, blank=True, null=True)
    user_edit = models.CharField(max_length=30, blank=True, null=True)
    tgl_insert = models.DateTimeField(blank=True, null=True)
    tgl_edit = models.DateTimeField(blank=True, null=True)
    sjenis = models.CharField(max_length=1, blank=True, null=True)
    kode_supplier = models.CharField(max_length=30, blank=True, null=True)
    j = models.CharField(max_length=1, blank=True, null=True)
    pr_no = models.CharField(max_length=25, blank=True, null=True)
    item_name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tabel_retur'


class TabelUpdatepo(models.Model):
    po_no = models.CharField(max_length=50, blank=True, null=True)
    kode_barang = models.CharField(db_column='KODE_BARANG', max_length=50, blank=True, null=True)  # Field name made lowercase.
    item_name = models.CharField(db_column='ITEM_NAME', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tabel_updatepo'


class Tesss(models.Model):
    tess = models.DecimalField(max_digits=18, decimal_places=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tesss'


class UserSeiwa(models.Model):
    no = models.CharField(max_length=10, blank=True, null=True)
    empl_no = models.CharField(max_length=7, blank=True, null=True)
    employee_name = models.CharField(max_length=50, blank=True, null=True)
    sections = models.CharField(max_length=1, blank=True, null=True)
    descr = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_seiwa'

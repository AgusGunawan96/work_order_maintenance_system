from django.shortcuts import render
from django.http import Http404, HttpResponse, JsonResponse
from django.db import connection 
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.db.models import F, OuterRef, Subquery, Value, CharField, Case, When, Value, IntegerField
from django.db.models.functions import Length 
from ceisa_app.forms import ceisaKirimImporHeaderForm, ceisaKirimImporBarangForm,ceisaKirimImporEntitasPengirimForm,ceisaKirimImporEntitasPenjualForm, ceisaKirimImporKemasanForm, ceisaKirimImporDokumenForm, ceisaKirimImporPengangkutForm, ceisaKirimImporKontainerForm
# from ceisa_app.forms 
# CREATE AG
from ceisa_app.forms import ceisaKirimEksporHeaderForm, ceisaKirimEksporBarangForm, ceisaKirimEksporEntitasPengirimForm, ceisaKirimEksporEntitasPenjualForm, ceisaKirimEksporKemasanForm,  ceisaKirimEksporDokumenForm, ceisaKirimEksporPengangkutForm, ceisaKirimEksporKontainerForm, ceisaKirimEksporbankDevisaForm, ceisaKirimEksporkesiapanBarangForm

import jwt 
import time 
import json
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from datetime import date
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import connections
from django.forms import formset_factory
# BUAT API 
import requests

# API GET START 
def get_access_token():
    # Define the API URL
    api_url = "https://apis-gw.beacukai.go.id/nle-oauth/v1/user/login"

    # Define the request payload as a dictionary
    payload = {
        "username": "seiwa_indo",
        "password": "Seindo17520"
    }

    try:
        # Send the POST request to the API
        response = requests.post(api_url, json=payload)

        # Check if the response was successful (HTTP status code 200)
        if response.status_code == 200:
            # Parse the JSON response content
            data = response.json()

            # Extract the access token from the response
            access_token = data.get("item", {}).get("access_token")

            if access_token:
                return access_token
            else:
                return None
        else:
            # Handle errors or other status codes as needed
            return None
    except Exception as e:
        # Handle exceptions if the request fails
        return None

# API GET END

@login_required
def index(request):
    access_token = get_access_token()
    context = {
        'access_token': access_token    }
    return render(request, 'ceisa_app/index.html', context)

# DOKUMEN IMPOR ADD START
def dokumen_impor_add(request):
    # NANTI DISINI DARI FORM AKAN DI CONVERT KE JSON 
    ceisaHForm = ceisaKirimImporHeaderForm()
    ceisaBForm = ceisaKirimImporBarangForm()
    ceisaEPengirimForm = ceisaKirimImporEntitasPengirimForm()
    ceisaEPenjualForm = ceisaKirimImporEntitasPenjualForm()
    ceisaKemForm = ceisaKirimImporKemasanForm()
    ceisaKonForm = ceisaKirimImporKontainerForm()
    ceisaDForm = ceisaKirimImporDokumenForm()
    ceisaPForm = ceisaKirimImporPengangkutForm()
    KemasanFormSet = formset_factory(ceisaKirimImporKemasanForm, extra=1)
    KontainerFormSet = formset_factory(ceisaKirimImporKontainerForm, extra=1)
    DokumenFormSet = formset_factory(ceisaKirimImporDokumenForm, extra=1)
    
    context = {
        'ceisaHForm'  : ceisaHForm,
        'ceisaBForm'  : ceisaBForm,
        'ceisaEPengirimForm'    : ceisaEPengirimForm,
        'ceisaEPenjualForm'    : ceisaEPenjualForm,
        'ceisaKemForm'    : KemasanFormSet,
        'ceisaKonForm'    : KontainerFormSet,
        'ceisaDForm'    : DokumenFormSet,
        'ceisaPForm'    : ceisaPForm,
    }
    return render(request, 'ceisa_app/dokumen_impor_add.html', context )
# DOKUMEN IMPOR ADD END

# DOKUMEN EKSPOR ADD START 
def dokumen_ekspor_add(request):
    ceisaHEForm = ceisaKirimEksporHeaderForm()
    ceisaBEForm = ceisaKirimEksporBarangForm()
    ceisaEEPengirimForm = ceisaKirimEksporEntitasPengirimForm()
    ceisaEEPenjualForm = ceisaKirimEksporEntitasPenjualForm()
    ceisaEKemForm = ceisaKirimEksporKemasanForm()
    ceisaEKonForm = ceisaKirimEksporKontainerForm()
    ceisaEDForm = ceisaKirimEksporDokumenForm()
    ceisaEPForm = ceisaKirimEksporPengangkutForm()
    ceisaEBDForm =  ceisaKirimEksporbankDevisaForm()
    ceisaEBForm = ceisaKirimEksporkesiapanBarangForm()
    KemasanFormSett = formset_factory(ceisaKirimEksporKemasanForm, extra=1)
    KontainerFormSett = formset_factory(ceisaKirimEksporKontainerForm, extra=1)
    DokumenFormSett = formset_factory(ceisaKirimEksporDokumenForm, extra=1)
    

    context = {
        'ceisaHEForm' : ceisaHEForm,
        'ceisaBEForm' : ceisaBEForm,
        'ceisaEEPengirimForm' : ceisaEEPengirimForm,
        'ceisaEEPenjualForm' : ceisaEEPenjualForm,
        'ceisaEKemForm' : KemasanFormSett,
        'ceisaEKonForm' : KontainerFormSett,
        'ceisaEDForm' : DokumenFormSett,
        'ceisaEPForm' : ceisaEPForm, 
        'ceisaEBDForm' : ceisaEBDForm,
        'ceisaEBForm' : ceisaEBForm,    
    }
    return render(request, 'ceisa_app/dokumen_ekspor_add.html', context )
# DOKUMEN EKSPOR ADD END 

@csrf_exempt  # For simplicity, using csrf_exempt; consider CSRF protection in production
def update_data(request):
    if request.method == 'POST':
        access_token = get_access_token()
        # print(access_token)
            # Define the API URL
        api_url = "https://apis-gw.beacukai.go.id/openapi/document"

        # Define the headers with the Authorization header
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        # request.POST.get('kodeTps', '')
        # CIF = fob + freight + asuransi -> Generate
        # Mari kita inisiasikan Value apabila boleh 0 
        po_numbers = request.POST.getlist('po_numbers[]', [])  # Get the list of 'po_numbers[]' from the POST data
        formatted_po_numbers = ','.join(["'" + number + "'" for number in po_numbers])
            # Create a placeholder for each PO number
        # placeholders = ', '.join(['%s'] * len(po_numbers))
        # Build the SQL query with placeholders
        database_alias = 'poseiwa_db'  # Replace with the alias of the desired database
        connection = connections[database_alias]
        with connection.cursor() as cursor:
          query = """
                  SELECT A.po_no, A.kode_barang, A.qty AS 'Satuan', A.unit, A.unit_price, A.amount AS 'CFR',
                         C.nama_barang AS 'Tipe', B.nama_supplier
                  FROM dbo.T_PO A
                  LEFT JOIN dbo.master_supplier B ON A.kode_supplier = B.kode_supplier
                  LEFT JOIN dbo.master_barang C ON A.kode_barang = C.kode_barang
                  WHERE A.po_no IN ('23071062','23071061','23071059')
                  """
          a = cursor.execute(query)
          rows = cursor.fetchall()
        # print(rows)
        # print(po_numbers)
        # print(formatted_po_numbers)
        # return HttpResponse("True")
        # Asuransi
        asuransi_value =  request.POST.get('asuransi','')
        default_asuransi_value = 0
        asuransi_value = float(asuransi_value) if asuransi_value else default_asuransi_value
        # Biaya Pengurang
        biayaPengurang_value = request.POST.get('biayaPengurang','')
        default_biayaPengurang_value = 0 
        biayaPengurang_value = float(biayaPengurang_value) if biayaPengurang_value else default_biayaPengurang_value
        # Biaya Tambahan 
        biayaTambahan_value = request.POST.get('biayaTambahan','')
        default_biayaTambahan_value = 0
        biayaTambahan_value = float(biayaTambahan_value) if biayaTambahan_value else default_biayaTambahan_value
        # Bruto 
        bruto_value       =request.POST.get('bruto','')
        default_bruto_value = 0
        bruto_value = float(bruto_value) if bruto_value else default_bruto_value
        # CIF
        cif_value   = request.POST.get('cif', '')
        default_cif_value = 0
        cif_value = float(cif_value) if cif_value else default_cif_value
        # FOB
        fob_value = request.POST.get('fob', '')
        default_fob_value = 0
        fob_value = float(fob_value) if fob_value else default_fob_value
        # Freight
        freight_value = request.POST.get('freight','')
        default_freight_value = 0
        freight_value = float(freight_value) if freight_value else default_freight_value
        # Harga Penyerahan
        hargaPenyerahan_value = request.POST.get('hargaPenyerahan','')
        default_hargaPenyerahan_value = 0
        hargaPenyerahan_value = float(hargaPenyerahan_value) if hargaPenyerahan_value else default_hargaPenyerahan_value
        # Jumlah Kontainer 
        jumlahKontainer_value = request.POST.get('jumlahKontainer','')
        default_jumlahKontainer_value = 0
        jumlahKontainer_value = float(jumlahKontainer_value) if jumlahKontainer_value else default_jumlahKontainer_value
        # Jumlah Tanda Pengaman
        tandaPengaman_value = request.POST.get('jumlahTandaPengaman','')
        default_tandaPengaman_value = 0
        tandaPengaman_value = float(tandaPengaman_value) if tandaPengaman_value else default_tandaPengaman_value
        # Netto
        netto_value = request.POST.get('netto','')
        default_netto_value = 0
        netto_value = float(netto_value) if netto_value else default_netto_value
        # Nilai Barang
        nilaiBarang_value = request.POST.get('nilaiBarang','')
        default_nilaiBarang_value = 0
        nilaiBarang_value = float(nilaiBarang_value) if nilaiBarang_value else default_nilaiBarang_value
        # Nilai Incoterm
        nilaiIncoterm_value = request.POST.get('nilaiIncoterm','')
        default_nilaiIncoterm_value = 0
        nilaiIncoterm_value = float(nilaiIncoterm_value) if nilaiIncoterm_value else default_nilaiIncoterm_value
        # Nilai Maklon
        nilaiMaklon_value = request.POST.get('nilaiMaklon','')
        default_nilaiMaklon_value = 0
        nilaiMaklon_value = float(nilaiMaklon_value) if nilaiMaklon_value else default_nilaiMaklon_value
        # Seri
        seri_value = request.POST.get('seri','')
        default_seri_value = 0
        seri_value = float(seri_value) if seri_value else default_seri_value
        # Total Dana sawit
        totalDanaSawit_value = request.POST.get('totalDanaSawit','')
        default_totalDanaSawit_value = 0
        totalDanaSawit_value = float(totalDanaSawit_value) if totalDanaSawit_value else default_totalDanaSawit_value
        # Volume
        volume_value = request.POST.get('volume','')
        default_volume_value = 0
        volume_value = float(volume_value) if volume_value else default_volume_value
        # VD
        vd_value = request.POST.get('vd','')
        default_vd_value = 0
        vd_value = float(vd_value) if vd_value else default_vd_value
        # NDPBM
        ndpbm_value = request.POST.get('ndpbm','')
        default_ndpbm_value = 0
        ndpbm_value = float(ndpbm_value) if ndpbm_value else default_ndpbm_value

        # CREATE AG EKSPOR
        # Asuransi 
        asuransi_valuee =  request.POST.get('asuransi','')
        default_asuransi_valuee = 0
        asuransi_valuee = float(asuransi_valuee) if asuransi_valuee else default_asuransi_valuee
        # Bruto 
        bruto_valuee = request.POST.get('bruto', '')
        default_bruto_valuee = 0
        bruto_valuee = float(bruto_valuee) if bruto_valuee else default_bruto_valuee
        # Cif
        cif_valuee = request.POST.get('cif', '')
        default_cif_valuee = 0
        cif_valuee = float(cif_valuee) if cif_valuee else default_cif_valuee
        # Fob
        fob_valuee = request.POST.get('fob', '')
        default_fob_valuee = 0
        fob_valuee = float(fob_valuee) if fob_valuee else default_fob_valuee
        # Freight
        freight_valuee = request.POST.get('freight', '')
        default_freight_valuee = 0
        freight_valuee = float(freight_valuee) if freight_valuee else default_freight_valuee
        # JumlahKontainer
        jumlahKontainer_valuee = request.POST.get('jumlahKontainer', '')
        default_jumlahKontainer_valuee = 0
        jumlahKontainer_valuee = float(jumlahKontainer_valuee) if jumlahKontainer_valuee else default_jumlahKontainer_valuee
        # Ndpbm
        ndpbm_valuee = request.POST.get('ndpbm', '')
        default_ndpbm_valuee = 0
        ndpbm_valuee = float(ndpbm_valuee) if ndpbm_valuee else default_ndpbm_valuee
        # Netto
        netto_valuee = request.POST.get('netto', '')
        default_netto_valuee = 0
        netto_valuee = float(netto_valuee) if netto_valuee else default_netto_valuee
        # NIlai Maklon
        nilaiMaklon_valuee = request.POST.get('nilaiMaklon', '')
        default_nilaiMaklon_valuee = 0
        nilaiMaklon_valuee = float(nilaiMaklon_valuee) if nilaiMaklon_valuee else default_nilaiMaklon_valuee
        # Seri
        seri_valuee = request.POST.get('seri', '')
        default_seri_valuee = 0
        seri_valuee = float(seri_valuee) if seri_valuee else default_seri_valuee
        # Total Dana Sawit
        totalDanaSawit_valuee = request.POST.get('totalDanaSawit', '')
        default_totalDanaSawit_valuee = 0
        totalDanaSawit_valuee = float(totalDanaSawit_valuee) if totalDanaSawit_valuee else default_totalDanaSawit_valuee

        
        data_dict = {
            "asalData": "S", #Otomatis
            "asuransi": asuransi_value,
            "biayaPengurang": biayaPengurang_value,
            "biayaTambahan": biayaTambahan_value,
            "bruto": bruto_value,
            "cif": cif_value,
            "disclaimer": request.POST.get('disclaimer',''),
            "flagVd": request.POST.get('flagVd',''),
            "fob": fob_value,
            "freight": freight_value,
            "hargaPenyerahan": hargaPenyerahan_value,
            "idPengguna": "ABCDE", #otomatis
            "jabatanTtd": "PRESIDENT DIRECTOR", #otomatis
            "jumlahKontainer": jumlahKontainer_value,
            "jumlahTandaPengaman": tandaPengaman_value,
            "kodeAsuransi": request.POST.get('kodeAsuransi',''),
            "kodeCaraBayar": request.POST.get('kodeAsuransi',''),
            "kodeDokumen": "20",
            "kodeIncoterm": request.POST.get('kodeIncoterm',''),
            "kodeJenisImpor": request.POST.get('kodeJenisImpor',''),
            "kodeJenisNilai": request.POST.get('kodeJenisNilai',''),
            "kodeJenisProsedur": request.POST.get('kodeJenisProsedur',''),
            "kodeKantor": "050100", #otomatis
            "kodePelMuat": "JPOSA",
            "kodePelTransit": "",
            "kodePelTujuan": "IDCGK",
            "kodeTps": "GDWD",
            "kodeTutupPu": request.POST.get('kodeTutupPu',''),
            "kodeValuta": request.POST.get('kodeJenisNilai',''), 
            "kotaTtd": "JAKARTA", #otomatis
            "namaTtd": "YASUTSUGU KUNIHIRO", #otomatis
            "ndpbm": ndpbm_value,
            "netto": netto_value,
            "nilaiBarang": nilaiBarang_value,
            "nilaiIncoterm": nilaiIncoterm_value,
            "nilaiMaklon": nilaiMaklon_value,
            "nomorAju": request.POST.get('nomorAju',''),
            # "nomorBc11": "032095", #hide
            "posBc11": "0017",
            "seri": seri_value,
            "subPosBc11": "00030000",
            "tanggalAju": "2023-09-04",
            "tanggalBc11": "2023-09-03",
            "tanggalTiba": "2023-09-03",
            "tanggalTtd": "2023-09-04",
            "totalDanaSawit": totalDanaSawit_value,
            "volume": volume_value,
            "vd": vd_value,
        }


        # Create a list for 'barang' data
        data_dict["barang"] = [
            {
        "asuransi": 0,
        "bruto": 0,
        "cif": 1234000.89,
        "cifRupiah": 1234000.89,
        "diskon": 0,
        "fob": 0,
        "freight": 0,
        "hargaEkspor": 0,
        "hargaPatokan": 0,
        "hargaPenyerahan": 0,
        "hargaPerolehan": 0,
        "hargaSatuan": 345.67,
        "hjeCukai": 0,
        "isiPerKemasan": 0,
        "jumlahBahanBaku": 0,
        "jumlahDilekatkan": 0,
        "jumlahKemasan": 1,
        "jumlahPitaCukai": 0,
        "jumlahRealisasi": 0,
        "jumlahSatuan": 5,
        "kapasitasSilinder": 0,
        "kodeJenisKemasan": "CT",
        "kodeKondisiBarang": "1",
        "kodeNegaraAsal": "JP",
        "kodeSatuanBarang": "RO",
        "merk": "-",
        "ndpbm": 1200.56,
        "netto": 5.6,
        "nilaiBarang": 0,
        "nilaiDanaSawit": 0,
        "nilaiDevisa": 0,
        "nilaiTambah": 0,
        "pernyataanLartas": "Y",
        "persentaseImpor": 0,
        "posTarif": "49089000",
        "saldoAkhir": 0.0,
        "saldoAwal": 0.0,
        "seriBarang": 1,
        "seriBarangDokAsal": 0,
        "seriIjin": 0,
        "tahunPembuatan": 0,
        "tarifCukai": 0,
        "tipe": "ISURB01",
        "uraian": "LABELS FOR RUBBER BELTS(MARK)",
        "volume": 0,
        "barangDokumen": [
          {
            "seriDokumen": "1"
          }
        ],
        "barangTarif": [
          {
            "jumlahSatuan": 1,
            "kodeFasilitasTarif": "1",
            "kodeJenisPungutan": "BM",
            "kodeJenisTarif": "1",
            "nilaiBayar": 123456.78,
            "nilaiFasilitas": 0.0,
            "seriBarang": 1,
            "tarif": 0.0,
            "tarifFasilitas": 100.0
          },
          {
            "jumlahSatuan": 1,
            "kodeFasilitasTarif": "1",
            "kodeJenisPungutan": "PPN",
            "kodeJenisTarif": "1",
            "nilaiBayar": 123456.78,
            "nilaiFasilitas": 0.0,
            "seriBarang": 1,
            "tarif": 10.0,
            "tarifFasilitas": 100.0
          },
          {
            "jumlahSatuan": 1,
            "kodeFasilitasTarif": "1",
            "kodeJenisPungutan": "PPH",
            "kodeJenisTarif": "1",
            "nilaiBayar": 123456.78,
            "nilaiFasilitas": 0.0,
            "seriBarang": 1,
            "tarif": 2.5,
            "tarifFasilitas": 100.0
          }
        ],
        "barangVd": [],
        # "barangVd": [
        #   {
        #     "kodeJenisVd": "NTR",
        #     "nilaiBarangVd": 123
        #   }
        # ],
        "barangSpekKhusus": [],
        "barangPemilik": []
      },
      {
        "asuransi": 2.34,
        "bruto": 23,
        "cif": 567,
        "cifRupiah": 567,
        "diskon": 165.84,
        "fob": 0,
        "freight": 0,
        "hargaEkspor": 0,
        "hargaPatokan": 0,
        "hargaPenyerahan": 0,
        "hargaPerolehan": 0,
        "hargaSatuan": 7.89,
        "hjeCukai": 300000,
        "isiPerKemasan": 15,
        "jumlahBahanBaku": 0,
        "jumlahDilekatkan": 0,
        "jumlahKemasan": 1,
        "jumlahPitaCukai": 4,
        "jumlahRealisasi": 0,
        "jumlahSatuan": 60,
        "kapasitasSilinder": 0,
        "kodeJenisKemasan": "PK",
        "kodeKondisiBarang": "1",
        "kodeNegaraAsal": "CU",
        "kodeSatuanBarang": "PCE",
        "merk": "-",
        "ndpbm": 14330,
        "netto": 170.25,
        "nilaiBarang": 0,
        "nilaiDanaSawit": 0,
        "nilaiDevisa": 0,
        "nilaiTambah": 0,
        "pernyataanLartas": "Y",
        "persentaseImpor": 0,
        "posTarif": "24029010",
        "saldoAkhir": 0.0,
        "saldoAwal": 0.0,
        "seriBarang": 2,
        "spesifikasiLain": "SPEK BARANG 1",
        "seriBarangDokAsal": 0,
        "seriIjin": 0,
        "tahunPembuatan": 0,
        "tarifCukai": 0,
        "tipe": "TIPE BARANG 2",
        "uraian": "BARANG 2",
        "volume": 0,
        "barangTarif": [
          {
            "jumlahSatuan": 60,
            "kodeFasilitasTarif": "1",
            "kodeJenisPungutan": "BM",
            "kodeJenisTarif": "1",
            "nilaiBayar": 87654.32,
            "nilaiFasilitas": 0,
            "seriBarang": 2,
            "tarif": 40,
            "tarifFasilitas": 100
          },
          {
            "jumlahKemasan": 4,
            "jumlahSatuan": 60,
            "kodeFasilitasTarif": "7",
            "kodeJenisPungutan": "CTEM",
            "kodeJenisTarif": "2",
            "kodeKemasan": "BX",
            "kodeKomoditiCukai": "3",
            "kodeSatuanBarang": "PCE",
            "kodeSubKomoditiCukai": "CRT",
            "nilaiBayar": 0,
            "nilaiFasilitas": 0,
            "nilaiSudahDilunasi": 6600000,
            "seriBarang": 2,
            "tarif": 110000
          },
          {
            "jumlahSatuan": 60,
            "kodeFasilitasTarif": "1",
            "kodeJenisPungutan": "PPH",
            "kodeJenisTarif": "1",
            "kodeSatuanBarang": "PCE",
            "nilaiBayar": 534015.41,
            "nilaiFasilitas": 0,
            "seriBarang": 2,
            "tarif": 2.5,
            "tarifFasilitas": 100
          },
          {
            "kodeJenisTarif": "1",
            "jumlahSatuan": 60,
            "kodeFasilitasTarif": "1",
            "kodeSatuanBarang": "PCE",
            "kodeJenisPungutan": "PPN",
            "nilaiBayar": 140000,
            "nilaiFasilitas": 0,
            "seriBarang": 1,
            "tarif": 10,
            "tarifFasilitas": 100
          }
        ],
        "barangVd": [],
        "barangDokumen": [],
        "barangSpekKhusus": [],
        "barangPemilik": []
      }
        ]
        # UNTUK ALAMAT 
        data_dict["entitas"]    = [
       {
        "alamatEntitas": "JL.LOMBOK I, BLOK M 2-2, KAW.INDUSTRI MM2100, GANDAMEKAR - GANDAMEKAR, CIKARANG BARAT, BEKASI, JAWA BARAT",
        "kodeEntitas": "1",
        "kodeJenisApi": "01",
        "kodeJenisIdentitas": "5",
        "kodeStatus": "AEO",
        "namaEntitas": "SEIWA INDONESIA",
        "nibEntitas": "8120010090198",
        "nomorIdentitas": "010712495055000",
        "seriEntitas": 1   
      },
      {
        "alamatEntitas": "JL.LOMBOK I, BLOK M 2-2, KAW.INDUSTRI MM2100, GANDAMEKAR - GANDAMEKAR, CIKARANG BARAT, BEKASI, JAWA BARAT",
        "kodeEntitas": "7",
        "kodeJenisIdentitas": "5",
        "namaEntitas": "SEIWA INDONESIA",
        "nomorIdentitas": "010712495055000",
        "seriEntitas": 2
      },

      {
        "alamatEntitas": request.POST.get('alamatEntitasPengirim',''),
        "kodeEntitas": "9",
        "kodeNegara": request.POST.get('kodeNegaraPengirim',''),
        "namaEntitas": request.POST.get('namaEntitasPengirim',''),
        "seriEntitas": 3
      },
      {
        "alamatEntitas": request.POST.get('alamatEntitasPenjual',''),
        "kodeEntitas": "10",
        "kodeNegara": request.POST.get('kodeNegaraPenjual',''),
        "namaEntitas": request.POST.get('namaEntitasPenjual',''),
        "seriEntitas": 4
      },
      {
        "alamatEntitas": "JL.LOMBOK I, BLOK M 2-2, KAW.INDUSTRI MM2100, GANDAMEKAR - GANDAMEKAR, CIKARANG BARAT, BEKASI, JAWA BARAT",
        "kodeEntitas": "11",
        "kodeJenisIdentitas": "5",
        "namaEntitas": "SEIWA INDONESIA",
        "nomorIdentitas": "010712495055000",
        "seriEntitas": 5
      }
        ]
        data_dict["kemasan"]    = [
        {
        "jumlahKemasan": 2,
        "kodeJenisKemasan": "CT",
        "merkKemasan": "Tanpa Merk",
        "seriKemasan": 1
      },
              {
        "jumlahKemasan": 2,
        "kodeJenisKemasan": "CT",
        "merkKemasan": "Tanpa Merk",
        "seriKemasan": 1
      }
        ]
    #     data_dict["kontainer"]  = [
    #     {
    #     "kodeJenisKontainer": "4",
    #     "kodeTipeKontainer": "99",
    #     "kodeUkuranKontainer": "40",
    #     "nomorKontainer": "",
    #     "seriKontainer": 1
    #   }
    #     ]
        data_dict["dokumen"]    = [
        {
        "idDokumen": "1",
        "kodeDokumen": "380",
        "kodeFasilitas": "",
        "nomorDokumen": "MPTS03847",
        "seriDokumen": 1,
        "tanggalDokumen": "2023-09-01"
      },
      {
        "idDokumen": "3",
        "kodeDokumen": "740",
        "kodeFasilitas": "",
        "nomorDokumen": "HEI-1406 3991",
        "seriDokumen": 3,
        "tanggalDokumen": "2023-09-01"
      }
      ,
    #   {
    #     "idDokumen": "4",
    #     "kodeDokumen": "860",
    #     "kodeFasilitas": "54",
    #     "namaFasilitas": "Preferensi Tarif Importasi Asean-China (ACFTA)",
    #     "nomorDokumen": "ACFTA 01",
    #     "seriDokumen": 4,
    #     "tanggalDokumen": "2021-12-25"
    #   }
        ]
        data_dict["pengangkut"] = [
                  {
        "kodeBendera": request.POST.get('kodeBendera',''),
        "namaPengangkut": request.POST.get('namaPengangkut',''),
        "nomorPengangkut": request.POST.get('nomorPengangkut',''),
        "kodeCaraAngkut": request.POST.get('kodeCaraAngkut',''),
        "seriPengangkut": 1
      }
        ]

        data_dict = {
            "asalData": "S",
            "asuransi": asuransi_valuee,
            "bruto": bruto_valuee,
            "cif": cif_valuee,
            "disclaimer": request.POST.get('disclaimer',''),
            "flagCurah": request.POST.get('flagCurah',''),
            "flagMigas": request.POST.get('flagMigas',''),
            "fob": fob_valuee,
            "freight": freight_valuee,
            "idPengguna": "ABCDE", #otomatis
            "jabatanTtd": "PRESIDENT DIRECTOR", #otomatis
            "jumlahKontainer": jumlahKontainer_valuee,
            "kodeAsuransi": request.POST.get('kodeAsuransi',''),
            "kodeCaraBayar": request.POST.get('kodeAsuransi',''),
            "kodeCaraDagang": request.POST.get('kodeCaraDagang', ''),
            "kodeDokumen": "20",
            "kodeIncoterm": request.POST.get('kodeIncoterm', ''),
            "kodeJenisEkspor": request.POST.get('kodeJenisEkspor', ''),
            "kodeJenisNilai": request.POST.get('kodeJenisNilai',''),
            "kodeJenisProsedur": request.POST.get('kodeJenisProsedur',''),           
            "kodeKantor": "050100", #otomatis
            "kodeKantorEkspor": "050100",
            "kodeKantorMuat": "050100",
            "kodeKantorPeriksa": "050100",
            "kodeKategoriEkspor": "21",
            "kodeLokasi": "2",
            "kodeNegaraTujuan": "SA",
            "kodePelBongkar": "IDCGK",
            "kodePelEkspor": "JPOSA",
            "kodePelMuat": "JPOSA",
            "kodePelTujuan": "IDCGK",
            "kodeTps": "GDWD",
            "kodeValuta": request.POST.get('kodeJenisNilai',''), 
            "kotaTtd": "JAKARTA",
            "namaTtd": "YASUTSUGU KUNIHIRO", #otomatis
            "ndpbm": ndpbm_valuee,
            "netto": netto_valuee,
            "nilaiMaklon": nilaiMaklon_valuee,
            "nomorAju": request.POST.get('nomorAju',''),
            # "nomorBc11": "032095", #hide
            "posBc11": "0017",
            "seri": seri_valuee,
            "subPosBc11": "00030000",
            "tanggalAju": "2023-09-04",
            "tanggalBc11": "2023-09-03",
            "tanggalEkspor": "2023-09-03",
             "tanggalPeriksa": "2023-09-03",
            "tanggalTtd": "2023-09-04",
            "totalDanaSawit": totalDanaSawit_valuee,
        }  

        data_dict["barang"] =  [
          {
            "cif": 0,
            "cifRupiah": 0,
            "fob": 7654000,
            "hargaEkspor": 0,
            "hargaPatokan": 0,
            "hargaPerolehan": 0,
            "hargaSatuan": 4.56,
            "jumlahKemasan": 1,
            "jumlahSatuan": 12,
            "kodeAsalBahanBaku": "0",
            "kodeBarang": "BARANG 1",
            "kodeDaerahAsal": "3175",
            "kodeDokumen": "30",
            "kodeJenisKemasan": "CT",
            "kodeNegaraAsal": "JP",
            "kodeSatuanBarang": "RO",
            "merk": "-",
            "ndpbm": 14250,
            "netto": 335.5,
            "nilaiBarang": 0,
            "nilaiDanaSawit": 0,
            "posTarif": "12345678",
            "seriBarang": 1,
            "spesifikasiLain": "ISURB01",
            "tipe": "ISURB01",
            "ukuran": "LABELS FOR RUBBER BELTS(MARK)",
            "uraian": "LABELS FOR RUBBER BELTS(MARK)",
            "volume": 388.5,
            "barangDokumen": [
              {
                "seriDokumen": 1
              }
            ],
            "barangPemilik": [],
            "barangTarif": []
          }
        ]
 
        data_dict["entitas"] = [
            {
              "alamatEntitas": "JL.LOMBOK I, BLOK M 2-2, KAW.INDUSTRI MM2100, GANDAMEKAR - GANDAMEKAR, CIKARANG BARAT, BEKASI, JAWA BARAT",
              "kodeEntitas": "1",
              "kodeJenisIdentitas": "5",
              "namaEntitas": "SEIWA INDONESIA",
              "nibEntitas": "8120010090198",
              "nomorIdentitas": "010712495055000",
              "seriEntitas": 1
            },
            {
              "alamatEntitas": "JL.LOMBOK I, BLOK M 2-2, KAW.INDUSTRI MM2100, GANDAMEKAR - GANDAMEKAR, CIKARANG BARAT, BEKASI, JAWA BARAT",
              "kodeEntitas": "7",
              "kodeJenisIdentitas": "5",
              "namaEntitas": "SEIWA INDONESIA",
              "nibEntitas": "8120010090198",
              "nomorIdentitas": "010712495055000",
              "seriEntitas": 2
            },
            {
              "alamatEntitas": request.POST.get('alamatEntitasPengirim',''),
              "kodeEntitas": "9",
              "kodeNegara":  request.POST.get('kodeNegaraPengirim',''),
              "namaEntitas":  request.POST.get('namaEntitasPengirim',''),
              "seriEntitas": 3
            },
            {
              "alamatEntitas": request.POST.get('alamatEntitasPenjual',''),
              "kodeEntitas": "10",
              "kodeNegara": request.POST.get('kodeNegaraPenjual',''),
              "namaEntitas": request.POST.get('namaEntitasPenjual',''),
              "seriEntitas": 4
            }
         ]
        data_dict["kemasan"] = [
            {
              "jumlahKemasan": 2,
              "kodeJenisKemasan": "CT",
              "merkKemasan": "Tanpa Merk",
              "seriKemasan": 1
            }
          ]
            #     data_dict["kontainer"]  = [
            #     {
            #     "kodeJenisKontainer": "4",
            #     "kodeTipeKontainer": "99",
            #     "kodeUkuranKontainer": "40",
            #     "nomorKontainer": "",
            #     "seriKontainer": 1
            #   }
            #     ]
        data_dict["kemasan"] = [
            {
              "idDokumen": "1",
              "kodeDokumen": "380",
              "nomorDokumen": "MPTS03847",
              "seriDokumen": 1,
              "tanggalDokumen": "2023-09-01"
            },
            {
              "idDokumen": "3",
              "kodeDokumen": "740",
              "nomorDokumen": "HEI-1406 3991",
              "seriDokumen": 3,
              "tanggalDokumen": "2023-09-01"
            }
          ]

        data_dict["pengangkut"] = [
            {
              "kodeBendera": request.POST.get('kodeBendera',''),
              "namaPengangkut": request.POST.get('namaPengangkut',''),
              "nomorPengangkut": request.POST.get('nomorPengangkut',''),
              "kodeCaraAngkut": request.POST.get('kodeCaraAngkut',''),
              "seriPengangkut": 1
            }
          ]
        data_dict["bankDevisa"] = [
            {
              "kodeBank": "9",
              "seriBank": 1
            }
          ]
        data_dict["kesiapanBarang"] = [
            {
              "kodeJenisBarang": "1",
              "kodeJenisGudang": "2",
              "namaPic": "YASUTSUGU KUNIHIRO",
              "alamat": "JAKARTA",
              "nomorTelpPic": "081111111111",
              "lokasiSiapPeriksa": "JAKARTA",
              "kodeCaraStuffing": "7",
              "kodeJenisPartOf": "2",
              "tanggalPkb": "2021-12-25",
              "waktuSiapPeriksa": "2022-11-22",
              "jumlahContainer20": 825,
              "jumlahContainer40": 181
            }
        ]
        
        # Serialize the dictionary to JSON
        json_data = json.dumps(data_dict)
        # DISINI AKAN BERAKHIR FUNGSINYA
        # Respond with a JSON response to the client
        print(requests.post(api_url, headers=headers, json=data_dict))

        try:
            # Send the POST request to the API with the access token in the header
            response = requests.post(api_url, headers=headers, json=data_dict)
            
            if response.status_code == 200:
                # Parse the JSON response content
                response_data = response.json()
                return JsonResponse(response_data)  # Return JSON response for success
            else:
                # Handle errors or other status codes as needed
                error_message = f"Error: {response.status_code}"
                error_response = {
                    'error_message': error_message,
                }
                return JsonResponse(error_response, status=response.status_code)

        except Exception as e:
            # Handle exceptions if the request fails
            error_message = str(e)
            error_response = {
                'error_message': error_message,
            }
            return JsonResponse(error_response, status=500)  # Return JSON response for internal server error

    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)  # Return 405 Method Not Allowed
    #     try:
    #         # Send the POST request to the API with the access token in the header
    #         response = requests.post(api_url, headers=headers, json=data_dict)
    #         # Check if the response was successful (HTTP status code 200)
    #         if response.status_code == 200:
    #             # Parse the JSON response content
    #             response_data = response.json()
    #             return response_data
    #         else:
    #             # Handle errors or other status codes as needed
    #             print(f"Error: {response.status_code}")
    #             print(response.text)
    #             return None
    #     except Exception as e:
    #             # Handle exceptions if the request fails
    #             print(f"Error: {str(e)}")
    #             print(f"Response Status Code: {response.status_code}")
    #             print(f"Response Text: {response.text}")
    #             return response.text

    #     response_data = {'message': 'Data Barang berhasil ditambahkanz'}
    #     return JsonResponse(response_data)
    # else:
    #     return JsonResponse({'message': 'Invalid request method'})
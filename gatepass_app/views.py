from django.shortcuts import render
from django.http import Http404, HttpResponse, JsonResponse
from django.db import connection 
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.db.models import F, OuterRef, Subquery, Value, CharField, Case, When, Value, IntegerField
from django.db.models.functions import Length 
from gatepass_app.models import gatepassPermision, gatepassHeader, gatepassDetail
# from gatepass_app.forms 
import jwt 
import time 
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from datetime import date
# Create your views here.
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    context = {
    }
    
    return render(request, 'gatepass_app/index.html', context )

@login_required
def tamu_index(request):
    return HttpResponse('jadi ini merupakan index dari Tamu')

@login_required
def kirim_barang_menu(request):
    return HttpResponse('jadi ini merupakan menu dari kirim barang ')

@login_required
def kirim_barang_local(request):
    return HttpResponse('jadi ini merupakan kirim barang local')

@login_required
def kirim_barang_import(request):
    return HttpResponse('jadi ini merupakan kirim barang import')

@login_required
def ambil_barang_index(request):
    return HttpResponse('jadi ini index dari ambil barang yang langsung ke form finish good')


# JADI INI AKAN JADI SEBUAH API YANG CONNECT KEDALAM  VISUAL STUDIONYA 
def post_tamu_masuk(request, GatepassNo, TanggalIn, NamaTamu, NamaPerusahaan, NomorIdentitas, Tujuan, TujuanDetail, NomorKendaraan, JenisKendaraan, BertemuDengan, Department, Status, Security):
    user = User.objects.filter(username = Security).first()
    security_id = gatepassPermision.objects.filter(user = user).first()
    formatted_date = datetime.strptime(TanggalIn, "%d-%m-%Y").strftime("%Y-%m-%d %H:%M:%S.%f%z")
    data_gatepassHeader_insert = {
        "security"        : security_id, 
        "ngatepass"       : GatepassNo, 
        "nama_tamu"       : NamaTamu, 
        "nomor_identitas" : NomorIdentitas, 
        "nomor_kendaraan" : NomorKendaraan, 
        "jenis_kendaraan" : JenisKendaraan, 
        "tanggal_masuk"   : formatted_date, 
        "status"          : Status, 
        "tipe"            : "Tamu", 
    }
    gatepassHeader_record = gatepassHeader(**data_gatepassHeader_insert)
    gatepassHeader_record.save()
    data_gatepassDetail_insert = {
        "gatepassH"         : gatepassHeader_record, 
        "nama_perusahaan"   : NamaPerusahaan, 
        "bertemu_dengan"    : BertemuDengan, 
        "department"        : Department, 
        "tujuanH"           : Tujuan, 
        "tujuanD"           : TujuanDetail, 
    }
    gatepassDetail_record = gatepassDetail(**data_gatepassDetail_insert)
    gatepassDetail_record.save()

    return JsonResponse('True', safe=False)





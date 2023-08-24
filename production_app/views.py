from django.shortcuts import render
from django.http import Http404, HttpResponse, JsonResponse
from django.db import connections
from django.contrib.auth.models import User, Group
from production_app.models import POCVLRecord, masterTagVL
from django.core.paginator import Paginator
from django.db.models import F, OuterRef, Subquery, Value, CharField, Case, When, Value, IntegerField
from django.db.models.functions import Length
# Create your views here.


def index(request):
    database_alias = 'sfc_db'  # Replace with the alias of the desired database
    connection = connections[database_alias]
    # Execute a SQL query
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Ab.Stand,Ab.cprodline,Ab.cshift,sum(Ab.qty) QTYPCS,count(Ab.Drum) DRUM,Ab.coperatorid,Ab.coperatorname From (SELECT SUBSTRING(cpatno,8,1) Stand,iif(left(citemno,4)='ARRG','RCVS',IIF(LEFT(citemno,4) ='ARRD','RCVS',cprodline)) cprodline, cshift,(nincomingqty) qty,(Cpatno) Drum,coperatorid,coperatorname FROM LSFC Where coperation='90'     
            AND SUBSTRING(cpatno,8,1) not in ('1','2','3','4','5','6','7','8','9') 
            AND cprodline in ('RB5','RBL')) ab
            Group By  Ab.Stand,ab.cprodline,ab.cshift,SUBSTRING(ab.Drum,8,1),ab.coperatorid,ab.coperatorname 
            Order By SUBSTRING(ab.Drum,8,1),ab.cshift Asc """)
        rows = cursor.fetchall()
    context = {
        'rows': rows
    }

    return render(request, 'production_app/index.html', context)

def insert_plc_database(request, Username, soNo, itemNo, poc, pocStatus, vib, vibStatus, runOut, runOutStatus, weightKg, weightN, centerDistance, topWidth, thickness, widthStatus, thicknessStatus, shift):
    user = User.objects.filter(username = Username).first()
    item_desc = masterTagVL.objects.filter(item_no = itemNo).first()
    data_to_insert = {
        'user'              : user,
        'so_no'             : soNo,
        'item_no'           : itemNo,
        'item_desc'         : item_desc.item_desc,
        'poc'               : poc,
        'poc_status'        : pocStatus,
        'vib'               : vib,
        'vib_status'        : vibStatus,
        'run_out'           : runOut,
        'run_out_status'    : runOutStatus,
        'weight_kg'         : weightKg,
        'weight_n'          : weightN,
        'center_distance'   : centerDistance,
        'top_width'         : topWidth,
        'thickness'         : thickness,
        'top_width_status'  : widthStatus,
        'thickness_status'  : thicknessStatus,
        'shift'             : shift,
    }
    object_record = POCVLRecord(**data_to_insert)
    object_record.save()
    return HttpResponse('True')

def report_poc_vl_index(request):
    reports_poc_vl = POCVLRecord.objects.all()
    context = {
        'reports'              : reports_poc_vl,
    }
    return render(request, 'production_app/pocvl_report_index.html', context )

import jwt
import time
from django.template.loader import render_to_string

def report_finishing_index(request):
    METABASE_SITE_URL = "http://172.16.202.225:3000"
    METABASE_SECRET_KEY = "cc81afc24eece1a20ef494e8b352bd73bd63c649c531c958a20aefdbcb4005e1"

    payload = {
      "resource": {"dashboard": 5},
      "params": {

      },
      "exp": round(time.time()) + (60 * 10) # 10 minute expiration
    }
    token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")

    iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#bordered=true&titled=true"
    html = render_to_string('production_app/report_finishing_index.html', {
        'title': 'Embedding Metabase',
        'iframeUrl': iframeUrl
    })
    return HttpResponse(html)

def report_poc_vl_filter_table_data_ajax(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    shift1 = request.GET.get('shift_1')
    shift3 = request.GET.get('shift_2')
    so_number = request.GET.get('so_number')

    queryset = POCVLRecord.objects.order_by('-created_at')

    if start_date:
        queryset = queryset.filter(created_at__gte=start_date)
    if end_date:
        queryset = queryset.filter(created_at__lte=end_date)
    if shift1 == "true":
        queryset = queryset.filter(shift=1)
    if shift3 == "true":
        queryset = queryset.filter(shift=3)
    
    if so_number:
        queryset = queryset.filter(so_no__icontains=so_number)
    
    # Calculate item_length using Subquery and annotate it
    queryset = queryset.annotate(
        item_length=F('poc') - Subquery(
            masterTagVL.objects.filter(item_no=OuterRef('item_no')).values('poc')[:1]
        )
    )

    # Define the actualLength calculation using Case and When expressions
    actual_length_calculation = Case(
        When(item_length__range=[-17.49, -12.5], then=Value(-15)),
        When(item_length__range=[-12.49, -7.5], then=Value(-10)),
        When(item_length__range=[-7.49, -2.5], then=Value(-5)),
        When(item_length__range=[-2.49, 2.5], then=Value(0)),
        When(item_length__range=[2.51, 7.5], then=Value(5)),
        When(item_length__range=[7.51, 12.5], then=Value(10)),
        When(item_length__range=[12.51, 17.5], then=Value(15)),
        default=Value(0),  # Default value if none of the conditions match
        output_field=IntegerField()
    )
    
    # Apply the actualLength calculation to the queryset
    queryset = queryset.annotate(
        item_length=actual_length_calculation
    )

    page_number = request.GET.get('page')
    items_per_page = 9999999
    paginator = Paginator(queryset, items_per_page)
    page_obj = paginator.get_page(page_number)

    data = [{'shift': item.shift,
             'nokar': item.user.username,
             'nama': item.user.first_name + " " + item.user.last_name,
             'sono': item.so_no,
             'itemno': item.item_no,
             'itemdesc': item.item_desc,
             'poc': item.poc,  # Use the original value of poc
             'pocStatus': item.poc_status,
             'vib': item.vib,
             'vibStatus': item.vib_status,
             'runout': item.run_out,
             'runoutStatus': item.run_out_status,
             'thickness': item.thickness,
             'thicknessStatus': item.thickness_status,
             'topWidth': item.top_width,
             'topWidthStatus': item.top_width_status,
             'length': item.item_length,  # Use the calculated item_length field
             'created_at': item.created_at} for item in page_obj]

    return JsonResponse({'data': data, 'has_next': page_obj.has_next()})


# def report_poc_vl_filter_table_data_ajax(request):
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')
#     shift1 = request.GET.get('shift_1')
#     shift3 = request.GET.get('shift_2')
#     so_number = request.GET.get('so_number') # Get the SO number parameter
#     # Log the values of shift1 and shift3
#     # Modify your queryset based on the filtering parameters
#     queryset = POCVLRecord.objects.order_by('-created_at')

#     if start_date:
#         queryset = queryset.filter(created_at__gte=start_date)
#         print("created_at__gte:", start_date)
#     if end_date:
#         queryset = queryset.filter(created_at__lte=end_date)
#     if shift1 == "true":
#         queryset = queryset.filter(shift=1)
#         print("Shift1:", shift1)
#     if shift3 == "true":
#         queryset = queryset.filter(shift=3)
#         print("Shift3:", shift3)

#     if so_number: # Apply the SO number filter if provided
#         queryset = queryset.filter(so_no__icontains=so_number)

#     page_number = request.GET.get('page')
#     item_per_page = 9999999 # ini untuk mengetahui berapa banyak yang akan kita akan paginate 
#     paginator = Paginator(queryset,item_per_page)
#     page_obj = paginator.get_page(page_number)


#     data = [{'shift': item.shift, 
#              'nokar': item.user.username, 
#              'nama': item.user.first_name +" "+ item.user.last_name, 
#              'sono': item.so_no, 
#              'itemno': item.item_no, 
#              'itemdesc': item.item_desc, 
#              'poc': item.poc, 
#              'pocStatus': item.poc_status, 
#              'vib': item.vib, 
#              'vibStatus': item.vib_status, 
#              'runout': item.run_out, 
#              'runoutStatus': item.run_out_status, 
#              'thickness': item.thickness, 
#              'thicknessStatus': item.thickness_status, 
#              'topWidth': item.top_width, 
#              'topWidthStatus': item.top_width_status, 
#              'created_at': item.created_at} for item in page_obj]
#     return JsonResponse({'data': data, 'has_next': page_obj.has_next()})

# def report_poc_vl_get_table_data_ajax(request):
#     page_number = request.GET.get('page')
#     item_per_page = 10 # ini untuk mengetahui berapa banyak yang akan kita akan paginate 
#     queryset = POCVLRecord.objects.order_by('-created_at')
#     paginator = Paginator(queryset,item_per_page)
#     page_obj = paginator.get_page(page_number)


#     data = [{'shift': item.shift, 
#              'nokar': item.user.username, 
#              'nama': item.user.first_name +" "+ item.user.last_name, 
#              'sono': item.so_no, 
#              'itemno': item.item_no, 
#              'itemdesc': item.item_desc, 
#              'poc': item.poc, 
#              'pocStatus': item.poc_status, 
#              'vib': item.vib, 
#              'vibStatus': item.vib_status, 
#              'runout': item.run_out, 
#              'runoutStatus': item.run_out_status, 
#              'thickness': item.thickness, 
#              'thicknessStatus': item.thickness_status, 
#              'topWidth': item.top_width, 
#              'topWidthStatus': item.top_width_status, 
#              'created_at': item.created_at} for item in page_obj]
#     return JsonResponse({'data': data, 'has_next': page_obj.has_next()})



# Shift 
# No. Kar 




# so_no
# center_distance
# weight_kg
# weight_n
# shift

# Nama
# SO
# Item No 
# Item Desc 
# POC 
# POC Status 
# VIB 
# VIB Status 
# RUNOUT 
# RUNOUT Status 
# Thickness 
# Thickness Status
# Top Width 
# Top Width status 
# created at 
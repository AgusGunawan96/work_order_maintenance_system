from django.urls import path
from production_app import views
from django.conf.urls.static import static
from django.conf import settings

app_name ='production_app'

urlpatterns = [
    path('insert_plc_database/<str:Username>/<str:soNo>/<str:itemNo>/<str:poc>/<str:pocStatus>/<str:vib>/<str:vibStatus>/<str:runOut>/<str:runOutStatus>/<str:weightKg>/<str:weightN>/<str:centerDistance>/<str:topWidth>/<str:thickness>/<str:widthStatus>/<str:thicknessStatus>/<int:shift>', views.insert_plc_database, name='insert_plc_database'),
    # REPORT POC VL START 
    path('report_poc_vl/index', views.report_poc_vl_index, name = 'report_poc_vl_index'),
    path('report_finishing/index', views.report_finishing_index, name = 'report_finishing_index'),
    # path('report_poc_vl/get_table_data_ajax', views.report_poc_vl_get_table_data_ajax, name = 'report_poc_vl_get_table_data_ajax'),
    path('report_poc_vl/report_poc_vl_filter_table_data_ajax', views.report_poc_vl_filter_table_data_ajax, name = 'report_poc_vl_filter_table_data_ajax'),
    # REPORT POC VL END
    path('', views.index, name = 'index'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

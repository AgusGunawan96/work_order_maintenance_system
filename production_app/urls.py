from django.urls import path
from production_app import views

app_name ='production_app'

urlpatterns = [
    path('insert_plc_database/<str:Username>/<str:soNo>/<str:itemNo>/<str:poc>/<str:pocStatus>/<str:vib>/<str:vibStatus>/<str:runOut>/<str:runOutStatus>/<str:weightKg>/<str:weightN>/<str:centerDistance>', views.insert_plc_database, name='insert_plc_database'),
    path('', views.index, name = 'index'),
]

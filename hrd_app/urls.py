from django.urls import path
from hrd_app import views
from django.conf.urls.static import static
from django.conf import settings

app_name ='hrd_app'

urlpatterns = [

    path('', views.index, name = 'index'),
    
    # BIODATA START
    path('biodata/biodata_index/', views.biodata_index, name = 'biodata_index'),
    # BIODATA END

    # CUTI START
    path('cuti/cuti_index/', views.cuti_index, name = 'cuti_index'),
    # CUTI END
    
    # KESEJAHTERAAN START
    path('kesejahteraan/kesejahteraan_index/', views.kesejahteraan_index, name = 'kesejahteraan_index'),
    # KESEJAHTERAAN END

    # MEDICAL TRAIN START
    path('medicalTrain/medical_train_index/', views.medical_train_index, name = 'medical_train_index'),
    path('medicalTrain/medical_train_complete_index/', views.medical_train_complete_index, name = 'medical_train_complete_index'),
    path('medicalTrain/medical_train_reject_index/', views.medical_train_reject_index, name = 'medical_train_reject_index'),
    path('medicalTrain/medical_train_add/', views.medical_train_add, name = 'medical_train_add'),
    path('medicalTrain/medical_train_delete/<int:medical_id>', views.medical_train_delete, name = 'medical_train_delete'),
    path('medicalTrain/medical_train_detail/<int:medical_id>', views.medical_train_detail, name = 'medical_train_detail'),
    path('medicalTrain/medical_train_download_report/<int:medical_id>', views.medical_train_download_report, name = 'medical_train_download_report'),
    path('medicalTrain/medical_train_download_report_excel/', views.medical_train_download_report_excel, name = 'medical_train_download_report_excel'),
    path('medicalTrain/medical_submit_atasan/<int:medical_id>/<str:is_approve>/<str:is_reject>', views.medical_submit_atasan, name = 'medical_submit_atasan'),
    path('medicalTrain/medical_submit_hr/<int:medical_id>/<str:is_approve>/<str:is_reject>', views.medical_submit_hr, name = 'medical_submit_hr'),
    path('medicalTrain/medical_print_atasan/', views.medical_print_atasan, name = 'medical_print_atasan'),
    # MEDICAL TRAIN END

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

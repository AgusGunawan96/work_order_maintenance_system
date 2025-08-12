# master_app/urls.py
from django.urls import path
from . import views

app_name = 'master_app'

urlpatterns = [
    # ===== DASHBOARD & INDEX =====
    path('', views.index, name='index'),  # Root index dengan routing otomatis
    path('dashboard/', views.dashboard_view, name='dashboard'),  # Dashboard khusus SDBM
    
    # ===== USER MANAGEMENT =====
    path('users/', views.userIndex, name='user_index'),
    path('users/sync/', views.userSynchronize, name='user_sync'),
    
    # ===== EMPLOYEE PROFILE (SDBM) =====
    path('profile/', views.employee_profile_view, name='employee_profile'),
    path('employee-info/<str:employee_number>/', views.get_employee_info, name='employee_info'),
    
    # ===== CREATE FUNCTIONS =====
    path('create/userdata/', views.CreateUserdata, name='create_userdata'),
    path('create/user-info/', views.CreateUserInfoData, name='create_user_info'),
    path('create/ip-registered/', views.CreateIPAddressRegistered, name='create_ip_registered'),
    path('create/ip-unregistered/', views.CreateIPAddressUnRegistered, name='create_ip_unregistered'),
    path('create/material/', views.CreateMaterial, name='create_material'),
    path('create/vendor/', views.CreateVendor, name='create_vendor'),
    path('create/approval-medical/', views.CreateApprovalMedical, name='create_approval_medical'),
    path('create/info-keluarga/', views.CreateInfoKeluarga, name='create_info_keluarga'),
    path('create/coa-code/', views.CreateCoaCode, name='create_coa_code'),
    path('create/location/', views.CreateLocation, name='create_location'),
    path('create/remain/', views.CreateRemain, name='create_remain'),
    path('create/province/', views.CreateProvince, name='create_province'),
    path('create/regency/', views.CreateRegency, name='create_regency'),
    path('create/district/', views.CreateDistrict, name='create_district'),
    path('create/village/', views.CreateVillage, name='create_village'),
    path('create/master-tag-vl/', views.CreateMasterTagVL, name='create_master_tag_vl'),
    
    # ===== UPDATE FUNCTIONS =====
    path('update/remain/', views.UpdateRemain, name='update_remain'),
    path('update/user-profile-gender-status/', views.UpdateUpdateUserProfileInfoGenderStatus, name='update_user_profile_gender_status'),
    path('update/user-profile-tanggal-lahir/', views.UpdateUserProfileInfoTanggalLahir, name='update_user_profile_tanggal_lahir'),
    
    # ===== UPLOAD FUNCTIONS =====
    path('upload/master-vl/', views.UploadMasterVL, name='upload_master_vl'),
    path('upload/master-low-modulus/', views.UploadMasterLowModulus, name='upload_master_low_modulus'),
    path('upload/master-medical/', views.UploadMasterMedical, name='upload_master_medical'),
    
    # ===== DOWNLOAD FUNCTIONS =====
    path('download/csv-master-vl/', views.download_csv_mastervl, name='download_csv_master_vl'),
    path('download/csv-master-low-modulus/', views.download_csv_masterLowModulus, name='download_csv_master_low_modulus'),
    path('download/csv-master-medical/', views.download_csv_mastermedical, name='download_csv_master_medical'),
    
    # ===== API untuk Visual Basic dan sistem eksternal =====
    # API POCVL (untuk Visual Basic)
    path('api/pocvl/check-user/<str:Username>/<str:Password>/', views.pocvl_check_user, name='pocvl_check_user'),
    path('api/pocvl/get-fullname/<str:Username>/', views.getFullName, name='get_fullname'),
    
    # API Gatepass
    path('api/gatepass/check-user/<str:Username>/<str:Password>/', views.gatepass_check_user, name='gatepass_check_user'),
    path('api/gatepass/get-security-name/<str:Username>/', views.getSecurityName, name='get_security_name'),
    
    # API SDBM (untuk sistem eksternal yang menggunakan SDBM)
    path('api/sdbm/check-user/<str:employee_number>/<str:password>/', views.sdbm_api_check_user, name='sdbm_api_check_user'),
    path('api/sdbm/employee-info/<str:employee_number>/', views.get_employee_info, name='sdbm_employee_info'),
    
    # ===== LEGACY API (backward compatibility) =====
    path('api/get-fullname/<str:Username>/', views.getFullName, name='legacy_get_fullname'),
    path('api/get-security-name/<str:Username>/', views.getSecurityName, name='legacy_get_security_name'),
]
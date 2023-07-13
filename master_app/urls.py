from django.urls import path
from master_app import views

app_name ='master_app'

urlpatterns = [
    path('', views.index, name = 'index'),

    # CHECK START
    path('pocvl_check_user/<str:Username>/<str:Password>', views.pocvl_check_user, name='pocvl_check_user'),
    # CHECK END

    # path('CreateUserdata/', views.CreateUserdata, name='CreateUserdata'),
    # path('CreateCoaCode/', views.CreateCoaCode, name= 'CreateCoaCode')
    # path('CreateUserInfoData/', views.CreateUserInfoData, name='CreateUserInfoData'),
    # path('CreateIPAddressUnRegistered/', views.CreateIPAddressUnRegistered, name='CreateIPAddressUnRegistered'),
    # path('CreateMaterial/', views.CreateMaterial, name='CreateMaterial'),
    # path('CreateVendor/', views.CreateVendor, name='CreateVendor'),
    # path('CreateApprovalMedical/', views.CreateApprovalMedical, name='CreateApprovalMedical'),
    # path('CreateInfoKeluarga/', views.CreateInfoKeluarga, name='CreateInfoKeluarga'),
    # path('CreateLocation/', views.CreateLocation, name='CreateLocation'),
    # path('CreateRemain/', views.CreateRemain, name='CreateRemain'),
    # path('CreateProvince/', views.CreateProvince, name='CreateProvince'),
    # path('CreateRegency/', views.CreateRegency, name='CreateRegency'),
    # path('CreateDistrict/', views.CreateDistrict, name='CreateDistrict'),
    # path('CreateVillage/', views.CreateVillage, name='CreateVillage'),


    path('UpdateRemain/', views.UpdateRemain, name='UpdateRemain'),
    # path('UpdateUpdateUserProfileInfoGenderStatus/', views.UpdateUpdateUserProfileInfoGenderStatus, name='UpdateUpdateUserProfileInfoGenderStatus'),
    # path('UpdateUserProfileInfoTanggalLahir/', views.UpdateUserProfileInfoTanggalLahir, name='UpdateUserProfileInfoTanggalLahir'),
]

from django.urls import path
from master_app import views

app_name ='master_app'

urlpatterns = [
    path('', views.index, name = 'index'),
    # path('CreateUserdata/', views.CreateUserdata, name='CreateUserdata'),
    # path('CreateUserInfoData/', views.CreateUserInfoData, name='CreateUserInfoData'),
    # path('CreateIPAddressUnRegistered/', views.CreateIPAddressUnRegistered, name='CreateIPAddressUnRegistered'),
    # path('CreateMaterial/', views.CreateMaterial, name='CreateMaterial'),
    # path('CreateVendor/', views.CreateVendor, name='CreateVendor'),
    # path('CreateApprovalMedical/', views.CreateApprovalMedical, name='CreateApprovalMedical'),
    # path('CreateInfoKeluarga/', views.CreateInfoKeluarga, name='CreateInfoKeluarga'),
    # path('UpdateUpdateUserProfileInfoGenderStatus/', views.UpdateUpdateUserProfileInfoGenderStatus, name='UpdateUpdateUserProfileInfoGenderStatus'),
    # path('UpdateUserProfileInfoTanggalLahir/', views.UpdateUserProfileInfoTanggalLahir, name='UpdateUserProfileInfoTanggalLahir'),
]

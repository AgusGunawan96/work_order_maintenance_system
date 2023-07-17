from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.urls import path, reverse_lazy

# LIBRARY FOR IMPORT DATA
from django.http import JsonResponse, HttpResponse
from csv import reader
from django.contrib.auth.models import User, Group
from master_app.models import UserProfileInfo, UserKeluargaInfo, Province, Regency, District, Village
from it_app.models import IPAddress, Hardware, ListLocation
from qc_app.models import rirMaterial, rirVendor
from hrd_app.models import medicalApprovalList, medicalRemain
from accounting_app.models import coaCode
from django.contrib.auth.decorators import user_passes_test
import csv
# Create your views here.
from django.contrib.auth.hashers import check_password
from datetime import datetime



# @permission_required('polls.add_choice')
@login_required
def index(request):
    # context={"breadcrumb":{"parent":"Color Version","child":"Layout Light"}}
    master_app = Group.objects.get(name="master_app").user_set.all()
    accounting_app = Group.objects.get(name="accounting_app").user_set.all()
    costcontrol_app = Group.objects.get(name="costcontrol_app").user_set.all()
    engineering_app = Group.objects.get(name="engineering_app").user_set.all()
    ga_app = Group.objects.get(name="ga_app").user_set.all()
    hrd_app = Group.objects.get(name="hrd_app").user_set.all()
    ie_app = Group.objects.get(name="ie_app").user_set.all()
    it_app = Group.objects.get(name="it_app").user_set.all()
    ppc_app = Group.objects.get(name="ppc_app").user_set.all()
    qc_app = Group.objects.get(name="qc_app").user_set.all()
    sales_app = Group.objects.get(name="sales_app").user_set.all()
    warehouse_app = Group.objects.get(name="warehouse_app").user_set.all()

    if request.user in it_app:
        return render(request,'it_app/dashboard.html')
    else:
        if request.user in master_app:
            return render(request, 'master_app/dashboard.html')
        else:
            if request.user in accounting_app:
                return render(request, 'accounting_app/dashboard.html')
            else:
                if request.user in costcontrol_app:
                    return render(request, 'costcontrol_app/dashboard.html')
                else:
                    if request.user in engineering_app:
                        return render(request, 'engineering_app/dashboard.html')
                    else:
                        if request.user in ga_app:
                            return render(request, 'ga_app/dashboard.html')
                        else:
                            if request.user in hrd_app:
                                return render(request, 'hrd_app/dashboard.html')
                            else:
                                if request.user in ie_app:
                                    return render(request, 'ie_app/dashboard.html')
                                else:
                                    if request.user in ppc_app:
                                        return render(request, 'ppc_app/dashboard.html')
                                    else:
                                        if request.user in qc_app:
                                            return render(request,'qc_app/dashboard.html')
                                        else:
                                            if request.user in sales_app:
                                                return render(request, 'sales_app/dashboard.html')
                                            else:
                                                if request.user in warehouse_app:
                                                    return render(request, 'warehouse_app/dashboard.html')
                                                else:
                                                    return render (request, 'master_app/dashboard.html')


    # return render(request,'it_app/index.html')

# VISUALBASIC START
def pocvl_check_user(request, Username, Password):
    user = User.objects.filter(username = Username).first()
    password_check = check_password(Password, user.password)
    if password_check:
        return HttpResponse('True')
    else:
        return HttpResponse('False')
    
def getFullName(request, Username):
    user = User.objects.filter(username__contains = Username).first()
    fullname = user.first_name +' '+ user.last_name
    return HttpResponse(fullname)

# VISUALBASIC END
# CREATE START
@login_required
def CreateUserdata(request):
    with open('templates/csv/list_user.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for id,first_name, last_name, username,  password, date_joined, *__ in csvf:
            user = User(id=id, username=username, first_name=first_name, last_name = last_name, is_staff = True, date_joined = date_joined ,is_active = True )
            d = datetime.strptime(user.date_joined, "%m/%d/%Y")
            user.date_joined = d.strftime("%Y-%m-%d-%H:%M:%S")
            user.set_password(password)
            data.append(user)
        User.objects.bulk_create(data)
    return JsonResponse('user csv is now working', safe=False)

@login_required
def CreateUserInfoData(request):
    with open('templates/csv/list_user_info.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for user_id, department_id, division_id, section_id, position, is_supervisor, is_manager, is_bod, *__ in csvf:
            user = UserProfileInfo(user_id=user_id, department_id=department_id, division_id = division_id, section_id = section_id
            ,  position = position, is_supervisor = is_supervisor, is_manager = is_manager, is_bod = is_bod
             )
            data.append(user)
        UserProfileInfo.objects.bulk_create(data)
    return JsonResponse('user Info csv is now working', safe=False)

@login_required
def place_value(number): 
    return ("{:,}".format(number)) 

# LANJUTAN
@login_required
def CreateIPAddressRegistered(request):
    with open('templates/csv/list_registered_ip.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for hardware_id, ip, name, *__ in csvf:
            IPAddressRegistered = IPAddress(hardware_id = hardware_id,ip = ip, name = name, is_used  = True)
            data.append(IPAddressRegistered)
        IPAddress.objects.bulk_create(data)
    return JsonResponse('IP Address Registered csv is now working', safe=False)

@login_required
def CreateIPAddressUnRegistered(request):
    with open('templates/csv/list_unregistered_ip.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for ip, *__ in csvf:
            IPAddressUNRegistered = IPAddress(ip = ip, is_used  = False)
            data.append(IPAddressUNRegistered)
        IPAddress.objects.bulk_create(data)
    return JsonResponse('IP Address Un Registered csv is now working', safe=False)

@login_required
def CreateMaterial(request):
    with open('templates/csv/material.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for name,classification_id,condition,location, classification_status, *__ in csvf:
            material = rirMaterial(name = name, classification_id = classification_id, condition = condition, location = location, classification_status = classification_status )
            data.append(material)
        rirMaterial.objects.bulk_create(data)
    return JsonResponse('Material csv is now working', safe=False)

@login_required 
def CreateVendor(request):
    with open('templates/csv/vendor.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for vendor_company, *__ in csvf:
            vendor = rirVendor(vendor_company = vendor_company)
            data.append(vendor)
        rirVendor.objects.bulk_create(data)
    return JsonResponse('Vendor csv is now working', safe=False)

@login_required
def CreateApprovalMedical(request):
    with open('templates/csv/ApprovalMedical.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for user_id, is_foreman, is_supervisor, is_manager, is_hr, *__ in csvf:
            ApprovalMedical = medicalApprovalList(user_id = user_id, is_foreman = is_foreman, is_supervisor = is_supervisor, is_manager = is_manager, is_hr = is_hr)
            data.append(ApprovalMedical)
        medicalApprovalList.objects.bulk_create(data)
    return JsonResponse('ApprovalMedical csv is now working', safe=False)

@login_required
def CreateInfoKeluarga(request):
    with open('templates/csv/userkeluargainfo.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for user_id, tanggal_lahir, gender, hubungan,nama_lengkap, *__ in csvf:
            user_table_id = User.objects.filter(username = user_id).first()
            InfoKeluarga = UserKeluargaInfo(user_id = user_table_id.id, tanggal_lahir = tanggal_lahir, gender = gender, hubungan = hubungan, nama_lengkap = nama_lengkap)
            data.append(InfoKeluarga)
        UserKeluargaInfo.objects.bulk_create(data)
    return JsonResponse('userkeluargainfo csv is now working', safe=False)

@login_required
def CreateCoaCode(request):
    with open('templates/csv/coacode.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for account_code, cost_centre, description, status, structure_code,  *__ in csvf:
            coacode = coaCode(account_code = account_code, cost_centre = cost_centre, description = description, status = status, structure_code = structure_code, )
            data.append(coacode)
        coaCode.objects.bulk_create(data)
    return JsonResponse('coacode csv is now working', safe=False)

@login_required
def CreateLocation(request):
    with open('templates/csv/list_location.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for location_name,   *__ in csvf:
            coacode = ListLocation(location_name = location_name,)
            data.append(coacode)
        ListLocation.objects.bulk_create(data)
    return JsonResponse('Location csv is now working', safe=False)

@login_required
def CreateRemain(request):
    with open('templates/csv/list_remain.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for user_id, marital_status, limit, used, remain,    *__ in csvf:
            user_table_id = User.objects.filter(username = user_id).first()
            medical_remain = medicalRemain(user = user_table_id, marital_status = marital_status, limit = limit, used = used, remain = remain,)
            data.append(medical_remain)
        medicalRemain.objects.bulk_create(data)
    return JsonResponse('Remain csv is now working', safe=False)
    return HttpResponse('jadi ini merupakan Create Remain')

@login_required
def CreateProvince(request):
    with open('templates/csv/list_province.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for id, province_name,   *__ in csvf:
            province = Province(id = id, province_name = province_name,)
            data.append(province)
        Province.objects.bulk_create(data)
    return JsonResponse('Province csv is now working', safe=False)

@login_required
def CreateRegency(request):
    with open('templates/csv/list_regency.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for id, province_id, regency_name,   *__ in csvf:
            regency = Regency(id = id, province_id = province_id, regency_name = regency_name,)
            data.append(regency)
        Regency.objects.bulk_create(data)
    return JsonResponse('Regency csv is now working', safe=False)

@login_required
def CreateDistrict(request):
    with open('templates/csv/list_district.csv', 'r', encoding="utf-8") as csv_file:
        csvf = reader(csv_file)
        data = []
        for id, regency_id ,district_name,   *__ in csvf:
            district = District(id = id, regency_id = regency_id, district_name = district_name,)
            data.append(district) 
        District.objects.bulk_create(data)
    return JsonResponse('District csv is now working', safe=False)

@login_required
def CreateVillage(request):
    with open('templates/csv/list_village.csv', 'r', encoding="utf-8") as csv_file:
        csvf = reader(csv_file)
        data = []
        for id, district_id, village_name,   *__ in csvf:
            village = Village(id = id, district_id = district_id, village_name = village_name,)
            data.append(village)
        Village.objects.bulk_create(data)
    return JsonResponse('Village csv is now working', safe=False)

# CREATE END

# UPDATE START

# def UpdateRemain(request):
#     # Read CSV File
#     with open('hrd_app/templates/csv/updateremain.csv') as f:
#         reader = csv.reader(f)
#         data = list(reader)
        
#     # Retrieve objects from the database and update fields
#     updates = []
#     invalid_rows = []
    
#     for row in data:
#         if len(row) != 5:
#             invalid_rows.append(row)
#             continue
        
#         username_row, marital_status_row, limit_row, used_row, remain_row = row
        
#         user = UserProfileInfo.objects.filter(user__username=username_row).first()
#         medical = medicalRemain.objects.filter(user=user).first()
        
#         if medical:
#             id_value = medical.id
#             marital_status_value = marital_status_row
#             limit_value = limit_row
#             used_value = used_row
#             remain_value = remain_row
#             updates.append(medicalRemain(id=id_value, marital_status=marital_status_value, limit=limit_value, used=used_value, remain=remain_value))
    
#     # Perform bulk update
#     medicalRemain.objects.bulk_update(updates, ['marital_status', 'limit', 'used', 'remain'])
    
#     # Prepare the response
#     response_data = {
#         'message': 'updateremain csv is now working',
#         'invalid_rows': invalid_rows,
#     }
    
#     return JsonResponse(response_data, safe=False)

@login_required
def UpdateRemain(request):
    # Read CSV File
    with open('hrd_app/templates/csv/updateremain.csv') as f:
        reader = csv.reader(f)
        data = list(reader)
    # Retrieve objects from database and update fields
        updates = []
    # Return the response object
        for username_row,marital_status_row,limit_row,used_row,remain_row , *__ in data:
            user = UserProfileInfo.objects.filter(user__username__contains=username_row).first()
            if user:
                medical = medicalRemain.objects.filter(user = user.id ).first()
                if medical:
                    id_value= medical.id 
                    marital_status_value = marital_status_row
                    limit_value =limit_row
                    used_value = used_row
                    remain_value = remain_row
                    updates.append(medicalRemain(id = id_value, marital_status = marital_status_value, limit = limit_value, used = used_value, remain = remain_value))
        medicalRemain.objects.bulk_update(updates, ['marital_status','limit','used','remain'])
    return JsonResponse('updateremain csv is now working', safe=False)

@login_required
def UpdateUpdateUserProfileInfoGenderStatus(request):
    # Read CSV file
    with open('templates/csv/updateuserprofileinfogenderandstatus.csv') as f:
        reader = csv.reader(f)
        data = list(reader)
    # Retrieve objects from database and update fields
    updates = []
    # Return the response object
    for username_row,contract_row,is_permanent_row,gender_row in data:
        user = UserProfileInfo.objects.filter(user__username=username_row).first()
        if user:
            id_value = user.id
            is_contract_value   = contract_row
            is_permanent_value  = is_permanent_row
            gender_value    = gender_row
            updates.append(UserProfileInfo(id=id_value, is_contract   = is_contract_value, is_permanent  = is_permanent_value, gender = gender_value))

    UserProfileInfo.objects.bulk_update(updates, ['is_contract', 'is_permanent', 'gender'])
    return JsonResponse('updateuserprofileinfogenderandstatus csv is now working', safe=False)

@login_required
def UpdateUserProfileInfoTanggalLahir(request):
    # Read CSV File
    with open('templates/csv/userprofileinfoupdatetanggallahir.csv') as f:
        reader = csv.reader(f)
        data = list(reader)
    # Retrieve objects from database and update fields
    updates = []
    # Return the response object
    for username_row, tanggal_lahir in data:
            user = UserProfileInfo.objects.filter(user__username=username_row).first()
            if user:
                id_value = user.id
                tanggal_lahir_value = tanggal_lahir
                updates.append(UserProfileInfo(id=id_value, tanggal_lahir=tanggal_lahir_value))
    # return HttpResponse(updates, content_type="application/json")
    UserProfileInfo.objects.bulk_update(updates, ['tanggal_lahir',])
    return JsonResponse('userprofileinfoupdatetanggallahir csv is now working', safe=False)

# UPDATE END
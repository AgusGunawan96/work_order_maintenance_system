from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.urls import path, reverse_lazy

# LIBRARY FOR IMPORT DATA
from django.http import JsonResponse, HttpResponse
from csv import reader
from django.contrib.auth.models import User, Group
from master_app.models import UserProfileInfo, UserKeluargaInfo
from it_app.models import IPAddress, Hardware
from qc_app.models import rirMaterial, rirVendor
from hrd_app.models import medicalApprovalList
from accounting_app.models import coaCode
from django.contrib.auth.decorators import user_passes_test
import csv
# Create your views here.

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

# CREATE END

# UPDATE START

@login_required
def UpdateUpdateUserProfileInfoGenderStatus(request):
    # Read CSV file
    with open('templates/csv/updateuserprofileinfogenderandstatus.csv') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        data = list(reader)
    # Extract IDs from CSV data
    ids = [row[0] for row in data]
    # Retrieve objects from database and update fields
    objects = UserProfileInfo.objects.filter(user__username__in=ids)
    # Return the response object
    for obj, row in zip(objects, data):
        obj.is_contract = row[1]
        obj.is_permanent = row[2]
        obj.gender = row[3]
    UserProfileInfo.objects.bulk_update(objects, ['is_contract', 'is_permanent', 'gender'])
    return JsonResponse('updateuserprofileinfogenderandstatus csv is now working', safe=False)

@login_required
def UpdateUserProfileInfoTanggalLahir(request):
    # Read CSV File
    with open('templates/csv/userprofileinfoupdatetanggallahir.csv') as f:
        reader = csv.reader(f)
        next(reader) # Skip header row
        data = list(reader)
    # Extract IDs from CSV data
    ids = [row[0] for row in data]
    # Retrieve objects from database and update fields
    objects = UserProfileInfo.objects.filter(user__username__in=ids)
    # Return the response object
    for obj, row in zip(objects, data):
        obj.tanggal_lahir = row[1]
    UserProfileInfo.objects.bulk_update(objects, ['tanggal_lahir',])
    return JsonResponse('userprofileinfoupdatetanggallahir csv is now working', safe=False)

# UPDATE END
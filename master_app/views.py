from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.urls import path, reverse_lazy

# LIBRARY FOR IMPORT DATA
from django.http import JsonResponse
from csv import reader
from django.contrib.auth.models import User, Group
from master_app.models import UserProfileInfo
from it_app.models import IPAddress, Hardware
from django.contrib.auth.decorators import user_passes_test
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
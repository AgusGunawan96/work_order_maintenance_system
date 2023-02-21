from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.urls import path, reverse_lazy

# LIBRARY FOR IMPORT DATA
from django.http import JsonResponse
from csv import reader
from django.contrib.auth.models import User
from master_app.models import UserProfileInfo
# Create your views here.

@login_required
# @permission_required('polls.add_choice')
def index(request):
    context={"breadcrumb":{"parent":"Color Version","child":"Layout Light"}}
    return render(request,'master_app/index.html',context)


def CreateUserdata(request):
    with open('templates/csv/list_user.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for id,username, password, first_name, last_name, *__ in csvf:
            user = User(id=id, username=username, first_name=first_name, last_name = last_name, is_staff = True )
            user.set_password(password)
            data.append(user)
        User.objects.bulk_create(data)
    return JsonResponse('user csv is now working', safe=False)

def CreateUserInfoData(request):
    with open('templates/csv/list_user_info.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for user_id, department_id, division_id, section_id, employee_ext, is_supervisor, is_manager, is_bod, profile_pic, position, *__ in csvf:
            user = UserProfileInfo(user_id=user_id, department_id=department_id, division_id = division_id, section_id = section_id
            , employee_ext = employee_ext, is_supervisor = is_supervisor, is_manager = is_manager, is_bod = is_bod
            , profile_pic = profile_pic, position = position )
            data.append(user)
        UserProfileInfo.objects.bulk_create(data)
    return JsonResponse('user Info csv is now working', safe=False)
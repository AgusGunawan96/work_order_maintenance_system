from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.urls import path, reverse_lazy

# Create your views here.

@login_required
# @permission_required('polls.add_choice')
def index(request):
    context={"breadcrumb":{"parent":"Color Version","child":"Layout Light"}}
    return render(request,'master_app/index.html',context)

from django.http import JsonResponse
from csv import reader
from django.contrib.auth.models import User

def userdata(request):
    with open('templates/csv/your_file.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for username, password, *__ in csvf:
            user = User(username=username)
            user.set_password(password)
            data.append(user)
        User.objects.bulk_create(data)
    return JsonResponse('user csv is now working', safe=False)
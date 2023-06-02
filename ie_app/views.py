from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.http import Http404, HttpResponse, JsonResponse
import datetime
import csv
import xlwt
from dateutil.relativedelta import relativedelta
from csv import reader
from master_app.models import UserProfileInfo, UserKeluargaInfo

# Create your views here.
def index(request):
    
    return render(request, 'ie_app/index.html')
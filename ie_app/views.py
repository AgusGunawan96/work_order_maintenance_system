from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.http import Http404, HttpResponse, JsonResponse
from ie_app.models import ImpPlanH,ImpPlanD, ImpPlanAttachment
import datetime
import csv
import xlwt
from dateutil.relativedelta import relativedelta
from csv import reader
from master_app.models import UserProfileInfo, UserKeluargaInfo

# Create your views here.
def index(request):
    return render(request, 'ie_app/index.html')

def improvement_plan_index(request):
    if request.method == "POST":
        classification_input = request.POST.get('rdo-ani')  # 'rdo-ani' matches the name attribute of the radio buttons
        dueDate_input = request.POST.get('due_date')
        problem_desc_input = request.POST.get('problem_desc')
        improvement_desc_input = request.POST.get('improvement_plan_desc')
        target_desc_input = request.POST.get('target_desc')
        benefit_desc_input = request.POST.get('benefit_desc')
        plan_maks = ImpPlanH.objects.filter(plan_no__contains=datetime.datetime.now().strftime('%Y%m')).count() + 1
        plan_no_input = "PLN" + datetime.datetime.now().strftime('%Y%m') + str("%003d" % ( plan_maks, ))  
        dueDate_input = datetime.datetime.strptime(dueDate_input, '%m/%d/%Y').strftime('%Y-%m-%d')
        improvement_header = ImpPlanH.objects.create(
            user = request.user,
            plan_no = plan_no_input,
            duedate = dueDate_input,
            classification  = classification_input,
        )
        files = request.FILES.getlist('attachment')
        for f in files:
             attachment = ImpPlanAttachment(attachment=f)
             attachment.planh = improvement_header
             attachment.save()
        ImpPlanD.objects.create(
            planh = improvement_header,
            plan_no = plan_no_input,
            problem_desc = problem_desc_input,
            improvement_desc = improvement_desc_input,
            target_desc = target_desc_input,
            benefit_desc = benefit_desc_input,
        )
        messages.success(request, 'Improvement Plan Added!')    
        return redirect('ie_app:improvement_plan_index')
    else:
        return render(request, 'ie_app/improvement_plan_index.html')

def improvement_plan_report(request):

    return HttpResponse("this is improvement report")
from django.shortcuts import render, redirect
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
from qc_app.models import rirHeader, rirDetailCoaContentJudgement, rirDetailCoaContentCheckedby, rirDetailAppearenceJudgement, rirDetailAppearenceCheckedby, rirDetailRestrictedSubstanceJudgement, rirDetailRestrictedSubstanceCheckedby, rirDetailEnvironmentalIssueJudgement, rirDetailEnvironmentalIssueCheckedby,rirDetailSampleTestJudgement, rirDetailSampleTestCheckedby, rirApprovalSupervisor, rirApprovalManager
from qc_app.forms import rirHeaderForms, rirDetailCoaContentJudgementForms, rirDetailCoaContentCheckedByForms, rirDetailAppearenceJudgementForms, rirDetailAppearenceCheckedByForms, rirDetailRestrictedSubstanceJudgementForms, rirDetailRestrictedSubstanceCheckedByForms, rirDetailEnvironmentalIssueJudgementForms, rirDetailEnvironmentalIssueCheckedByForms, rirDetailSampleTestJudgementForms, rirDetailSampleTestCheckedByForms, rirApprovalSupervisorReturnForms, rirApprovalSupervisorPassForms, rirApprovalManagerReturnForms, rirApprovalManagerPassForms
from django.http import HttpResponse
# Create your views here.
@login_required
def dashboard(request):
    return render(request, 'qc_app/dashboard.html')

@login_required
def rir_add(request):
    if request.method == "POST":
        rir_form = rirHeaderForms(data=request.POST)
        if rir_form.is_valid():
            rir = rir_form.save(commit=False)
            rir_maks = rirHeader.objects.filter(rir_no__contains=datetime.datetime.now().strftime('%Y%m')).count() + 1
            rir_no = "RIR" + datetime.datetime.now().strftime('%Y%m') + str("%003d" % ( rir_maks, ))  
            rir.rir_no = rir_no   
            coaContent = rirDetailCoaContentJudgementForms().save(commit=False)
            coaContent.header = rir
            rir.save()
            coaContent.save()
            return redirect('qc_app:rir_judgement_index')
        else:
            print(rir_form.errors)
    else:
        rir_form = rirHeaderForms()
    context = {
    'form': rirHeaderForms,
}
    return render(request, 'qc_app/rir_add.html', context)

@login_required
def rir_judgement_index(request):
    judgement_coa = rirDetailCoaContentJudgement.objects.order_by('-id')
    judgement_appearance = rirDetailAppearenceJudgement.objects.order_by('-id')
    judgement_restirected_substance = rirDetailRestrictedSubstanceJudgement.objects.order_by('-id')
    judgement_sample_test = rirDetailSampleTestJudgement.objects.order_by('-id')
    judgement_environmental_issue = rirDetailEnvironmentalIssueJudgement.objects.order_by('-id')
    context = {
        'judgement_coa' : judgement_coa,
        'judgement_appearance ' : judgement_appearance,
        'judgement_restirected_substance  ' : judgement_restirected_substance,
        'judgement_sample_test' : judgement_sample_test,
        'judgement_environmental_issue' : judgement_environmental_issue,
        
    }
    return render(request, 'qc_app/rir_judgement_index.html', context)
    return HttpResponse('ini merupakan RIR Judgement Index')

@login_required
def rir_judgement_detail(request):
    return HttpResponse('Ini merupakan RIR Detail')

@login_required
def rir_judgement_approve(request):
    return HttpResponse('ini merupakan judgement apabila di Approve')

@login_required
def rir_judgement_special_judgement(request):
    return HttpResponse('ini merupakan judgement dan masih masuk ke dalam check')

@login_required
def rir_checked_by_index(request):
    checkedby_coa = rirDetailCoaContentCheckedby.objects.order_by('-id')
    checkedby_appearance = rirDetailAppearenceCheckedby.objects.order_by('-id')
    checkedby_restirected_substance = rirDetailRestrictedSubstanceCheckedby.objects.order_by('-id')
    checkedby_sample_test = rirDetailSampleTestCheckedby.objects.order_by('-id')
    checkedby_environmental_issue = rirDetailEnvironmentalIssueCheckedby.objects.order_by('-id')
    context = {
        'checkedby_coa' : checkedby_coa,
        'checkedby_appearance ' : checkedby_appearance,
        'checkedby_restirected_substance  ' : checkedby_restirected_substance,
        'checkedby_sample_test' : checkedby_sample_test,
        'checkedby_environmental_issue' : checkedby_environmental_issue,
        
    }
    return render(request, 'qc_app/rir_checkedby_index.html', context)
    return HttpResponse('ini merupakan RIR Checked By Index')

@login_required
def rir_checked_by_detail(request):
    return HttpResponse('ini merupakan Checked by Detail')

@login_required
def rir_special_judgement_index(request):
    return HttpResponse('ini merupakan RIR Special Judgement Index')

@login_required
def rir_special_judgement_detail(request):
    return HttpResponse('ini merupakan RIR Special Judgement Detail')

@login_required
def rir_supervisor_approval(request):
    return HttpResponse('ini merupakan Approval dari supervisor')

@login_required
def rir_manager_approval(request):
    return HttpResponse('ini merupakan Approval dari Manager')

@login_required
def rir_supervisor_return(request):
    return HttpResponse('ini merupakan Return dari supervisor')

@login_required
def rir_manager_return(request):
    return HttpResponse('ini merupakan return dari manager')

from io import BytesIO
@login_required
def rir_download_report(request):
    context = {
        # Add context variables here
    }
    return render(request, 'qc_app/rir_download_report.html', context)
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
            rir_maks = rirHeader.objects.filter(ticket_no__contains=datetime.datetime.now().strftime('%Y%m')).count() + 1
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

@login_required
def rir_download_report(request):
    return HttpResponse('ini merupakan download report untuk RIR')
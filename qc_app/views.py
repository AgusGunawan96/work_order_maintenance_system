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
from qc_app.models import rirHeader, rirDetailCoaContentJudgement, rirDetailCoaContentCheckedby, rirDetailAppearenceJudgement, rirDetailAppearenceCheckedby, rirDetailRestrictedSubstanceJudgement, rirDetailRestrictedSubstanceCheckedby, rirDetailEnvironmentalIssueJudgement, rirDetailEnvironmentalIssueCheckedby,rirDetailSampleTestJudgement, rirDetailSampleTestCheckedby, rirApprovalSupervisor, rirApprovalManager, specialJudgement
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
    judgement_coa = rirDetailCoaContentJudgement.objects.filter(coa_content_judgement = False).order_by('-id')
    judgement_appearance = rirDetailAppearenceJudgement.objects.filter(appearence_judgement = False).order_by('-id')
    judgement_restricted_substance = rirDetailRestrictedSubstanceJudgement.objects.filter(restricted_substance_judgement = False).order_by('-id')
    judgement_sample_test = rirDetailSampleTestJudgement.objects.filter(sample_test_judgement = False).order_by('-id')
    judgement_environmental_issue = rirDetailEnvironmentalIssueJudgement.objects.filter(environmental_issue_judgement = False).order_by('-id')
    context = {
        'judgement_coa' : judgement_coa,
        'judgement_appearance ' : judgement_appearance,
        'judgement_restricted_substance  ' : judgement_restricted_substance,
        'judgement_sample_test' : judgement_sample_test,
        'judgement_environmental_issue' : judgement_environmental_issue,
        
    }
    return render(request, 'qc_app/rir_judgement_index.html', context)
    return HttpResponse('ini merupakan RIR Judgement Index')

@login_required
def rir_judgement_detail(request, rir_id):

    rir_header                         = rirHeader.objects.get(pk=rir_id)
    rir_coa_judgement                  = rirDetailCoaContentJudgement.objects.filter(header_id=rir_header).first()
    rir_coa_checkedby                  = rirDetailCoaContentCheckedby.objects.filter(coa_content_judgement_id=rir_coa_judgement).first()
    rir_appearance_judgement           = rirDetailAppearenceJudgement.objects.filter(header_id=rir_header).first()
    rir_appearance_checkedby           = rirDetailAppearenceCheckedby.objects.filter(appearence_judgement_id=rir_appearance_judgement).first()
    rir_sampletest_judgement           = rirDetailSampleTestJudgement.objects.filter(header_id=rir_header).first()
    rir_sampletest_checkedby           = rirDetailSampleTestCheckedby.objects.filter(sample_test_judgement_id=rir_sampletest_judgement).first()
    rir_restrictedsubstance_judgement  = rirDetailRestrictedSubstanceJudgement.objects.filter(header_id=rir_header).first()
    rir_restrictedsubstance_checkedby  = rirDetailRestrictedSubstanceCheckedby.objects.filter(restricted_substance_judgement_id=rir_restrictedsubstance_judgement).first()
    rir_environmentalissue_judgement   = rirDetailEnvironmentalIssueJudgement.objects.filter(header_id=rir_header).first()
    rir_environmentalissue_checkedby   = rirDetailEnvironmentalIssueCheckedby.objects.filter(environmental_issue_judgement_id=rir_environmentalissue_judgement).first()
    rir_special_judgement              = specialJudgement.objects.filter(rir=rir_header).first()
    rir_approval_supervisor            = rirApprovalSupervisor.objects.filter(specialjudgement=rir_special_judgement).first()
    rir_approval_manager               = rirApprovalManager.objects.filter(rir_approval_supervisor=rir_approval_supervisor).first()

    context = {
        'rir_header'                        : rir_header,
        'rir_coa_judgement'                 : rir_coa_judgement,
        'rir_coa_checkedby'                 : rir_coa_checkedby,
        'rir_appearance_judgement'          : rir_appearance_judgement,
        'rir_appearance_checkedby'          : rir_appearance_checkedby,
        'rir_sampletest_judgement'          : rir_sampletest_judgement,
        'rir_sampletest_checkedby'          : rir_sampletest_checkedby,
        'rir_restrictedsubstance_judgement' : rir_restrictedsubstance_judgement,
        'rir_restrictedsubstance_checkedby' : rir_restrictedsubstance_checkedby,
        'rir_environmentalissue_judgement'  : rir_environmentalissue_judgement,
        'rir_environmentalissue_checkedby'  : rir_environmentalissue_checkedby,
        'rir_special_judgement'             : rir_special_judgement,
        'rir_approval_supervisor'           : rir_approval_supervisor,
        'rir_approval_manager'              : rir_approval_manager,
    }
    return render(request, 'qc_app/rir_judgement_detail.html', context)

@login_required
def rir_judgement_approve(request):
    return HttpResponse('ini merupakan judgement apabila di Approve')

@login_required
def rir_judgement_special_judgement(request):
    return HttpResponse('ini merupakan judgement dan masih masuk ke dalam check')

@login_required
def rir_checked_by_index(request):
    checkedby_coa = rirDetailCoaContentCheckedby.objects.filter(coa_content_checked_by = False ).order_by('-id')
    checkedby_appearance = rirDetailAppearenceCheckedby.objects.filter(appearence_checked_by = False ).order_by('-id')
    checkedby_restricted_substance = rirDetailRestrictedSubstanceCheckedby.objects.filter(restricted_substance_checked_by = False ).order_by('-id')
    checkedby_sample_test = rirDetailSampleTestCheckedby.objects.filter(sample_test_checked_by = False ).order_by('-id')
    checkedby_environmental_issue = rirDetailEnvironmentalIssueCheckedby.objects.filter(environmental_issue_checked_by = False ).order_by('-id')
    context = {
        'checkedby_coa' : checkedby_coa,
        'checkedby_appearance ' : checkedby_appearance,
        'checkedby_restricted_substance  ' : checkedby_restricted_substance,
        'checkedby_sample_test' : checkedby_sample_test,
        'checkedby_environmental_issue' : checkedby_environmental_issue,
        
    }
    return render(request, 'qc_app/rir_checkedby_index.html', context)
    return HttpResponse('ini merupakan RIR Checked By Index')

@login_required
def rir_checked_by_detail(request, rir_detail):
    return HttpResponse('ini merupakan Checked by Detail')

@login_required
def rir_special_judgement_index(request):
    return HttpResponse('ini merupakan RIR Special Judgement Index')

@login_required
def rir_special_judgement_detail(request, rir_detail):
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
def rir_download_report(request, rir_id):

    rir_header                         = rirHeader.objects.get(pk=rir_id)
    rir_coa_judgement                  = rirDetailCoaContentJudgement.objects.filter(header_id=rir_header).first()
    rir_coa_checkedby                  = rirDetailCoaContentCheckedby.objects.filter(coa_content_judgement_id=rir_coa_judgement).first()
    rir_appearance_judgement           = rirDetailAppearenceJudgement.objects.filter(header_id=rir_header).first()
    rir_appearance_checkedby           = rirDetailAppearenceCheckedby.objects.filter(appearence_judgement_id=rir_appearance_judgement).first()
    rir_sampletest_judgement           = rirDetailSampleTestJudgement.objects.filter(header_id=rir_header).first()
    rir_sampletest_checkedby           = rirDetailSampleTestCheckedby.objects.filter(sample_test_judgement_id=rir_sampletest_judgement).first()
    rir_restrictedsubstance_judgement  = rirDetailRestrictedSubstanceJudgement.objects.filter(header_id=rir_header).first()
    rir_restrictedsubstance_checkedby  = rirDetailRestrictedSubstanceCheckedby.objects.filter(restricted_substance_judgement_id=rir_restrictedsubstance_judgement).first()
    rir_environmentalissue_judgement   = rirDetailEnvironmentalIssueJudgement.objects.filter(header_id=rir_header).first()
    rir_environmentalissue_checkedby   = rirDetailEnvironmentalIssueCheckedby.objects.filter(environmental_issue_judgement_id=rir_environmentalissue_judgement).first()
    rir_special_judgement              = specialJudgement.objects.filter(rir=rir_header).first()
    rir_approval_supervisor            = rirApprovalSupervisor.objects.filter(specialjudgement=rir_special_judgement).first()
    rir_approval_manager               = rirApprovalManager.objects.filter(rir_approval_supervisor=rir_approval_supervisor).first()

    context = {
        'rir_header'                        : rir_header,
        'rir_coa_judgement'                 : rir_coa_judgement,
        'rir_coa_checkedby'                 : rir_coa_checkedby,
        'rir_appearance_judgement'          : rir_appearance_judgement,
        'rir_appearance_checkedby'          : rir_appearance_checkedby,
        'rir_sampletest_judgement'          : rir_sampletest_judgement,
        'rir_sampletest_checkedby'          : rir_sampletest_checkedby,
        'rir_restrictedsubstance_judgement' : rir_restrictedsubstance_judgement,
        'rir_restrictedsubstance_checkedby' : rir_restrictedsubstance_checkedby,
        'rir_environmentalissue_judgement'  : rir_environmentalissue_judgement,
        'rir_environmentalissue_checkedby'  : rir_environmentalissue_checkedby,
        'rir_special_judgement'             : rir_special_judgement,
        'rir_approval_supervisor'           : rir_approval_supervisor,
        'rir_approval_manager'              : rir_approval_manager,
    }

    return render(request, 'qc_app/rir_download_report.html', context)
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
from qc_app.models import rirHeader, rirDetailCoaContentJudgement, rirDetailCoaContentCheckedby, rirDetailAppearenceJudgement, rirDetailAppearenceCheckedby, rirDetailRestrictedSubstanceJudgement, rirDetailRestrictedSubstanceCheckedby, rirDetailEnvironmentalIssueJudgement, rirDetailEnvironmentalIssueCheckedby,rirDetailSampleTestJudgement, rirDetailSampleTestCheckedby, rirApprovalSupervisor, rirApprovalManager, specialJudgement, rirCoaContentAttachment, rirAppearanceAttachment, rirSampleTestAttachment, rirEnvironmentalIssueAttachment, rirRestrictedSubstanceAttachment, rirApprovalList
from qc_app.forms import rirHeaderForms, rirDetailCoaContentJudgementForms, rirDetailCoaContentCheckedByForms, rirDetailAppearenceJudgementForms, rirDetailAppearenceCheckedByForms, rirDetailRestrictedSubstanceJudgementForms, rirDetailRestrictedSubstanceCheckedByForms, rirDetailEnvironmentalIssueJudgementForms, rirDetailEnvironmentalIssueCheckedByForms, rirDetailSampleTestJudgementForms, rirDetailSampleTestCheckedByForms, rirApprovalSupervisorReturnForms, rirApprovalSupervisorPassForms, rirApprovalManagerReturnForms, rirApprovalManagerPassForms, rirCoaContentAttachmentForms, rirAppearanceAttachmentForms, rirSampleTestAttachmentForms, rirEnvironmentalIssueAttachmentForms, rirRestrictedSubstanceAttachmentForms, rirSpecialJudgementForms, rirApprovalSupervisorForms, rirApprovalManagerForms
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
            rir.save()
            # Membuat COA Content jika ada
            if rir.category.coa_content:
                coaContent = rirDetailCoaContentJudgementForms().save(commit=False)
                coaContent.header = rir
                coaContent.save()
            elif rir.category.appearance:
                appearance = rirDetailAppearenceJudgementForms().save(commit=False)
                appearance.header = rir
                appearance.save()
            # Langsung kita buatkan untuk COA Contentnya 
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
    coa                     = rirDetailCoaContentJudgement.objects.filter(coa_content_judgement = False).filter(header__is_special_judgement = False).order_by('-id')
    appearance              = rirDetailAppearenceJudgement.objects.filter(appearence_judgement = False).filter(header__is_special_judgement = False).order_by('-id')
    restricted_substance    = rirDetailRestrictedSubstanceJudgement.objects.filter(restricted_substance_judgement = False).filter(header__is_special_judgement = False).order_by('-id')
    sample_test             = rirDetailSampleTestJudgement.objects.filter(sample_test_judgement = False).filter(header__is_special_judgement = False).order_by('-id')
    environmental_issue     = rirDetailEnvironmentalIssueJudgement.objects.filter(environmental_issue_judgement = False).filter(header__is_special_judgement = False).order_by('-id')
    context = {
        'judgement_coa' : coa,
        'judgement_appearance' : appearance,
        'judgement_restricted_substance' : restricted_substance,
        'judgement_sample_test' : sample_test,
        'judgement_environmental_issue' : environmental_issue,
        
    }
    return render(request, 'qc_app/rir_judgement_index.html', context)

@login_required
def rir_detail(request, rir_id):

    rir_header                                   = rirHeader.objects.get(pk=rir_id)
    rir_coa_judgement                            = rirDetailCoaContentJudgement.objects.filter(header_id=rir_header).first()
    rir_coa_checkedby                            = rirDetailCoaContentCheckedby.objects.filter(coa_content_judgement_id=rir_coa_judgement).first()
    rir_appearance_judgement                     = rirDetailAppearenceJudgement.objects.filter(header_id=rir_header).first()
    rir_appearance_checkedby                     = rirDetailAppearenceCheckedby.objects.filter(appearence_judgement_id=rir_appearance_judgement).first()
    rir_sampletest_judgement                     = rirDetailSampleTestJudgement.objects.filter(header_id=rir_header).first()
    rir_sampletest_checkedby                     = rirDetailSampleTestCheckedby.objects.filter(sample_test_judgement_id=rir_sampletest_judgement).first()
    rir_restrictedsubstance_judgement            = rirDetailRestrictedSubstanceJudgement.objects.filter(header_id=rir_header).first()
    rir_restrictedsubstance_checkedby            = rirDetailRestrictedSubstanceCheckedby.objects.filter(restricted_substance_judgement_id=rir_restrictedsubstance_judgement).first()
    rir_environmentalissue_judgement             = rirDetailEnvironmentalIssueJudgement.objects.filter(header_id=rir_header).first()
    rir_environmentalissue_checkedby             = rirDetailEnvironmentalIssueCheckedby.objects.filter(environmental_issue_judgement_id=rir_environmentalissue_judgement).first()
    rir_special_judgement                        = specialJudgement.objects.filter(rir=rir_header).first()
    rir_approval_supervisor                      = rirApprovalSupervisor.objects.filter(specialjudgement=rir_special_judgement).first()
    rir_approval_manager                         = rirApprovalManager.objects.filter(rir_approval_supervisor=rir_approval_supervisor).first()
    rir_coa_judgement_attachment                 = rirCoaContentAttachment.objects.filter(rir_id = rir_id).filter(is_judgement = True ).values('attachment')
    rir_appearance_judgement_attachment          = rirAppearanceAttachment.objects.filter(rir_id = rir_id).filter(is_judgement = True ).values('attachment')
    rir_sampletest_judgement_attachment          = rirSampleTestAttachment.objects.filter(rir_id = rir_id).filter(is_judgement = True ).values('attachment')
    rir_restrictedsubstance_judgement_attachment = rirRestrictedSubstanceAttachment.objects.filter(rir_id = rir_id).filter(is_judgement = True ).values('attachment')
    rir_environmentalissue_judgement_attachment  = rirEnvironmentalIssueAttachment.objects.filter(rir_id = rir_id).filter(is_judgement = True ).values('attachment')
    rir_coa_checkedby_attachment                 = rirCoaContentAttachment.objects.filter(rir_id = rir_id).filter(is_checkedby = True ).values('attachment')
    rir_appearance_checkedby_attachment          = rirAppearanceAttachment.objects.filter(rir_id = rir_id).filter(is_checkedby = True ).values('attachment')
    rir_sampletest_checkedby_attachment          = rirSampleTestAttachment.objects.filter(rir_id = rir_id).filter(is_checkedby = True ).values('attachment')
    rir_restrictedsubstance_checkedby_attachment = rirRestrictedSubstanceAttachment.objects.filter(rir_id = rir_id).filter(is_checkedby = True ).values('attachment')
    rir_environmentalissue_checkedby_attachment  = rirEnvironmentalIssueAttachment.objects.filter(rir_id = rir_id).filter(is_checkedby = True ).values('attachment')
    rir_approval_checkedby_list                  = rirApprovalList.objects.filter(is_checked_by = True).filter(user_id = request.user.id).first()
    rir_approval_judgement_list                  = rirApprovalList.objects.filter(is_judgement = True).filter(user_id = request.user.id).first()
    rir_approval_supervisor_list                 = rirApprovalList.objects.filter(is_supervisor = True).filter(user_id = request.user.id).first()
    rir_approval_manager_list                    = rirApprovalList.objects.filter(is_manager = True).filter(user_id = request.user.id).first()
    

    context = {
        'rir_header'                                    : rir_header,
        'rir_coa_judgement'                             : rir_coa_judgement,
        'rir_coa_checkedby'                             : rir_coa_checkedby,
        'rir_appearance_judgement'                      : rir_appearance_judgement,
        'rir_appearance_checkedby'                      : rir_appearance_checkedby,
        'rir_sampletest_judgement'                      : rir_sampletest_judgement,
        'rir_sampletest_checkedby'                      : rir_sampletest_checkedby,
        'rir_restrictedsubstance_judgement'             : rir_restrictedsubstance_judgement,
        'rir_restrictedsubstance_checkedby'             : rir_restrictedsubstance_checkedby,
        'rir_environmentalissue_judgement'              : rir_environmentalissue_judgement,
        'rir_environmentalissue_checkedby'              : rir_environmentalissue_checkedby,
        'rir_special_judgement'                         : rir_special_judgement,
        'rir_approval_supervisor'                       : rir_approval_supervisor,
        'rir_approval_manager'                          : rir_approval_manager,
        'rir_coa_judgement_attachment'                  : rir_coa_judgement_attachment,
        'rir_appearance_judgement_attachment'           : rir_appearance_judgement_attachment,
        'rir_sampletest_judgement_attachment'           : rir_sampletest_judgement_attachment,
        'rir_restrictedsubstance_judgement_attachment'  : rir_restrictedsubstance_judgement_attachment,
        'rir_environmentalissue_judgement_attachment'   : rir_environmentalissue_judgement_attachment,
        'rir_coa_checkedby_attachment'                  : rir_coa_checkedby_attachment,
        'rir_appearance_checkedby_attachment'           : rir_appearance_checkedby_attachment,
        'rir_sampletest_checkedby_attachment'           : rir_sampletest_checkedby_attachment,
        'rir_restrictedsubstance_checkedby_attachment'  : rir_restrictedsubstance_checkedby_attachment,
        'rir_environmentalissue_checkedby_attachment'   : rir_environmentalissue_checkedby_attachment,
        'rir_approval_checkedby_list'                   : rir_approval_checkedby_list,
        'rir_approval_judgement_list'                   : rir_approval_judgement_list,
        'rir_approval_supervisor_list'                  : rir_approval_supervisor_list,
        'rir_approval_manager_list'                     : rir_approval_manager_list,


        'form_rir_coa_attachment'                       : rirCoaContentAttachmentForms,
        'form_rir_appearance_attachment'                : rirAppearanceAttachmentForms,
        'form_rir_sampletest_attachment'                : rirSampleTestAttachmentForms,
        'form_rir_restrictedsubstance_attachment'       : rirRestrictedSubstanceAttachmentForms,
        'form_rir_environmental_attachment'             : rirEnvironmentalIssueAttachmentForms,
        
        'form_rir_coa_judgement_detail'                 : rirDetailCoaContentJudgementForms,
        'form_rir_appearance_judgement_detail'          : rirDetailAppearenceJudgementForms,
        'form_rir_sampletest_judgement_detail'          : rirDetailSampleTestJudgementForms,
        'form_rir_restrictedsubstance_judgement_detail' : rirDetailRestrictedSubstanceJudgementForms,
        'form_rir_environmentalissue_judgement_detail'  : rirDetailEnvironmentalIssueJudgementForms,

        'form_rir_coa_checkedby_detail'                 : rirDetailCoaContentCheckedByForms,
        'form_rir_appearance_checkedby_detail'          : rirDetailAppearenceCheckedByForms,
        'form_rir_sampletest_checkedby_detail'          : rirDetailSampleTestCheckedByForms,
        'form_rir_restrictedsubstance_checkedby_detail' : rirDetailRestrictedSubstanceCheckedByForms,
        'form_rir_environmentalissue_checkedby_detail'  : rirDetailEnvironmentalIssueCheckedByForms,

    }
    return render(request, 'qc_app/rir_detail.html', context)

@login_required
def rir_judgement_coa_approve(request, rir_id):
    # Memanggil Approval dan Header dari COA Content
    rir_approval = rirApprovalList.objects.filter(user = request.user).first()
    rir_header = rirHeader.objects.get(pk=rir_id)
    # Update data Coa Content Judgement
    rir_detail_coaContent_judgement = rirDetailCoaContentJudgement.objects.filter(header = rir_id).first()
    post = request.POST.copy()
    post.update({'coa_content_judgement': True})
    rir_detail_coaContent_judgement_form  = rirDetailCoaContentJudgementForms(request.POST, instance = rir_detail_coaContent_judgement)
    if rir_detail_coaContent_judgement_form.is_valid():
        # Simpan Data Coa Content Judgement
        rir_detail_coaContent_judgement = rir_detail_coaContent_judgement_form.save(commit=False)
        rir_detail_coaContent_judgement.coa_content_judgement = True
        rir_detail_coaContent_judgement.coa_content_user_judgement = rir_approval
        rir_detail_coaContent_judgement.save()
        # Simpan Attachment Coa Content Judgement (Apabila ada)
        files = request.FILES.getlist('attachment')
        for f in files:
            attachment = rirCoaContentAttachment(attachment=f)
            attachment.rir = rir_header
            attachment.is_judgement = True
            attachment.save()
        # Membuat Coa Content Checkedby dan kondisi Special Judgement
        rir_detail_coaContent_checkedby = rirDetailCoaContentCheckedByForms().save(commit=False)
        rir_detail_coaContent_checkedby.coa_content_judgement   = rir_detail_coaContent_judgement
        rir_detail_coaContent_checkedby.save()
        messages.success(request, 'RIR Approved')
        return redirect('qc_app:rir_judgement_index')
    return redirect('qc_app:rir_detail', rir_id)

@login_required
def rir_judgement_appearance_approve(request, rir_id):
    # Memanggil Approval dan Header di Appearance
    rir_approval = rirApprovalList.objects.filter(user = request.user).first()
    rir_header = rirHeader.objects.get(pk=rir_id)
    # Update data Appearance Judgement
    rir_detail_appearance_judgement = rirDetailAppearenceJudgement.objects.filter(header = rir_id).first()
    post = request.POST.copy()
    post.update({'appearance_judgement': True})
    rir_detail_appearance_judgement_form  = rirDetailAppearenceJudgementForms(request.POST, instance = rir_detail_appearance_judgement)
    if rir_detail_appearance_judgement_form.is_valid():
        # Simpan Data Appearance Judgement
        rir_detail_appearance_judgement = rir_detail_appearance_judgement_form.save(commit=False)
        rir_detail_appearance_judgement.appearence_judgement = True
        rir_detail_appearance_judgement.appearence_user_judgement = rir_approval
        rir_detail_appearance_judgement.save()
        # Simpan Attachment Apppearance Judgement (Apabila ada)
        files = request.FILES.getlist('attachment')
        for f in files:
            attachment = rirAppearanceAttachment(attachment=f)
            attachment.rir = rir_header
            attachment.is_judgement = True
            attachment.save()
        # Membuat Appearance Checkedby dan kondisi Special Judgement
        rir_detail_appearance_checkedby = rirDetailAppearenceCheckedByForms().save(commit=False)
        rir_detail_appearance_checkedby.appearence_judgement   = rir_detail_appearance_judgement
        rir_detail_appearance_checkedby.save()
        messages.success(request, 'RIR Appearance Approved')
        return redirect('qc_app:rir_judgement_index')
    return redirect('qc_app:rir_detail', rir_id)

@login_required
def rir_judgement_sampletest_approve(request, rir_id):
    # Memanggil Approval dan Header di Sample Test
    rir_approval = rirApprovalList.objects.filter(user = request.user).first()
    rir_header = rirHeader.objects.get(pk=rir_id)
    # Update data Sample Test Judgement
    rir_detail_sampletest_judgement = rirDetailSampleTestJudgement.objects.filter(header = rir_id).first()
    post = request.POST.copy()
    post.update({'sample_test_judgement': True})
    rir_detail_sampletest_judgement_form  = rirDetailSampleTestJudgementForms(request.POST, instance = rir_detail_sampletest_judgement)
    if rir_detail_sampletest_judgement_form.is_valid():
        # Simpan Data Sample Test Judgement
        rir_detail_sampletest_judgement = rir_detail_sampletest_judgement_form.save(commit=False)
        rir_detail_sampletest_judgement.sample_test_judgement = True
        rir_detail_sampletest_judgement.sample_test_user_judgement = rir_approval
        rir_detail_sampletest_judgement.save()
        # Simpan Attachment Sample Test Judgement (Apabila ada)
        files = request.FILES.getlist('attachment')
        for f in files:
            attachment = rirSampleTestAttachment(attachment=f)
            attachment.rir = rir_header
            attachment.is_judgement = True
            attachment.save()
        # Membuat Sample Test Checkedby dan kondisi Special Judgement
        rir_detail_sampletest_checkedby = rirDetailSampleTestCheckedByForms().save(commit=False)
        rir_detail_sampletest_checkedby.sample_test_judgement   = rir_detail_sampletest_judgement
        rir_detail_sampletest_checkedby.save()
        messages.success(request, 'RIR Sample Test Approved')
        return redirect('qc_app:rir_judgement_index')
    return redirect('qc_app:rir_detail', rir_id)

@login_required
def rir_judgement_restrictedsubstance_approve(request, rir_id):
    # Memanggil Approval dan Header di Restricted Substance
    rir_approval = rirApprovalList.objects.filter(user = request.user).first()
    rir_header = rirHeader.objects.get(pk=rir_id)
    # Update data Restricted Substance Judgement
    rir_detail_restrictedsubstance_judgement = rirDetailRestrictedSubstanceJudgement.objects.filter(header = rir_id).first()
    post = request.POST.copy()
    post.update({'restricted_substance_judgement': True})
    rir_detail_restrictedsubstance_judgement_form  = rirDetailRestrictedSubstanceJudgementForms(request.POST, instance = rir_detail_restrictedsubstance_judgement)
    if rir_detail_restrictedsubstance_judgement_form.is_valid():
        # Simpan Data Restricted Substance Judgement
        rir_detail_restrictedsubstance_judgement = rir_detail_restrictedsubstance_judgement_form.save(commit=False)
        rir_detail_restrictedsubstance_judgement.restricted_substance_judgement = True
        rir_detail_restrictedsubstance_judgement.restricted_substance_user_judgement = rir_approval
        rir_detail_restrictedsubstance_judgement.save()
        # Simpan Attachment Restricted Substance Judgement (Apabila ada)
        files = request.FILES.getlist('attachment')
        for f in files:
            attachment = rirRestrictedSubstanceAttachment(attachment=f)
            attachment.rir = rir_header
            attachment.is_judgement = True
            attachment.save()
        # Membuat Restricted Substance Checkedby dan kondisi Special Judgement
        rir_detail_restrictedsubstance_checkedby = rirDetailRestrictedSubstanceCheckedByForms().save(commit=False)
        rir_detail_restrictedsubstance_checkedby.restricted_substance_judgement   = rir_detail_restrictedsubstance_judgement
        rir_detail_restrictedsubstance_checkedby.save()
        messages.success(request, 'RIR Restricted Substance Approved')
        return redirect('qc_app:rir_judgement_index')
    return redirect('qc_app:rir_detail', rir_id)

@login_required
def rir_judgement_environmentalissue_approve(request, rir_id):
    # Memanggil Approval dan Header di Environmental Issue
    rir_approval = rirApprovalList.objects.filter(user = request.user).first()
    rir_header = rirHeader.objects.get(pk=rir_id)
    # Update data Environmental Issue Judgement
    rir_detail_environmentalissue_judgement = rirDetailEnvironmentalIssueJudgement.objects.filter(header = rir_id).first()
    post = request.POST.copy()
    post.update({'environmental_issue_judgement': True})
    rir_detail_environmentalissue_judgement_form  = rirDetailEnvironmentalIssueJudgementForms(request.POST, instance = rir_detail_environmentalissue_judgement)
    if rir_detail_environmentalissue_judgement_form.is_valid():
        # Simpan Data Environmental Issue Judgement
        rir_detail_environmentalissue_judgement = rir_detail_environmentalissue_judgement_form.save(commit=False)
        rir_detail_environmentalissue_judgement.environmental_issue_judgement = True
        rir_detail_environmentalissue_judgement.environmental_issue_user_judgement = rir_approval
        rir_detail_environmentalissue_judgement.save()
        # Simpan Attachment Environmental Issue Judgement (Apabila ada)
        files = request.FILES.getlist('attachment')
        for f in files:
            attachment = rirEnvironmentalIssueAttachment(attachment=f)
            attachment.rir = rir_header
            attachment.is_judgement = True
            attachment.save()
        # Membuat Environmental Issue Checkedby dan kondisi Special Judgement
        rir_detail_environmentalissue_checkedby = rirDetailEnvironmentalIssueCheckedByForms().save(commit=False)
        rir_detail_environmentalissue_checkedby.environmental_issue_judgement   = rir_detail_environmentalissue_judgement
        rir_detail_environmentalissue_checkedby.save()
        messages.success(request, 'RIR Environmental Issue Approved')
        return redirect('qc_app:rir_judgement_index')
    return redirect('qc_app:rir_detail', rir_id)

@login_required
def rir_checkedby_coa_approve(request, rir_id):
    # Memanggil Approval dan Header dari COA Content
    rir_approval = rirApprovalList.objects.filter(user = request.user).first()
    rir_header = rirHeader.objects.get(pk=rir_id)
    # Update data Coa Content Judgement
    rir_detail_coaContent_checkedby = rirDetailCoaContentCheckedby.objects.filter(coa_content_judgement__header_id = rir_id).first()
    # return HttpResponse(rir_detail_coaContent_checkedby)
    post = request.POST.copy()
    post.update({'coa_content_checked_by': True})
    rir_detail_coaContent_checkedby_form  = rirDetailCoaContentCheckedByForms(request.POST, instance = rir_detail_coaContent_checkedby)
    if rir_detail_coaContent_checkedby_form.is_valid():
        #Simpan Data Coa Content Checked By
        rir_detail_coaContent_checkedby = rir_detail_coaContent_checkedby_form.save(commit=False)
        rir_detail_coaContent_checkedby.coa_content_checked_by = True
        rir_detail_coaContent_checkedby.coa_content_user_checked_by = rir_approval
        rir_detail_coaContent_checkedby.save()
        #Simpan Data Coa Content Checked By apabila ada
        files = request.FILES.getlist('attachment')
        for f in files:
            attachment = rirCoaContentAttachment(attachment=f)
            attachment.rir = rir_header
            attachment.is_checkedby = True
            attachment.save()
        #Akan terjadi kondisi apabila adanya special judgement
        if rir_detail_coaContent_checkedby.is_special_judgement:
            # Kondisi apabila adanya special judgement (langsung akan dibuatkan approval kepada manager dan supervisor untuk ditindak lebih lanjut)
            # Update Special Judgement pada RIR Header
            rir_header.is_special_judgement = True
            rir_header.save()
            # Membuat Special Judgement untuk approval
            rir_special_judgement = rirSpecialJudgementForms().save(commit=False)
            rir_special_judgement.rir_id = rir_id
            rir_special_judgement.save()
            # Membuat Approval supervisor
            rir_approval_supervisor = rirApprovalSupervisorForms().save(commit=False)
            rir_approval_supervisor.specialjudgement = rir_special_judgement
            rir_approval_supervisor.save()
            return redirect('qc_app:rir_special_judgement_index')
        else:
            # Kondisi apabila tidak adanya special judgement(maka akan dibuat sesuai dengan adanya category) dan akan membuat judgement judgement berikutnya
            if rir_header.category.appearance:
                rir_detail_appearance_judgement = rirDetailAppearenceJudgementForms().save(commit=False)
                rir_detail_appearance_judgement.header = rir_header
                rir_detail_appearance_judgement.save()
            if rir_header.category.restricted_substance:
                rir_detail_restricted_substance_judgement = rirDetailRestrictedSubstanceJudgementForms().save(commit=False)
                rir_detail_restricted_substance_judgement.header = rir_header
                rir_detail_restricted_substance_judgement.save()
            if rir_header.category.environmental_issue:
                rir_detail_environmental_issue = rirDetailEnvironmentalIssueJudgementForms().save(commit=False)
                rir_detail_environmental_issue.header = rir_header
                rir_detail_environmental_issue.save()
            if rir_header.category.sample_test:
                rir_detail_sample_test = rirDetailSampleTestJudgementForms().save(commit=False)
                rir_detail_sample_test.header = rir_header
                rir_detail_sample_test.save()
            return redirect('qc_app:rir_judgement_index')
        
@login_required
def rir_checkedby_appearance_approve(request, rir_id):
    # Memanggil Approval dan Header dari Appearance
    rir_approval = rirApprovalList.objects.filter(user = request.user).first()
    rir_header = rirHeader.objects.get(pk=rir_id)
    # Update data Appearance Checked By
    rir_detail_appearance_checkedby = rirDetailAppearenceCheckedby.objects.filter(appearence_judgement__header_id = rir_id).first()
    # return HttpResponse(rir_detail_appearance_checkedby)
    post = request.POST.copy()
    post.update({'appearence_checked_by': True})
    rir_detail_appearance_checkedby_form  = rirDetailAppearenceCheckedByForms(request.POST, instance = rir_detail_appearance_checkedby)
    if rir_detail_appearance_checkedby_form.is_valid():
        #Simpan Data Appearance Checked By
        rir_detail_appearance_checkedby = rir_detail_appearance_checkedby_form.save(commit=False)
        rir_detail_appearance_checkedby.appearence_checked_by = True
        rir_detail_appearance_checkedby.appearence_user_checked_by = rir_approval
        rir_detail_appearance_checkedby.save()
        #Simpan Data Appearance Checked By apabila ada
        files = request.FILES.getlist('attachment')
        for f in files:
            attachment = rirAppearanceAttachment(attachment=f)
            attachment.rir = rir_header
            attachment.is_checkedby = True
            attachment.save()
        #Akan terjadi kondisi apabila adanya special judgement
        if rir_detail_appearance_checkedby.is_special_judgement:
            # Kondisi apabila adanya special judgement (langsung akan dibuatkan approval kepada manager dan supervisor untuk ditindak lebih lanjut)
            # Update Special Judgement pada RIR Header
            rir_header.is_special_judgement = True
            rir_header.save()
            # Membuat Special Judgement untuk approval
            rir_special_judgement = rirSpecialJudgementForms().save(commit=False)
            rir_special_judgement.rir_id = rir_id
            rir_special_judgement.save()
            # Membuat Approval supervisor
            rir_approval_supervisor = rirApprovalSupervisorForms().save(commit=False)
            rir_approval_supervisor.specialjudgement = rir_special_judgement
            rir_approval_supervisor.save()
            return redirect('qc_app:rir_special_judgement_index')
        else:
            return redirect('qc_app:rir_judgement_index')

@login_required
def rir_checkedby_sampletest_approve(request, rir_id):
    # Memanggil Approval dan Header dari Sample Test
    rir_approval = rirApprovalList.objects.filter(user = request.user).first()
    rir_header = rirHeader.objects.get(pk=rir_id)
    # Update data Sample Test Judgement
    rir_detail_sampletest_checkedby = rirDetailSampleTestCheckedby.objects.filter(sample_test_judgement__header_id = rir_id).first()
    # return HttpResponse(rir_detail_sampletest_checkedby)
    post = request.POST.copy()
    post.update({'sample_test_checked_by': True})
    rir_detail_sampletest_checkedby_form  = rirDetailSampleTestCheckedByForms(request.POST, instance = rir_detail_sampletest_checkedby)
    if rir_detail_sampletest_checkedby_form.is_valid():
        #Simpan Data Sample Test Checked By
        rir_detail_sampletest_checkedby = rir_detail_sampletest_checkedby_form.save(commit=False)
        rir_detail_sampletest_checkedby.sample_test_checked_by = True
        rir_detail_sampletest_checkedby.sample_test_user_checked_by = rir_approval
        rir_detail_sampletest_checkedby.save()
        #Simpan Data Sample Test Checked By apabila ada
        files = request.FILES.getlist('attachment')
        for f in files:
            attachment = rirSampleTestAttachment(attachment=f)
            attachment.rir = rir_header
            attachment.is_checkedby = True
            attachment.save()
        #Akan terjadi kondisi apabila adanya special judgement
        if rir_detail_sampletest_checkedby.is_special_judgement:
            # Kondisi apabila adanya special judgement (langsung akan dibuatkan approval kepada manager dan supervisor untuk ditindak lebih lanjut)
            # Update Special Judgement pada RIR Header
            rir_header.is_special_judgement = True
            rir_header.save()
            # Membuat Special Judgement untuk approval
            rir_special_judgement = rirSpecialJudgementForms().save(commit=False)
            rir_special_judgement.rir_id = rir_id
            rir_special_judgement.save()
            # Membuat Approval supervisor
            rir_approval_supervisor = rirApprovalSupervisorForms().save(commit=False)
            rir_approval_supervisor.specialjudgement = rir_special_judgement
            rir_approval_supervisor.save()
            return redirect('qc_app:rir_special_judgement_index')
        else:
            return redirect('qc_app:rir_judgement_index')
        

@login_required
def rir_checkedby_restrictedsubstance_approve(request, rir_id):
    # Memanggil Approval dan Header dari Restricted Substance
    rir_approval = rirApprovalList.objects.filter(user = request.user).first()
    rir_header = rirHeader.objects.get(pk=rir_id)
    # Update data Restricted Substance Judgement
    rir_detail_restrictedsubstance_checkedby = rirDetailRestrictedSubstanceCheckedby.objects.filter(restricted_substance_judgement__header_id = rir_id).first()
    # return HttpResponse(rir_detail_restrictedsubstance_checkedby)
    post = request.POST.copy()
    post.update({'restricted_substance_checked_by': True})
    rir_detail_restrictedsubstance_checkedby_form  = rirDetailRestrictedSubstanceCheckedByForms(request.POST, instance = rir_detail_restrictedsubstance_checkedby)
    if rir_detail_restrictedsubstance_checkedby_form.is_valid():
        #Simpan Data Restricted Substance Checked By
        rir_detail_restrictedsubstance_checkedby = rir_detail_restrictedsubstance_checkedby_form.save(commit=False)
        rir_detail_restrictedsubstance_checkedby.restricted_substance_checked_by = True
        rir_detail_restrictedsubstance_checkedby.restricted_substance_user_checked_by = rir_approval
        rir_detail_restrictedsubstance_checkedby.save()
        #Simpan Data Restricted Substance Checked By apabila ada
        files = request.FILES.getlist('attachment')
        for f in files:
            attachment = rirRestrictedSubstanceAttachment(attachment=f)
            attachment.rir = rir_header
            attachment.is_checkedby = True
            attachment.save()
        #Akan terjadi kondisi apabila adanya special judgement
        if rir_detail_restrictedsubstance_checkedby.is_special_judgement:
            # Kondisi apabila adanya special judgement (langsung akan dibuatkan approval kepada manager dan supervisor untuk ditindak lebih lanjut)
            # Update Special Judgement pada RIR Header
            rir_header.is_special_judgement = True
            rir_header.save()
            # Membuat Special Judgement untuk approval
            rir_special_judgement = rirSpecialJudgementForms().save(commit=False)
            rir_special_judgement.rir_id = rir_id
            rir_special_judgement.save()
            # Membuat Approval supervisor
            rir_approval_supervisor = rirApprovalSupervisorForms().save(commit=False)
            rir_approval_supervisor.specialjudgement = rir_special_judgement
            rir_approval_supervisor.save()
            return redirect('qc_app:rir_special_judgement_index')
        else:
            return redirect('qc_app:rir_judgement_index')


@login_required
def rir_checkedby_environmentalissue_approve(request, rir_id):
    # Memanggil Approval dan Header dari Environmental Issue
    rir_approval = rirApprovalList.objects.filter(user = request.user).first()
    rir_header = rirHeader.objects.get(pk=rir_id)
    # Update data Environmental Issue Judgement
    rir_detail_environmentalissue_checkedby = rirDetailEnvironmentalIssueCheckedby.objects.filter(environmental_issue_judgement__header_id = rir_id).first()
    # return HttpResponse(rir_detail_environmentalissue_checkedby)
    post = request.POST.copy()
    post.update({'environmental_issue_checked_by': True})
    rir_detail_environmentalissue_checkedby_form  = rirDetailEnvironmentalIssueCheckedByForms(request.POST, instance = rir_detail_environmentalissue_checkedby)
    if rir_detail_environmentalissue_checkedby_form.is_valid():
        #Simpan Data Environmental Issue Checked By
        rir_detail_environmentalissue_checkedby = rir_detail_environmentalissue_checkedby_form.save(commit=False)
        rir_detail_environmentalissue_checkedby.environmental_issue_checked_by = True
        rir_detail_environmentalissue_checkedby.environmental_issue_user_checked_by = rir_approval
        rir_detail_environmentalissue_checkedby.save()
        #Simpan Data Environmental Issue Checked By apabila ada
        files = request.FILES.getlist('attachment')
        for f in files:
            attachment = rirEnvironmentalIssueAttachment(attachment=f)
            attachment.rir = rir_header
            attachment.is_checkedby = True
            attachment.save()
        #Akan terjadi kondisi apabila adanya special judgement
        if rir_detail_environmentalissue_checkedby.is_special_judgement:
            # Kondisi apabila adanya special judgement (langsung akan dibuatkan approval kepada manager dan supervisor untuk ditindak lebih lanjut)
            # Update Special Judgement pada RIR Header
            rir_header.is_special_judgement = True
            rir_header.save()
            # Membuat Special Judgement untuk approval
            rir_special_judgement = rirSpecialJudgementForms().save(commit=False)
            rir_special_judgement.rir_id = rir_id
            rir_special_judgement.save()
            # Membuat Approval supervisor
            rir_approval_supervisor = rirApprovalSupervisorForms().save(commit=False)
            rir_approval_supervisor.specialjudgement = rir_special_judgement
            rir_approval_supervisor.save()
            return redirect('qc_app:rir_special_judgement_index')
        else:
            return redirect('qc_app:rir_judgement_index')


@login_required
def rir_checked_by_index(request):
    checkedby_coa = rirDetailCoaContentCheckedby.objects.filter(coa_content_checked_by = False ).order_by('-id')
    checkedby_appearance = rirDetailAppearenceCheckedby.objects.filter(appearence_checked_by = False ).order_by('-id')
    checkedby_restricted_substance = rirDetailRestrictedSubstanceCheckedby.objects.filter(restricted_substance_checked_by = False ).order_by('-id')
    checkedby_sample_test = rirDetailSampleTestCheckedby.objects.filter(sample_test_checked_by = False ).order_by('-id')
    checkedby_environmental_issue = rirDetailEnvironmentalIssueCheckedby.objects.filter(environmental_issue_checked_by = False ).order_by('-id')
    context = {
        'checkedby_coa' : checkedby_coa,
        'checkedby_appearance' : checkedby_appearance,
        'checkedby_restricted_substance' : checkedby_restricted_substance,
        'checkedby_sample_test' : checkedby_sample_test,
        'checkedby_environmental_issue' : checkedby_environmental_issue,
        
    }
    return render(request, 'qc_app/rir_checkedby_index.html', context)

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
from django.shortcuts import render, redirect
from accounting_app.models import cashPayment, cashPaymentAttachment, cashPaymentApprovalManager, cashPaymentApprovalAccountingManager, cashPaymentApprovalPresident, cashPaymentApprovalCashier
from django.contrib.auth.decorators import login_required
from accounting_app.forms import cashPaymentForms, cashPaymentAttachmentForms, cashPaymentApprovalManagerForms, cashPaymentApprovalAccountingManagerForms, cashPaymentApprovalPresidentForms, cashPaymentApprovalCashierForms
from django.contrib import messages
from django.http import Http404, HttpResponse
import datetime

# Create your views here.
@login_required
def dashboard(request):
    return render(request, 'accounting_app/dashboard.html')

@login_required
def cashPayment_index(request):
    cashPayments = cashPayment.objects.order_by('-created_at')
    managers = cashPaymentApprovalManager.objects.order_by('-id')
    managersAccountings = cashPaymentApprovalAccountingManager.objects.order_by('-id')
    presidents = cashPaymentApprovalPresident.objects.order_by('-id')
    cashiers = cashPaymentApprovalCashier.objects.order_by('-id')
    context = {
         'cashpayments'             : cashPayments,
         'managers'                 : managers,
         'managersAccountings'      : managersAccountings,
         'presidents'               : presidents,
         'cashiers'                 : cashiers,
         'form_manager'             : cashPaymentApprovalManagerForms,
         'form_manager_accounting'  : cashPaymentApprovalAccountingManagerForms,
         'form_president'           : cashPaymentApprovalPresidentForms,
         'form_cashier'             : cashPaymentApprovalCashierForms,
    }
    return render(request, 'accounting_app/cashPayment_index.html', context)

@login_required
def cashPayment_add(request):
    if request.method == "POST":
         cashPayment_form = cashPaymentForms (data=request.POST)
         approval_manager_form = cashPaymentApprovalManagerForms(data=request.POST)
         cashPayment_attachment_form = cashPaymentAttachmentForms(data=request.POST)
         if cashPayment_form.is_valid() and approval_manager_form.is_valid() and cashPayment_attachment_form.is_valid() :
            # Simpan data cashPayment
            cashPayment = cashPayment_form.save(commit=False)
            cashPayment.assignee = request.user
            cashPayment.save()
            # Simpan data RP total di cashPayment
            rp_total = 0
            if(cashPayment.rp_detail_1 is not None):
                 rp_total = rp_total + cashPayment.rp_detail_1
            if(cashPayment.rp_detail_2 is not None):
                 rp_total = rp_total + cashPayment.rp_detail_2
            if(cashPayment.rp_detail_3 is not None):
                 rp_total = rp_total + cashPayment.rp_detail_3
            if(cashPayment.rp_detail_4 is not None):
                 rp_total = rp_total + cashPayment.rp_detail_4
            if(cashPayment.rp_detail_5 is not None):
                 rp_total = rp_total + cashPayment.rp_detail_5
            if(cashPayment.rp_detail_6 is not None):
                 rp_total = rp_total + cashPayment.rp_detail_6
            if(cashPayment.rp_detail_7 is not None):
                 rp_total = rp_total + cashPayment.rp_detail_7
            if(cashPayment.rp_detail_8 is not None):
                 rp_total = rp_total + cashPayment.rp_detail_8
            if(cashPayment.rp_detail_9 is not None):
                 rp_total = rp_total + cashPayment.rp_detail_9
            if(cashPayment.rp_detail_10 is not None):
                 rp_total = rp_total + cashPayment.rp_detail_10
            if(cashPayment.rp_detail_11 is not None):
                 rp_total = rp_total + cashPayment.rp_detail_11
            if(cashPayment.rp_detail_12 is not None):
                 rp_total = rp_total + cashPayment.rp_detail_12
            cashPayment.rp_total = rp_total
            cashPayment.save()
            # Simpan data attachment
            files = request.FILES.getlist('attachment')
            for f in files:
                 attachment = cashPaymentAttachment(attachment=f)
                 attachment.cashPayment = cashPayment
                 attachment.save()
            # membuat data Approval Manager
            manager = approval_manager_form.save(commit=False)
            manager.cashPayment = cashPayment
            manager.save()
            messages.success(request, 'Success Add Cash Payment', 'success')
            return redirect('accounting_app:cashPayment_index')
         else:
              print(cashPayment_form.errors and approval_manager_form.errors and cashPayment_attachment_form)
    else:
         cashPayment_form = cashPaymentForms()
         cashPayment_attachment_form = cashPaymentAttachmentForms()
         approval_manager_form = cashPaymentApprovalManagerForms()

    context = {
    'cashPayment_form'  : cashPaymentForms,
    'cashPayment_attachment_form'  : cashPaymentAttachmentForms,
    'manager_form'      : cashPaymentApprovalManagerForms,
    }
    return render(request, 'accounting_app/cashPayment_add.html', context)

@login_required
def cashPayment_detail(request, cashPayment_id):
    cashPayment_detail = cashPayment.objects.get(pk=cashPayment_id)
    attachment = cashPaymentAttachment.objects.filter(cashPayment = cashPayment_detail).values('attachment',)
    context = {
         'cashPayment'  : cashPayment_detail,
         'attachment'   : attachment,
    }
    return render(request, 'accounting_app/cashPayment_detail.html', context)

@login_required
def cashPayment_manager_approve(request, cashPayment_id):
    try:
        # mengambil data task yang akan di approve berdasarkan cashPayment id
        manager = cashPaymentApprovalManager.objects.get(pk=cashPayment_id)
        # mengapprove
        manager.is_approve_manager = True
        manager.manager = request.user
        manager.save()
        # membuat approval manager accounting
        approval_manager_accounting_form = cashPaymentApprovalAccountingManagerForms(data=request.POST)
        manager_accounting = approval_manager_accounting_form.save(commit=False)
        manager_accounting.cashPayment_approval_manager = manager
        manager_accounting.save()
        # set Message sukses dan redirect ke halaman daftar CashPayment
        messages.success(request, 'Approved Successfully')
        return redirect('accounting_app:cashPayment_index')
    except cashPaymentApprovalManager.DoesNotExist:
        raise Http404("Cash Payment Error!")

@login_required
def cashPayment_manager_reject(request,cashPayment_id):
    # try:
        # mengambil data task yang akan reject berdasarkan task id
        manager = cashPaymentApprovalManager.objects.get(pk=cashPayment_id)
        post = request.POST.copy() 
        post.update({'is_rejected_manager': True})
        request.POST = post
        approval_manager_form = cashPaymentApprovalManagerForms(request.POST, instance=manager)
        if approval_manager_form.is_valid():
            reject = approval_manager_form.save(commit=False)
            reject.manager = request.user
            reject.save()
            return redirect('accounting_app:cashPayment_index')
        return HttpResponse(approval_manager_form)
    
@login_required
def cashPayment_accounting_manager_approve(request, cashPayment_id):
    try:
        manager_accounting = cashPaymentApprovalAccountingManager.objects.get(pk=cashPayment_id)
        # mengapprove
        manager_accounting.is_approve_manager_accounting = True
        manager_accounting.manager_accounting = request.user
        manager_accounting.save()
        #  membuat approval president
        approval_president_form = cashPaymentApprovalPresidentForms(data=request.POST)
        president = approval_president_form.save(commit=False)
        president.cashPayment_approval_accounting_manager = manager_accounting
        president.save()
        return redirect('accounting_app:cashPayment_index')
    except cashPaymentApprovalAccountingManager.DoesNotExist:
        raise Http404("Cash Payment Error!")

@login_required
def cashPayment_accounting_manager_reject(request,cashPayment_id):
    # try:
        # mengambil data task yang akan reject berdasarkan task id
        accounting_manager = cashPaymentApprovalAccountingManager.objects.get(pk=cashPayment_id)
        post = request.POST.copy() 
        post.update({'is_rejected_manager_accounting': True})
        request.POST = post
        approval_accounting_manager_form = cashPaymentApprovalAccountingManagerForms(request.POST, instance=accounting_manager)
        if approval_accounting_manager_form.is_valid():
            reject = approval_accounting_manager_form.save(commit=False)
            reject.manager_accounting = request.user
            reject.save()
            return redirect('accounting_app:cashPayment_index')
        return HttpResponse(approval_accounting_manager_form)    
    
@login_required
def cashPayment_president_approval(request, cashPayment_id):
    try:
        president = cashPaymentApprovalPresident.objects.get(pk=cashPayment_id)
        # mengapprove
        president.is_approve_president = True
        president.president = request.user
        president.save()
        # membuat approval cashier
        approval_cashier_form = cashPaymentApprovalCashierForms(data=request.POST)
        ticket_no = "TKT-" + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + "-" + str(president.cashPayment_approval_accounting_manager.cashPayment_approval_manager.cashPayment.assignee)
        cashier = approval_cashier_form.save(commit=False)
        cashier.cashPayment_approval_president = president
        cashier.ticket_no = ticket_no
        cashier.save()
        return redirect('accounting_app:cashPayment_index')
    except cashPaymentApprovalPresident.DoesNotExist:
        raise Http404("Cash Payment Error!")
    
@login_required
def cashPayment_president_reject(request,cashPayment_id):
    # try:
        # mengambil data task yang akan reject berdasarkan task id
        president = cashPaymentApprovalPresident.objects.get(pk=cashPayment_id)
        post = request.POST.copy() 
        post.update({'is_rejected_president': True})
        request.POST = post
        approval_president_form = cashPaymentApprovalPresidentForms(request.POST, instance=president)
        if approval_president_form.is_valid():
            reject = approval_president_form.save(commit=False)
            reject.president = request.user
            reject.save()
            return redirect('accounting_app:cashPayment_index')
        return HttpResponse(approval_president_form)   

@login_required
def cashPayment_cashier_approval(request, cashPayment_id):
    try:
        cashier = cashPaymentApprovalCashier.objects.get(pk=cashPayment_id)
        # Mengapprove
        cashier.is_approve_cashier = True
        cashier.cashier = request.user
        cashier.save()
        return redirect('accounting_app:cashPayment_index')
    except cashPaymentApprovalCashier.DoesNotExist:
        raise Http404("Cash Payment Error!")

@login_required
def cashPayment_cashier_reject(request,cashPayment_id):
    # try:
        # mengambil data task yang akan reject berdasarkan task id
        cashier = cashPaymentApprovalCashier.objects.get(pk=cashPayment_id)
        post = request.POST.copy() 
        post.update({'is_rejected_cashier': True})
        request.POST = post
        approval_cashier_form = cashPaymentApprovalCashierForms(request.POST, instance=cashier)
        if approval_cashier_form.is_valid():
            reject = approval_cashier_form.save(commit=False)
            reject.cashier = request.user
            reject.save()
            return redirect('accounting_app:cashPayment_index')
        return HttpResponse(approval_cashier_form)   



from django.shortcuts import render, redirect
from accounting_app.models import cashPayment, cashPaymentApprovalManager, cashPaymentApprovalAccountingManager, cashPaymentApprovalPresident, cashPaymentApprovalCashier
from django.contrib.auth.decorators import login_required
from accounting_app.forms import cashPaymentForms, cashPaymentApprovalManagerForms, cashPaymentApprovalAccountingManagerForms, cashPaymentApprovalPresidentForms, cashPaymentApprovalCashierForms
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

    return render(request, 'accounting_app/cashPayment_add.html')

@login_required
def cashPayment_detail(request, cashPayment_id):
    cashPayment = cashPayment.objects.get(pk=cashPayment_id)
    return render(request, 'accounting_app/detail.html', {'cashPayment':cashPayment})

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
            return redirect('accounting_app:ticket_index')
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
            return redirect('accounting_app:ticket_index')
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
        cashier = approval_cashier_form.save(commit=False)
        cashier.cashPayment_approval_president = president
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
            return redirect('accounting_app:ticket_index')
        return HttpResponse(approval_president_form)   

@login_required
def cashPayment_cashier_approval(request, cashPayment_id):
    try:
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
            return redirect('accounting_app:ticket_index')
        return HttpResponse(approval_cashier_form)   



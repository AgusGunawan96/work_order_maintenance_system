from django.shortcuts import render, redirect
from accounting_app.models import cashPayment, cashPaymentAttachment, cashPaymentApprovalManager, cashPaymentApprovalAccountingManager, cashPaymentApprovalPresident, cashPaymentApprovalCashier, cashPaymentBalance, cashierAttachment, advAttachment, settleAttachment, advanceApprovalManager, advanceApprovalAccountingManager, advanceApprovalPresident, advanceApprovalCashier
from django.contrib.auth.decorators import login_required
from accounting_app.forms import cashPaymentForms, cashPaymentAttachmentForms, cashPaymentApprovalManagerForms, cashPaymentApprovalAccountingManagerForms, cashPaymentApprovalPresidentForms, cashPaymentApprovalCashierForms, cashPaymentDebitForms, cashPaymentCreditForms, cashPaymentSettleForms, cashPaymentBalanceForms, cashPaymentCashierAttachmentForms, cashPaymentSettleAttachmentForms, cashPaymentAdvAttachmentForms, cashPaymentAdvForms, cashPaymentCashierForms, advanceApprovalManagerForms, advanceApprovalAccountingManagerForms, advanceApprovalPresidentForms, advanceApprovalCashierForms
from django.contrib import messages
from django.http import Http404, HttpResponse,JsonResponse
import datetime
import csv
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
import xlwt
from csv import reader

# Create your views here.
@login_required
def dashboard(request):
    return render(request, 'accounting_app/dashboard.html')

# CASHPAYMENT START
@login_required
def cashPayment_settle_index(request, filter_month = False, filter_year = False):
    settle = cashPayment.objects.filter(is_settle__exact = True)
    attachment_settle = settleAttachment.objects.order_by('-id')
    context = {
        'settles'       : settle,
        'settle_attachments'    : attachment_settle,
    }
    return render(request, 'accounting_app/cashPayment_settle_index.html', context)
    return HttpResponse(settle)

@login_required
def cashPayment_adv_index(request, filter_month = False, filter_year = False):
    adv = cashPayment.objects.filter(is_adv__exact = True)
    attachment_adv = advAttachment.objects.order_by('-id')
    context = {
        'advs'   :   adv,
        'adv_attachments'    : attachment_adv,
    }
    return render(request, 'accounting_app/cashPayment_adv_index.html', context)
    return HttpResponse(adv)
    return HttpResponse("Adv Index")    

@login_required
def cashPayment_index(request):
    cashPayments = cashPayment.objects.order_by('-created_at')
    managers = cashPaymentApprovalManager.objects.order_by('-id')
    managersAccountings = cashPaymentApprovalAccountingManager.objects.order_by('-id')
    presidents = cashPaymentApprovalPresident.objects.order_by('-id')
    cashiers = cashPaymentApprovalCashier.objects.order_by('-id')
    attachments = cashPaymentAttachment.objects.order_by('-id')
    downloadcsv = cashPaymentBalance.objects.order_by('cashPayment_balance_no')
    downloadcsv = list(downloadcsv)
    del downloadcsv[0]
    # return HttpResponse(downloadcsv)
        
    context = {
         'cashpayments'             : cashPayments,
         'managers'                 : managers,
         'managersAccountings'      : managersAccountings,
         'presidents'               : presidents,
         'cashiers'                 : cashiers,
         'attachments'              : attachments,
         'csv_list'                 : downloadcsv,
         'form_cashier_attachment'  : cashPaymentCashierAttachmentForms,
         'form_settle_attachment'   : cashPaymentSettleAttachmentForms,
         'form_adv_attachment'      : cashPaymentAdvAttachmentForms,
         'form_manager'             : cashPaymentApprovalManagerForms,
         'form_manager_accounting'  : cashPaymentApprovalAccountingManagerForms,
         'form_president'           : cashPaymentApprovalPresidentForms,
         'form_cashier'             : cashPaymentApprovalCashierForms,
         'form_cashier_transfer'    : cashPaymentCashierForms,
         'form_debit'               : cashPaymentDebitForms,
         'form_credit'              : cashPaymentCreditForms,
         'form_settle'              : cashPaymentSettleForms,
         'form_adv'                 : cashPaymentAdvForms,
    }
    return render(request, 'accounting_app/cashPayment_index.html', context)
    return HttpResponse(calculate_cashPayment_balance_open())

@login_required
def cashPayment_monitoring(request):
    cashPayments = cashPayment.objects.order_by('created_at')
    context = {
         'cashPayments'             : cashPayments,
    }
    return render(request, 'accounting_app/cashPayment_monitoring.html', context)

@login_required
def cashPayment_settle_add(request):
     if request.method == "POST":
        cashPayment_settle_form = cashPaymentSettleForms(data=request.POST)
        cashPayment_balance = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=datetime.datetime.now().strftime('%Y%m')).first()
        balance_month = datetime.datetime.now().strftime('%Y%m')
        balance_month_previous = datetime.datetime.strptime(balance_month, '%Y%m') - relativedelta(months=1)
        balance_previous = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=datetime.datetime.strftime(balance_month_previous, '%Y%m')).first()
        if cashPayment_settle_form.is_valid():
            #  simpan data cashPayment
            cashPayment_settle = cashPayment_settle_form.save(commit=False)
            ticket_maks = cashPayment.objects.filter(ticket_no__contains=datetime.datetime.now().strftime('%Y%m')).count() + 1
            ticket_no = "CP" + datetime.datetime.now().strftime('%Y%m') + str("%003d" % ( ticket_maks, ))        
            cashPayment_settle.ticket_no = ticket_no
            cashPayment_settle.is_settle = True
            if(cashPayment_settle.is_debit):
                if(cashPayment_balance is None):
                    balance = cashPaymentBalanceForms().save(commit=False)
                    if(balance_previous is not None):
                        balance_previous.balance_cashPayment_close = calculate_cashPayment_balance_open()
                        balance_previous.exchange_rate_close = balance_previous.exchange_rate_open
                        balance.balance_cashPayment_open = calculate_cashPayment_balance_open() 
                        balance.exchange_rate_open = balance_previous.exchange_rate_open
                        balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                        balance_previous.save()
                        balance.save()
                    else:
                        balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                        balance.save()
                else:
                    cashPayment_balance.save()
                    cashPayment_settle.save()
            if(cashPayment_settle.is_credit):
                if(cashPayment_balance is None):
                    balance = cashPaymentBalanceForms().save(commit=False)
                    if(balance_previous is not None):
                        balance_previous.balance_cashPayment_close = calculate_cashPayment_balance_open()
                        balance_previous.exchange_rate_close = balance_previous.exchange_rate_open
                        balance.balance_cashPayment_open = calculate_cashPayment_balance_open() 
                        balance.exchange_rate_open = balance_previous.exchange_rate_open
                        balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                        balance_previous.save()
                        balance.save()
                    else:
                        balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                        balance.save()
                else:
                    cashPayment_balance.save()
                    cashPayment_settle.save()
            cashPayment_settle.save()
            # Simpan data attachment
            files = request.FILES.getlist('attachment')
            for f in files:
                 attachment = settleAttachment(attachment=f)
                 attachment.cashPayment = cashPayment_settle
                 attachment.save()
            messages.success(request, 'Success Add Settle Cash Payment', 'success')
            return redirect('accounting_app:cashPayment_index')
        
@login_required
def cashPayment_adv_add(request):
     if request.method == "POST":
        cashPayment_adv_form = cashPaymentAdvForms(data=request.POST)
        cashPayment_balance = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=datetime.datetime.now().strftime('%Y%m')).first()
        balance_month = datetime.datetime.now().strftime('%Y%m')
        balance_month_previous = datetime.datetime.strptime(balance_month, '%Y%m') - relativedelta(months=1)
        balance_previous = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=datetime.datetime.strftime(balance_month_previous, '%Y%m')).first()
        if cashPayment_adv_form.is_valid():
            #  simpan data cashPayment
            cashPayment_adv = cashPayment_adv_form.save(commit=False)
            ticket_maks = cashPayment.objects.filter(ticket_no__contains=datetime.datetime.now().strftime('%Y%m')).count() + 1
            ticket_no = "CP" + datetime.datetime.now().strftime('%Y%m') + str("%003d" % ( ticket_maks, ))        
            cashPayment_adv.ticket_no = ticket_no
            cashPayment_adv.is_adv = True
            if(cashPayment_adv.is_debit):
                if(cashPayment_balance is None):
                    balance = cashPaymentBalanceForms().save(commit=False)
                    if(balance_previous is not None):
                        balance_previous.balance_cashPayment_close = calculate_cashPayment_balance_open()
                        balance_previous.exchange_rate_close = balance_previous.exchange_rate_open
                        balance.balance_cashPayment_open = calculate_cashPayment_balance_open() 
                        balance.exchange_rate_open = balance_previous.exchange_rate_open
                        balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                        balance_previous.save()
                        balance.save()
                    else:
                        balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                        balance.save()
                else:
                    cashPayment_balance.save()
                    cashPayment_adv.save()
            if(cashPayment_adv.is_credit):
                if(cashPayment_balance is None):
                    balance = cashPaymentBalanceForms().save(commit=False)
                    if(balance_previous is not None):
                        balance_previous.balance_cashPayment_close = calculate_cashPayment_balance_open()
                        balance_previous.exchange_rate_close = balance_previous.exchange_rate_open
                        balance.exchange_rate_open = balance_previous.exchange_rate_open
                        balance.balance_cashPayment_open = calculate_cashPayment_balance_open()
                        balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                        balance_previous.save()
                        balance.save()
                    else:
                        balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                        balance.save()
                else:
                    cashPayment_balance.save()
                    cashPayment_adv.save()
            cashPayment_adv.save()
            # Simpan data attachment
            files = request.FILES.getlist('attachment')
            for f in files:
                 attachment = advAttachment(attachment=f)
                 attachment.cashPayment = cashPayment_adv
                 attachment.save()
            messages.success(request, 'Success Add Adv Cash Payment', 'success')
            return redirect('accounting_app:cashPayment_index')
        
@login_required
def cashPayment_debit_add(request):
     if request.method == "POST":
        cashPayment_debit_form = cashPaymentDebitForms (data=request.POST)
        if cashPayment_debit_form.is_valid():
            #  simpan data cashPayment

            # cashPayment_balance = masterAccounting.objects.get(pk=1)
            cashPayment_balance = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=datetime.datetime.now().strftime('%Y%m')).first()
            balance_month = datetime.datetime.now().strftime('%Y%m')
            balance_month_previous = datetime.datetime.strptime(balance_month, '%Y%m') - relativedelta(months=1)
            balance_previous = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=datetime.datetime.strftime(balance_month_previous, '%Y%m')).first()
            # Menambahkan CashPayment Debit
            cashPayment_debit = cashPayment_debit_form.save(commit=False)
            ticket_maks = cashPayment.objects.filter(ticket_no__contains=datetime.datetime.now().strftime('%Y%m')).count() + 1
            ticket_no = "CP" + datetime.datetime.now().strftime('%Y%m') + str("%003d" % ( ticket_maks, ))        
            cashPayment_debit.ticket_no = ticket_no
            cashPayment_debit.is_debit = True
            # Edit Penambahan balance pada Accounting
            # cashPayment_balance.balance_cashPayment = cashPayment_balance.balance_cashPayment + cashPayment_debit.rp_total
            # Menambahkan Master balance
            if(cashPayment_balance is None):
                balance = cashPaymentBalanceForms().save(commit=False)
                if(balance_previous is not None):
                    balance_previous.balance_cashPayment_close = calculate_cashPayment_balance_open()
                    balance_previous.exchange_rate_close = balance_previous.exchange_rate_open
                    balance.balance_cashPayment_open = calculate_cashPayment_balance_open() 
                    balance.exchange_rate_open = balance_previous.exchange_rate_open
                    balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                    balance_previous.save()
                    balance.save()
                else:
                    balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                    balance.save()
            else:
                cashPayment_balance.save()
            cashPayment_debit.save()

            messages.success(request, 'Success Add Debit Cash Payment', 'success')
            return redirect('accounting_app:cashPayment_index')

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
    'cashPayment_form'              : cashPaymentForms,
    'cashPayment_attachment_form'   : cashPaymentAttachmentForms,
    'manager_form'                  : cashPaymentApprovalManagerForms,
    }
    return render(request, 'accounting_app/cashPayment_add.html', context)

# CASH PAYMENT START
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
def cashPayment_manager_check(request, cashPayment_id):
    try:
        # Mengambil data manager yang akan di check berdasarkan cashPayment id
        manager = cashPaymentApprovalManager.objects.get(pk=cashPayment_id)
        # Approve Check
        manager.is_checked_manager = True
        manager.save()
        messages.success(request, 'Checked Succcesfully')
        return redirect('accounting_app:cashPayment_index')
    except cashPaymentApprovalManager.DoesNotExist:
         raise Http404("Cash Payment Error!")

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
            messages.success(request, 'Reject Succcesfully')
            return redirect('accounting_app:cashPayment_index')
        return HttpResponse(approval_manager_form)

@login_required
def cashPayment_accounting_manager_check(request, cashPayment_id):
    try:
        # Mengambil data manager accounting yang akan di check berdasarkan cashPayment id
        manager_accounting = cashPaymentApprovalAccountingManager.objects.get(pk=cashPayment_id)
        # Approve Check
        manager_accounting.is_checked_manager_accounting = True
        manager_accounting.save()
        messages.success(request, 'Checked Succcesfully')
        return redirect('accounting_app:cashPayment_index')
    except cashPaymentApprovalAccountingManager.DoesNotExist:
         raise Http404("Cash Payment Error!")


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
        messages.success(request, 'Approve Succcesfully')
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
            messages.success(request, 'Reject Succcesfully')
            return redirect('accounting_app:cashPayment_index')
        return HttpResponse(approval_accounting_manager_form)    

@login_required
def cashPayment_president_check(request, cashPayment_id):
    try:
        # Mengambil data manager accounting yang akan di check berdasarkan cashPayment id
        president = cashPaymentApprovalPresident.objects.get(pk=cashPayment_id)
        # Approve Check
        president.is_checked_president = True
        president.save()
        messages.success(request, 'Checked Succcesfully')
        return redirect('accounting_app:cashPayment_index')
    except cashPaymentApprovalPresident.DoesNotExist:
         raise Http404("Cash Payment Error!")
        
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
        ticket_maks = cashPayment.objects.filter(ticket_no__contains=datetime.datetime.now().strftime('%Y%m')).count() + 1
        ticket_no = "CP" + datetime.datetime.now().strftime('%Y%m') + str("%003d" % ( ticket_maks, ))
        cashier = approval_cashier_form.save(commit=False)
        cashier.cashPayment_approval_president = president
        cashier.save()
        # Create Ticket number dan credit menjadi True buat cashPayment
        cashPayment_id = president.cashPayment_approval_accounting_manager.cashPayment_approval_manager.cashPayment.id
        cashpayment = cashPayment.objects.get(pk=cashPayment_id)
        cashpayment.is_credit = True
        cashpayment.ticket_no = ticket_no
        cashpayment.save()
       
        messages.success(request, 'Approval Succcesfully')
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
            messages.success(request, 'Reject Succcesfully')
            return redirect('accounting_app:cashPayment_index')
        return HttpResponse(approval_president_form)   

@login_required
def cashPayment_cashier_check(request, cashPayment_id):
    try:
        # Mengambil data manager accounting yang akan di check berdasarkan cashPayment id
        cashier = cashPaymentApprovalCashier.objects.get(pk=cashPayment_id)
        # Approve Check
        cashier.is_checked_cashier = True
        cashier.save()
        messages.success(request, 'Checked Succcesfully')
        return redirect('accounting_app:cashPayment_index')
    except cashPaymentApprovalCashier.DoesNotExist:
         raise Http404("Cash Payment Error!")
    
@login_required
def cashPayment_cashier_approval(request, cashPayment_id):
    try:
     if request.method == "POST":
        cashPayment_credit_form = cashPaymentCashierForms(data=request.POST)
        cashier = cashPaymentApprovalCashier.objects.get(pk=cashPayment_id)
        # cashPayment_balance = masterAccounting.objects.get(pk=1)
        cashPayment_balance = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=datetime.datetime.now().strftime('%Y%m')).first()
        balance_month = datetime.datetime.now().strftime('%Y%m')
        balance_month_previous = datetime.datetime.strptime(balance_month, '%Y%m') - relativedelta(months=1)
        balance_previous = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=datetime.datetime.strftime(balance_month_previous, '%Y%m')).first()
        if request.POST['password'] and request.POST['type'] == 'Transfer Cash':
            identity = cashier.cashPayment_approval_president.cashPayment_approval_accounting_manager.cashPayment_approval_manager.cashPayment.assignee
            user = User.objects.get(username=identity)
            valid_password = check_password(request.POST['password'], user.password)
            if valid_password: #apabila password sudah benar
                if cashPayment_credit_form.is_valid():
                    # Mengapprove
                    cashier.is_approve_cashier = True
                    cashier.cashier = request.user
                    # Menambahkan remark pada cashPayment
                    cashPayment_form = cashPayment_credit_form.save(commit=False)
                    cashPayment_id = cashier.cashPayment_approval_president.cashPayment_approval_accounting_manager.cashPayment_approval_manager.cashPayment.id
                    cashPayment_credit = cashPayment.objects.get(pk=cashPayment_id)
                    cashPayment_credit.remark = cashPayment_form.remark
                    cashPayment_credit.type   = cashPayment_form.type
                    # Mengurangi Balance pada Master Balance
                    # cashPayment_balance.balance_cashPayment = cashPayment_balance.balance_cashPayment - cashPayment_credit.rp_total
                    # cashPayment_balance.save()
                    # Edit untuk cashPayment
                    if(cashPayment_balance is None):
                        balance = cashPaymentBalanceForms().save(commit=False)
                        if(balance_previous is not None):
                            balance_previous.balance_cashPayment_close = calculate_cashPayment_balance_open()
                            balance_previous.exchange_rate_close = balance_previous.exchange_rate_open
                            balance.balance_cashPayment_open = calculate_cashPayment_balance_open() 
                            balance.exchange_rate_open = balance_previous.exchange_rate_open
                            balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                            balance_previous.save()
                            balance.save()
                        else:
                            balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                            balance.save()
                    else:
                        cashPayment_balance.save()
                                # Simpan data attachment
                    files = request.FILES.getlist('attachment')
                    for f in files:
                         attachment = cashierAttachment(attachment=f)
                         attachment.cashPayment = cashPayment_credit
                         attachment.save()
                    cashPayment_credit.save()
                    cashier.save()
                    messages.success(request, 'Transfer Succcesfully')
            else:
                messages.warning(request, 'Password yang dimasukan salah')
                return redirect('accounting_app:cashPayment_index')
            # mari kita buat Validasi password dari Assignee, apakah sudah sesuai apa belum
        else:
            if cashPayment_credit_form.is_valid():
                # Mengapprove
                cashier.is_approve_cashier = True
                cashier.cashier = request.user
                # Menambahkan remark pada cashPayment
                cashPayment_form = cashPayment_credit_form.save(commit=False)
                cashPayment_id = cashier.cashPayment_approval_president.cashPayment_approval_accounting_manager.cashPayment_approval_manager.cashPayment.id
                cashPayment_credit = cashPayment.objects.get(pk=cashPayment_id)
                cashPayment_credit.remark = cashPayment_form.remark
                cashPayment_credit.type   = cashPayment_form.type
                # Mengurangi Balance pada Master Balance
                # cashPayment_balance.balance_cashPayment = cashPayment_balance.balance_cashPayment - cashPayment_credit.rp_total
                # cashPayment_balance.save()
                # Edit untuk cashPayment
                if(cashPayment_balance is None):
                    balance = cashPaymentBalanceForms().save(commit=False)
                    if(balance_previous is not None):
                        balance_previous.balance_cashPayment_close = calculate_cashPayment_balance_open()
                        balance_previous.exchange_rate_close = balance_previous.exchange_rate_open
                        balance.balance_cashPayment_open = calculate_cashPayment_balance_open() 
                        balance.exchange_rate_open = balance_previous.exchange_rate_open
                        balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                        balance_previous.save()
                        balance.save()
                    else:
                        balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                        balance.save()
                else:
                    cashPayment_balance.save()
                            # Simpan data attachment
                files = request.FILES.getlist('attachment')
                for f in files:
                     attachment = cashierAttachment(attachment=f)
                     attachment.cashPayment = cashPayment_credit
                     attachment.save()
                cashPayment_credit.save()
                cashier.save()
                messages.success(request, 'Transfer Succcesfully')
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
            messages.success(request, 'Reject Succcesfully')
            return redirect('accounting_app:cashPayment_index')
        return HttpResponse(approval_cashier_form)   
# CASH PAYMENT END

# ADVANCE START
@login_required
def advance_add(request):
    if request.method == "POST":
         cashPayment_form               = cashPaymentForms (data=request.POST)
         approval_manager_form          = advanceApprovalManagerForms(data=request.POST)
         cashPayment_attachment_form    = cashPaymentAdvAttachmentForms(data=request.POST)
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
            cashPayment.is_adv = True
            cashPayment.save()
            # Simpan data attachment
            files = request.FILES.getlist('attachment')
            for f in files:
                 attachment = advAttachment(attachment=f)
                 attachment.cashPayment = cashPayment
                 attachment.save()
            # membuat data Approval Manager
            manager = approval_manager_form.save(commit=False)
            manager.advance = cashPayment
            manager.save()
            messages.success(request, 'Success Add Advance', 'success')
            return redirect('accounting_app:advance_index')
         else:
              print(cashPayment_form.errors and approval_manager_form.errors and cashPayment_attachment_form)
    else:
         cashPayment_form = cashPaymentForms()
         cashPayment_attachment_form = cashPaymentAdvAttachmentForms()
         approval_manager_form = advanceApprovalManagerForms()

    context = {
    'cashPayment_form'              : cashPaymentForms,
    'cashPayment_attachment_form'   : cashPaymentAdvAttachmentForms,
    'manager_form'                  : advanceApprovalManagerForms,
    }
    return render(request, 'accounting_app/advance_add.html', context)

@login_required
def advance_index(request):
    cashPayments        = cashPayment.objects.order_by('-created_at')
    managers            = advanceApprovalManager.objects.order_by('-id')
    managersAccountings = advanceApprovalAccountingManager.objects.order_by('-id')
    presidents          = advanceApprovalPresident.objects.order_by('-id')
    cashiers            = advanceApprovalCashier.objects.order_by('-id')
    attachments         = advAttachment.objects.order_by('-id')
    downloadcsv         = cashPaymentBalance.objects.order_by('cashPayment_balance_no')
    downloadcsv         = list(downloadcsv)
    del downloadcsv[0]
    # return HttpResponse(attachments)
        
    context = {
         'cashpayments'             : cashPayments,
         'managers'                 : managers,
         'managersAccountings'      : managersAccountings,
         'presidents'               : presidents,
         'cashiers'                 : cashiers,
         'attachments'              : attachments,
         'csv_list'                 : downloadcsv,
         'form_cashier_attachment'  : cashPaymentCashierAttachmentForms,
         'form_settle_attachment'   : cashPaymentSettleAttachmentForms,
         'form_adv_attachment'      : cashPaymentAdvAttachmentForms,
         'form_manager'             : advanceApprovalManagerForms,
         'form_manager_accounting'  : advanceApprovalAccountingManagerForms,
         'form_president'           : advanceApprovalPresidentForms,
         'form_cashier'             : advanceApprovalCashierForms,
         'form_cashier_transfer'    : cashPaymentCashierForms,
         'form_debit'               : cashPaymentDebitForms,
         'form_credit'              : cashPaymentCreditForms,
         'form_settle'              : cashPaymentSettleForms,
         'form_adv'                 : cashPaymentAdvForms,
    }
    return render(request, 'accounting_app/advance_index.html', context)

@login_required
def advance_monitoring(request):
    cashPayments = cashPayment.objects.order_by('created_at')
    context = {
         'cashPayments'             : cashPayments,
    }
    return render(request, 'accounting_app/advance_monitoring.html', context)

@login_required
def advance_detail(request, cashPayment_id):
    advance_detail = cashPayment.objects.get(pk=cashPayment_id)
    attachment = advAttachment.objects.filter(cashPayment = advance_detail).values('attachment',)
    context = {
         'cashPayment'  : advance_detail,
         'attachment'   : attachment,
    }
    return render(request, 'accounting_app/advance_detail.html', context)

@login_required
def advance_manager_check(request, cashPayment_id):
    try:
        # Mengambil data manager yang akan di check berdasarkan cashPayment id
        manager = advanceApprovalManager.objects.get(pk=cashPayment_id)
        # Approve Check
        manager.is_checked_manager = True
        manager.save()
        messages.success(request, 'Checked Succcesfully')
        return redirect('accounting_app:advance_index')
    except advanceApprovalManager.DoesNotExist:
         raise Http404("Advance Error!")
    
@login_required
def advance_manager_approve(request, cashPayment_id):
    try:
        # mengambil data task yang akan di approve berdasarkan cashPayment id
        manager = advanceApprovalManager.objects.get(pk=cashPayment_id)
        # mengapprove
        manager.is_approve_manager = True
        manager.manager = request.user
        manager.save()
        # membuat approval manager accounting
        approval_manager_accounting_form = advanceApprovalAccountingManagerForms(data=request.POST)
        manager_accounting = approval_manager_accounting_form.save(commit=False)
        manager_accounting.advance_approval_manager = manager
        manager_accounting.save()
        # set Message sukses dan redirect ke halaman daftar CashPayment
        messages.success(request, 'Approved Successfully')
        return redirect('accounting_app:advance_index')
    except advanceApprovalManager.DoesNotExist:
        raise Http404("Advance Error!")

@login_required
def advance_manager_reject(request,cashPayment_id):
    # try:
        # mengambil data task yang akan reject berdasarkan task id
        manager = advanceApprovalManager.objects.get(pk=cashPayment_id)
        post = request.POST.copy() 
        post.update({'is_rejected_manager': True})
        request.POST = post
        approval_manager_form = advanceApprovalManagerForms(request.POST, instance=manager)
        if approval_manager_form.is_valid():
            reject = approval_manager_form.save(commit=False)
            reject.manager = request.user
            reject.save()
            messages.success(request, 'Reject Succcesfully')
            return redirect('accounting_app:advance_index')
        return HttpResponse(approval_manager_form)

@login_required
def advance_accounting_manager_check(request, cashPayment_id):
    try:
        # Mengambil data manager accounting yang akan di check berdasarkan cashPayment id
        manager_accounting = advanceApprovalAccountingManager.objects.get(pk=cashPayment_id)
        # Approve Check
        manager_accounting.is_checked_manager_accounting = True
        manager_accounting.save()
        messages.success(request, 'Checked Succcesfully')
        return redirect('accounting_app:advance_index')
    except advanceApprovalAccountingManager.DoesNotExist:
         raise Http404("Advance Error!")

@login_required
def advance_accounting_manager_approve(request, cashPayment_id):
    try:
        manager_accounting = advanceApprovalAccountingManager.objects.get(pk=cashPayment_id)
        # mengapprove
        manager_accounting.is_approve_manager_accounting = True
        manager_accounting.manager_accounting = request.user
        manager_accounting.save()
        #  membuat approval president
        approval_president_form = advanceApprovalPresidentForms(data=request.POST)
        president = approval_president_form.save(commit=False)
        president.advance_approval_accounting_manager = manager_accounting
        president.save()
        messages.success(request, 'Approve Succcesfully')
        return redirect('accounting_app:advance_index')
    except advanceApprovalAccountingManager.DoesNotExist:
        raise Http404("Advance Error!")

@login_required
def advance_accounting_manager_reject(request,cashPayment_id):
    # try:
        # mengambil data task yang akan reject berdasarkan task id
        accounting_manager = advanceApprovalAccountingManager.objects.get(pk=cashPayment_id)
        post = request.POST.copy() 
        post.update({'is_rejected_manager_accounting': True})
        request.POST = post
        approval_accounting_manager_form = advanceApprovalAccountingManagerForms(request.POST, instance=accounting_manager)
        if approval_accounting_manager_form.is_valid():
            reject = approval_accounting_manager_form.save(commit=False)
            reject.manager_accounting = request.user
            reject.save()
            messages.success(request, 'Reject Succcesfully')
            return redirect('accounting_app:advance_index')
        return HttpResponse(approval_accounting_manager_form)   

@login_required
def advance_president_check(request, cashPayment_id):
    try:
        # Mengambil data manager accounting yang akan di check berdasarkan cashPayment id
        president = advanceApprovalPresident.objects.get(pk=cashPayment_id)
        # Approve Check
        president.is_checked_president = True
        president.save()
        messages.success(request, 'Checked Succcesfully')
        return redirect('accounting_app:advance_index')
    except advanceApprovalPresident.DoesNotExist:
         raise Http404("Advance Error!")

@login_required
def advance_president_approval(request, cashPayment_id):
    try:
        president = advanceApprovalPresident.objects.get(pk=cashPayment_id)
        # mengapprove
        president.is_approve_president = True
        president.president = request.user
        president.save()
        # membuat approval cashier
        approval_cashier_form = advanceApprovalCashierForms(data=request.POST)
        ticket_maks = cashPayment.objects.filter(ticket_no__contains=datetime.datetime.now().strftime('%Y%m')).count() + 1
        ticket_no = "CP" + datetime.datetime.now().strftime('%Y%m') + str("%003d" % ( ticket_maks, ))
        cashier = approval_cashier_form.save(commit=False)
        cashier.advance_approval_president = president
        cashier.save()
        # Create Ticket number dan credit menjadi True buat cashPayment
        cashPayment_id = president.advance_approval_accounting_manager.advance_approval_manager.advance.id
        cashpayment = cashPayment.objects.get(pk=cashPayment_id)
        cashpayment.is_credit = True
        cashpayment.ticket_no = ticket_no
        cashpayment.save()
       
        messages.success(request, 'Approval Succcesfully')
        return redirect('accounting_app:advance_index')
    except cashPaymentApprovalPresident.DoesNotExist:
        raise Http404("Advance Error!")
    
@login_required
def advance_president_reject(request,cashPayment_id):
    # try:
        # mengambil data task yang akan reject berdasarkan task id
        president = advanceApprovalPresident.objects.get(pk=cashPayment_id)
        post = request.POST.copy() 
        post.update({'is_rejected_president': True})
        request.POST = post
        approval_president_form = advanceApprovalPresidentForms(request.POST, instance=president)
        if approval_president_form.is_valid():
            reject = approval_president_form.save(commit=False)
            reject.president = request.user
            reject.save()
            messages.success(request, 'Reject Succcesfully')
            return redirect('accounting_app:advance_index')
        return HttpResponse(approval_president_form) 

@login_required
def advance_cashier_check(request, cashPayment_id):
    try:
        # Mengambil data manager accounting yang akan di check berdasarkan cashPayment id
        cashier = advanceApprovalCashier.objects.get(pk=cashPayment_id)
        # Approve Check
        cashier.is_checked_cashier = True
        cashier.save()
        messages.success(request, 'Checked Succcesfully')
        return redirect('accounting_app:advance_index')
    except advanceApprovalCashier.DoesNotExist:
         raise Http404("Advance Error!")

@login_required
def advance_cashier_approval(request, cashPayment_id):
    try:
     if request.method == "POST":
        cashPayment_credit_form = cashPaymentCashierForms(data=request.POST)
        cashier = advanceApprovalCashier.objects.get(pk=cashPayment_id)
        # cashPayment_balance = masterAccounting.objects.get(pk=1)
        cashPayment_balance = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=datetime.datetime.now().strftime('%Y%m')).first()
        balance_month = datetime.datetime.now().strftime('%Y%m')
        balance_month_previous = datetime.datetime.strptime(balance_month, '%Y%m') - relativedelta(months=1)
        balance_previous = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=datetime.datetime.strftime(balance_month_previous, '%Y%m')).first()
        if request.POST['password'] and request.POST['type'] == 'Transfer Cash':
            identity = cashier.advance_approval_president.advance_approval_accounting_manager.advance_approval_manager.advance.assignee
            user = User.objects.get(username=identity)
            valid_password = check_password(request.POST['password'], user.password)
            if valid_password: #apabila password sudah benar
                if cashPayment_credit_form.is_valid():
                    # Mengapprove
                    cashier.is_approve_cashier = True
                    cashier.cashier = request.user
                    # Menambahkan remark pada cashPayment
                    cashPayment_form = cashPayment_credit_form.save(commit=False)
                    cashPayment_id = cashier.advance_approval_president.advance_approval_accounting_manager.advance_approval_manager.advance.id
                    cashPayment_credit = cashPayment.objects.get(pk=cashPayment_id)
                    cashPayment_credit.adv = cashPayment_form.remark
                    cashPayment_credit.type   = cashPayment_form.type
                    # Mengurangi Balance pada Master Balance
                    # cashPayment_balance.balance_cashPayment = cashPayment_balance.balance_cashPayment - cashPayment_credit.rp_total
                    # cashPayment_balance.save()
                    # Edit untuk cashPayment
                    if(cashPayment_balance is None):
                        balance = cashPaymentBalanceForms().save(commit=False)
                        if(balance_previous is not None):
                            balance_previous.balance_cashPayment_close = calculate_cashPayment_balance_open()
                            balance_previous.exchange_rate_close = balance_previous.exchange_rate_open
                            balance.balance_cashPayment_open = calculate_cashPayment_balance_open() 
                            balance.exchange_rate_open = balance_previous.exchange_rate_open
                            balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                            balance_previous.save()
                            balance.save()
                        else:
                            balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                            balance.save()
                    else:
                        cashPayment_balance.save()
                                # Simpan data attachment
                    files = request.FILES.getlist('attachment')
                    for f in files:
                         attachment = cashierAttachment(attachment=f)
                         attachment.cashPayment = cashPayment_credit
                         attachment.save()
                    cashPayment_credit.save()
                    cashier.save()
                    messages.success(request, 'Transfer Succcesfully')
            else:
                messages.warning(request, 'Password yang dimasukan salah')
                return redirect('accounting_app:advance_index')
            # mari kita buat Validasi password dari Assignee, apakah sudah sesuai apa belum
        else:
            if cashPayment_credit_form.is_valid():
                # Mengapprove
                cashier.is_approve_cashier = True
                cashier.cashier = request.user
                # Menambahkan remark pada cashPayment
                cashPayment_form = cashPayment_credit_form.save(commit=False)
                cashPayment_id = cashier.advance_approval_president.advance_approval_accounting_manager.advance_approval_manager.advance.id
                cashPayment_credit = cashPayment.objects.get(pk=cashPayment_id)
                cashPayment_credit.adv = cashPayment_form.remark
                cashPayment_credit.type   = cashPayment_form.type
                # Mengurangi Balance pada Master Balance
                # cashPayment_balance.balance_cashPayment = cashPayment_balance.balance_cashPayment - cashPayment_credit.rp_total
                # cashPayment_balance.save()
                # Edit untuk cashPayment
                if(cashPayment_balance is None):
                    balance = cashPaymentBalanceForms().save(commit=False)
                    if(balance_previous is not None):
                        balance_previous.balance_cashPayment_close = calculate_cashPayment_balance_open()
                        balance_previous.exchange_rate_close = balance_previous.exchange_rate_open
                        balance.balance_cashPayment_open = calculate_cashPayment_balance_open() 
                        balance.exchange_rate_open = balance_previous.exchange_rate_open
                        balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                        balance_previous.save()
                        balance.save()
                    else:
                        balance.cashPayment_balance_no = datetime.datetime.now().strftime('%Y%m')
                        balance.save()
                else:
                    cashPayment_balance.save()
                            # Simpan data attachment
                files = request.FILES.getlist('attachment')
                for f in files:
                     attachment = cashierAttachment(attachment=f)
                     attachment.cashPayment = cashPayment_credit
                     attachment.save()
                cashPayment_credit.save()
                cashier.save()
                messages.success(request, 'Transfer Succcesfully')
        return redirect('accounting_app:advance_index')
    except advanceApprovalCashier.DoesNotExist:
        raise Http404("Advance Error!")

@login_required
def advance_cashier_reject(request,cashPayment_id):
    # try:
        # mengambil data task yang akan reject berdasarkan task id
        cashier = advanceApprovalCashier.objects.get(pk=cashPayment_id)
        post = request.POST.copy() 
        post.update({'is_rejected_cashier': True})
        request.POST = post
        approval_cashier_form = advanceApprovalCashierForms(request.POST, instance=cashier)
        if approval_cashier_form.is_valid():
            reject = approval_cashier_form.save(commit=False)
            reject.cashier = request.user
            reject.save()
            messages.success(request, 'Reject Succcesfully')
            return redirect('accounting_app:advance_index')
        return HttpResponse(approval_cashier_form) 

# ADVANCE END
@login_required
def export_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response)
    writer.writerow(['Username', 'First name', 'Last name', 'Email address'])

    users = User.objects.all().values_list('username', 'first_name', 'last_name', 'email')
    for user in users:
        writer.writerow(user)
    # cashPayment_balance = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=datetime.datetime.now().strftime('%Y%m')).first()
    return response

@login_required
def export_cashPayment_csv(request):
#     post = request.POST.copy()
#     # return HttpResponse(post['date_filter'])
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="'+post['date_filter']+'.csv"'
#     writer = csv.writer(response)
#     writer.writerow([datetime.datetime.strptime(post['date_filter'], '%Y%m').strftime('%B - %Y'), '', '','', '' , '', '', '', '', '', ''])
#     writer.writerow(['Month', 'Date', 'Rpr', 'Rph', 'US$', 'ticket_no', 'remark', 'Debit', 'Credit', 'Balance Rp', 'Balance USD'])
#     # balance_month = datetime.datetime.now().strftime('%Y%m')
#     balance_month = post['date_filter']
#     balance_month_previous = datetime.datetime.strptime(balance_month, '%Y%m') - relativedelta(months=1)
#     cashPayment_balance_previous = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=datetime.datetime.strftime(balance_month_previous, '%Y%m')).first()
#     cashPayment_balance_filter = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=balance_month).first()
#     cashpayments = cashPayment.objects.filter(ticket_no__contains=balance_month).all().values_list('updated_at', 'rp_total' , 'ticket_no', 'remark', 'is_debit', 'is_credit', 'is_settle', 'settle', 'is_adv', 'adv')
#     # cashpayments = cashPayment.objects.all().values_list(datetime.datetime.strptime('updated_at', '%b'), datetime.datetime.strptime('updated_at', '%D'), 'rp_total', cashPayment_balance_previous.exchange_rate_close, 'rp_total' / cashPayment_balance_previous.exchange_rate_close, 'ticket_no', 'remark',  'remark',  'remark',  'remark')
#     # cashpayments = cashPayment.objects.raw(''' SELECT DATENAME(MONTH, accounting_app_cashpayment.updated_at) AS Month, DAY(accounting_app_cashpayment.updated_at) AS Date,
# 	# 	                                    accounting_app_cashpayment.rp_total AS Rpr, accounting_app_cashpaymentbalance.exchange_rate_close AS Rph, 
# 	# 	                                    accounting_app_cashpayment.rp_total / accounting_app_cashpaymentbalance.exchange_rate_close AS 'US$', accounting_app_cashpayment.ticket_no, 
# 	# 	                                    accounting_app_cashpayment.remark, IIF(accounting_app_cashpayment.is_debit = 1, rp_total, 0) AS Debit, IIF(accounting_app_cashpayment.is_credit = 1, rp_total, 0) AS Credit
#     #                                         FROM accounting_app_cashpayment, accounting_app_cashpaymentbalance
#     #                                          '''
#     balance_temp = cashPayment_balance_previous.balance_cashPayment_close
#     balance_temp_us = balance_temp / cashPayment_balance_previous.exchange_rate_close
#     writer.writerow(['', '', '','', '' , '', 'Balance brought forward from '+ datetime.datetime.strftime(balance_month_previous, '%B - %Y'), '', '', balance_temp, balance_temp_us])
#     writer.writerow(['', '', '','', '' , '', '', '', '', balance_temp, balance_temp_us])
#     writer.writerow(['', '', '','', '' , '', '', '', '', balance_temp, balance_temp_us])
#     writer.writerow(['', '', '','', cashPayment_balance_filter.exchange_rate_open - cashPayment_balance_previous.exchange_rate_close, '', 'Exchange gain/loss frm '+ str(cashPayment_balance_previous.exchange_rate_close) + ' ,- to ' + str(cashPayment_balance_filter.exchange_rate_open), '', '', balance_temp, balance_temp_us])
#     for cashpayment in cashpayments:
#         if(cashpayment[4]):
#             rp_debit = cashpayment[1]
#             balance_temp = balance_temp + cashpayment[1]
#         else:
#             rp_debit = 0
#         if(cashpayment[5]):
#             rp_credit = cashpayment[1]
#             balance_temp = balance_temp - cashpayment[1]
#         else:
#             rp_credit = 0
#         if(cashpayment[6]):
#             remark = cashpayment[7]
#         else:
#             if(cashpayment[8]):
#                 remark = cashpayment[9]
#             else:
#                 remark = cashpayment[3]
#         if(cashpayment[1]):
#             balance_temp_us_kiri = cashpayment[1] / cashPayment_balance_filter.exchange_rate_open
#         else:
#             balance_temp_us_kiri = 0
#         if(cashpayment[1]):
#             balance_temp_idr_kiri = cashpayment[1]
#         else:
#             balance_temp_idr_kiri = 0
        

#         balance_temp_us = balance_temp / cashPayment_balance_filter.exchange_rate_open
#         writer.writerow([datetime.datetime.strftime(cashpayment[0], '%b'), datetime.datetime.strftime(cashpayment[0], '%d'), balance_temp_idr_kiri,cashPayment_balance_filter.exchange_rate_open, balance_temp_us_kiri , cashpayment[2], remark, rp_debit, rp_credit, balance_temp, balance_temp_us])
    
#     return response
        return HttpResponse("di Uncomment dulu")

def calculate_cashPayment_balance_open():
    balance_month = datetime.datetime.now().strftime('%Y%m')
    balance_month_previous = datetime.datetime.strptime(balance_month, '%Y%m') - relativedelta(months=1)
    balance_previous = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=datetime.datetime.strftime(balance_month_previous, '%Y%m')).first()
    balance_temp = balance_previous.balance_cashPayment_close
    cashpayments = cashPayment.objects.filter(ticket_no__contains=balance_month_previous).all().values_list('created_at', 'rp_total' , 'ticket_no', 'remark', 'is_debit', 'is_credit', 'is_settle', 'settle', 'is_adv', 'adv',)
    for cashpayment in cashpayments:
        if(cashpayment[4]):
            balance_temp = balance_temp + cashpayment[1]
        if(cashpayment[5]):
            balance_temp = balance_temp - cashpayment[1]
    return balance_temp


def export_cashPayment_xls(request):
    post = request.POST.copy()
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="'+post['date_filter']+'.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(datetime.datetime.strptime(post['date_filter'], '%Y%m').strftime('%B - %Y'), cell_overwrite_ok=True) # this will make a sheet named Users Data

    # Sheet header, first row
    # ws.write(row_num, col_num, columns[col_num], font_style) # at 0 row 0 column 
    row_num = 0
    font_style = xlwt.XFStyle()
    columns = [datetime.datetime.strptime(post['date_filter'], '%Y%m').strftime('%B - %Y'), '', '','', '' , '', '', '', '', '', '']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style) # at 0 row 0 column 

    row_num = 1
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Month', 'Date', 'Rpr', 'Rph', 'US$', 'No. Voucher', 'Remarks', 'Debit', 'Credit', 'Balance Rp', 'Balance USD', ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style) # at 0 row 0 column 

    balance_month = post['date_filter']
    balance_month_previous = datetime.datetime.strptime(balance_month, '%Y%m') - relativedelta(months=1)
    cashPayment_balance_previous = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=datetime.datetime.strftime(balance_month_previous, '%Y%m')).first()
    cashPayment_balance_filter = cashPaymentBalance.objects.filter(cashPayment_balance_no__contains=balance_month).first()
    cashpayments = cashPayment.objects.filter(ticket_no__contains=balance_month).all().values_list('created_at', 'rp_total' , 'ticket_no', 'remark', 'is_debit', 'is_credit', 'is_settle', 'settle', 'is_adv', 'adv',)
    balance_temp = cashPayment_balance_previous.balance_cashPayment_close
    balance_temp_us = balance_temp / cashPayment_balance_previous.exchange_rate_close

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    #Format Currency
    currency_us = xlwt.XFStyle()
    currency_us.num_format_str = '$#,##0.00'
    #Format Currency
    currency_idr = xlwt.XFStyle()
    currency_idr.num_format_str = f'#,##0.00'
    #Format Currency Kredit
    currency_idr_kredit = xlwt.XFStyle()
    currency_idr_kredit.num_format_str = f'(#,##0.00)'
    #Format currency IDR Bold
    currency_idr_bold = xlwt.XFStyle()
    currency_idr_bold.num_format_str = '#,##0.00'
    currency_idr_bold.font.bold = True
    #Format currency US Bold
    currency_us_bold = xlwt.XFStyle()
    currency_us_bold.num_format_str = '$#,##0.00'
    currency_us_bold.font.bold = True
    #Font Bold
    font_bold = xlwt.XFStyle()
    font_bold.font.bold = True

    row_num = 2
    font_style = xlwt.XFStyle()
    columns = ['', '', '','', '' , '', 'Balance brought forward from '+ datetime.datetime.strftime(balance_month_previous, '%B - %Y'), '', '', balance_temp, balance_temp_us]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)  
        if col_num == 9:
            ws.write(row_num, col_num, columns[col_num], currency_idr)
        if col_num == 10:
            ws.write(row_num, col_num, columns[col_num], currency_us)
    row_num = 3
    font_style = xlwt.XFStyle()
    columns = ['', '', '','', '' , '', '', '', '', balance_temp, balance_temp_us]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)  
        if col_num == 9:
            ws.write(row_num, col_num, columns[col_num], currency_idr)
        if col_num == 10:
            ws.write(row_num, col_num, columns[col_num], currency_us)

    row_num = 4
    font_style = xlwt.XFStyle()
    columns = ['', '', '','', '' , '', '', '', '', balance_temp, balance_temp_us]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)  
        if col_num == 9:
            ws.write(row_num, col_num, columns[col_num], currency_idr)
        if col_num == 10:
            ws.write(row_num, col_num, columns[col_num], currency_us)
            
    row_num = 5
    font_style = xlwt.XFStyle()
    columns = ['', '', '','', (balance_temp / cashPayment_balance_previous.exchange_rate_close) - (balance_temp / cashPayment_balance_filter.exchange_rate_open), '', 'Exchange gain/loss frm '+ "{:,}".format(cashPayment_balance_previous.exchange_rate_close) + ' ,- to ' + "{:,}".format(cashPayment_balance_filter.exchange_rate_open), '', '', balance_temp, balance_temp_us]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)  
        if col_num == 4:
            ws.write(row_num, col_num, columns[col_num], font_bold)
        if col_num == 7:
            ws.write(row_num, col_num, columns[col_num], currency_idr)
        if col_num == 8:
            ws.write(row_num, col_num, columns[col_num], currency_idr)
        if col_num == 9:
            ws.write(row_num, col_num, columns[col_num], currency_idr)
        if col_num == 10:
            ws.write(row_num, col_num, columns[col_num], currency_us)

    # BODY DARI Excel laporan yang akan dibuat
    balance_total_debit_temp = 0
    balance_total_credit_temp = 0
    for cashpayment in cashpayments:    
        if(cashpayment[4]):
            rp_debit = cashpayment[1]
            balance_temp = balance_temp + cashpayment[1]
            balance_total_debit_temp += cashpayment[1]
        else:
            rp_debit = 0
        if(cashpayment[5]):
            rp_credit = cashpayment[1]
            balance_temp = balance_temp - cashpayment[1]
            balance_total_credit_temp += cashpayment[1]
        else:
            rp_credit = 0
        if(cashpayment[6]):
            remark = cashpayment[7]
        else:
            if(cashpayment[8]):
                remark = cashpayment[9]
            else:
                remark = cashpayment[3]
        if(cashpayment[1]):
            balance_temp_us_kiri = cashpayment[1] / cashPayment_balance_filter.exchange_rate_open
        else:
            balance_temp_us_kiri = 0
        if(cashpayment[1]):
            balance_temp_idr_kiri = cashpayment[1]
        else:
            balance_temp_idr_kiri = 0
        row_num += 1
        balance_temp_us = balance_temp / cashPayment_balance_filter.exchange_rate_open
        row = [datetime.datetime.strftime(cashpayment[0], '%b'),
                datetime.datetime.strftime(cashpayment[0], '%d'),
                balance_temp_idr_kiri,
                cashPayment_balance_filter.exchange_rate_open,
                balance_temp_us_kiri,
                cashpayment[2],
                remark,
                rp_debit,
                rp_credit,
                balance_temp,
                balance_temp_us]
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
            if col_num == 2:
                if(row[8]):
                    ws.write(row_num, col_num, row[col_num], currency_idr_kredit)
                else:
                    ws.write(row_num, col_num, row[col_num], currency_idr)
            if col_num == 3:
                ws.write(row_num, col_num, row[col_num], currency_idr)
            if col_num == 4:
                ws.write(row_num, col_num, row[col_num], currency_us)
            if col_num == 6:
                if cashpayment[6] or cashpayment[8]:
                    ws.write(row_num, col_num, row[col_num], font_bold)
                else:
                    ws.write(row_num, col_num, row[col_num], font_style)
            if col_num == 7:
                ws.write(row_num, col_num, row[col_num], currency_idr)
            if col_num == 8:
                ws.write(row_num, col_num, row[col_num], currency_idr)
            if col_num == 9:
                ws.write(row_num, col_num, row[col_num], currency_idr)
            if col_num == 10:
                ws.write(row_num, col_num, row[col_num], currency_us)
    row_num += 1 
    row = ['',
        '',
        '',
        '',
        '',
        '',
        '',
        balance_total_debit_temp,
        balance_total_credit_temp,
        balance_temp,
        balance_temp_us]
    for col_num in range(len(row)):
        ws.write(row_num, col_num, row[col_num], font_style)
        if col_num == 7:
            ws.write(row_num, col_num, row[col_num], currency_idr_bold)
        if col_num == 8:
            ws.write(row_num, col_num, row[col_num], currency_idr_bold)
        if col_num == 9:
            ws.write(row_num, col_num, row[col_num], currency_idr_bold)
        if col_num == 10:
            ws.write(row_num, col_num, row[col_num], currency_us_bold)           
    wb.save(response)

    return response
@login_required
def CreateCashPayment(request):
    with open('templates/csv/list_cashPayment.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for ticket_no, remark, settle, rp_total, is_credit, is_debit, is_settle, *__ in csvf:
            cashpayment = cashPayment(ticket_no=ticket_no, remark=remark, settle = settle, rp_total = rp_total
            ,  is_credit = is_credit, is_debit = is_debit, is_settle = is_settle
             )
            data.append(cashpayment)
        cashPayment.objects.bulk_create(data)
    return JsonResponse('Cash Payment csv is now working', safe=False)
# CASHPAYMENT END
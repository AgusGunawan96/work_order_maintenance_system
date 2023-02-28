from django.shortcuts import render

# Create your views here.
def index(request):
    
    return render(request, 'accounting_app/index.html')

def cashPayment_index(request):

    return render(request, 'accounting_app/cashPayment_index.html')

def cashPayment_add(request):

    return render(request, 'accounting_app/cashPayment_add.html')
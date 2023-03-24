from django.shortcuts import render
from django.http import Http404, HttpResponse,JsonResponse
from ppc_app.models import customerRevice, customerReviceAttachment
import datetime
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    
    return render(request, 'ppc_app/index.html')

@login_required
def customerRevice_index(request):
    customerRevices = customerRevice.objects.order_by('-created_at')
    return render(request, 'starter_kit/comingsoon-bg-video.html')
    # return HttpResponse('Customer Revice Index')

@login_required
def customerRevice_add(request):
    return HttpResponse('Customer Revice Add')

@login_required
def millingSchedule_index(request):
    customerRevices = customerRevice.objects.order_by('-created_at')
    return render(request, 'starter_kit/comingsoon-bg-video.html')
    # return HttpResponse('Milling Schedule Index')
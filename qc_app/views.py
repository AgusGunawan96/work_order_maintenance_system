from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from qc_app.models import rirHeader, rirDetail, specialJudgement, rirApprovalSupervisor, rirApprovalManager

# Create your views here.
def index(request):
    
    return render(request, 'qc_app/index.html')
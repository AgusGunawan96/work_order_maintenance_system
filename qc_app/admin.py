from django.contrib import admin
from qc_app.models import rirHeader, specialJudgement, rirApprovalSupervisor, rirApprovalManager, rirApprovalList
import datetime 


# Register your models here.
admin.site.register(rirHeader)
admin.site.register(specialJudgement)
admin.site.register(rirApprovalSupervisor)
admin.site.register(rirApprovalManager)
admin.site.register(rirApprovalList)

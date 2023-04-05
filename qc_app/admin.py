from django.contrib import admin
from qc_app.models import rirHeader, rirDetail, specialJudgement, rirApprovalSupervisor, rirApprovalManager
import datetime 


# Register your models here.
admin.site.register(rirHeader)
admin.site.register(rirDetail)
admin.site.register(specialJudgement)
admin.site.register(rirApprovalSupervisor)
admin.site.register(rirApprovalManager)

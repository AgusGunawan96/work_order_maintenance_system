from django.contrib import admin
from qc_app.models import rirHeader, specialJudgement, rirApprovalSupervisor, rirApprovalManager, rirApprovalList, rirMaterial, categoryTypeRIR
import datetime 

class categoryTypeRIRAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'coa_content', 'appearance', 'restricted_substance', 'environmental_issue', 'sample_test')
    search_fields = ['name',]
    list_filter = ['coa_content', 'appearance', 'restricted_substance' , 'environmental_issue' , 'sample_test']
# Register your models here.
admin.site.register(rirHeader)
admin.site.register(specialJudgement)
admin.site.register(rirApprovalSupervisor)
admin.site.register(rirApprovalManager)
admin.site.register(rirApprovalList)
admin.site.register(rirMaterial)
admin.site.register(categoryTypeRIR, categoryTypeRIRAdmin)
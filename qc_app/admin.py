from django.contrib import admin
from qc_app.models import rirHeader, specialJudgement, rirApprovalSupervisor, rirApprovalManager, rirApprovalList, rirMaterial, categoryTypeRIR
import datetime 

class categoryTypeRIRAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'coa_content', 'appearance', 'restricted_substance', 'environmental_issue', 'sample_test')
    search_fields = ['name',]
    list_filter = ['coa_content', 'appearance', 'restricted_substance' , 'environmental_issue' , 'sample_test']

class rirApprovalListAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'no_karyawan','is_judgement','is_checked_by', 'is_supervisor', 'is_manager')
    def first_name(self, obj):
        return obj.user.first_name
    def last_name(self, obj):
        return obj.user.last_name
    def no_karyawan(self, obj):
        return obj.user.username
    
# Register your models here.
admin.site.register(rirHeader)
admin.site.register(specialJudgement)
admin.site.register(rirApprovalSupervisor)
admin.site.register(rirApprovalManager)
admin.site.register(rirApprovalList, rirApprovalListAdmin)
admin.site.register(rirMaterial)
admin.site.register(categoryTypeRIR, categoryTypeRIRAdmin)
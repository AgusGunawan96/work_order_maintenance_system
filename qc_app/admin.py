from django.contrib import admin
from qc_app.models import rirHeader, specialJudgement, rirApprovalSupervisor, rirApprovalManager, rirApprovalList, rirMaterial, categoryTypeRIR, rirVendor, rirDetailCoaContentJudgement, rirDetailCoaContentCheckedby, rirDetailAppearenceJudgement, rirDetailAppearenceCheckedby, rirDetailSampleTestJudgement, rirDetailEnvironmentalIssueJudgement, rirDetailRestrictedSubstanceJudgement, rirDetailSampleTestCheckedby, rirDetailEnvironmentalIssueCheckedby, rirDetailRestrictedSubstanceCheckedby
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
    
class rirHeaderAdmin(admin.ModelAdmin):
    list_display = ('rir_no', 'incoming_type','po_number','category_name', 'material_name', 'lot_no','incoming_at', 'incoming_at_external', 'is_special_judgement', 'is_return', 'is_sa')
    search_fields = ['material','po_number',]
    list_filter = ['incoming_type', 'category', 'incoming_at', 'incoming_at_external', 'is_special_judgement','is_return', 'is_sa']
    def category_name(self, obj):
        return obj.category.name
    def material_name(self, obj):
        return obj.material.name

class rirDetailCoaContentJudgementAdmin(admin.ModelAdmin):
    list_display = ('rir_no','category_name', 'material_name', 'created_at')
    search_field = ['rir_no',]
    def rir_no(self, obj):
        return obj.header.rir_no
    def category_name(self, obj):
        return obj.header.category.name
    def material_name(self, obj):
        return obj.header.material.name
class rirDetailCoaContentCheckedbyAdmin(admin.ModelAdmin):
    list_display = ('rir_no', 'category_name', 'material_name', 'created_at', 'updated_at')
    search_field = ['rir_no',]
    def rir_no(self, obj):
        return obj.coa_content_judgement.header.rir_no
    def category_name(self, obj):
        return obj.coa_content_judgement.header.category.name
    def material_name(self, obj):
        return obj.coa_content_judgement.header.material.name
    
class rirDetailAppearenceJudgementAdmin(admin.ModelAdmin):
    list_display = ('rir_no','category_name', 'material_name', 'created_at', 'updated_at')
    search_field = ['rir_no',]
    def rir_no(self, obj):
        return obj.header.rir_no
    def category_name(self, obj):
        return obj.header.category.name
    def material_name(self, obj):
        return obj.header.material.name
class rirDetailAppearenceCheckedbyAdmin(admin.ModelAdmin):
    list_display = ('rir_no', 'category_name', 'material_name', 'created_at', 'updated_at')
    search_field = ['rir_no',]
    def rir_no(self, obj):
        return obj.appearence.header.rir_no
    def category_name(self, obj):
        return obj.appearence.header.category.name
    def material_name(self, obj):
        return obj.appearence.header.material.name

class rirDetailSampleTestJudgementAdmin(admin.ModelAdmin):
    list_display = ('rir_no','category_name', 'material_name', 'created_at', 'updated_at')
    search_field = ['rir_no',]
    def rir_no(self, obj):
        return obj.header.rir_no
    def category_name(self, obj):
        return obj.header.category.name
    def material_name(self, obj):
        return obj.header.material.name
class rirDetailSampleTestCheckedbyAdmin(admin.ModelAdmin):
    list_display = ('rir_no', 'category_name', 'material_name', 'created_at', 'updated_at')
    search_field = ['rir_no',]
    def rir_no(self, obj):
        return obj.sample_test_judgement.header.rir_no
    def category_name(self, obj):
        return obj.sample_test_judgement.header.category.name
    def material_name(self, obj):
        return obj.sample_test_judgement.header.material.name

class rirDetailEnvironmentalIssueJudgementAdmin(admin.ModelAdmin):
    list_display = ('rir_no','category_name', 'material_name', 'created_at', 'updated_at')
    search_field = ['rir_no',]
    def rir_no(self, obj):
        return obj.header.rir_no
    def category_name(self, obj):
        return obj.header.category.name
    def material_name(self, obj):
        return obj.header.material.name
class rirDetailEnvironmentalIssueCheckedbyAdmin(admin.ModelAdmin):
    list_display = ('rir_no', 'category_name', 'material_name', 'created_at', 'updated_at')
    search_field = ['rir_no',]
    def rir_no(self, obj):
        return obj.environmental_issue_judgement.header.rir_no
    def category_name(self, obj):
        return obj.environmental_issue_judgement.header.category.name
    def material_name(self, obj):
        return obj.environmental_issue_judgement.header.material.name

class rirDetailRestrictedSubstanceJudgementAdmin(admin.ModelAdmin):
    list_display = ('rir_no','category_name', 'material_name', 'created_at', 'updated_at')
    search_field = ['rir_no',]
    def rir_no(self, obj):
        return obj.header.rir_no
    def category_name(self, obj):
        return obj.header.category.name
    def material_name(self, obj):
        return obj.header.material.name
class rirDetailRestrictedSubstanceCheckedbyAdmin(admin.ModelAdmin):
    list_display = ('rir_no', 'category_name', 'material_name', 'created_at', 'updated_at')
    search_field = ['rir_no',]
    def rir_no(self, obj):
        return obj.restricted_substance_judgement.header.rir_no
    def category_name(self, obj):
        return obj.restricted_substance_judgement.header.category.name
    def material_name(self, obj):
        return obj.restricted_substance_judgement.header.material.name
    
# Register your models here.
admin.site.register(rirHeader, rirHeaderAdmin)
admin.site.register(specialJudgement)
admin.site.register(rirApprovalSupervisor)
admin.site.register(rirApprovalManager)
admin.site.register(rirApprovalList, rirApprovalListAdmin)
admin.site.register(rirMaterial)
admin.site.register(rirVendor)
admin.site.register(categoryTypeRIR, categoryTypeRIRAdmin)

admin.site.register(rirDetailCoaContentJudgement, rirDetailCoaContentJudgementAdmin)
admin.site.register(rirDetailCoaContentCheckedby, rirDetailCoaContentCheckedbyAdmin)
admin.site.register(rirDetailAppearenceJudgement, rirDetailAppearenceJudgementAdmin)
admin.site.register(rirDetailAppearenceCheckedby, rirDetailAppearenceCheckedbyAdmin)
admin.site.register(rirDetailSampleTestJudgement, rirDetailSampleTestJudgementAdmin)
admin.site.register(rirDetailSampleTestCheckedby, rirDetailSampleTestCheckedbyAdmin)
admin.site.register(rirDetailEnvironmentalIssueJudgement, rirDetailEnvironmentalIssueJudgementAdmin)
admin.site.register(rirDetailEnvironmentalIssueCheckedby, rirDetailEnvironmentalIssueCheckedbyAdmin)
admin.site.register(rirDetailRestrictedSubstanceJudgement, rirDetailRestrictedSubstanceJudgementAdmin)
admin.site.register(rirDetailRestrictedSubstanceCheckedby, rirDetailRestrictedSubstanceCheckedbyAdmin)



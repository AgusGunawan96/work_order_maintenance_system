from django.contrib import admin
from hrd_app.models import medicalApprovalList, medicalHeader

class medicalApprovalListAdmin(admin.ModelAdmin):
    list_display = ('no_karyawan', 'first_name', 'last_name', 'is_foreman', 'is_supervisor', 'is_manager', 'is_hr')
    def first_name(self, obj):
        return obj.user.first_name
    def last_name(self, obj):
        return obj.user.last_name
    def no_karyawan(self, obj):
        return obj.user.username
    
# Register your models here.
admin.site.register(medicalApprovalList, medicalApprovalListAdmin)
admin.site.register(medicalHeader)

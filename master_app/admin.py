from django.contrib import admin
from master_app.models import Department, Division, Section, UserProfileInfo
# Register your models here.

class UserProfileInfoAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name', 'user__username']
    list_display = ('name','position', 'department', 'division', 'section')
    list_filter = ['department__department_name', 'division__division_name', 'section__section_name',]

    def department(self, obj):
        return obj.department.department_name
    def division(self, obj):
        return obj.division.division_name
    def section(self, obj):
        return obj.section.section_name
    
    def name(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name


admin.site.register(Department)
admin.site.register(Division)
admin.site.register(Section)
admin.site.register(UserProfileInfo, UserProfileInfoAdmin)

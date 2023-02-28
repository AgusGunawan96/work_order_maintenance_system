from django.contrib import admin
from master_app.models import Department, Division, Section, UserProfileInfo
# Register your models here.

class UserProfileInfoAdmin(admin.ModelAdmin):
    search_fields = ['user_id']

admin.site.register(Department)
admin.site.register(Division)
admin.site.register(Section)
admin.site.register(UserProfileInfo, UserProfileInfoAdmin)

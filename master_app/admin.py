from django.contrib import admin
from master_app.models import Department, Division, Section, UserProfileInfo
# Register your models here.
admin.site.register(Department)
admin.site.register(Division)
admin.site.register(Section)
admin.site.register(UserProfileInfo)

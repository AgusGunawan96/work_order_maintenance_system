from django.contrib import admin
from production_app.models import POCVLPermission, POCLowModulusPermission, masterTagLowModulus
# Register your models here.


admin.site.register(POCVLPermission)
admin.site.register(POCLowModulusPermission)
admin.site.register(masterTagLowModulus)
from django.contrib import admin
from it_app.models import Ticket, Hardware, TicketApprovalSupervisor, TicketApprovalManager, TicketApprovalIT, TicketProgressIT, HardwareInfo, HardwareType, IPAddress, ITComputerList, ListLocation, ListLocationDetail, ITApprovalList, ITReportH, ITReportD
# Register your models here.
class TicketAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('id', 'title', 'assignee', 'description', 'updated_at')
    search_fields = ['title','description']

class ITComputerListAdmin(admin.ModelAdmin):
    list_display = ('ip', 'computer_name', 'location', 'is_dhcp', 'antivirus')

# class IPAddressAdmin(admin.ModelAdmin):
#     date_hierarchy = 'created_at'
#     list_display = ('ip', 'is_used', 'name', 'hardware')
#     search_fields = ['name','hardware']
#     list_filter = ['hardware', 'is_used',]
#     def hardware(self, obj):
#         return obj.hardware.hardware_name
    
admin.site.register(Ticket, TicketAdmin)
admin.site.register(HardwareType)
admin.site.register(Hardware)
admin.site.register(HardwareInfo)
admin.site.register(TicketApprovalManager)
admin.site.register(TicketApprovalSupervisor)
admin.site.register(TicketApprovalIT)
admin.site.register(TicketProgressIT)
admin.site.register(ITComputerList, ITComputerListAdmin)
admin.site.register(ListLocation)
admin.site.register(ListLocationDetail)
admin.site.register(ITApprovalList)
admin.site.register(ITReportH) 
admin.site.register(ITReportD) 

# admin.site.register(IPAddress, IPAddressAdmin)
from django.contrib import admin
from it_app.models import Ticket, Hardware, TicketApprovalSupervisor, TicketApprovalManager, TicketApprovalIT, TicketProgressIT, HardwareInfo, HardwareType
# Register your models here.
class TicketAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('id', 'title', 'assignee', 'description', 'updated_at')
    search_fields = ['title','description']


admin.site.register(Ticket, TicketAdmin)
admin.site.register(HardwareType)
admin.site.register(Hardware)
admin.site.register(HardwareInfo)
admin.site.register(TicketApprovalManager)
admin.site.register(TicketApprovalSupervisor)
admin.site.register(TicketApprovalIT)
admin.site.register(TicketProgressIT)

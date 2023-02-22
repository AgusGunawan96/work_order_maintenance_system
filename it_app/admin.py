from django.contrib import admin
from it_app.models import Ticket
# Register your models here.
class TicketAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('id', 'title', 'assignee', 'description', 'updated_at')
    search_fields = ['title','description']

admin.site.register(Ticket, TicketAdmin)
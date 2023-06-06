from django.urls import path
from it_app import views
from django.conf.urls.static import static
from django.conf import settings

app_name ='it_app'

urlpatterns = [
    path('profile/', views.profile, name = 'profile'),
    path('dashboard/', views.dashboard, name = 'dashboard'),

    # TICKET START
    path('ticket/', views.ticket_index, name = 'ticket_index'),
    path('ticket/add/', views.ticket_add, name='ticket_add'),
    path('ticket/ticket_monitoring/', views.ticket_monitoring, name='ticket_monitoring'),
    path('ticket/ticket_detail/<int:ticket_id>', views.ticket_detail, name='ticket_detail'),
    path('ticket/ticket_supervisor_approve/<int:ticket_id>', views.ticket_supervisor_approve, name='ticket_supervisor_approve'),
    path('ticket/ticket_supervisor_reject/<int:ticket_id>', views.ticket_supervisor_reject, name='ticket_supervisor_reject'),
    path('ticket/ticket_manager_approve/<int:ticket_id>', views.ticket_manager_approve, name='ticket_manager_approve'),
    path('ticket/ticket_manager_reject/<int:ticket_id>', views.ticket_manager_reject, name='ticket_manager_reject'),
    path('ticket/ticket_it_approve/<int:ticket_id>', views.ticket_it_approve, name='ticket_it_approve'),
    path('ticket/ticket_it_reject/<int:ticket_id>', views.ticket_it_reject, name='ticket_it_reject'),
    # TICKET END

    # IP ADDRESS START
    # path('ipAddress/', views.ipAddress_index, name = 'ipAddress_index'),
    # path('ipAddress/add/<int:ipAddress_id>', views.ipAddress_add, name='ipAddress_add'),
    # path('ipAddress/unreg/<int:ipAddress_id>', views.ipAddress_unreg, name='ipAddress_unreg'),
    # IP ADDRESS END

    # COMPUTER START
    path('computer/', views.computer_index, name = 'computer_index'),
    path('computer/add/', views.computer_add, name = 'computer_add'),
     
    # COMPUTER END 
    # HARDWARE START
    path('hardware/', views.hardware_index, name = 'hardware_index'),
    path('hardware/edit/', views.hardware_edit, name='hardware_edit'),
    # HARDWARE END
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

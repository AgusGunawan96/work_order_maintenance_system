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
    path('computer/computer_download/', views.computer_download, name = 'computer_download'),
     
    # COMPUTER END 
    # HARDWARE START
    path('hardware/', views.hardware_index, name = 'hardware_index'),
    path('hardware/edit/', views.hardware_edit, name='hardware_edit'),
    # HARDWARE END
    
    # IT REPORT START
    path('report_it/', views.report_it_index, name = 'report_it_index'),
    path('report_it/detail/<int:report_id>', views.report_it_detail, name = 'report_it_detail'),
    path('report_it/create_project', views.report_it_create_project, name = 'report_it_create_project'),
    path('report_it/create_task/<int:report_id>', views.report_it_create_task, name = 'report_it_create_task'),
    path('report_it/edit_task/<int:report_id>', views.report_it_edit_task, name = 'report_it_edit_task'),
    path('report_it/complete_project/<int:report_id>', views.report_it_complete_project, name = 'report_it_complete_project'),
    path('report_it/confirmed_task/<int:report_id>', views.report_it_confirmed_task, name = 'report_it_confirmed_task'),
    path('report_it/verified_project/<int:report_id>', views.report_it_verified_project, name = 'report_it_verified_project'),

    # IT REPORT END
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from qc_app import views
from django.conf.urls.static import static
from django.conf import settings

app_name ='qc_app'

urlpatterns = [
    path('dashboard/', views.dashboard, name = 'qc_dashboard'),
    path('rir/rir_add/', views.rir_add, name = 'rir_add'),
    path('rir/rir_judgement_index/', views.rir_judgement_index, name = 'rir_judgement_index'),
    path('rir/rir_judgement_detail/<int:rir_id>', views.rir_judgement_detail, name = 'rir_judgement_detail'),
    path('rir/rir_checked_by_index/', views.rir_checked_by_index, name = 'rir_checked_by_index'),
    path('rir/rir_checked_by_detail/<int:rir_id>', views.rir_checked_by_detail, name = 'rir_checked_by_detail'),
    path('rir/rir_special_judgement_index/', views.rir_special_judgement_index, name = 'rir_special_judgement_index'),
    path('rir/rir_special_judgement_detail/<int:rir_id>', views.rir_special_judgement_detail, name = 'rir_special_judgement_detail'),
    path('rir/rir_supervisor_approval/<int:rir_id>', views.rir_supervisor_approval, name = 'rir_supervisor_approval'),
    path('rir/rir_manager_approval/<int:rir_id>', views.rir_manager_approval, name = 'rir_manager_approval'),
    path('rir/rir_supervisor_return/<int:rir_id>', views.rir_supervisor_return, name = 'rir_supervisor_return'),
    path('rir/rir_manager_return/<int:rir_id>', views.rir_manager_return, name = 'rir_manager_return'),
    path('rir/rir_download_report/<int:rir_id>', views.rir_download_report, name = 'rir_download_report'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

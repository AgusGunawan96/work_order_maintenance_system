from django.urls import path
from qc_app import views
from django.conf.urls.static import static
from django.conf import settings

app_name ='qc_app'

urlpatterns = [
    path('dashboard/', views.dashboard, name = 'qc_dashboard'),

    path('rir/rir_add/', views.rir_add, name = 'rir_add'),

    path('rir/rir_judgement_index/', views.rir_judgement_index, name = 'rir_judgement_index'),
    path('rir/rir_checked_by_index/', views.rir_checked_by_index, name = 'rir_checked_by_index'),
    path('rir/rir_list_sa_index/', views.rir_list_sa_index, name = 'rir_list_sa_index'),
    path('rir/rir_list_return_index/', views.rir_list_return_index, name = 'rir_list_return_index'),
    path('rir/rir_special_judgement_index/', views.rir_special_judgement_index, name = 'rir_special_judgement_index'),

    path('rir/rir_detail/<int:rir_id>', views.rir_detail, name = 'rir_detail'),

    path('rir/rir_supervisor_approval/<int:rir_id>', views.rir_supervisor_approval, name = 'rir_supervisor_approval'),
    path('rir/rir_manager_approval/<int:rir_id>', views.rir_manager_approval, name = 'rir_manager_approval'),

    path('rir/rir_download_report/<int:rir_id>', views.rir_download_report, name = 'rir_download_report'),

    path('rir/rir_judgement_coa_approve/<int:rir_id>', views.rir_judgement_coa_approve, name='rir_judgement_coa_approve'),
    path('rir/rir_judgement_appearance_approve/<int:rir_id>', views.rir_judgement_appearance_approve, name='rir_judgement_appearance_approve'),
    path('rir/rir_judgement_sampletest_approve/<int:rir_id>', views.rir_judgement_sampletest_approve, name='rir_judgement_sampletest_approve'),
    path('rir/rir_judgement_restrictedsubstance_approve/<int:rir_id>', views.rir_judgement_restrictedsubstance_approve, name='rir_judgement_restrictedsubstance_approve'),
    path('rir/rir_judgement_environmentalissue_approve/<int:rir_id>', views.rir_judgement_environmentalissue_approve, name='rir_judgement_environmentalissue_approve'),

    path('rir/rir_checkedby_coa_approve/<int:rir_id>', views.rir_checkedby_coa_approve, name='rir_checkedby_coa_approve'),
    path('rir/rir_checkedby_appearance_approve/<int:rir_id>', views.rir_checkedby_appearance_approve, name='rir_checkedby_appearance_approve'),
    path('rir/rir_checkedby_sampletest_approve/<int:rir_id>', views.rir_checkedby_sampletest_approve, name='rir_checkedby_sampletest_approve'),
    path('rir/rir_checkedby_restrictedsubstance_approve/<int:rir_id>', views.rir_checkedby_restrictedsubstance_approve, name='rir_checkedby_restrictedsubstance_approve'),
    path('rir/rir_checkedby_environmentalissue_approve/<int:rir_id>', views.rir_checkedby_environmentalissue_approve, name='rir_checkedby_environmentalissue_approve'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

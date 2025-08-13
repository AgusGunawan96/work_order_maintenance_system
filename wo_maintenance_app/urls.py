# wo_maintenance_app/urls.py - ENHANCED dengan SDBM Integration

from django.urls import path
from wo_maintenance_app import views

app_name = 'wo_maintenance_app'

urlpatterns = [
    # ===== DASHBOARD & OVERVIEW =====
    path('', views.dashboard_index, name='dashboard'),
    path('dashboard/', views.dashboard_index, name='dashboard_index'),
    
    # ===== INPUT LAPORAN =====
    path('input/', views.input_laporan, name='input_laporan'),
    path('input-laporan/', views.input_laporan, name='input_pengajuan'),
    
    # ===== ENHANCED DAFTAR LAPORAN dengan SDBM =====
    path('daftar/', views.enhanced_daftar_laporan, name='daftar_laporan'),
    path('daftar-pengajuan/', views.enhanced_daftar_laporan, name='daftar_pengajuan'),
    path('list/', views.enhanced_daftar_laporan, name='pengajuan_list'),
    
    # ===== LEGACY DAFTAR LAPORAN (fallback) =====
    path('daftar-legacy/', views.daftar_laporan, name='daftar_laporan_legacy'),
    
    # ===== DETAIL LAPORAN =====
    path('detail/<str:nomor_pengajuan>/', views.detail_laporan, name='detail_laporan'),
    path('detail-pengajuan/<str:nomor_pengajuan>/', views.detail_laporan, name='detail_pengajuan'),
    
    # ===== ENHANCED REVIEW SYSTEM - SITI FATIMAH dengan SDBM =====
    path('review/', views.review_dashboard, name='review_dashboard'),
    path('review/dashboard/', views.review_dashboard, name='review_dashboard_alt'),
    path('review/pengajuan/', views.review_pengajuan_list, name='review_pengajuan_list'),
    path('review/pengajuan/<str:nomor_pengajuan>/', views.review_pengajuan_detail, name='review_pengajuan_detail'),
    path('review/history/', views.review_history, name='review_history'),
    
    # ===== SDBM INTEGRATION ENDPOINTS =====
    path('sdbm/validate/', views.validate_sdbm_integration, name='validate_sdbm_integration'),
    path('sdbm/test-assignment/<str:target_section>/', views.test_sdbm_assignment, name='test_sdbm_assignment'),
    path('sdbm/supervisor-lookup/<str:target_section>/', views.sdbm_supervisor_lookup, name='sdbm_supervisor_lookup'),
    path('sdbm/assignment-preview/', views.sdbm_assignment_preview, name='sdbm_assignment_preview'),
    
    # ===== AJAX & API ENDPOINTS =====
    path('ajax/update-status/', views.update_pengajuan_status, name='update_pengajuan_status'),
    path('ajax/search-mesin/', views.search_mesin_ajax, name='search_mesin_ajax'),
    path('ajax/get-mesin-by-line/', views.get_mesin_by_line, name='get_mesin_by_line'),
    path('ajax/test-mesin/', views.test_mesin_connection, name='test_mesin_connection'),
    path('ajax/debug-db/', views.debug_database_structure, name='debug_database_structure'),
    path('ajax/get-mesin-by-line-simple/', views.get_mesin_by_line_simple, name='get_mesin_by_line_simple'),
    
    # ===== ENHANCED AJAX untuk SDBM =====
    path('ajax/sdbm/get-supervisors/', views.ajax_get_sdbm_supervisors, name='ajax_get_sdbm_supervisors'),
    path('ajax/sdbm/validate-section/', views.ajax_validate_sdbm_section, name='ajax_validate_sdbm_section'),
    path('ajax/sdbm/assignment-status/', views.ajax_sdbm_assignment_status, name='ajax_sdbm_assignment_status'),

    # ===== ASSIGNMENT SYSTEM =====
    path('create-assignment-tables/', views.create_assignment_tables, name='create_assignment_tables'),
    path('debug/assignment-status/', views.debug_assignment_status, name='debug_assignment_status'),
    path('debug/test-assignment/<str:history_id>/<int:section_id>/<str:approver>/', views.debug_test_assignment, name='debug_test_assignment'),
    path('debug/section-supervisors/<int:section_id>/', views.debug_section_supervisors, name='debug_section_supervisors'),
    
    # ===== ENHANCED DEBUG untuk SDBM =====
    path('debug/sdbm-validation/', views.validate_sdbm_integration, name='debug_sdbm_validation'),
    path('debug/sdbm-assignment-test/<str:target_section>/', views.test_sdbm_assignment, name='debug_sdbm_assignment_test'),
    path('debug/sdbm-mapping/', views.debug_sdbm_mapping, name='debug_sdbm_mapping'),
    path('debug/sdbm-employees/<str:target_section>/', views.debug_sdbm_employees, name='debug_sdbm_employees'),
    
    # ===== ADDITIONAL DEBUG VIEWS =====
    path('debug/form-validation/', views.debug_form_validation, name='debug_form_validation'),
    path('debug/ajax-mesin-response/', views.debug_ajax_mesin_response, name='debug_ajax_mesin_response'),
    path('debug/form-choices/', views.debug_form_choices, name='debug_form_choices'),
    path('debug/test/', views.debug_test_view, name='debug_test_view'),
    path('debug/minimal-approved/', views.minimal_approved_view, name='minimal_approved_view'),
    path('debug/review-flow/<str:history_id>/', views.debug_review_flow, name='debug_review_flow'),
    
    # ===== REVIEW SYSTEM AJAX =====
    path('ajax/review/pending-count/', views.get_pending_review_count, name='get_pending_review_count'),
    path('ajax/review/force-init/', views.force_review_initialization, name='force_review_initialization'),
    path('ajax/review/stats/', views.quick_review_stats, name='quick_review_stats'),
]
# wo_maintenance_app/urls.py - TAMBAHKAN URLs untuk debugging

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
    
    # ===== DAFTAR LAPORAN =====
    path('daftar/', views.daftar_laporan, name='daftar_laporan'),
    path('daftar-pengajuan/', views.daftar_laporan, name='daftar_pengajuan'),
    path('list/', views.daftar_laporan, name='pengajuan_list'),
    
    # ===== DETAIL LAPORAN =====
    path('detail/<str:nomor_pengajuan>/', views.detail_laporan, name='detail_laporan'),
    path('detail-pengajuan/<str:nomor_pengajuan>/', views.detail_laporan, name='detail_pengajuan'),
    
    # ===== DEBUG & TESTING VIEWS (untuk troubleshooting database) =====
    path('debug-test/', views.debug_test_view, name='debug_test_view'),
    path('minimal-approved/', views.minimal_approved_view, name='minimal_approved_view'),
    
    # ===== REVIEW SYSTEM - SITI FATIMAH =====
    path('review/', views.review_dashboard, name='review_dashboard'),
    path('review/dashboard/', views.review_dashboard, name='review_dashboard_alt'),
    path('review/pengajuan/', views.review_pengajuan_list, name='review_pengajuan_list'),
    path('review/pengajuan/<str:nomor_pengajuan>/', views.review_pengajuan_detail, name='review_pengajuan_detail'),
    path('review/history/', views.review_history, name='review_history'),
    
    # ===== AJAX & API ENDPOINTS =====
    path('ajax/update-status/', views.update_pengajuan_status, name='update_pengajuan_status'),
    path('ajax/search-mesin/', views.search_mesin_ajax, name='search_mesin_ajax'),
    path('ajax/get-mesin-by-line/', views.get_mesin_by_line, name='get_mesin_by_line'),
    path('ajax/test-mesin/', views.test_mesin_connection, name='test_mesin_connection'),
    path('ajax/debug-db/', views.debug_database_structure, name='debug_database_structure'),
    path('ajax/get-mesin-by-line-simple/', views.get_mesin_by_line_simple, name='get_mesin_by_line_simple'),

    # ===== ASSIGNMENT SYSTEM =====
    path('create-assignment-tables/', views.create_assignment_tables, name='create_assignment_tables'),
    
    # ===== REVIEW SYSTEM AJAX ENDPOINTS =====
    path('ajax/pending-review-count/', views.get_pending_review_count, name='get_pending_review_count'),
    path('ajax/force-review-init/', views.force_review_initialization, name='force_review_initialization'),
    path('ajax/review-stats/', views.quick_review_stats, name='quick_review_stats'),
    
    # ===== DEBUG ENDPOINTS (SUPERUSER ONLY) =====
    path('debug/assignment-status/', views.debug_assignment_status, name='debug_assignment_status'),
    path('debug/test-assignment/<str:history_id>/<int:section_id>/<str:approver>/', views.debug_test_assignment, name='debug_test_assignment'),
    path('debug/section-supervisors/<int:section_id>/', views.debug_section_supervisors, name='debug_section_supervisors'),
    path('debug/form-validation/', views.debug_form_validation, name='debug_form_validation'),
    path('debug/ajax-response/', views.debug_ajax_mesin_response, name='debug_ajax_response'),  
    path('debug/form-choices/', views.debug_form_choices, name='debug_form_choices'),
    path('debug/review-flow/<str:history_id>/', views.debug_review_flow, name='debug_review_flow'),
]
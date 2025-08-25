# wo_maintenance_app/urls.py - UPDATED dengan Monitoring System URLs yang Fix

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
    path('enhanced/', views.enhanced_daftar_laporan, name='enhanced_daftar_laporan'),
    
    # ===== LEGACY DAFTAR LAPORAN (fallback) =====
    path('daftar-legacy/', views.daftar_laporan, name='daftar_laporan_legacy'),
    
    # ===== DETAIL LAPORAN =====
    path('detail/<str:nomor_pengajuan>/', views.detail_laporan, name='detail_laporan'),
    path('detail-pengajuan/<str:nomor_pengajuan>/', views.detail_laporan, name='detail_pengajuan'),
    
    # ===== ENHANCED DETAIL ROUTE =====
    path('enhanced-detail/<str:nomor_pengajuan>/', views.enhanced_pengajuan_detail, name='enhanced_pengajuan_detail'),
    
    # ===== HISTORY PENGAJUAN - NEW FEATURE =====
    path('history/', views.history_pengajuan_list, name='history_pengajuan_list'),
    path('history/list/', views.history_pengajuan_list, name='history_list'),
    path('history/<str:nomor_pengajuan>/', views.history_pengajuan_detail, name='history_pengajuan_detail'),
    path('history/detail/<str:nomor_pengajuan>/', views.history_pengajuan_detail, name='history_detail'),
    
    # ===== MONITORING INFORMASI SYSTEM - FIXED VERSION =====
    path('monitoring/', views.monitoring_informasi_system, name='monitoring_informasi_system'),
    path('monitor/', views.monitoring_informasi_system, name='monitor'),  # Alias pendek
    path('monitoring/system/', views.monitoring_informasi_system, name='monitoring_system'),  # Alternative URL
    path('ajax/monitoring/refresh/', views.ajax_monitoring_refresh, name='ajax_monitoring_refresh'),

    path('ajax/monitoring/refresh-database/', views.ajax_monitoring_refresh_database, name='ajax_monitoring_refresh_database'),
    
    
    # ===== ENHANCED REVIEW SYSTEM - SITI FATIMAH dengan Auto Transfer =====
    path('review/', views.review_dashboard, name='review_dashboard'),
    path('review/dashboard/', views.review_dashboard, name='review_dashboard_alt'),
    path('review/pengajuan/', views.review_pengajuan_list, name='review_pengajuan_list'),
    path('review/pengajuan/<str:nomor_pengajuan>/', views.review_pengajuan_detail, name='review_pengajuan_detail'),
    path('review/history/', views.review_history, name='review_history'),
    path('review-list/', views.review_pengajuan_list, name='review_list'),
    
    # ===== ENHANCED REVIEW dengan Auto Transfer ke Tabel Main =====
    path('review/pengajuan/<str:nomor_pengajuan>/enhanced/', views.review_pengajuan_detail_enhanced, name='review_pengajuan_detail_enhanced'),
    path('review/pengajuan/<str:nomor_pengajuan>/with-transfer/', views.enhanced_review_pengajuan_detail_with_transfer, name='enhanced_review_with_transfer'),
    
    # ===== AJAX ENDPOINTS untuk Section Change =====
    path('ajax/review/preview-section-change/', views.ajax_preview_section_change, name='ajax_preview_section_change'),
    path('ajax/review/confirm-section-change/', views.ajax_confirm_section_change, name='ajax_confirm_section_change'),
    path('ajax/review/section-mapping-info/', views.ajax_get_section_mapping_info, name='ajax_get_section_mapping_info'),
    
    # ===== AJAX ENDPOINTS untuk History =====
    path('ajax/history/stats/', views.ajax_get_history_stats, name='ajax_get_history_stats'),
    path('ajax/history/quick-status/', views.ajax_quick_update_status, name='ajax_quick_update_status'),
    
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
    path('debug/minimal-approved/', views.minimal_approved_view, name='debug_minimal_approved_view'),
    path('debug/review-flow/<str:history_id>/', views.debug_review_flow, name='debug_review_flow'),
    
    # ===== REVIEW SYSTEM AJAX =====
    path('ajax/review/pending-count/', views.get_pending_review_count, name='get_pending_review_count'),
    path('ajax/review/force-init/', views.force_review_initialization, name='force_review_initialization'),
    path('ajax/review/stats/', views.quick_review_stats, name='quick_review_stats'),

    # ===== ENHANCED DEBUG & TESTING =====
    path('debug/test-review-button/', views.test_review_button_visibility, name='test_review_button_visibility'),
    path('debug/quick-fix-review/', views.quick_fix_review_system, name='quick_fix_review_system'),
    path('debug/status-validation/', views.debug_status_validation, name='debug_status_validation'),
    
    # ===== ENHANCED DEBUG untuk Section Mapping =====
    path('debug/section-mapping/<int:sdbm_section_id>/', views.debug_section_mapping, name='debug_section_mapping'),
    
    # ===== NEW: ID FORMAT TESTING & MIGRATION =====
    path('debug/test-id-generation/', views.test_id_generation, name='test_id_generation'),
    path('debug/migrate-existing-ids/', views.migrate_existing_ids, name='migrate_existing_ids'),
    path('debug/validate-id-formats/', views.validate_id_formats, name='validate_id_formats'),

    # AJAX endpoints untuk number WO preview
    path('ajax/preview-number-wo/', views.ajax_preview_number_wo_change, name='ajax_preview_number_wo'),
    path('debug/number-wo-generation/', views.debug_number_wo_generation, name='debug_number_wo_generation'),

    # Tambahkan di urlpatterns
path('keep-session-alive/', views.keep_session_alive, name='keep_session_alive'),

# Session-Based Checker APIs (No Database Models Required)
    path('api/session/save-checker/', views.session_save_checker, name='session_save_checker'),
    path('api/session/get-checkers/', views.session_get_checkers, name='session_get_checkers'),
    path('api/session/clear-checker/', views.session_clear_checker, name='session_clear_checker'),
    # ===== DATABASE CHECKER API ENDPOINTS =====
    path('database/save-checker/', views.save_checker_to_database_api, name='save_checker_database'),
    path('database/get-checkers/', views.get_all_checkers_from_database_api, name='get_checkers_database'),
]


# ===== MONITORING SYSTEM VALIDATION =====
def validate_monitoring_url_patterns():
    """
    Function untuk validate monitoring URLs
    """
    import logging
    logger = logging.getLogger(__name__)
    
    monitoring_urls = [
        'monitoring_informasi_system',
        'monitor',
        'monitoring_system',
        'ajax_monitoring_refresh'
    ]
    
    existing_urls = [pattern.name for pattern in urlpatterns]
    missing_urls = []
    
    for monitoring_url in monitoring_urls:
        if monitoring_url not in existing_urls:
            missing_urls.append(monitoring_url)
    
    if missing_urls:
        logger.error(f"MISSING MONITORING URLS: {missing_urls}")
        return False
    else:
        logger.info("✅ All monitoring URLs exist")
        return True


# ===== ENHANCED URL VALIDATION dengan Monitoring =====
def validate_enhanced_url_patterns_with_monitoring():
    """
    Enhanced function untuk validate semua URL patterns termasuk monitoring endpoints
    """
    import logging
    logger = logging.getLogger(__name__)
    
    url_map = {}
    ajax_endpoints = []
    history_endpoints = []
    review_endpoints = []
    monitoring_endpoints = []  # NEW
    
    for pattern in urlpatterns:
        url_name = pattern.name
        url_route = pattern.pattern._route if hasattr(pattern.pattern, '_route') else str(pattern.pattern)
        
        url_map[url_name] = url_route
        
        # Kategorisasi endpoints
        if 'ajax' in url_route:
            ajax_endpoints.append(url_name)
            
        if 'history' in url_route:
            history_endpoints.append(url_name)
            
        if 'review' in url_route:
            review_endpoints.append(url_name)
            
        if 'monitoring' in url_route or 'monitor' in url_route:  # NEW
            monitoring_endpoints.append(url_name)
    
    # Log semua URLs
    logger.info("=== ENHANCED WO MAINTENANCE URL PATTERNS WITH MONITORING ===")
    logger.info(f"Total URLs: {len(url_map)}")
    logger.info(f"AJAX Endpoints: {len(ajax_endpoints)}")
    logger.info(f"History Endpoints: {len(history_endpoints)}")
    logger.info(f"Review Endpoints: {len(review_endpoints)}")
    logger.info(f"Monitoring Endpoints: {len(monitoring_endpoints)}")  # NEW
    
    for name, route in url_map.items():
        category = ""
        if name in ajax_endpoints:
            category += "[AJAX] "
        if name in history_endpoints:
            category += "[HISTORY] "
        if name in review_endpoints:
            category += "[REVIEW] "
        if name in monitoring_endpoints:  # NEW
            category += "[MONITORING] "
        
        logger.info(f"  {category}{name}: {route}")
    
    logger.info("=== END ENHANCED URL PATTERNS WITH MONITORING ===")
    
    return {
        'all_urls': url_map,
        'ajax_endpoints': ajax_endpoints,
        'history_endpoints': history_endpoints,
        'review_endpoints': review_endpoints,
        'monitoring_endpoints': monitoring_endpoints  # NEW
    }

# Enhanced Critical URLs yang harus ada untuk monitoring system
ENHANCED_CRITICAL_URLS_WITH_MONITORING = [
    'dashboard',
    'daftar_laporan',
    'detail_laporan', 
    'history_pengajuan_list',
    'history_pengajuan_detail',
    'monitoring_informasi_system',      # NEW: Monitoring system
    'ajax_monitoring_refresh',          # NEW: Monitoring AJAX
    'review_dashboard',
    'review_pengajuan_list',
    'review_pengajuan_detail',
    'enhanced_pengajuan_detail',
    'ajax_get_history_stats',
    'ajax_quick_update_status',
    'ajax_preview_section_change',
    'ajax_confirm_section_change',
    'ajax_get_section_mapping_info'
]

def check_enhanced_critical_urls_with_monitoring():
    """
    Enhanced check untuk memastikan semua critical URLs exist termasuk monitoring endpoints
    """
    import logging
    logger = logging.getLogger(__name__)
    
    existing_urls = [pattern.name for pattern in urlpatterns]
    missing_urls = []
    monitoring_urls = []
    
    for critical_url in ENHANCED_CRITICAL_URLS_WITH_MONITORING:
        if critical_url not in existing_urls:
            missing_urls.append(critical_url)
        
        # Track monitoring related URLs
        if 'monitoring' in critical_url:
            monitoring_urls.append(critical_url)
    
    if missing_urls:
        logger.error(f"MISSING ENHANCED CRITICAL URLS WITH MONITORING: {missing_urls}")
        return False
    else:
        logger.info("✅ All enhanced critical URLs with monitoring exist")
        logger.info(f"✅ Monitoring URLs available: {len(monitoring_urls)}")
        return True

# Export functions
__all__ = [
    'validate_enhanced_url_patterns_with_monitoring',
    'check_enhanced_critical_urls_with_monitoring',
    'validate_monitoring_url_patterns',
    'ENHANCED_CRITICAL_URLS_WITH_MONITORING'
]
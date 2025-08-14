# wo_maintenance_app/urls.py - ENHANCED dengan Section Change URLs

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
    
    # ===== ENHANCED DETAIL ROUTE =====
    path('enhanced-detail/<str:nomor_pengajuan>/', views.enhanced_pengajuan_detail, name='enhanced_pengajuan_detail'),
    
    # ===== ENHANCED REVIEW SYSTEM - SITI FATIMAH dengan Section Change =====
    path('review/', views.review_dashboard, name='review_dashboard'),
    path('review/dashboard/', views.review_dashboard, name='review_dashboard_alt'),
    path('review/pengajuan/', views.review_pengajuan_list, name='review_pengajuan_list'),
    path('review/pengajuan/<str:nomor_pengajuan>/', views.review_pengajuan_detail, name='review_pengajuan_detail'),
    path('review/history/', views.review_history, name='review_history'),
    
    # ===== ENHANCED REVIEW dengan Section Change Support =====
    path('review/pengajuan/<str:nomor_pengajuan>/enhanced/', views.review_pengajuan_detail_enhanced, name='review_pengajuan_detail_enhanced'),
    
    # ===== AJAX ENDPOINTS untuk Section Change =====
    path('ajax/review/preview-section-change/', views.ajax_preview_section_change, name='ajax_preview_section_change'),
    path('ajax/review/confirm-section-change/', views.ajax_confirm_section_change, name='ajax_confirm_section_change'),
    path('ajax/review/section-mapping-info/', views.ajax_get_section_mapping_info, name='ajax_get_section_mapping_info'),
    
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

    # ===== ENHANCED DEBUG & TESTING =====
    path('debug/test-review-button/', views.test_review_button_visibility, name='test_review_button_visibility'),
    path('debug/quick-fix-review/', views.quick_fix_review_system, name='quick_fix_review_system'),
    path('debug/status-validation/', views.debug_status_validation, name='debug_status_validation'),
    
    # ===== ENHANCED DEBUG untuk Section Mapping =====
    path('debug/section-mapping/<int:sdbm_section_id>/', views.debug_section_mapping, name='debug_section_mapping'),
    # path('debug/section-change-preview/<str:history_id>/<str:target_section>/', views.debug_section_change_preview, name='debug_section_change_preview'),
    
    # ===== FALLBACK ROUTES untuk Backward Compatibility =====
    path('enhanced/', views.enhanced_daftar_laporan, name='enhanced_daftar_laporan'),
    path('review-list/', views.review_pengajuan_list, name='review_list'),
]

# ===== ENHANCED URL VALIDATION untuk Section Change =====
def validate_enhanced_url_patterns():
    """
    Enhanced function untuk validate semua URL patterns termasuk section change endpoints
    """
    import logging
    logger = logging.getLogger(__name__)
    
    url_map = {}
    ajax_endpoints = []
    section_change_endpoints = []
    
    for pattern in urlpatterns:
        url_name = pattern.name
        url_route = pattern.pattern._route if hasattr(pattern.pattern, '_route') else str(pattern.pattern)
        
        url_map[url_name] = url_route
        
        # Kategorisasi endpoints
        if 'ajax' in url_route:
            ajax_endpoints.append(url_name)
            
        if 'section' in url_route or 'review' in url_route:
            section_change_endpoints.append(url_name)
    
    # Log semua URLs
    logger.info("=== ENHANCED WO MAINTENANCE URL PATTERNS ===")
    logger.info(f"Total URLs: {len(url_map)}")
    logger.info(f"AJAX Endpoints: {len(ajax_endpoints)}")
    logger.info(f"Section Change Related: {len(section_change_endpoints)}")
    
    for name, route in url_map.items():
        category = ""
        if name in ajax_endpoints:
            category += "[AJAX] "
        if name in section_change_endpoints:
            category += "[SECTION] "
        
        logger.info(f"  {category}{name}: {route}")
    
    logger.info("=== END ENHANCED URL PATTERNS ===")
    
    return {
        'all_urls': url_map,
        'ajax_endpoints': ajax_endpoints,
        'section_change_endpoints': section_change_endpoints
    }

# Enhanced Critical URLs yang harus ada untuk section change
ENHANCED_CRITICAL_URLS = [
    'dashboard',
    'daftar_laporan',
    'detail_laporan', 
    'review_dashboard',
    'review_pengajuan_list',
    'review_pengajuan_detail',
    'enhanced_pengajuan_detail',
    'ajax_preview_section_change',    # NEW: Required untuk section change preview
    'ajax_confirm_section_change',    # NEW: Required untuk section change confirmation
    'ajax_get_section_mapping_info'   # NEW: Required untuk section mapping info
]

def check_enhanced_critical_urls():
    """
    Enhanced check untuk memastikan semua critical URLs exist termasuk section change endpoints
    """
    import logging
    logger = logging.getLogger(__name__)
    
    existing_urls = [pattern.name for pattern in urlpatterns]
    missing_urls = []
    section_change_urls = []
    
    for critical_url in ENHANCED_CRITICAL_URLS:
        if critical_url not in existing_urls:
            missing_urls.append(critical_url)
        
        # Track section change related URLs
        if 'section' in critical_url or 'preview' in critical_url or 'confirm' in critical_url:
            section_change_urls.append(critical_url)
    
    if missing_urls:
        logger.error(f"MISSING ENHANCED CRITICAL URLS: {missing_urls}")
        return False
    else:
        logger.info("✅ All enhanced critical URLs exist")
        logger.info(f"✅ Section change URLs available: {len(section_change_urls)}")
        return True

# ===== ENHANCED URL Helper Functions =====
def get_section_change_urls():
    """
    Get all URLs related to section change functionality
    """
    section_urls = {}
    
    for pattern in urlpatterns:
        url_name = pattern.name
        url_route = str(pattern.pattern)
        
        if any(keyword in url_name for keyword in ['section', 'preview', 'confirm']):
            section_urls[url_name] = url_route
    
    return section_urls

def get_ajax_urls():
    """
    Get all AJAX endpoints
    """
    ajax_urls = {}
    
    for pattern in urlpatterns:
        url_name = pattern.name
        url_route = str(pattern.pattern)
        
        if 'ajax' in url_route:
            ajax_urls[url_name] = url_route
    
    return ajax_urls
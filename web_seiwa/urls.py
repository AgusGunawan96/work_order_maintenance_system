# web_seiwa/urls.py - File URLs utama yang diperbaiki
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

# Import views untuk SDBM authentication
from master_app.views import sdbm_login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ===== AUTHENTICATION URLs =====
    # SDBM Login (prioritas utama)
    path('login/', sdbm_login_view, name='login'),  # Default login menggunakan SDBM
    path('sdbm-login/', sdbm_login_view, name='sdbm_login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    
    # ===== ROOT & DASHBOARD =====
    path('', include('master_app.urls')),  # Root URL langsung ke master_app
    
    # ===== APPLICATION URLs =====
    path('master/', include('master_app.urls')),
    path('accounting/', include('accounting_app.urls')),
    path('hrd/', include('hrd_app.urls')),
    path('ga/', include('ga_app.urls')),
    path('ppc/', include('ppc_app.urls')),
    path('costcontrol/', include('costcontrol_app.urls')),
    path('sales/', include('sales_app.urls')),
    path('ie/', include('ie_app.urls')),
    path('qc/', include('qc_app.urls')),
    path('warehouse/', include('warehouse_app.urls')),
    path('engineering/', include('engineering_app.urls')),
    path('it/', include('it_app.urls')),
    path('timing/', include('timing_app.urls')),
    path('production/', include('production_app.urls')),
    path('gatepass/', include('gatepass_app.urls')),
    path('ceisa/', include('ceisa_app.urls')),
    path('dailyactivity/', include('dailyactivity_app.urls')),
    
    # ===== WO MAINTENANCE APP (BARU) =====
    path('wo-maintenance/', include('wo_maintenance_app.urls')),
    
    # ===== APLIKASI OPSIONAL (Comment sementara untuk mencegah error) =====
    # Uncomment setelah file URLs dibuat dan ditest
    # path('POSEIWA/', include('POSEIWA.urls')),
    # path('sfc_2/', include('sfc_2.urls')),
    # path('seiwa/', include('seiwa.urls')),     # COMMENT DULU
    # path('wingo/', include('wingoapp.urls')),  # COMMENT DULU
]

# ===== STATIC & MEDIA FILES =====
# Untuk development - serve media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Hanya tambahkan jika STATICFILES_DIRS ada dan tidak kosong
    if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# ===== ERROR HANDLERS (opsional) =====
# Uncomment jika ingin custom error pages
# handler404 = 'master_app.views.custom_404'
# handler500 = 'master_app.views.custom_500'
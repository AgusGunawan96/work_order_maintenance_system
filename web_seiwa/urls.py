"""web_seiwa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from master_app import views as view_master
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # path('', include('wingoapp.urls')),
    path('', view_master.index, name='index'),
    path("accounts/", include("django.contrib.auth.urls")),
    path('accounting_app/', include('accounting_app.urls')),
    path('hrd_app/', include('hrd_app.urls')),
    path('ga_app/', include('ga_app.urls')),
    path('ppc_app/', include('ppc_app.urls')),
    path('costcontrol_app/', include('costcontrol_app.urls')),
    path('sales_app/', include('sales_app.urls')),
    path('ie_app/', include('ie_app.urls')),
    path('qc_app/', include('qc_app.urls')),
    path('warehouse_app/', include('warehouse_app.urls')),
    path('engineering_app/', include('engineering_app.urls')),
    path('it_app/', include('it_app.urls')),
    path('master_app/', include('master_app.urls')),
    path('timing_app/', include('timing_app.urls')),
    path('production_app/', include('production_app.urls')),
    path('gatepass_app/', include('gatepass_app.urls')),
    path('admin/', admin.site.urls),
    path('select2/', include('django_select2.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

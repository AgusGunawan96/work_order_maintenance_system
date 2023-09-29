from django.urls import path
from ceisa_app import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'ceisa_app'

urlpatterns = [
    path('', views.index, name = 'index'),
    path('dokumen_impor/add', views.dokumen_impor_add, name = 'dokumen_impor_add'),
    path('dokumen_ekspor/add', views.dokumen_ekspor_add, name = 'dokumen_ekspor_add'),
    path('get_access_token', views.get_access_token, name = 'get_access_token'),
    path('update_data/', views.update_data, name='update_data'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



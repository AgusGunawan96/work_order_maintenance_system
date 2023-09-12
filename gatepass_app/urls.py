from django.urls import path
from gatepass_app import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'gatepass_app'

urlpatterns = [
    path('', views.index, name = 'index'),
    path('post_tamu_masuk/<str:GatepassNo>/<str:TanggalIn>/<str:NamaTamu>/<str:NamaPerusahaan>/<str:NomorIdentitas>/<str:Tujuan>/<str:TujuanDetail>/<str:NomorKendaraan>/<str:JenisKendaraan>/<str:BertemuDengan>/<str:Department>/<str:Status>/<str:Security>', views.post_tamu_masuk, name='post_tamu_masuk'),
    path('tamu', views.tamu_index, name = 'tamu_index'),
    path('kirim_barang', views.kirim_barang_menu, name = 'kirim_barang_menu'),
    path('kirim_barang_local', views.kirim_barang_local, name = 'kirim_barang_local'),
    path('kirim_barang_import', views.kirim_barang_import, name = 'kirim_barang_import'),
    path('ambil_barang', views.ambil_barang_index, name = 'ambil_barang_index'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

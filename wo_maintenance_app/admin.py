# wo_maintenance_app/admin.py
from django.contrib import admin
from .models import TabelPengajuan, TabelMsection, TabelMesin, TabelPekerjaan

# Admin untuk TabelPengajuan
@admin.register(TabelPengajuan)
class TabelPengajuanAdmin(admin.ModelAdmin):
    list_display = ['history_id', 'oleh', 'status', 'approve', 'tgl_insert']
    list_filter = ['status', 'approve', 'tgl_insert']
    search_fields = ['history_id', 'oleh', 'deskripsi_perbaikan']
    date_hierarchy = 'tgl_insert'
    readonly_fields = ['history_id', 'tgl_his', 'jam_his', 'number_wo', 'tgl_insert']
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('history_id', 'tgl_his', 'jam_his', 'number_wo')
        }),
        ('Detail Pengajuan', {
            'fields': ('id_line', 'id_mesin', 'id_section', 'id_pekerjaan', 'deskripsi_perbaikan')
        }),
        ('Status & Approval', {
            'fields': ('status', 'approve', 'status_pekerjaan')
        }),
        ('Informasi User', {
            'fields': ('user_insert', 'oleh', 'tgl_insert')
        }),
    )

# Admin untuk TabelMsection
@admin.register(TabelMsection)
class TabelMsectionAdmin(admin.ModelAdmin):
    list_display = ['id_section', 'seksi', 'status', 'tgl_insert']
    list_filter = ['status']
    search_fields = ['seksi', 'keterangan']
    readonly_fields = ['tgl_insert', 'tgl_edit']

# Admin untuk TabelMesin
@admin.register(TabelMesin)
class TabelMesinAdmin(admin.ModelAdmin):
    list_display = ['id_mesin', 'mesin', 'nomer', 'id_line', 'status']
    list_filter = ['status', 'id_line']
    search_fields = ['mesin', 'nomer', 'keterangan']

# Admin untuk TabelPekerjaan
@admin.register(TabelPekerjaan)
class TabelPekerjaanAdmin(admin.ModelAdmin):
    list_display = ['id_pekerjaan', 'pekerjaan', 'status']
    list_filter = ['status']
    search_fields = ['pekerjaan', 'keterangan']
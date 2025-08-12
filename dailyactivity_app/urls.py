# dailyactivity_app/urls.py
from django.urls import path
from dailyactivity_app import views

app_name = 'dailyactivity_app'  # Menetapkan nama aplikasi untuk namespace

urlpatterns = [
    path('dashboard/', views.dashboard_index, name='dashboard_index'),

    # Real-time endpoints
    path('api/check-updates/<str:tanggal>/', views.check_laporan_updates, name='check_laporan_updates'),
    path('api/get-data/<str:tanggal>/', views.get_laporan_data_ajax, name='get_laporan_data_ajax'),

    path('mechanical/', views.mechanical_index, name='mechanical_index'),
    path('mechanical/submit/', views.mechanical_submit, name='mechanical_submit'),  # Uncomment this line
    path('mechanical/tanggal/', views.tanggal_mechanical, name='tanggal_mechanical'),
    path('mechanical/data/<str:tanggal>/', views.data_mechanical, name='data_mechanical'),  # Rute baru untuk data berdasarkan tanggal
    path('machinemechanical/upload_excel/', views.upload_machinemechanical_excel, name='upload_machinemechanical_excel'),
    path('edit-mechanical-data/<int:id>/', views.edit_mechanical_data, name='edit_mechanical_data'),
    path('delete-mechanical-data/<int:id>/', views.delete_mechanical_data, name='delete_mechanical_data'),
    path('schedule/', views.schedule_index, name='schedule_index'),  # Path untuk schedulemechanical
    path('schedule/submit', views.schedule_submit, name='schedule_submit'),
    path('schedule/tanggal/', views.tanggal_schedule, name='tanggal_schedule'),
    path('schedule/data/<str:tanggal>/', views.data_schedule, name='data_schedule'),
    path('schedule/edit/<int:id>/', views.edit_schedule, name='edit_schedule'),
    path('delete-schedule/<int:id>/', views.delete_schedule, name='delete_schedule'),

    # path('schedule/delete/<int:id>/', views.delete_schedule, name='delete_schedule'),
    # path('mechanical/mechanical_index/lookup_deskripsi_wo/', views.lookup_deskripsi_wo, name='lookup_deskripsi_wo'),
    path('mechanical/mechanical_index/lookup_data_table/', views.lookup_data_table, name='lookup_data_table'),
    # path('mechanical_index/lookup_data_table/', views.lookup_data_table, name='lookup_data_table'),
    

    path('laporanmechanical/', views.laporanmechanical_index, name='laporanmechanical_index'),
    path('laporanmechanical/submit/', views.laporanmechanical_submit, name='laporanmechanical_submit'), 
    path('laporanmechanical/tanggal/', views.tanggal_laporanmechanical, name='tanggal_laporanmechanical'),
    path('laporanmechanical/data/<str:tanggal>/', views.data_laporanmechanical, name='data_laporanmechanical'),
    path('laporanmechanical/edit/<int:id>/', views.edit_laporanmechanical, name='edit_laporanmechanical'),
    path('laporanmechanical/delete/<int:id>/', views.delete_laporanmechanical, name='delete_laporanmechanical'),
    path('laporanmechanical/add_comment/<int:laporan_id>/', views.add_comment, name='add_comment'),
    
    


    path('electrical/', views.electrical_index, name='electrical_index'),
    path('electrical/submit/', views.electrical_submit, name='electrical_submit'),  # Uncomment this line
    path('electrical/tanggal/', views.tanggal_electrical, name='tanggal_electrical'),
    path('electrical/data/<str:tanggal>/', views.data_electrical, name='data_electrical'),
    path('edit-electrical-data/<int:id>/', views.edit_electrical_data, name='edit_electrical_data'),
    path('delete-electrical-data/<int:id>/', views.delete_electrical_data, name='delete_electrical_data'),
    path('machineelectrical/upload_excel/', views.upload_machineelectrical_excel, name='upload_machineelectrical_excel'),
    # path('electrical/get_masalah/<str:number_wo>/', views.get_masalah, name='get_masalah'),
    

    path('utility/', views.utility_index, name='utility_index'),
    path('utility/submit/', views.utility_submit, name='utility_submit'),  # Uncomment this line
    path('utility/tanggal/', views.tanggal_utility, name='tanggal_utility'),
    path('utility/data/<str:tanggal>/', views.data_utility, name='data_utility'),
    path('edit-utility-data/<int:id>/', views.edit_utility_data, name='edit_utility_data'),
    path('delete-utility-data/<int:id>/', views.delete_utility_data, name='delete_utility_data'),
    path('machineutility/upload_excel/', views.upload_machineutility_excel, name='upload_machineutility_excel'),
    path('laporan/', views.laporan_index, name='laporan_index'),
    path('laporan/submit/', views.laporan_submit, name='laporan_submit'), 
    path('laporan/tanggal/', views.tanggal_laporan, name='tanggal_laporan'),
    path('laporan/data/<str:tanggal>/', views.data_laporan, name='data_laporan'),
    path('laporan/edit/<int:id>/', views.edit_laporan, name='edit_laporan'),
    path('laporan/delete/<int:id>/', views.delete_laporan, name='delete_laporan'),


    

    path('shift/', views.shift_index, name='shift_index'),
    path('location/', views.location_index, name='location_index'),
    path('upload-location-excel/', views.upload_location_excel, name='upload_location_excel'),
    path('category/', views.category_index, name='category_index'),
    path('status/', views.status_index, name='status_index'),
    path('machine/mechanical/', views.machinemechanical_index, name='machinemechanical_index'),
    path('machine/edit/<int:pk>/', views.edit_machinemechanical, name='edit_machinemechanical'),
    path('machine/delete/<int:pk>/', views.delete_machinemechanical, name='delete_machinemechanical'),
    
    
    path('machine/electrical/', views.machineelectrical_index, name='machineelectrical_index'),
    path('machine/electrical/edit/<int:pk>/', views.edit_machineelectrical, name='edit_machineelectrical'),
    path('machine/electrical/delete/<int:pk>/', views.delete_machineelectrical, name='delete_machineelectrical'),
    path('machine/utility/', views.machineutility_index, name='machineutility_index'),
    path('machine/utility/edit/<int:pk>/', views.edit_machineutility, name='edit_machineutility'),
    path('machine/utility/delete/<int:pk>/', views.delete_machineutility, name='delete_machineutility'),

    path('shift/edit/<int:pk>/', views.edit_shift, name='edit_shift'),
    path('shift/delete/<int:pk>/', views.delete_shift, name='delete_shift'),
    path('location/edit/<int:pk>/', views.edit_location, name='edit_location'),
    path('location/delete/<int:pk>/', views.delete_location, name='delete_location'),
    path('category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('category/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('status/edit/<int:pk>/', views.edit_status, name='edit_status'),
    path('status/delete/<int:pk>/', views.delete_status, name='delete_status'),

    path('picmechanical/', views.picmechanical_index, name='picmechanical_index'),
    path('picmechanical/edit/<int:pk>/', views.edit_picmechanical, name='edit_picmechanical'),
    path('picmechanical/delete/<int:pk>/', views.delete_picmechanical, name='delete_picmechanical'),

    path('picelectrical/', views.picelectrical_index, name='picelectrical_index'),
    path('picelectrical/edit/<int:pk>/', views.edit_picelectrical, name='edit_picelectrical'),
    path('picelectrical/delete/<int:pk>/', views.delete_picelectrical, name='delete_picelectrical'),

    path('picutility/', views.picutility_index, name='picutility_index'),
    path('picutility/edit/<int:pk>/', views.edit_picutility, name='edit_picutility'),
    path('picutility/delete/<int:pk>/', views.delete_picutility, name='delete_picutility'),

    path('picit/', views.picit_index, name='picit_index'),
    path('picit/edit/<int:pk>/', views.edit_picit, name='edit_picit'),
    path('picit/delete/<int:pk>/', views.delete_picit, name='delete_picit'),

    path('piclaporan/', views.piclaporan_index, name='piclaporan_index'),
    path('piclaporan/edit/<int:pk>/', views.edit_piclaporan, name='edit_piclaporan'),
    path('piclaporan/delete/<int:pk>/', views.delete_piclaporan, name='delete_piclaporan'),

    path('piclembur/', views.piclembur_index, name='piclembur_index'),
    path('piclembur/edit/<int:pk>/', views.edit_piclembur, name='edit_piclembur'),
    path('piclembur/delete/<int:pk>/', views.delete_piclembur, name='delete_piclembur'),

    path('piclaporanmechanical/', views.piclaporanmechanical_index, name='piclaporanmechanical_index'),
    path('piclaporanmechanical/edit/<int:pk>/', views.edit_piclaporanmechanical, name='edit_piclaporanmechanical'),
    path('piclaporanmechanical/delete/<int:pk>/', views.delete_piclaporanmechanical, name='delete_piclaporanmechanical'),

    path('piclemburmechanical/', views.piclemburmechanical_index, name='piclemburmechanical_index'),
    path('piclemburmechanical/edit/<int:pk>/', views.edit_piclemburmechanical, name='edit_piclemburmechanical'),
    path('piclemburmechanical/delete/<int:pk>/', views.delete_piclemburmechanical, name='delete_piclemburmechanical'),


    path('it/', views.it_index, name='it_index'),
    path('it/submit/', views.it_submit, name='it_submit'),  # Uncomment this line
    path('it/tanggal/', views.tanggal_it, name='tanggal_it'),
    path('it/data/<str:tanggal>/', views.data_it, name='data_it'),
    path('edit-it-data/<int:id>/', views.edit_it_data, name='edit_it_data'),
    path('delete-it-data/<int:id>/', views.delete_it_data, name='delete_it_data'),


    path('get_machines_by_location_mechanical/<int:location_id>/', views.get_machines_by_location_mechanical, name='get_machines_by_location_mechanical'),
    path('get_machine_number_mechanical/<int:machine_id>/', views.get_machine_number_mechanical, name='get_machine_number_mechanical'),

    path('get_machines_by_location_electrical/<int:location_id>/', views.get_machines_by_location_electrical, name='get_machines_by_location_electrical'),
    path('get_machine_number_electrical/<int:machine_id>/', views.get_machine_number_electrical, name='get_machine_number_electrical'),

    path('get_machines_by_location_utility/<int:location_id>/', views.get_machines_by_location_utility, name='get_machines_by_location_utility'),
    path('get_machine_number_utility/<int:machine_id>/', views.get_machine_number_utility, name='get_machine_number_utility'),

    path('it_project/', views.it_project, name='it_project'),
     path('it-tanggal-project/', views.it_tanggal_project, name='it_tanggal_project'),
    path('it-data-project/', views.it_data_project, name='it_data_project_all'),
    path('it-data-project/<str:date>/', views.it_data_project, name='it_data_project'),
    # path('it_tanggal_project/', views.it_tanggal_project, name='it_tanggal_project'),
    #  path('it_data_project/', views.it_data_project, name='it_data_project'),
    path('it_project/<int:project_id>/', views.it_project_detail, name='it_project_detail'),
    path('delete_issue/<int:issue_id>/', views.delete_issue, name='delete_issue'),
    path('submit_issues/', views.submit_issues, name='submit_issues'),
     path('it_project/delete/<int:project_id>/', views.delete_project, name='delete_project'),

     path('it_project_detail/<int:project_id>/', views.it_project_detail, name='it_project_detail'),
    path('submit_issues/', views.submit_issues, name='submit_issues'), 
     
     path('export-excel/<int:project_id>/', views.export_excel, name='export_excel'),
     path('report-data-it/', views.report_data_it, name='report_data_it'),
     
]

from django.urls import path
from it_app import views

app_name ='it_app'

urlpatterns = [
    path('profile/', views.profile, name = 'profile'),
    path('dashboard/', views.dashboard, name = 'dashboard'),
    path('ticket/', views.ticket_index, name = 'ticket_index'),
    path('ticket/add/', views.ticket_add, name='ticket_add'),
    path('ticket/edit/<int:ticket_id>', views.ticket_edit, name='ticket_edit'),
    path('ticket/delete/<int:ticket_id>', views.ticket_delete, name='ticket_delete'),
    path('ticket/<int:ticket_id>', views.ticket_detail, name='ticket_detail'),
]

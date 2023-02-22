from django.urls import path
from it_app import views

app_name ='it_app'

urlpatterns = [
    path('profile/', views.profile, name = 'profile'),
    path('dashboard/', views.dashboard, name = 'dashboard'),
    path('ticket/', views.ticket_index, name = 'ticket_index'),
    path('ticket/<int:ticket_id>', views.ticket_by_id, name='ticket_by_id'),
]

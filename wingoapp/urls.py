from django.urls import path
from . import views
urlpatterns = [


    path('',views.starter_kit,name='starter_kit'),
    path('starter_kit',views.starter_kit,name='starter_kit'),

]
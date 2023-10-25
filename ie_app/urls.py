from django.urls import path
from ie_app import views
from django.conf.urls.static import static
from django.conf import settings

app_name ='ie_app'

urlpatterns = [
    path('', views.index, name = 'index'),
    path('improvementPlan/improvement_plan_index/', views.improvement_plan_index, name = 'improvement_plan_index'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

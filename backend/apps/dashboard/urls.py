from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/kpis', views.KPIView.as_view(), name='dashboard-kpis'),
]

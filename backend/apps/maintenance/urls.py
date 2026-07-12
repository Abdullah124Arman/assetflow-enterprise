from django.urls import path
from . import views

urlpatterns = [
    path('maintenance-requests', views.MaintenanceRequestListCreateView.as_view(), name='maintenance-requests-list-create'),
    path('maintenance-requests/<uuid:pk>', views.MaintenanceRequestActionView.as_view(), name='maintenance-request-action'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('reports/utilization', views.UtilizationReportView.as_view(), name='report-utilization'),
    path('reports/maintenance-frequency', views.MaintenanceFrequencyReportView.as_view(), name='report-maintenance-freq'),
    path('reports/idle-assets', views.IdleAssetsReportView.as_view(), name='report-idle-assets'),
    path('reports/retirement-watch', views.RetirementWatchReportView.as_view(), name='report-retirement-watch'),
    path('reports/allocation-summary', views.AllocationSummaryReportView.as_view(), name='report-allocation-summary'),
    path('reports/booking-heatmap', views.BookingHeatmapReportView.as_view(), name='report-booking-heatmap'),
]

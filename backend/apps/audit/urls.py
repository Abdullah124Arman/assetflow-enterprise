from django.urls import path
from .views import AuditCycleCreateView, AuditCycleAuditorsView, AuditItemUpdateView, AuditCycleCloseView

urlpatterns = [
    path('audit-cycles', AuditCycleCreateView.as_view(), name='audit_cycle_create'),
    path('audit-cycles/<uuid:pk>/auditors', AuditCycleAuditorsView.as_view(), name='audit_cycle_auditors'),
    path('audit-items/<uuid:pk>', AuditItemUpdateView.as_view(), name='audit_item_update'),
    path('audit-cycles/<uuid:pk>/close', AuditCycleCloseView.as_view(), name='audit_cycle_close'),
]

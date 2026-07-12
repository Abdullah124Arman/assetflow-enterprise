from django.urls import path
from .views import (
    AllocationCreateView, AllocationReturnView,
    TransferRequestListCreateView, TransferRequestActionView
)

urlpatterns = [
    path('allocations', AllocationCreateView.as_view(), name='allocation-create'),
    path('allocations/<uuid:pk>/return', AllocationReturnView.as_view(), name='allocation-return'),
    path('transfer-requests', TransferRequestListCreateView.as_view(), name='transfer-request-list-create'),
    path('transfer-requests/<uuid:pk>', TransferRequestActionView.as_view(), name='transfer-request-action'),
]

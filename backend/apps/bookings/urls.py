from django.urls import path
from .views import BookingListView, BookingDetailView

urlpatterns = [
    path('bookings', BookingListView.as_view(), name='booking-list'),
    path('bookings/<uuid:pk>', BookingDetailView.as_view(), name='booking-detail'),
]

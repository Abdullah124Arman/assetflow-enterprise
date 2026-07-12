from django.contrib import admin
from django.urls import path, include
from rest_framework.views import APIView
from rest_framework.response import Response

class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        return Response({'data': {'status': 'ok'}})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health', HealthCheckView.as_view(), name='health'),
    path('auth/', include('apps.auth.urls')),
    path('', include('apps.org.urls')),
    path('', include('apps.assets.urls')),
    path('', include('apps.allocations.urls')),
    path('', include('apps.bookings.urls')),
    path('', include('apps.maintenance.urls')),
    path('', include('apps.audit.urls')),
    path('', include('apps.dashboard.urls')),
    path('', include('apps.reports.urls')),
    path('', include('apps.notifications.urls')),
]

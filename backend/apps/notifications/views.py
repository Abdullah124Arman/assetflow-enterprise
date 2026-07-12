from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notification
from common.permissions import IsAuthenticated

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]
    schema_name = 'notification'

    def get(self, request):
        notif_type = request.query_params.get('type', 'all')
        
        queryset = Notification.objects.filter(user=request.user).order_by('-created_at')
        
        if notif_type != 'all':
            queryset = queryset.filter(type=notif_type)
            
        data = []
        for notif in queryset:
            data.append({
                'id': str(notif.id),
                'type': notif.type,
                'message': notif.message,
                'entity_type': notif.entity_type if notif.entity_type else '',
                'entity_id': str(notif.entity_id) if notif.entity_id else '',
                'read': notif.read,
                'created_at': notif.created_at.isoformat()
            })
            
        return Response({
            'data': {
                'notifications': {
                    'notification': data
                }
            }
        })

class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]
    schema_name = 'notification'

    def patch(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.read = True
        notification.save()
        
        return Response({
            'data': {
                'notification': {
                    'id': str(notification.id),
                    'read': notification.read
                }
            }
        })

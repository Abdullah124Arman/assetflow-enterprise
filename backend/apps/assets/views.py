from rest_framework import generics, views, status
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Max
from .models import AssetCategory, Asset
from apps.allocations.models import Allocation
from apps.maintenance.models import MaintenanceRequest
from .serializers import AssetCategorySerializer, AssetSerializer, AssetHistorySerializer
from common.permissions import IsAdminOrReadOnly, IsAdminOrAssetManagerOrReadOnly
from apps.org.views import log_activity
from common.exceptions import custom_exception_handler

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        category = serializer.save()
        log_activity(self.request.user, "category.create", "asset_category", category.id)

class CategoryDetailView(generics.RetrieveUpdateAPIView):
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_update(self, serializer):
        category = serializer.save()
        log_activity(self.request.user, "category.update", "asset_category", category.id)

class AssetListCreateView(generics.ListCreateAPIView):
    serializer_class = AssetSerializer
    permission_classes = [IsAdminOrAssetManagerOrReadOnly]

    def get_queryset(self):
        queryset = Asset.objects.all()
        user = self.request.user
        
        if user and user.is_authenticated and user.role in ['dept_head', 'employee']:
            queryset = queryset.filter(department_id=user.department_id)

        # GET /assets?tag=&serial=&qr=&category=&status=&department=&location=
        tag = self.request.query_params.get('tag')
        serial = self.request.query_params.get('serial')
        qr = self.request.query_params.get('qr')
        category = self.request.query_params.get('category')
        status_filter = self.request.query_params.get('status')
        department = self.request.query_params.get('department')
        location = self.request.query_params.get('location')

        if tag: queryset = queryset.filter(tag=tag)
        if serial: queryset = queryset.filter(serial_number=serial)
        if qr: queryset = queryset.filter(qr_code=qr)
        if category: queryset = queryset.filter(category_id=category)
        if status_filter: queryset = queryset.filter(status=status_filter)
        if department: queryset = queryset.filter(department_id=department)
        if location: queryset = queryset.filter(location=location)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if 'tag' in data:
            return Response({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'tag is immutable and server-generated',
                    'details': {}
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Generate AF-%04d
            # In a real system, we might use a sequence or lock a config table
            # Here, we do a simple MAX on existing tags
            max_tag = Asset.objects.aggregate(Max('tag'))['tag__max']
            if max_tag and max_tag.startswith('AF-'):
                try:
                    num = int(max_tag[3:])
                    new_tag = f"AF-{num+1:04d}"
                except ValueError:
                    new_tag = "AF-0001"
            else:
                new_tag = "AF-0001"
            
            data['tag'] = new_tag
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            asset = serializer.save()
            log_activity(request.user, "asset.create", "asset", asset.id)
            
            return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)

class AssetHistoryView(views.APIView):
    permission_classes = [IsAdminOrAssetManagerOrReadOnly]

    def get(self, request, pk):
        user = request.user
        if user and user.is_authenticated and user.role in ['dept_head', 'employee']:
            asset = generics.get_object_or_404(Asset.objects.filter(department_id=user.department_id), pk=pk)
        else:
            asset = generics.get_object_or_404(Asset, pk=pk)

        
        allocations = Allocation.objects.filter(asset=asset)
        maintenance = MaintenanceRequest.objects.filter(asset=asset)
        
        history = []
        for alloc in allocations:
            history.append({
                'id': alloc.id,
                'type': 'allocation',
                'date': alloc.allocated_date,
                'status': alloc.status,
                'details': {
                    'holder_type': alloc.holder_type,
                    'holder_id': alloc.holder_id
                }
            })
            
        for mr in maintenance:
            history.append({
                'id': mr.id,
                'type': 'maintenance',
                'date': mr.created_at,
                'status': mr.status,
                'details': {
                    'issue': mr.issue,
                    'priority': mr.priority
                }
            })
            
        # Merge and sort by date descending
        history.sort(key=lambda x: x['date'], reverse=True)
        
        serializer = AssetHistorySerializer(history, many=True)
        return Response({'data': {'history': serializer.data}})

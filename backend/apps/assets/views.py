from rest_framework import generics
from .models import AssetCategory
from .serializers import AssetCategorySerializer
from common.permissions import IsAdminOrReadOnly
from apps.org.views import log_activity

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

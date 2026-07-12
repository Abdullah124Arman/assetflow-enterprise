from django.urls import path
from .views import CategoryListCreateView, CategoryDetailView, AssetListCreateView, AssetHistoryView

urlpatterns = [
    path('categories', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<uuid:pk>', CategoryDetailView.as_view(), name='category-detail'),
    path('assets', AssetListCreateView.as_view(), name='asset-list-create'),
    path('assets/<uuid:pk>/history', AssetHistoryView.as_view(), name='asset-history'),
]

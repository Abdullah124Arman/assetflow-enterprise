from django.urls import path
from .views import DepartmentListCreateView, DepartmentDetailView, EmployeeListView, EmployeeRolePatchView

urlpatterns = [
    path('departments', DepartmentListCreateView.as_view(), name='department-list'),
    path('departments/<uuid:pk>', DepartmentDetailView.as_view(), name='department-detail'),
    path('employees', EmployeeListView.as_view(), name='employee-list'),
    path('employees/<uuid:pk>/role', EmployeeRolePatchView.as_view(), name='employee-role-patch'),
]

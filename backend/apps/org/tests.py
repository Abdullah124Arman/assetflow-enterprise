import pytest
from rest_framework.test import APIClient
from apps.auth.models import User
from apps.org.models import Department

@pytest.fixture
def client():
    return APIClient(HTTP_ACCEPT='application/xml', CONTENT_TYPE='application/xml')

@pytest.mark.django_db
def test_employee_department_scoping(client):
    dept1 = Department.objects.create(name="Dept 1", status="active")
    dept2 = Department.objects.create(name="Dept 2", status="active")
    
    user1 = User.objects.create_user(email="user1@test.com", name="User 1", password="pw", role="employee", department=dept1)
    user2 = User.objects.create_user(email="user2@test.com", name="User 2", password="pw", role="employee", department=dept2)
    
    # Authenticate as user1
    client.force_authenticate(user=user1)
    
    # Check departments
    response = client.get('/departments')
    assert response.status_code == 200
    assert b'Dept 1' in response.content
    assert b'Dept 2' not in response.content # Scoped to their own department
    
    # Check employees
    response = client.get('/employees')
    assert response.status_code == 200
    assert b'user1@test.com' in response.content
    assert b'user2@test.com' not in response.content

@pytest.mark.django_db
def test_admin_role_patch(client):
    dept = Department.objects.create(name="Admin Dept", status="active")
    admin_user = User.objects.create_superuser(email="admin@test.com", name="Admin", password="pw", department=dept)
    target_user = User.objects.create_user(email="target@test.com", name="Target", password="pw", role="employee", department=dept)
    
    client.force_authenticate(user=admin_user)
    
    xml_data = """
    <employee>
      <role>dept_head</role>
    </employee>
    """
    response = client.patch(f'/employees/{target_user.id}/role', data=xml_data, content_type='application/xml')
    assert response.status_code == 200
    
    target_user.refresh_from_db()
    assert target_user.role == 'dept_head'

import pytest
from rest_framework.test import APIClient
from apps.auth.models import User
from apps.org.models import Department

@pytest.fixture
def client():
    return APIClient(HTTP_ACCEPT='application/xml', CONTENT_TYPE='application/xml')

@pytest.fixture
def department():
    return Department.objects.create(name="Engineering", status="active")

@pytest.mark.django_db
def test_signup_creates_employee(client, department):
    xml_data = f"""
    <auth_request>
      <name>Test User</name>
      <email>test@example.com</email>
      <password>SecurePass123!</password>
      <department_id>{department.id}</department_id>
      <role>admin</role> <!-- This should be ignored -->
    </auth_request>
    """
    response = client.post('/auth/signup', data=xml_data, content_type='application/xml')
    assert response.status_code == 200
    
    user = User.objects.get(email="test@example.com")
    assert user.role == 'employee' # Role must be hardcoded
    assert user.name == 'Test User'

@pytest.mark.django_db
def test_login_returns_token(client):
    User.objects.create_user(email="test2@example.com", name="Test 2", password="password123", role="employee")
    
    xml_data = """
    <auth_request>
      <email>test2@example.com</email>
      <password>password123</password>
    </auth_request>
    """
    response = client.post('/auth/login', data=xml_data, content_type='application/xml')
    assert response.status_code == 200
    assert b'<access_token>' in response.content
    assert b'<refresh_token>' in response.content

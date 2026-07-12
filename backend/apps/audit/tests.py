import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from apps.audit.models import AuditCycle, AuditAuditor, AuditItem, AuditDiscrepancyReport, AuditCycleStatus
from apps.assets.models import Asset, AssetCategory
from apps.org.models import Department
from apps.auth.models import User
from django.utils import timezone
import datetime

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db):
    user = User.objects.create(email="admin@example.com", name="Admin", role="admin", password="hash")
    return user

@pytest.fixture
def auditor_user(db):
    user = User.objects.create(email="auditor@example.com", name="Auditor", role="employee", password="hash")
    return user

@pytest.fixture
def other_user(db):
    user = User.objects.create(email="other@example.com", name="Other", role="employee", password="hash")
    return user

@pytest.fixture
def category(db):
    return AssetCategory.objects.create(name="Laptop")

@pytest.fixture
def department(db, admin_user):
    return Department.objects.create(name="Engineering", head=admin_user)

@pytest.fixture
def assets(db, category, department):
    asset1 = Asset.objects.create(tag="AF-0001", name="Dell XPS", category=category, department=department, location="HQ")
    asset2 = Asset.objects.create(tag="AF-0002", name="MacBook Pro", category=category, department=department, location="HQ")
    asset3 = Asset.objects.create(tag="AF-0003", name="ThinkPad", category=category, department=department, location="Branch")
    return [asset1, asset2, asset3]

@pytest.mark.django_db
def test_create_audit_cycle(api_client, admin_user, department, assets):
    api_client.force_authenticate(user=admin_user)
    xml_data = f"""
    <audit_cycle>
      <name>Q3 Audit</name>
      <scope_department_id>{department.id}</scope_department_id>
      <start_date>2026-07-01</start_date>
      <end_date>2026-07-31</end_date>
    </audit_cycle>
    """
    response = api_client.post(reverse('audit_cycle_create'), data=xml_data, content_type='application/xml')
    assert response.status_code == status.HTTP_201_CREATED
    
    cycle = AuditCycle.objects.get(name="Q3 Audit")
    items = AuditItem.objects.filter(audit_cycle=cycle)
    # 3 assets in total, all belong to the department
    assert items.count() == 3

@pytest.mark.django_db
def test_assign_auditor(api_client, admin_user, auditor_user, department):
    api_client.force_authenticate(user=admin_user)
    cycle = AuditCycle.objects.create(name="Q3 Audit", scope_department=department, start_date="2026-07-01", end_date="2026-07-31", created_by=admin_user)
    
    xml_data = f"""
    <audit_cycle_auditors>
      <user_ids>
        <user_id>{auditor_user.id}</user_id>
      </user_ids>
    </audit_cycle_auditors>
    """
    response = api_client.post(reverse('audit_cycle_auditors', kwargs={'pk': cycle.id}), data=xml_data, content_type='application/xml')
    assert response.status_code == status.HTTP_200_OK
    assert AuditAuditor.objects.filter(audit_cycle=cycle, user=auditor_user).exists()

@pytest.mark.django_db
def test_update_audit_item_permission(api_client, admin_user, auditor_user, other_user, department, assets):
    cycle = AuditCycle.objects.create(name="Q3 Audit", scope_department=department, start_date="2026-07-01", end_date="2026-07-31", created_by=admin_user)
    AuditAuditor.objects.create(audit_cycle=cycle, user=auditor_user)
    item = AuditItem.objects.create(audit_cycle=cycle, asset=assets[0])

    xml_data = """
    <audit_item>
      <verification>verified</verification>
    </audit_item>
    """
    
    # other user should fail
    api_client.force_authenticate(user=other_user)
    response = api_client.patch(reverse('audit_item_update', kwargs={'pk': item.id}), data=xml_data, content_type='application/xml')
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # assigned auditor should succeed
    api_client.force_authenticate(user=auditor_user)
    response = api_client.patch(reverse('audit_item_update', kwargs={'pk': item.id}), data=xml_data, content_type='application/xml')
    assert response.status_code == status.HTTP_200_OK
    item.refresh_from_db()
    assert item.verification == "verified"

@pytest.mark.django_db
def test_close_audit_cycle(api_client, admin_user, department, assets):
    cycle = AuditCycle.objects.create(name="Q3 Audit", scope_department=department, start_date="2026-07-01", end_date="2026-07-31", created_by=admin_user)
    item1 = AuditItem.objects.create(audit_cycle=cycle, asset=assets[0], verification="verified")
    item2 = AuditItem.objects.create(audit_cycle=cycle, asset=assets[1], verification="missing")
    item3 = AuditItem.objects.create(audit_cycle=cycle, asset=assets[2], verification="damaged")

    api_client.force_authenticate(user=admin_user)
    response = api_client.post(reverse('audit_cycle_close', kwargs={'pk': cycle.id}))
    assert response.status_code == status.HTTP_200_OK
    
    cycle.refresh_from_db()
    assert cycle.status == AuditCycleStatus.CLOSED

    assets[1].refresh_from_db()
    assert assets[1].status == "lost"

    reports = AuditDiscrepancyReport.objects.filter(audit_cycle=cycle)
    assert reports.count() == 1
    assert "missing_items" in reports[0].report_json
    assert "damaged_items" in reports[0].report_json


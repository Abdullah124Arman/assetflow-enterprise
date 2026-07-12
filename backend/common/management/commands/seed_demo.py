"""
Seed demo data for AssetFlow Enterprise - Management Command
Creates a full cross-role demo dataset with:
  - 2 departments (Engineering, Operations)
  - 5 users: 1 admin, 1 asset_manager, 1 dept_head, 2 employees (across 2 depts)
  - 3 asset categories (IT Equipment, Office Furniture, Meeting Rooms)
  - ~15 assets: mix of available, allocated, under_maintenance, bookable
  - Active allocations (to demo the double-allocation 409 block)
  - 1 active booking on a bookable resource (to demo the overlap 409 block)
  - Maintenance requests in each kanban column
  - 1 open audit cycle with some items pre-verified
"""
import uuid
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection


class Command(BaseCommand):
    help = 'Seed database with demo data for AssetFlow Enterprise smoke testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        # Import models here to avoid AppRegistryNotReady
        from apps.auth.models import User
        from apps.org.models import Department, ActivityLog
        from apps.assets.models import AssetCategory, Asset
        from apps.allocations.models import Allocation, TransferRequest
        from apps.bookings.models import Booking
        from apps.maintenance.models import MaintenanceRequest
        from apps.audit.models import AuditCycle, AuditAuditor, AuditItem
        from apps.notifications.models import Notification

        if options['flush']:
            self.stdout.write(self.style.WARNING('Flushing existing data...'))
            # Delete in FK-safe order
            Notification.objects.all().delete()
            ActivityLog.objects.all().delete()
            AuditItem.objects.all().delete()
            AuditAuditor.objects.all().delete()
            AuditCycle.objects.all().delete()
            MaintenanceRequest.objects.all().delete()
            Booking.objects.all().delete()
            TransferRequest.objects.all().delete()
            Allocation.objects.all().delete()
            Asset.objects.all().delete()
            AssetCategory.objects.all().delete()
            # Unset head_id before deleting users/departments
            Department.objects.all().update(head=None)
            User.objects.all().delete()
            Department.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Flushed.'))

        now = timezone.now()

        # ──────────────────────────────────────────────
        # 1. DEPARTMENTS
        # ──────────────────────────────────────────────
        self.stdout.write('Creating departments...')
        dept_eng = Department.objects.create(
            name='Engineering',
            status='active',
        )
        dept_ops = Department.objects.create(
            name='Operations',
            status='active',
        )
        self.stdout.write(f'  ✓ Engineering  id={dept_eng.id}')
        self.stdout.write(f'  ✓ Operations   id={dept_ops.id}')

        # ──────────────────────────────────────────────
        # 2. USERS (5 total, 4 roles)
        # ──────────────────────────────────────────────
        self.stdout.write('Creating users...')
        admin = User.objects.create_user(
            email='admin@assetflow.demo',
            name='Arun Kumar',
            password='Demo@1234',
            role='admin',
            department=dept_eng,
        )
        asset_mgr = User.objects.create_user(
            email='manager@assetflow.demo',
            name='Neha Gupta',
            password='Demo@1234',
            role='asset_manager',
            department=dept_eng,
        )
        dept_head = User.objects.create_user(
            email='depthead@assetflow.demo',
            name='Ravi Sharma',
            password='Demo@1234',
            role='dept_head',
            department=dept_ops,
        )
        emp1 = User.objects.create_user(
            email='employee1@assetflow.demo',
            name='Priya Shah',
            password='Demo@1234',
            role='employee',
            department=dept_eng,
        )
        emp2 = User.objects.create_user(
            email='employee2@assetflow.demo',
            name='Vikram Patel',
            password='Demo@1234',
            role='employee',
            department=dept_ops,
        )
        self.stdout.write(f'  ✓ admin        {admin.email}  id={admin.id}')
        self.stdout.write(f'  ✓ asset_mgr    {asset_mgr.email}  id={asset_mgr.id}')
        self.stdout.write(f'  ✓ dept_head    {dept_head.email}  id={dept_head.id}')
        self.stdout.write(f'  ✓ employee1    {emp1.email}  id={emp1.id}')
        self.stdout.write(f'  ✓ employee2    {emp2.email}  id={emp2.id}')

        # Assign department heads
        dept_eng.head = admin  # admin heads Engineering
        dept_eng.save()
        dept_ops.head = dept_head  # dept_head heads Operations
        dept_ops.save()

        # ──────────────────────────────────────────────
        # 3. ASSET CATEGORIES
        # ──────────────────────────────────────────────
        self.stdout.write('Creating asset categories...')
        cat_it = AssetCategory.objects.create(
            name='IT Equipment',
            custom_fields=[
                {'key': 'warranty_period', 'label': 'Warranty Period (months)', 'type': 'number', 'required': True},
                {'key': 'os_version', 'label': 'OS Version', 'type': 'string', 'required': False},
            ]
        )
        cat_furniture = AssetCategory.objects.create(
            name='Office Furniture',
            custom_fields=[
                {'key': 'material', 'label': 'Material', 'type': 'string', 'required': False},
            ]
        )
        cat_rooms = AssetCategory.objects.create(
            name='Meeting Rooms',
            custom_fields=[
                {'key': 'capacity', 'label': 'Capacity', 'type': 'number', 'required': True},
                {'key': 'has_projector', 'label': 'Has Projector', 'type': 'boolean', 'required': False},
            ]
        )
        self.stdout.write(f'  ✓ IT Equipment      id={cat_it.id}')
        self.stdout.write(f'  ✓ Office Furniture  id={cat_furniture.id}')
        self.stdout.write(f'  ✓ Meeting Rooms     id={cat_rooms.id}')

        # ──────────────────────────────────────────────
        # 4. ASSETS (~15 total)
        # ──────────────────────────────────────────────
        self.stdout.write('Creating assets...')

        # IT Equipment (6 assets) — Engineering dept
        laptops_and_it = []
        for i, (name, sn, cost, cond, loc, stat, bookable) in enumerate([
            ('Dell Latitude 5540',     'DL5540-001', Decimal('85000.00'),  'Good',     'HQ Floor 2',  'available',          False),
            ('Dell Latitude 5540 #2',  'DL5540-002', Decimal('85000.00'),  'Good',     'HQ Floor 2',  'allocated',          False),
            ('MacBook Pro 14"',        'MBP14-001',  Decimal('189999.00'), 'Excellent','HQ Floor 3',  'available',          False),
            ('HP LaserJet Pro',        'HPLJ-001',   Decimal('32000.00'),  'Good',     'HQ Floor 1',  'under_maintenance',  False),
            ('Cisco IP Phone 8841',    'CIP-001',    Decimal('12500.00'),  'Fair',     'HQ Floor 2',  'available',          False),
            ('Samsung Monitor 27"',    'SM27-001',   Decimal('24000.00'),  'Good',     'HQ Floor 2',  'allocated',          False),
        ], start=1):
            asset = Asset.objects.create(
                tag=f'AF-{i:04d}',
                name=name,
                category=cat_it,
                serial_number=sn,
                acquisition_date=date.today() - timedelta(days=180 + i * 30),
                acquisition_cost=cost,
                condition=cond,
                location=loc,
                status=stat,
                is_bookable=bookable,
                department=dept_eng,
                custom_field_values={'warranty_period': 36, 'os_version': 'N/A'},
            )
            laptops_and_it.append(asset)
            self.stdout.write(f'  ✓ {asset.tag} {name} [{stat}]')

        # Office Furniture (4 assets) — Operations dept
        furniture_assets = []
        for i, (name, cost, stat) in enumerate([
            ('Ergonomic Standing Desk',  Decimal('45000.00'), 'available'),
            ('Herman Miller Chair',      Decimal('78000.00'), 'allocated'),
            ('Filing Cabinet 4-Drawer',  Decimal('12000.00'), 'available'),
            ('Whiteboard 6x4 ft',        Decimal('8500.00'),  'available'),
        ], start=7):
            asset = Asset.objects.create(
                tag=f'AF-{i:04d}',
                name=name,
                category=cat_furniture,
                acquisition_date=date.today() - timedelta(days=365 + i * 15),
                acquisition_cost=cost,
                condition='Good',
                location='HQ Floor 1',
                status=stat,
                is_bookable=False,
                department=dept_ops,
                custom_field_values={'material': 'Mixed'},
            )
            furniture_assets.append(asset)
            self.stdout.write(f'  ✓ {asset.tag} {name} [{stat}]')

        # Meeting Rooms (3 assets — BOOKABLE) — shared
        room_assets = []
        for i, (name, loc, dept, capacity) in enumerate([
            ('Boardroom Alpha',   'HQ Floor 3', dept_eng, 20),
            ('Huddle Room Beta',  'HQ Floor 2', dept_eng, 6),
            ('Training Hall',     'HQ Floor 1', dept_ops, 40),
        ], start=11):
            asset = Asset.objects.create(
                tag=f'AF-{i:04d}',
                name=name,
                category=cat_rooms,
                acquisition_date=date.today() - timedelta(days=730),
                acquisition_cost=Decimal('0.00'),
                condition='Good',
                location=loc,
                status='available',
                is_bookable=True,
                department=dept,
                custom_field_values={'capacity': capacity, 'has_projector': True},
            )
            room_assets.append(asset)
            self.stdout.write(f'  ✓ {asset.tag} {name} [bookable]')

        # 2 more assets for variety — retired and lost
        retired_asset = Asset.objects.create(
            tag='AF-0014',
            name='Old HP ProBook',
            category=cat_it,
            serial_number='HPPB-OLD-001',
            acquisition_date=date.today() - timedelta(days=1800),
            acquisition_cost=Decimal('55000.00'),
            condition='Poor',
            location='Storage B2',
            status='retired',
            is_bookable=False,
            department=dept_eng,
            custom_field_values={'warranty_period': 12},
        )
        self.stdout.write(f'  ✓ {retired_asset.tag} Old HP ProBook [retired]')

        lost_asset = Asset.objects.create(
            tag='AF-0015',
            name='Logitech Webcam C920',
            category=cat_it,
            serial_number='LWBC920-003',
            acquisition_date=date.today() - timedelta(days=400),
            acquisition_cost=Decimal('7500.00'),
            condition='Unknown',
            location='Unknown',
            status='lost',
            is_bookable=False,
            department=dept_ops,
            custom_field_values={'warranty_period': 24},
        )
        self.stdout.write(f'  ✓ {lost_asset.tag} Logitech Webcam C920 [lost]')

        # ──────────────────────────────────────────────
        # 5. ALLOCATIONS (for assets marked 'allocated')
        # ──────────────────────────────────────────────
        self.stdout.write('Creating allocations...')

        # Dell Laptop #2 (AF-0002) → Priya Shah (employee1, Engineering)
        alloc_dell2 = Allocation.objects.create(
            asset=laptops_and_it[1],  # AF-0002 - Dell Latitude 5540 #2
            holder_type='employee',
            holder_id=emp1.id,
            expected_return_date=date.today() + timedelta(days=90),
        )
        # Force allocated_date since auto_now_add
        Allocation.objects.filter(id=alloc_dell2.id).update(allocated_date=date.today() - timedelta(days=30))
        self.stdout.write(f'  ✓ AF-0002 → Priya Shah (active)')

        # Samsung Monitor (AF-0006) → Vikram Patel (employee2, Operations)
        alloc_monitor = Allocation.objects.create(
            asset=laptops_and_it[5],  # AF-0006 - Samsung Monitor
            holder_type='employee',
            holder_id=emp2.id,
            expected_return_date=date.today() + timedelta(days=60),
        )
        Allocation.objects.filter(id=alloc_monitor.id).update(allocated_date=date.today() - timedelta(days=15))
        self.stdout.write(f'  ✓ AF-0006 → Vikram Patel (active)')

        # Herman Miller Chair (AF-0008) → Operations dept (dept allocation)
        alloc_chair = Allocation.objects.create(
            asset=furniture_assets[1],  # AF-0008 - Herman Miller Chair
            holder_type='department',
            holder_id=dept_ops.id,
            expected_return_date=None,  # permanent allocation
        )
        Allocation.objects.filter(id=alloc_chair.id).update(allocated_date=date.today() - timedelta(days=60))
        self.stdout.write(f'  ✓ AF-0008 → Operations Dept (active, permanent)')

        # ──────────────────────────────────────────────
        # 6. BOOKINGS (1 active booking to demo overlap block)
        # ──────────────────────────────────────────────
        self.stdout.write('Creating bookings...')

        # Booking on Boardroom Alpha (AF-0011) — tomorrow 10:00-11:00
        tomorrow = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        booking_alpha = Booking.objects.create(
            resource_asset=room_assets[0],  # AF-0011 - Boardroom Alpha
            booked_by=emp1,
            start_time=tomorrow,
            end_time=tomorrow + timedelta(hours=1),
            status='upcoming',
            purpose='Sprint Planning - Q3 Review',
        )
        self.stdout.write(f'  ✓ Boardroom Alpha: {booking_alpha.start_time} → {booking_alpha.end_time} (Priya)')

        # A past completed booking for history
        past = (now - timedelta(days=2)).replace(hour=14, minute=0, second=0, microsecond=0)
        Booking.objects.create(
            resource_asset=room_assets[1],  # AF-0012 - Huddle Room Beta
            booked_by=asset_mgr,
            start_time=past,
            end_time=past + timedelta(hours=1),
            status='completed',
            purpose='Asset inventory sync',
        )
        self.stdout.write(f'  ✓ Huddle Room Beta: completed past booking (Neha)')

        # ──────────────────────────────────────────────
        # 7. MAINTENANCE REQUESTS (1 per kanban column)
        # ──────────────────────────────────────────────
        self.stdout.write('Creating maintenance requests...')

        # Column 1: Pending
        mr_pending = MaintenanceRequest.objects.create(
            asset=laptops_and_it[4],  # AF-0005 - Cisco IP Phone
            raised_by=emp1,
            issue='Phone display flickering intermittently, cannot read caller ID',
            priority='medium',
            status='pending',
        )
        self.stdout.write(f'  ✓ Pending: Cisco IP Phone (raised by Priya)')

        # Column 2: Approved (asset AF-0004 is already under_maintenance)
        mr_approved = MaintenanceRequest.objects.create(
            asset=laptops_and_it[3],  # AF-0004 - HP LaserJet Pro
            raised_by=emp2,
            issue='Paper jam sensor malfunction, prints only blank pages',
            priority='high',
            status='approved',
            approved_by=asset_mgr,
        )
        self.stdout.write(f'  ✓ Approved: HP LaserJet Pro (approved by Neha)')

        # Column 3: Technician Assigned
        mr_assigned = MaintenanceRequest.objects.create(
            asset=furniture_assets[3],  # AF-0010 - Whiteboard
            raised_by=dept_head,
            issue='Whiteboard surface is stained, markers no longer erase properly',
            priority='low',
            status='technician_assigned',
            approved_by=admin,
            technician_name='Rajesh Kumar (Facilities)',
        )
        self.stdout.write(f'  ✓ Tech Assigned: Whiteboard (technician: Rajesh)')

        # Column 4: In Progress (create one more for variety)
        mr_in_progress = MaintenanceRequest.objects.create(
            asset=laptops_and_it[0],  # AF-0001 - Dell Latitude
            raised_by=emp1,
            issue='Battery draining within 2 hours, needs replacement',
            priority='high',
            status='in_progress',
            approved_by=asset_mgr,
            technician_name='Dell Service Center',
        )
        # Keep AF-0001 as available for demo (battery replacement doesn't require status change in seed)
        self.stdout.write(f'  ✓ In Progress: Dell Latitude battery (Dell Service Center)')

        # Column 5: Resolved (historical)
        mr_resolved = MaintenanceRequest.objects.create(
            asset=laptops_and_it[2],  # AF-0003 - MacBook Pro
            raised_by=asset_mgr,
            issue='Screen replaced under AppleCare warranty',
            priority='medium',
            status='resolved',
            approved_by=admin,
            technician_name='Apple Authorized Service',
            resolved_at=now - timedelta(days=7),
        )
        self.stdout.write(f'  ✓ Resolved: MacBook Pro screen (historical)')

        # ──────────────────────────────────────────────
        # 8. AUDIT CYCLE (1 open, with pre-verified items)
        # ──────────────────────────────────────────────
        self.stdout.write('Creating audit cycle...')

        audit_cycle = AuditCycle.objects.create(
            name='Q3 2026 Asset Verification — Engineering',
            scope_department=dept_eng,
            start_date=date.today() - timedelta(days=3),
            end_date=date.today() + timedelta(days=14),
            status='open',
            created_by=admin,
        )
        self.stdout.write(f'  ✓ Audit cycle: {audit_cycle.name}')

        # Assign auditors: asset_mgr and emp1
        AuditAuditor.objects.create(audit_cycle=audit_cycle, user=asset_mgr)
        AuditAuditor.objects.create(audit_cycle=audit_cycle, user=emp1)
        self.stdout.write(f'  ✓ Auditors: Neha Gupta, Priya Shah')

        # Create audit items for Engineering dept assets
        eng_assets = Asset.objects.filter(department=dept_eng)
        audit_items = []
        for asset in eng_assets:
            item = AuditItem.objects.create(
                audit_cycle=audit_cycle,
                asset=asset,
                verification='pending',
            )
            audit_items.append(item)

        # Pre-verify a couple of items
        if len(audit_items) >= 3:
            # Verify AF-0001 (Dell Latitude)
            audit_items[0].verification = 'verified'
            audit_items[0].verified_by = asset_mgr
            audit_items[0].verified_at = now - timedelta(hours=6)
            audit_items[0].notes = 'Physically verified at desk E2-14'
            audit_items[0].save()
            self.stdout.write(f'  ✓ Verified: {audit_items[0].asset.tag}')

            # Verify AF-0002 (Dell Laptop #2)
            audit_items[1].verification = 'verified'
            audit_items[1].verified_by = emp1
            audit_items[1].verified_at = now - timedelta(hours=4)
            audit_items[1].notes = 'Confirmed with Priya Shah, asset in use'
            audit_items[1].save()
            self.stdout.write(f'  ✓ Verified: {audit_items[1].asset.tag}')

            # Mark one as damaged
            if len(audit_items) >= 4:
                audit_items[3].verification = 'damaged'
                audit_items[3].verified_by = asset_mgr
                audit_items[3].verified_at = now - timedelta(hours=2)
                audit_items[3].notes = 'Printer toner leaking, paper tray broken'
                audit_items[3].save()
                self.stdout.write(f'  ✓ Damaged: {audit_items[3].asset.tag}')

        # ──────────────────────────────────────────────
        # 9. ACTIVITY LOGS (seed a few for dashboard)
        # ──────────────────────────────────────────────
        self.stdout.write('Creating activity logs...')
        activities = [
            (admin, 'department.create', 'department', dept_eng.id),
            (admin, 'department.create', 'department', dept_ops.id),
            (asset_mgr, 'asset.register', 'asset', laptops_and_it[0].id),
            (asset_mgr, 'asset.allocate', 'asset', laptops_and_it[1].id),
            (emp1, 'booking.create', 'booking', booking_alpha.id),
            (emp1, 'maintenance_request.create', 'maintenance_request', mr_pending.id),
            (asset_mgr, 'maintenance_request.approve', 'maintenance_request', mr_approved.id),
            (admin, 'audit_cycle.create', 'audit_cycle', audit_cycle.id),
        ]
        for user, action, entity_type, entity_id in activities:
            ActivityLog.objects.create(
                user=user,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
            )
        self.stdout.write(f'  ✓ {len(activities)} activity log entries')

        # ──────────────────────────────────────────────
        # 10. NOTIFICATIONS (seed a few)
        # ──────────────────────────────────────────────
        self.stdout.write('Creating notifications...')
        notifications = [
            (emp1, 'asset_assigned', 'Dell Latitude 5540 #2 has been allocated to you', 'asset', laptops_and_it[1].id),
            (emp2, 'asset_assigned', 'Samsung Monitor 27" has been allocated to you', 'asset', laptops_and_it[5].id),
            (emp1, 'booking_confirmed', f'Boardroom Alpha booked for {booking_alpha.start_time.strftime("%b %d %H:%M")}', 'booking', booking_alpha.id),
            (asset_mgr, 'maintenance_raised', 'New maintenance request: Cisco IP Phone display flickering', 'maintenance_request', mr_pending.id),
            (admin, 'audit_started', f'Audit cycle "{audit_cycle.name}" has been created', 'audit_cycle', audit_cycle.id),
            (asset_mgr, 'audit_assignment', 'You have been assigned as auditor for Q3 2026 audit', 'audit_cycle', audit_cycle.id),
            (emp1, 'audit_assignment', 'You have been assigned as auditor for Q3 2026 audit', 'audit_cycle', audit_cycle.id),
        ]
        for user, ntype, msg, entity_type, entity_id in notifications:
            Notification.objects.create(
                user=user,
                type=ntype,
                message=msg,
                entity_type=entity_type,
                entity_id=entity_id,
            )
        self.stdout.write(f'  ✓ {len(notifications)} notifications')

        # ──────────────────────────────────────────────
        # SUMMARY
        # ──────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('═══════════════════════════════════════════════'))
        self.stdout.write(self.style.SUCCESS('  DEMO DATA SEEDED SUCCESSFULLY'))
        self.stdout.write(self.style.SUCCESS('═══════════════════════════════════════════════'))
        self.stdout.write('')
        self.stdout.write('  Login credentials (all passwords: Demo@1234):')
        self.stdout.write(f'    Admin:         admin@assetflow.demo')
        self.stdout.write(f'    Asset Manager: manager@assetflow.demo')
        self.stdout.write(f'    Dept Head:     depthead@assetflow.demo')
        self.stdout.write(f'    Employee 1:    employee1@assetflow.demo')
        self.stdout.write(f'    Employee 2:    employee2@assetflow.demo')
        self.stdout.write('')
        self.stdout.write('  Hard-block demo targets:')
        self.stdout.write(f'    Double-alloc test: Try allocating AF-0002 (already → Priya Shah)')
        self.stdout.write(f'    Overlap test:      Book Boardroom Alpha (AF-0011) at {booking_alpha.start_time.strftime("%H:%M")}-{booking_alpha.end_time.strftime("%H:%M")} tomorrow')
        self.stdout.write(f'    Back-to-back OK:   Book AF-0011 at {booking_alpha.end_time.strftime("%H:%M")}-{(booking_alpha.end_time + timedelta(hours=1)).strftime("%H:%M")} tomorrow')
        self.stdout.write('')
        self.stdout.write(f'  Audit cycle ID: {audit_cycle.id}')
        self.stdout.write(f'  Boardroom booking ID: {booking_alpha.id}')
        self.stdout.write(f'  Allocated asset IDs: AF-0002, AF-0006, AF-0008')
        self.stdout.write('')

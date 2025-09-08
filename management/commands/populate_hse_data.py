from django.core.management.base import BaseCommand
from inspection_management.models.business_unit import BusinessUnit
from inspection_management.models.site import Site
from inspection_management.models.company import Company
from inspection_management.models.data_group import DataGroup
from users.models.user import User
from inspection_management.models.hse_workflow_models import HSEObservation
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Populate HSE workflow data with test data'

    def handle(self, *args, **options):
        self.stdout.write('Creating HSE workflow test data...')
        
        # Ensure business units exist
        business_unit = self.ensure_business_units()
        
        # Create test users with proper roles
        self.create_test_users()
        
        # Create test observations
        self.create_test_observations(business_unit)
        
        self.stdout.write(self.style.SUCCESS('Successfully created HSE workflow test data!'))

    def create_test_users(self):
        """Create test users with different roles"""
        # Create Admin user
        admin_user, created = User.objects.get_or_create(
            username='admin_user',
            defaults={
                'email': 'admin@test.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'password': make_password('admin123'),
                'role': 'ADMIN',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created admin user: {admin_user.username}')

        # Create Manager user
        manager_user, created = User.objects.get_or_create(
            username='manager_user',
            defaults={
                'email': 'manager@test.com',
                'first_name': 'Manager',
                'last_name': 'User',
                'password': make_password('manager123'),
                'role': 'MANAGER',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created manager user: {manager_user.username}')

        # Create Inspector user
        inspector_user, created = User.objects.get_or_create(
            username='inspector_user',
            defaults={
                'email': 'inspector@test.com',
                'first_name': 'Inspector',
                'last_name': 'User',
                'password': make_password('inspector123'),
                'role': 'INSPECTOR',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created inspector user: {inspector_user.username}')

    def create_test_observations(self, business_unit):
        """Create test observations with proper workflow states"""
        # Get test users
        admin_user = User.objects.filter(role='ADMIN').first()
        manager_user = User.objects.filter(role='MANAGER').first()
        inspector_user = User.objects.filter(role='INSPECTOR').first()

        # Create test observations with different workflow states
        test_observations = [
            {
                'title': 'Safety Equipment Check',
                'description': 'Regular safety equipment inspection needed',
                'risk_level': 'MEDIUM',
                'risk_category': 'Safety',
                'workflow_state': 'DRAFT',
                'created_by': admin_user,
                'affected_department': business_unit
            },
            {
                'title': 'Fire Safety Audit',
                'description': 'Comprehensive fire safety audit required',
                'risk_level': 'HIGH',
                'risk_category': 'Safety',
                'workflow_state': 'PENDING_VALIDATION',
                'created_by': admin_user,
                'validated_by': manager_user,
                'affected_department': business_unit
            },
            {
                'title': 'Environmental Compliance Check',
                'description': 'Environmental compliance verification needed',
                'risk_level': 'CRITICAL',
                'risk_category': 'Environmental',
                'workflow_state': 'ASSIGNED',
                'created_by': admin_user,
                'validated_by': manager_user,
                'assigned_to': inspector_user,
                'affected_department': business_unit
            },
            {
                'title': 'Health Protocol Review',
                'description': 'Health and safety protocol review',
                'risk_level': 'LOW',
                'risk_category': 'Health',
                'workflow_state': 'IN_PROGRESS',
                'created_by': admin_user,
                'validated_by': manager_user,
                'assigned_to': inspector_user,
                'affected_department': business_unit
            }
        ]

        for obs_data in test_observations:
            observation, created = HSEObservation.objects.get_or_create(
                title=obs_data['title'],
                defaults=obs_data
            )
            if created:
                self.stdout.write(f'Created observation: {observation.title} (Status: {observation.workflow_state})')

    def ensure_business_units(self):
        """Ensure business units exist"""
        # Get first user for changed_by field
        user = User.objects.first()
        if not user:
            # Create a default user if none exists
            user = User.objects.create(
                username='default_user',
                email='default@test.com',
                first_name='Default',
                last_name='User',
                password=make_password('default123'),
                is_active=True
            )
            self.stdout.write(f'Created default user: {user.username}')

        # Create company if it doesn't exist
        company, created = Company.objects.get_or_create(
            name='Test Company',
            defaults={'description': 'Test company for HSE workflow'}
        )
        if created:
            self.stdout.write(f'Created company: {company.name}')

        # Create site if it doesn't exist
        site, created = Site.objects.get_or_create(
            name='Test Site',
            company=company,
            defaults={'description': 'Test site for HSE workflow'}
        )
        if created:
            self.stdout.write(f'Created site: {site.name}')

        # Create data group if it doesn't exist
        data_group, created = DataGroup.objects.get_or_create(
            name='Test Data Group',
            defaults={'description': 'Test data group for HSE workflow'}
        )
        if created:
            self.stdout.write(f'Created data group: {data_group.name}')

        # Create business unit if it doesn't exist
        business_unit, created = BusinessUnit.objects.get_or_create(
            name='Test Department',
            site=site,
            data_group=data_group,
            defaults={'description': 'Test department for HSE workflow'}
        )
        if created:
            self.stdout.write(f'Created business unit: {business_unit.name}')

        return business_unit


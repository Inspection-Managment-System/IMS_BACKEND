#!/usr/bin/env python
"""
Simple script to set up test data for HSE workflow
Run this with: python setup_test_data.py
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ims_backend.settings')
django.setup()

from inspection_management.models.business_unit import BusinessUnit
from inspection_management.models.site import Site
from inspection_management.models.company import Company
from inspection_management.models.datagroup import DataGroup
from users.models.user import User
from users.models.userprofile import UserProfile
from inspection_management.models.hse_workflow_models import HSEObservation
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group

def setup_test_data():
    print("Setting up HSE workflow test data...")
    
    # Ensure business units exist
    business_unit = ensure_business_units()
    
    # Create test users with proper roles
    create_test_users()
    
    # Create test observations
    create_test_observations(business_unit)
    
    print("Successfully set up HSE workflow test data!")

def create_test_users():
    """Create test users with different roles"""
    # Create groups for roles
    admin_group, created = Group.objects.get_or_create(name='ADMIN')
    if created:
        print(f'Created admin group')
    
    manager_group, created = Group.objects.get_or_create(name='MANAGER')
    if created:
        print(f'Created manager group')
    
    inspector_group, created = Group.objects.get_or_create(name='INSPECTOR')
    if created:
        print(f'Created inspector group')

    # Create Admin user
    admin_user, created = User.objects.get_or_create(
        username='admin_user',
        defaults={
            'email': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'password': make_password('admin123'),
            'is_active': True
        }
    )
    if created:
        print(f'Created admin user: {admin_user.username}')
        # Create UserProfile for admin
        UserProfile.objects.create(user=admin_user, role=admin_group)

    # Create Manager user
    manager_user, created = User.objects.get_or_create(
        username='manager_user',
        defaults={
            'email': 'manager@test.com',
            'first_name': 'Manager',
            'last_name': 'User',
            'password': make_password('manager123'),
            'is_active': True
        }
    )
    if created:
        print(f'Created manager user: {manager_user.username}')
        # Create UserProfile for manager
        UserProfile.objects.create(user=manager_user, role=manager_group)

    # Create Inspector user
    inspector_user, created = User.objects.get_or_create(
        username='inspector_user',
        defaults={
            'email': 'inspector@test.com',
            'first_name': 'Inspector',
            'last_name': 'User',
            'password': make_password('inspector123'),
            'is_active': True
        }
    )
    if created:
        print(f'Created inspector user: {inspector_user.username}')
        # Create UserProfile for inspector
        UserProfile.objects.create(user=inspector_user, role=inspector_group)

def create_test_observations(business_unit):
    """Create test observations with proper workflow states"""
    # Get test users by role
    admin_user = UserProfile.objects.filter(role__name='ADMIN').first().user if UserProfile.objects.filter(role__name='ADMIN').first() else None
    manager_user = UserProfile.objects.filter(role__name='MANAGER').first().user if UserProfile.objects.filter(role__name='MANAGER').first() else None
    inspector_user = UserProfile.objects.filter(role__name='INSPECTOR').first().user if UserProfile.objects.filter(role__name='INSPECTOR').first() else None

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
            print(f'Created observation: {observation.title} (Status: {observation.workflow_state})')

def ensure_business_units():
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
        print(f'Created default user: {user.username}')

    # Create data group if it doesn't exist
    data_group, created = DataGroup.objects.get_or_create(
        name='Test Data Group'
    )
    if created:
        print(f'Created data group: {data_group.name}')

    # Create company if it doesn't exist
    company, created = Company.objects.get_or_create(
        name='Test Company',
        defaults={
            'description': 'Test company for HSE workflow',
            'changed_by': user,
            'group': data_group
        }
    )
    if created:
        print(f'Created company: {company.name}')

    # Create site if it doesn't exist
    site, created = Site.objects.get_or_create(
        name='Test Site',
        company=company,
        defaults={
            'description': 'Test site for HSE workflow',
            'changed_by': user,
            'group': data_group
        }
    )
    if created:
        print(f'Created site: {site.name}')

    # Create business unit if it doesn't exist
    business_unit, created = BusinessUnit.objects.get_or_create(
        name='Test Department',
        site=site,
        defaults={
            'description': 'Test department for HSE workflow',
            'changed_by': user,
            'group': data_group
        }
    )
    if created:
        print(f'Created business unit: {business_unit.name}')

    return business_unit

if __name__ == '__main__':
    setup_test_data()

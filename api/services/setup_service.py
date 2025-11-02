from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from inspection_management.models import DataGroup
from users.models import UserProfile, SystemSettings

User = get_user_model()


def create_default_roles():
    """Create system roles with permissions"""
    roles = {
        'Admin': 'all',
        'Manager': 'manage',
        'Inspector': 'inspect',
        'Mitigation User': 'mitigate'
    }
    
    for role_name, _ in roles.items():
        Group.objects.get_or_create(name=role_name)


@transaction.atomic
def initialize_system(data):
    """Initialize system with first admin user"""
    
    # Create system roles
    create_default_roles()
    
    # Create organization data group
    data_group = DataGroup.objects.create(
        name=data['organization_name']
    )
    
    # Create admin user
    user = User.objects.create_user(
        username=data['admin_username'],
        email=data['admin_email'],
        password=data['admin_password'],
        first_name=data.get('admin_name', '').split()[0] if data.get('admin_name') else '',
        last_name=' '.join(data.get('admin_name', '').split()[1:]) if data.get('admin_name') else '',
        is_staff=True
    )
    
    # Create user profile
    profile = UserProfile.objects.create(user=user)
    profile.role = Group.objects.get(name='Admin')
    profile.data_groups.add(data_group)
    profile.save()
    
    # Mark setup as completed
    SystemSettings.mark_setup_completed()
    
    return {
        'user': user,
        'data_group': data_group,
        'profile': profile
    }


def check_setup_status():
    """Check if system needs setup"""
    # Check if any non-superuser exists
    has_users = User.objects.filter(is_superuser=False).exists()
    
    # Check settings
    setup_completed = SystemSettings.is_setup_completed()
    
    return {
        'needs_setup': not has_users and not setup_completed,
        'setup_completed': setup_completed,
        'has_users': has_users
    }


from django.core.management.base import BaseCommand
from inspection_management.models.external_departments import ExternalDepartment
from users.models import User
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Setup internal departments and assign mitigation users to them'

    def handle(self, *args, **options):
        # Get the mitigation user
        try:
            mitigation_user = User.objects.get(username='mitigation_user')
            self.stdout.write(self.style.SUCCESS(f'Found mitigation user: {mitigation_user.username}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Mitigation user not found. Please create a user with username "mitigation_user"'))
            return

        # Create internal departments based on existing external departments
        internal_departments = [
            {
                'name': 'Internal Safety Engineering',
                'department_type': 'SAFETY',
                'description': 'Internal safety engineering department for mitigation work',
                'contact_person': 'Safety Engineer',
                'contact_email': 'safety@internal.com',
                'contact_phone': '+1-555-0101',
                'is_available': True,
                'status': 'ACTIVE'
            },
            {
                'name': 'Internal Environmental Services',
                'department_type': 'ENVIRONMENTAL',
                'description': 'Internal environmental services department for mitigation work',
                'contact_person': 'Environmental Specialist',
                'contact_email': 'environmental@internal.com',
                'contact_phone': '+1-555-0102',
                'is_available': True,
                'status': 'ACTIVE'
            },
            {
                'name': 'Internal Quality Control',
                'department_type': 'QUALITY',
                'description': 'Internal quality control department for mitigation work',
                'contact_person': 'Quality Manager',
                'contact_email': 'quality@internal.com',
                'contact_phone': '+1-555-0103',
                'is_available': True,
                'status': 'ACTIVE'
            },
            {
                'name': 'Internal Maintenance',
                'department_type': 'MAINTENANCE',
                'description': 'Internal maintenance department for mitigation work',
                'contact_person': 'Maintenance Supervisor',
                'contact_email': 'maintenance@internal.com',
                'contact_phone': '+1-555-0104',
                'is_available': True,
                'status': 'ACTIVE'
            }
        ]

        created_departments = []
        for dept_data in internal_departments:
            # Check if department already exists
            existing_dept = ExternalDepartment.objects.filter(name=dept_data['name']).first()
            if existing_dept:
                self.stdout.write(self.style.WARNING(f'Department {dept_data["name"]} already exists'))
                created_departments.append(existing_dept)
            else:
                # Create new department
                dept = ExternalDepartment.objects.create(
                    name=dept_data['name'],
                    department_type=dept_data['department_type'],
                    description=dept_data['description'],
                    contact_person=dept_data['contact_person'],
                    contact_email=dept_data['contact_email'],
                    contact_phone=dept_data['contact_phone'],
                    is_available=dept_data['is_available'],
                    status=dept_data['status'],
                    created_by=mitigation_user  # Use mitigation user as creator
                )
                created_departments.append(dept)
                self.stdout.write(self.style.SUCCESS(f'Created department: {dept.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Setup complete! Created/found {len(created_departments)} internal departments'))
        self.stdout.write(self.style.SUCCESS('Internal departments available for assignment:'))
        for dept in created_departments:
            self.stdout.write(self.style.SUCCESS(f'  - {dept.name} ({dept.department_type})'))
        
        self.stdout.write(self.style.SUCCESS(f'\n📝 Note: Mitigation user "{mitigation_user.username}" can be assigned to any of these departments'))
        self.stdout.write(self.style.SUCCESS('   When selecting "Internal User" assignment, choose any department and then select the mitigation user from the dropdown.'))

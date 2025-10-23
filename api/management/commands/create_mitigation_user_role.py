from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Create Mitigation User role with appropriate permissions'

    def handle(self, *args, **options):
        # Create or get the Mitigation User group
        mitigation_user_group, created = Group.objects.get_or_create(name='Mitigation User')
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created new Mitigation User role'))
        else:
            self.stdout.write(self.style.WARNING('Mitigation User role already exists'))
        
        # Get content types for models the mitigation user needs access to
        from inspection_management.models import Evince
        evince_content_type = ContentType.objects.get_for_model(Evince)
        
        # Define permissions for mitigation user
        permissions_to_add = [
            ('view_evince', evince_content_type),
            ('change_evince', evince_content_type),
        ]
        
        # Add permissions to the group
        for codename, content_type in permissions_to_add:
            try:
                permission = Permission.objects.get(
                    codename=codename,
                    content_type=content_type
                )
                mitigation_user_group.permissions.add(permission)
                self.stdout.write(self.style.SUCCESS(f'  Added permission: {codename}'))
            except Permission.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'  Permission not found: {codename}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Mitigation User role setup complete!'))
        self.stdout.write(self.style.SUCCESS('   Permissions granted:'))
        self.stdout.write(self.style.SUCCESS('   - View HSE Risk Assessments assigned to them'))
        self.stdout.write(self.style.SUCCESS('   - Submit mitigation actions'))
        self.stdout.write(self.style.SUCCESS('   - Upload evidence'))
        self.stdout.write(self.style.SUCCESS('   - Mark mitigation work as completed'))


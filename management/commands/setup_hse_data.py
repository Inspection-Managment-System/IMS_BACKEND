from django.core.management.base import BaseCommand
from inspection_management.models.company import Company
from inspection_management.models.site import Site
from inspection_management.models.datagroup import DataGroup
from inspection_management.models.business_unit import BusinessUnit
from users.models.user import User


class Command(BaseCommand):
    help = 'Setup required data for HSE workflow'

    def handle(self, *args, **options):
        try:
            # Get or create DataGroup
            data_group, created = DataGroup.objects.get_or_create(
                name="HSE Default Group",
                defaults={
                    'attachment_name': '',
                    'attachment': ''
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created DataGroup: HSE Default Group'))
            else:
                self.stdout.write(self.style.SUCCESS('Using existing DataGroup: HSE Default Group'))

            # Get first user
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
                return

            # Get or create Company
            company, created = Company.objects.get_or_create(
                name="HSE Default Company",
                defaults={
                    'description': 'Default company for HSE observations',
                    'changed_by': user,
                    'group': data_group
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created Company: HSE Default Company'))
            else:
                self.stdout.write(self.style.SUCCESS('Using existing Company: HSE Default Company'))

            # Get or create Site
            site, created = Site.objects.get_or_create(
                name="HSE Default Site",
                defaults={
                    'description': 'Default site for HSE observations',
                    'company': company,
                    'changed_by': user,
                    'group': data_group
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created Site: HSE Default Site'))
            else:
                self.stdout.write(self.style.SUCCESS('Using existing Site: HSE Default Site'))

            # Get or create BusinessUnit
            business_unit, created = BusinessUnit.objects.get_or_create(
                name="HSE Default Department",
                defaults={
                    'description': 'Default department for HSE observations',
                    'site': site,
                    'changed_by': user,
                    'group': data_group
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created BusinessUnit: HSE Default Department'))
            else:
                self.stdout.write(self.style.SUCCESS('Using existing BusinessUnit: HSE Default Department'))

            self.stdout.write(self.style.SUCCESS('HSE data setup completed successfully!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error setting up HSE data: {e}'))

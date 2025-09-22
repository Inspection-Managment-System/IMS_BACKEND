from django.core.management.base import BaseCommand
from hazard_identification.models import HazardCategory


class Command(BaseCommand):
    help = 'Populate default hazard categories'

    def handle(self, *args, **options):
        categories = [
            {
                'name': 'Safety',
                'description': 'Safety-related hazards including physical safety risks',
                'color': '#dc2626',
                'icon': 'fas fa-shield-alt'
            },
            {
                'name': 'Health',
                'description': 'Health-related hazards including chemical and biological risks',
                'color': '#ea580c',
                'icon': 'fas fa-heartbeat'
            },
            {
                'name': 'Environmental',
                'description': 'Environmental hazards including pollution and contamination',
                'color': '#16a34a',
                'icon': 'fas fa-leaf'
            },
            {
                'name': 'Fire',
                'description': 'Fire-related hazards including flammable materials and ignition sources',
                'color': '#dc2626',
                'icon': 'fas fa-fire'
            },
            {
                'name': 'Electrical',
                'description': 'Electrical hazards including exposed wires and equipment',
                'color': '#f59e0b',
                'icon': 'fas fa-bolt'
            },
            {
                'name': 'Mechanical',
                'description': 'Mechanical hazards including moving parts and equipment',
                'color': '#6b7280',
                'icon': 'fas fa-cog'
            },
            {
                'name': 'Chemical',
                'description': 'Chemical hazards including toxic substances and spills',
                'color': '#8b5cf6',
                'icon': 'fas fa-flask'
            },
            {
                'name': 'Structural',
                'description': 'Structural hazards including building and infrastructure risks',
                'color': '#64748b',
                'icon': 'fas fa-building'
            },
            {
                'name': 'Ergonomic',
                'description': 'Ergonomic hazards including repetitive motion and poor posture',
                'color': '#06b6d4',
                'icon': 'fas fa-user-injured'
            },
            {
                'name': 'Noise',
                'description': 'Noise-related hazards including excessive sound levels',
                'color': '#f97316',
                'icon': 'fas fa-volume-up'
            }
        ]

        created_count = 0
        for category_data in categories:
            category, created = HazardCategory.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully populated {created_count} hazard categories')
        )

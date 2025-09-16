from django.core.management.base import BaseCommand
from inspection_management.models import Evince, InspectionResult, InspectionTest
from api.models import HSERiskAssessmentResult

class Command(BaseCommand):
    help = 'Delete all HSE Risk Assessment evinces and related data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        # Find all HSE Risk Assessment evinces
        hse_evinces = Evince.objects.filter(evince_type='hse_risk_management')
        
        if hse_evinces.count() == 0:
            self.stdout.write(
                self.style.SUCCESS('No HSE Risk Assessment evinces found.')
            )
            return
        
        self.stdout.write(f'Found {hse_evinces.count()} HSE Risk Assessment evinces:')
        for evince in hse_evinces:
            self.stdout.write(f'  - ID: {evince.id}, Name: {evince.name}, Status: {evince.status}')
        
        if not options['confirm']:
            confirm = input('\nAre you sure you want to delete these evinces? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write('Deletion cancelled.')
                return
        
        # Delete related data and evinces
        total_deleted = 0
        for evince in hse_evinces:
            # Delete related data
            results_count = InspectionResult.objects.filter(evince=evince).count()
            tests_count = InspectionTest.objects.filter(evince=evince).count()
            hse_results_count = HSERiskAssessmentResult.objects.filter(evince=evince).count()
            
            InspectionResult.objects.filter(evince=evince).delete()
            InspectionTest.objects.filter(evince=evince).delete()
            HSERiskAssessmentResult.objects.filter(evince=evince).delete()
            evince.delete()
            
            self.stdout.write(f'Deleted evince {evince.id} and {results_count} results, {tests_count} tests, {hse_results_count} HSE results')
            total_deleted += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {total_deleted} HSE Risk Assessment evinces')
        )

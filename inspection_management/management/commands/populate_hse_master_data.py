from django.core.management.base import BaseCommand
from inspection_management.models import AnalysisType, InspectionAnalysis, Parameter, Unit, DataGroup, Location, Equipment
from users.models.user import User


class Command(BaseCommand):
    help = 'Populate HSE-specific master data for analysis types, inspection analyses, and parameters'

    def handle(self, *args, **options):
        self.stdout.write('Adding HSE master data...')
        
        try:
            # Get required objects
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                self.stdout.write(self.style.ERROR('No admin user found. Please create a superuser first.'))
                return
            
            # Get or create HSE DataGroup
            hse_group, created = DataGroup.objects.get_or_create(
                name='HSE'
            )
            if created:
                self.stdout.write(f'Created DataGroup: {hse_group.name}')
            
            # Get or create HSE Analysis Types
            hse_analysis_types = [
                {
                    'name': 'HSE Safety Inspection',
                    'description': 'Safety-related inspections and observations'
                },
                {
                    'name': 'HSE Environmental Monitoring',
                    'description': 'Environmental monitoring and assessment'
                },
                {
                    'name': 'HSE Health Assessment',
                    'description': 'Health and occupational health assessments'
                },
                {
                    'name': 'HSE Compliance Audit',
                    'description': 'Compliance and regulatory audits'
                }
            ]
            
            for analysis_type_data in hse_analysis_types:
                analysis_type, created = AnalysisType.objects.get_or_create(
                    name=analysis_type_data['name'],
                    defaults={
                        'description': analysis_type_data['description'],
                        'changed_by': admin_user,
                        'group': hse_group
                    }
                )
                if created:
                    self.stdout.write(f'Created Analysis Type: {analysis_type.name}')
                else:
                    self.stdout.write(f'Analysis Type already exists: {analysis_type.name}')
            
            # Get required objects for InspectionAnalysis
            first_location = Location.objects.first()
            first_equipment = Equipment.objects.first()
            first_analysis_type = AnalysisType.objects.filter(name__icontains='HSE').first()
            
            if not first_location:
                self.stdout.write(self.style.ERROR('No locations found. Please create locations first.'))
                return
            
            if not first_analysis_type:
                self.stdout.write(self.style.ERROR('No HSE analysis types found. Please run this command again.'))
                return
            
            # Get or create HSE Inspection Analyses for each HSE Analysis Type
            hse_inspection_analyses = [
                # Safety Inspection Analyses
                {
                    'name': 'Safety Equipment Check',
                    'description': 'Inspection of safety equipment and PPE',
                    'reported_name': 'Safety Equipment Check',
                    'alias_name': 'SEC',
                    'analysis_type_name': 'HSE Safety Inspection'
                },
                {
                    'name': 'Emergency Response Check',
                    'description': 'Check of emergency response procedures and equipment',
                    'reported_name': 'Emergency Response Check',
                    'alias_name': 'ERC',
                    'analysis_type_name': 'HSE Safety Inspection'
                },
                {
                    'name': 'Incident Investigation',
                    'description': 'Investigation of safety incidents and near misses',
                    'reported_name': 'Incident Investigation',
                    'alias_name': 'II',
                    'analysis_type_name': 'HSE Safety Inspection'
                },
                # Environmental Monitoring Analyses
                {
                    'name': 'Environmental Sampling',
                    'description': 'Environmental sample collection and analysis',
                    'reported_name': 'Environmental Sampling',
                    'alias_name': 'ES',
                    'analysis_type_name': 'HSE Environmental Monitoring'
                },
                {
                    'name': 'Air Quality Monitoring',
                    'description': 'Monitoring of air quality and emissions',
                    'reported_name': 'Air Quality Monitoring',
                    'alias_name': 'AQM',
                    'analysis_type_name': 'HSE Environmental Monitoring'
                },
                {
                    'name': 'Waste Management Check',
                    'description': 'Check of waste management procedures',
                    'reported_name': 'Waste Management Check',
                    'alias_name': 'WMC',
                    'analysis_type_name': 'HSE Environmental Monitoring'
                },
                # Health Assessment Analyses
                {
                    'name': 'Health Risk Assessment',
                    'description': 'Assessment of health risks in workplace',
                    'reported_name': 'Health Risk Assessment',
                    'alias_name': 'HRA',
                    'analysis_type_name': 'HSE Health Assessment'
                },
                {
                    'name': 'Occupational Health Check',
                    'description': 'Check of occupational health conditions',
                    'reported_name': 'Occupational Health Check',
                    'alias_name': 'OHC',
                    'analysis_type_name': 'HSE Health Assessment'
                },
                # Compliance Audit Analyses
                {
                    'name': 'Compliance Verification',
                    'description': 'Verification of regulatory compliance',
                    'reported_name': 'Compliance Verification',
                    'alias_name': 'CV',
                    'analysis_type_name': 'HSE Compliance Audit'
                },
                {
                    'name': 'Regulatory Audit',
                    'description': 'Comprehensive regulatory compliance audit',
                    'reported_name': 'Regulatory Audit',
                    'alias_name': 'RA',
                    'analysis_type_name': 'HSE Compliance Audit'
                }
            ]
            
            for inspection_analysis_data in hse_inspection_analyses:
                # Get the specific analysis type for this inspection analysis
                analysis_type = AnalysisType.objects.filter(
                    name=inspection_analysis_data['analysis_type_name']
                ).first()
                
                if not analysis_type:
                    self.stdout.write(f'Analysis type not found: {inspection_analysis_data["analysis_type_name"]}')
                    continue
                
                inspection_analysis, created = InspectionAnalysis.objects.get_or_create(
                    name=inspection_analysis_data['name'],
                    defaults={
                        'description': inspection_analysis_data['description'],
                        'changed_by': admin_user,
                        'group': hse_group,
                        'analysis_type': analysis_type,
                        'location': first_location,
                        'equipment': first_equipment,
                        'reported_name': inspection_analysis_data['reported_name'],
                        'alias_name': inspection_analysis_data['alias_name']
                    }
                )
                if created:
                    self.stdout.write(f'Created Inspection Analysis: {inspection_analysis.name}')
                else:
                    self.stdout.write(f'Inspection Analysis already exists: {inspection_analysis.name}')
            
            # Get or create HSE Units
            hse_units = [
                {
                    'name': 'Risk Level',
                    'description': 'Risk level measurement unit'
                },
                {
                    'name': 'Safety Score',
                    'description': 'Safety score measurement unit'
                },
                {
                    'name': 'Percentage',
                    'description': 'Percentage measurement unit'
                },
                {
                    'name': 'Count',
                    'description': 'Count measurement unit'
                },
                {
                    'name': 'Yes/No',
                    'description': 'Yes/No measurement unit'
                }
            ]
            
            for unit_data in hse_units:
                unit, created = Unit.objects.get_or_create(
                    name=unit_data['name'],
                    defaults={
                        'description': unit_data['description'],
                        'changed_by': admin_user,
                        'group': hse_group
                    }
                )
                if created:
                    self.stdout.write(f'Created Unit: {unit.name}')
                else:
                    self.stdout.write(f'Unit already exists: {unit.name}')
            
            # Get or create HSE Parameters
            hse_parameters = [
                # Safety Parameters
                {
                    'name': 'Risk Level',
                    'description': 'Risk level assessment (Low, Medium, High, Critical)',
                    'inspection_analysis_name': 'Safety Equipment Check',
                    'unit_name': 'Risk Level',
                    'min_value': 1,
                    'max_value': 4,
                    'avg_value': 2,
                    'checklist_data_type': 'yes_no'
                },
                {
                    'name': 'Safety Score',
                    'description': 'Safety compliance score (0-100)',
                    'inspection_analysis_name': 'Safety Equipment Check',
                    'unit_name': 'Safety Score',
                    'min_value': 0,
                    'max_value': 100,
                    'avg_value': 75,
                    'checklist_data_type': 'yes_no'
                },
                {
                    'name': 'Equipment Condition',
                    'description': 'Condition of safety equipment',
                    'inspection_analysis_name': 'Safety Equipment Check',
                    'unit_name': 'Yes/No',
                    'checklist_data_type': 'satisfactory_unsatisfactory'
                },
                # Environmental Parameters
                {
                    'name': 'Air Quality Index',
                    'description': 'Air quality measurement',
                    'inspection_analysis_name': 'Air Quality Monitoring',
                    'unit_name': 'Count',
                    'min_value': 0,
                    'max_value': 500,
                    'avg_value': 50,
                    'checklist_data_type': 'yes_no'
                },
                {
                    'name': 'Environmental Impact',
                    'description': 'Environmental impact assessment',
                    'inspection_analysis_name': 'Environmental Sampling',
                    'unit_name': 'Risk Level',
                    'min_value': 1,
                    'max_value': 4,
                    'avg_value': 2,
                    'checklist_data_type': 'yes_no'
                },
                # Health Parameters
                {
                    'name': 'Health Risk Score',
                    'description': 'Health risk assessment score',
                    'inspection_analysis_name': 'Health Risk Assessment',
                    'unit_name': 'Safety Score',
                    'min_value': 0,
                    'max_value': 100,
                    'avg_value': 25,
                    'checklist_data_type': 'yes_no'
                },
                {
                    'name': 'Exposure Level',
                    'description': 'Level of exposure to hazard',
                    'inspection_analysis_name': 'Occupational Health Check',
                    'unit_name': 'Risk Level',
                    'min_value': 1,
                    'max_value': 4,
                    'avg_value': 2,
                    'checklist_data_type': 'yes_no'
                },
                # Compliance Parameters
                {
                    'name': 'Compliance Percentage',
                    'description': 'Regulatory compliance percentage',
                    'inspection_analysis_name': 'Compliance Verification',
                    'unit_name': 'Percentage',
                    'min_value': 0,
                    'max_value': 100,
                    'avg_value': 85,
                    'checklist_data_type': 'yes_no'
                },
                {
                    'name': 'Corrective Actions Required',
                    'description': 'Number of corrective actions required',
                    'inspection_analysis_name': 'Regulatory Audit',
                    'unit_name': 'Count',
                    'min_value': 0,
                    'max_value': 50,
                    'avg_value': 5,
                    'checklist_data_type': 'yes_no'
                }
            ]
            
            for parameter_data in hse_parameters:
                # Get the inspection analysis for this parameter
                inspection_analysis = InspectionAnalysis.objects.filter(
                    name=parameter_data['inspection_analysis_name']
                ).first()
                
                # Get the unit for this parameter
                unit = Unit.objects.filter(
                    name=parameter_data['unit_name']
                ).first()
                
                if not inspection_analysis:
                    self.stdout.write(f'Inspection analysis not found: {parameter_data["inspection_analysis_name"]}')
                    continue
                    
                if not unit:
                    self.stdout.write(f'Unit not found: {parameter_data["unit_name"]}')
                    continue
                
                parameter, created = Parameter.objects.get_or_create(
                    name=parameter_data['name'],
                    defaults={
                        'description': parameter_data['description'],
                        'changed_by': admin_user,
                        'group': hse_group,
                        'inspection_analysis': inspection_analysis,
                        'unit': unit,
                        'min_value': parameter_data.get('min_value'),
                        'max_value': parameter_data.get('max_value'),
                        'avg_value': parameter_data.get('avg_value'),
                        'checklist_data_type': parameter_data.get('checklist_data_type', 'yes_no')
                    }
                )
                if created:
                    self.stdout.write(f'Created Parameter: {parameter.name}')
                else:
                    self.stdout.write(f'Parameter already exists: {parameter.name}')
            
            self.stdout.write(
                self.style.SUCCESS('Successfully populated HSE master data!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error populating HSE master data: {str(e)}')
            )

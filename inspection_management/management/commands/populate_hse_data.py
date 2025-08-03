from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
import json

from inspection_management.models.hse_models import (
    HSEEnvironmentalData,
    HSESafetyIncident,
    HSEEquipment,
    HSECompliance,
    HSETraining
)
from inspection_management.models.inspection_point import InspectionPoint
from inspection_management.models.business_unit import BusinessUnit
from users.models.user import User


class Command(BaseCommand):
    help = 'Populate HSE system with demo data'

    def handle(self, *args, **options):
        self.stdout.write('Creating HSE demo data...')

        # Create sample data if dependencies don't exist
        inspection_points = self.ensure_inspection_points()
        business_units = self.ensure_business_units()
        users = self.ensure_users()

        self.create_environmental_data(inspection_points, users)
        self.create_safety_incidents(business_units, users)
        self.create_equipment(business_units, users)
        self.create_compliance_records(business_units, users)
        self.create_training_records(users)

        self.stdout.write(self.style.SUCCESS('Successfully created HSE demo data'))

    def ensure_inspection_points(self):
        """Ensure we have inspection points"""
        if InspectionPoint.objects.exists():
            return list(InspectionPoint.objects.all())
        
        # Create sample inspection points
        points = []
        locations = ['Production Area A', 'Storage Facility B', 'Waste Treatment Plant', 'Air Quality Station', 'Water Treatment Plant']
        
        for i, location in enumerate(locations):
            point = InspectionPoint.objects.create(
                name=f"Inspection Point {i+1}",
                description=f"Environmental monitoring station at {location}",
                location=location,
                is_active=True
            )
            points.append(point)
        
        self.stdout.write(f'Created {len(points)} inspection points')
        return points

    def ensure_business_units(self):
        """Ensure we have business units"""
        if BusinessUnit.objects.exists():
            return list(BusinessUnit.objects.all())
        
        # Create sample business units
        units = []
        unit_names = ['Production Unit', 'Maintenance Department', 'Safety Division', 'Environmental Control', 'Quality Assurance']
        
        for i, name in enumerate(unit_names):
            unit = BusinessUnit.objects.create(
                name=name,
                description=f"Business unit for {name}",
                is_active=True
            )
            units.append(unit)
        
        self.stdout.write(f'Created {len(units)} business units')
        return units

    def ensure_users(self):
        """Ensure we have users"""
        if User.objects.exists():
            return list(User.objects.all())
        
        # Create sample users
        users = []
        user_data = [
            {'first_name': 'John', 'last_name': 'Smith', 'email': 'john.smith@company.com'},
            {'first_name': 'Sarah', 'last_name': 'Johnson', 'email': 'sarah.johnson@company.com'},
            {'first_name': 'Mike', 'last_name': 'Davis', 'email': 'mike.davis@company.com'},
            {'first_name': 'Lisa', 'last_name': 'Wilson', 'email': 'lisa.wilson@company.com'},
            {'first_name': 'David', 'last_name': 'Brown', 'email': 'david.brown@company.com'},
        ]
        
        for user_info in user_data:
            user = User.objects.create(
                username=user_info['email'],
                email=user_info['email'],
                first_name=user_info['first_name'],
                last_name=user_info['last_name'],
                is_active=True
            )
            users.append(user)
        
        self.stdout.write(f'Created {len(users)} users')
        return users

    def create_environmental_data(self, inspection_points, users):
        """Create environmental monitoring data"""
        # Clear existing data
        HSEEnvironmentalData.objects.all().delete()
        
        for i in range(50):
            inspection_point = random.choice(inspection_points)
            user = random.choice(users)
            
            # Generate more realistic environmental data
            timestamp = timezone.now() - timedelta(days=random.randint(0, 30))
            
            HSEEnvironmentalData.objects.create(
                inspection_point=inspection_point,
                recorded_by=user,
                timestamp=timestamp,
                air_quality_pm25=round(random.uniform(8, 45), 2),
                air_quality_pm10=round(random.uniform(15, 180), 2),
                air_quality_vocs=round(random.uniform(0.05, 2.5), 3),
                air_quality_nox=round(random.uniform(3, 50), 2),
                air_quality_sox=round(random.uniform(0.5, 15), 2),
                water_quality_ph=round(random.uniform(6.5, 8.5), 1),
                water_quality_temperature=round(random.uniform(15, 35), 1),
                water_quality_dissolved_oxygen=round(random.uniform(4, 12), 2),
                emissions_co2=round(random.uniform(100, 500), 2),
                emissions_ch4=round(random.uniform(0.1, 5), 3),
                waste_generation=round(random.uniform(50, 200), 2),
                waste_disposal=round(random.uniform(40, 180), 2),
                notes=f"Environmental reading {i+1} - {inspection_point.name}"
            )
        
        self.stdout.write(f'Created {HSEEnvironmentalData.objects.count()} environmental records')

    def create_safety_incidents(self, business_units, users):
        """Create safety incident records"""
        # Clear existing data
        HSESafetyIncident.objects.all().delete()
        
        incident_types = ['near_miss', 'minor_injury', 'major_injury', 'property_damage', 'environmental_spill', 'fire_explosion']
        severities = ['low', 'medium', 'high', 'critical']
        statuses = ['reported', 'investigating', 'corrective_action', 'resolved', 'closed']
        
        for i in range(20):
            incident_type = random.choice(incident_types)
            severity = random.choice(severities)
            status = random.choice(statuses)
            
            incident_date = timezone.now() - timedelta(days=random.randint(1, 90))
            
            HSESafetyIncident.objects.create(
                title=f"Safety Incident {i+1}",
                description=f"Description of {incident_type.replace('_', ' ')} incident",
                incident_type=incident_type,
                severity=severity,
                status=status,
                location=random.choice(business_units),
                reported_by=random.choice(users),
                incident_date=incident_date,
                reported_date=incident_date,
                affected_personnel=f"Personnel affected: {random.randint(0, 5)}",
                root_cause="Root cause analysis pending",
                corrective_actions="Corrective actions being implemented",
                cost_estimate=round(random.uniform(1000, 50000), 2)
            )
        
        self.stdout.write(f'Created {HSESafetyIncident.objects.count()} safety incidents')

    def create_equipment(self, business_units, users):
        """Create HSE equipment records"""
        # Clear existing data
        HSEEquipment.objects.all().delete()
        
        equipment_types = ['air_monitor', 'water_treatment', 'emission_control', 'waste_management', 'safety_equipment', 'monitoring_device']
        statuses = ['operational', 'maintenance', 'out_of_service', 'calibration_due', 'repair_needed']
        
        for i in range(15):
            equipment_type = random.choice(equipment_types)
            status = random.choice(statuses)
            
            HSEEquipment.objects.create(
                name=f"{equipment_type.replace('_', ' ').title()} {i+1}",
                equipment_type=equipment_type,
                location=random.choice(business_units),
                status=status,
                manufacturer=f"Manufacturer {i+1}",
                model_number=f"MOD-{i+1:03d}",
                serial_number=f"SN-{i+1:06d}",
                installation_date=timezone.now().date() - timedelta(days=random.randint(100, 1000)),
                last_maintenance=timezone.now().date() - timedelta(days=random.randint(30, 180)),
                next_maintenance=timezone.now().date() + timedelta(days=random.randint(30, 180)),
                calibration_due=timezone.now().date() + timedelta(days=random.randint(10, 90)),
                responsible_person=random.choice(users),
                specifications=f"Technical specifications for {equipment_type}",
                performance_metrics=json.dumps({
                    "efficiency": round(random.uniform(85, 98), 2),
                    "uptime": round(random.uniform(90, 99), 2),
                    "last_calibration": str(timezone.now().date() - timedelta(days=random.randint(30, 180)))
                }),
                compliance_status="compliant",
                notes=f"Equipment notes for {equipment_type}"
            )
        
        self.stdout.write(f'Created {HSEEquipment.objects.count()} equipment records')

    def create_compliance_records(self, business_units, users):
        """Create compliance records"""
        # Clear existing data
        HSECompliance.objects.all().delete()
        
        compliance_types = ['environmental_permit', 'safety_regulation', 'health_standard', 'waste_management', 'emission_control', 'water_quality']
        statuses = ['compliant', 'non_compliant', 'pending_review', 'under_investigation']
        
        for i in range(12):
            compliance_type = random.choice(compliance_types)
            status = random.choice(statuses)
            
            HSECompliance.objects.create(
                title=f"{compliance_type.replace('_', ' ').title()} Compliance {i+1}",
                compliance_type=compliance_type,
                status=status,
                business_unit=random.choice(business_units),
                permit_number=f"PERMIT-{i+1:03d}",
                issue_date=timezone.now().date() - timedelta(days=random.randint(100, 500)),
                expiry_date=timezone.now().date() + timedelta(days=random.randint(30, 365)),
                renewal_date=timezone.now().date() + timedelta(days=random.randint(10, 30)),
                responsible_person=random.choice(users),
                requirements=f"Compliance requirements for {compliance_type}",
                current_status=f"Current status: {status}",
                violations="No violations reported",
                corrective_actions="No corrective actions required",
                last_audit=timezone.now().date() - timedelta(days=random.randint(30, 180)),
                next_audit=timezone.now().date() + timedelta(days=random.randint(30, 180))
            )
        
        self.stdout.write(f'Created {HSECompliance.objects.count()} compliance records')

    def create_training_records(self, users):
        """Create training records"""
        # Clear existing data
        HSETraining.objects.all().delete()
        
        training_types = ['safety_training', 'environmental_training', 'compliance_training', 'equipment_training', 'emergency_response']
        statuses = ['scheduled', 'in_progress', 'completed', 'overdue', 'cancelled']
        
        for i in range(25):
            training_type = random.choice(training_types)
            status = random.choice(statuses)
            employee = random.choice(users)
            trainer = random.choice(users) if random.choice([True, False]) else None
            
            HSETraining.objects.create(
                title=f"{training_type.replace('_', ' ').title()} {i+1}",
                training_type=training_type,
                status=status,
                employee=employee,
                trainer=trainer,
                scheduled_date=timezone.now() + timedelta(days=random.randint(-30, 30)),
                completed_date=timezone.now() - timedelta(days=random.randint(0, 60)) if status == 'completed' else None,
                due_date=timezone.now() + timedelta(days=random.randint(-10, 90)),
                duration_hours=round(random.uniform(2, 8), 1),
                certification_number=f"CERT-{i+1:04d}" if status == 'completed' else None,
                certification_expiry=timezone.now().date() + timedelta(days=random.randint(30, 365)) if status == 'completed' else None,
                score=round(random.uniform(70, 100), 1) if status == 'completed' else None,
                notes=f"Training notes for {training_type}"
            )
        
        self.stdout.write(f'Created {HSETraining.objects.count()} training records') 
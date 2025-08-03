from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
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


class HSEEnvironmentalDataViewSet(viewsets.ModelViewSet):
    """HSE Environmental Data API"""
    permission_classes = [IsAuthenticated]
    queryset = HSEEnvironmentalData.objects.all()
    
    def list(self, request):
        """Get environmental data with filtering"""
        try:
            inspection_point_id = request.query_params.get('inspection_point')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            queryset = self.queryset
            
            if inspection_point_id:
                queryset = queryset.filter(inspection_point_id=inspection_point_id)
            
            if start_date:
                queryset = queryset.filter(timestamp__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(timestamp__lte=end_date)
            
            data = []
            for item in queryset:
                data.append({
                    'id': item.id,
                    'inspection_point': {
                        'id': item.inspection_point.id,
                        'name': item.inspection_point.name
                    },
                    'timestamp': item.timestamp,
                    'air_quality': {
                        'pm25': item.air_quality_pm25,
                        'pm10': item.air_quality_pm10,
                        'vocs': item.air_quality_vocs,
                        'nox': item.air_quality_nox,
                        'sox': item.air_quality_sox
                    },
                    'water_quality': {
                        'ph': item.water_quality_ph,
                        'temperature': item.water_quality_temperature,
                        'dissolved_oxygen': item.water_quality_dissolved_oxygen
                    },
                    'emissions': {
                        'co2': item.emissions_co2,
                        'ch4': item.emissions_ch4
                    },
                    'waste': {
                        'generation': item.waste_generation,
                        'disposal': item.waste_disposal
                    },
                    'recorded_by': {
                        'id': item.recorded_by.id,
                        'name': f"{item.recorded_by.first_name} {item.recorded_by.last_name}"
                    },
                    'notes': item.notes
                })
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """Create new environmental data"""
        try:
            data = request.data
            inspection_point_id = data.get('inspection_point_id')
            recorded_by_id = data.get('recorded_by_id')
            
            if not inspection_point_id or not recorded_by_id:
                return Response(
                    {'error': 'inspection_point_id and recorded_by_id are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            environmental_data = HSEEnvironmentalData.objects.create(
                inspection_point_id=inspection_point_id,
                recorded_by_id=recorded_by_id,
                air_quality_pm25=data.get('air_quality_pm25'),
                air_quality_pm10=data.get('air_quality_pm10'),
                air_quality_vocs=data.get('air_quality_vocs'),
                air_quality_nox=data.get('air_quality_nox'),
                air_quality_sox=data.get('air_quality_sox'),
                water_quality_ph=data.get('water_quality_ph'),
                water_quality_temperature=data.get('water_quality_temperature'),
                water_quality_dissolved_oxygen=data.get('water_quality_dissolved_oxygen'),
                emissions_co2=data.get('emissions_co2'),
                emissions_ch4=data.get('emissions_ch4'),
                waste_generation=data.get('waste_generation'),
                waste_disposal=data.get('waste_disposal'),
                notes=data.get('notes')
            )
            
            return Response({
                'id': environmental_data.id,
                'message': 'Environmental data created successfully'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get environmental dashboard data"""
        try:
            # Get recent environmental data
            recent_data = HSEEnvironmentalData.objects.filter(
                timestamp__gte=timezone.now() - timedelta(days=7)
            ).order_by('-timestamp')[:10]
            
            # Calculate averages
            avg_air_quality = HSEEnvironmentalData.objects.aggregate(
                avg_pm25=Avg('air_quality_pm25'),
                avg_pm10=Avg('air_quality_pm10'),
                avg_vocs=Avg('air_quality_vocs')
            )
            
            # Get compliance status
            total_readings = HSEEnvironmentalData.objects.count()
            compliant_readings = HSEEnvironmentalData.objects.filter(
                air_quality_pm25__lte=35,  # Example threshold
                air_quality_pm10__lte=150   # Example threshold
            ).count()
            
            compliance_rate = (compliant_readings / total_readings * 100) if total_readings > 0 else 0
            
            dashboard_data = {
                'recent_readings': [
                    {
                        'id': item.id,
                        'inspection_point': item.inspection_point.name if item.inspection_point else 'Unknown',
                        'timestamp': item.timestamp,
                        'air_quality_pm25': float(item.air_quality_pm25) if item.air_quality_pm25 else 0,
                        'air_quality_pm10': float(item.air_quality_pm10) if item.air_quality_pm10 else 0,
                        'status': 'compliant' if (item.air_quality_pm25 or 0) <= 35 else 'exceedance'
                    } for item in recent_data
                ],
                'averages': {
                    'avg_pm25': float(avg_air_quality['avg_pm25']) if avg_air_quality['avg_pm25'] else 0,
                    'avg_pm10': float(avg_air_quality['avg_pm10']) if avg_air_quality['avg_pm10'] else 0,
                    'avg_vocs': float(avg_air_quality['avg_vocs']) if avg_air_quality['avg_vocs'] else 0
                },
                'compliance_rate': round(compliance_rate, 2),
                'total_readings': total_readings,
                'compliant_readings': compliant_readings
            }
            
            return Response(dashboard_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HSESafetyIncidentViewSet(viewsets.ModelViewSet):
    """HSE Safety Incident API"""
    permission_classes = [IsAuthenticated]
    queryset = HSESafetyIncident.objects.all()
    
    def list(self, request):
        """Get safety incidents with filtering"""
        try:
            status_filter = request.query_params.get('status')
            severity_filter = request.query_params.get('severity')
            incident_type = request.query_params.get('incident_type')
            
            queryset = self.queryset
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            if severity_filter:
                queryset = queryset.filter(severity=severity_filter)
            
            if incident_type:
                queryset = queryset.filter(incident_type=incident_type)
            
            # Convert choice fields to readable format
            def get_incident_type_display(incident_type):
                type_map = {
                    'near_miss': 'Near Miss',
                    'minor_injury': 'Minor Injury',
                    'major_injury': 'Major Injury',
                    'property_damage': 'Property Damage',
                    'environmental_spill': 'Environmental Spill',
                    'fire_explosion': 'Fire/Explosion'
                }
                return type_map.get(incident_type, incident_type.replace('_', ' ').title())
            
            def get_severity_display(severity):
                severity_map = {
                    'low': 'Low',
                    'medium': 'Medium',
                    'high': 'High',
                    'critical': 'Critical'
                }
                return severity_map.get(severity, severity.title())
            
            def get_status_display(status):
                status_map = {
                    'reported': 'Reported',
                    'investigating': 'Investigating',
                    'corrective_action': 'Corrective Action',
                    'resolved': 'Resolved',
                    'closed': 'Closed'
                }
                return status_map.get(status, status.replace('_', ' ').title())
            
            data = []
            for item in queryset:
                data.append({
                    'id': item.id,
                    'title': item.title,
                    'description': item.description,
                    'incident_type': get_incident_type_display(item.incident_type),
                    'severity': get_severity_display(item.severity),
                    'status': get_status_display(item.status),
                    'location': {
                        'id': item.location.id,
                        'name': item.location.name
                    } if item.location else None,
                    'reported_by': {
                        'id': item.reported_by.id,
                        'name': f"{item.reported_by.first_name} {item.reported_by.last_name}"
                    } if item.reported_by else None,
                    'reported_date': item.reported_date,
                    'incident_date': item.incident_date,
                    'affected_personnel': item.affected_personnel,
                    'root_cause': item.root_cause,
                    'corrective_actions': item.corrective_actions,
                    'cost_estimate': float(item.cost_estimate) if item.cost_estimate else None,
                    'investigation_lead': {
                        'id': item.investigation_lead.id,
                        'name': f"{item.investigation_lead.first_name} {item.investigation_lead.last_name}"
                    } if item.investigation_lead else None,
                    'resolution_date': item.resolution_date
                })
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """Create new safety incident"""
        try:
            data = request.data
            reported_by_id = data.get('reported_by_id')
            location_id = data.get('location_id')
            
            if not reported_by_id or not location_id:
                return Response(
                    {'error': 'reported_by_id and location_id are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            incident = HSESafetyIncident.objects.create(
                title=data.get('title'),
                description=data.get('description'),
                incident_type=data.get('incident_type'),
                severity=data.get('severity'),
                status=data.get('status', 'reported'),
                location_id=location_id,
                reported_by_id=reported_by_id,
                incident_date=data.get('incident_date'),
                affected_personnel=data.get('affected_personnel'),
                root_cause=data.get('root_cause'),
                corrective_actions=data.get('corrective_actions'),
                cost_estimate=data.get('cost_estimate'),
                investigation_lead_id=data.get('investigation_lead_id')
            )
            
            return Response({
                'id': incident.id,
                'message': 'Safety incident created successfully'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get safety incident dashboard data"""
        try:
            # Get incident statistics
            total_incidents = HSESafetyIncident.objects.count()
            open_incidents = HSESafetyIncident.objects.filter(
                status__in=['reported', 'investigating', 'corrective_action']
            ).count()
            
            # Get incidents by type
            incidents_by_type = HSESafetyIncident.objects.values('incident_type').annotate(
                count=Count('id')
            )
            
            # Get incidents by severity
            incidents_by_severity = HSESafetyIncident.objects.values('severity').annotate(
                count=Count('id')
            )
            
            # Get recent incidents
            recent_incidents = HSESafetyIncident.objects.filter(
                incident_date__gte=timezone.now() - timedelta(days=30)
            ).order_by('-incident_date')[:5]
            
            # Convert choice fields to readable format
            def get_incident_type_display(incident_type):
                type_map = {
                    'near_miss': 'Near Miss',
                    'minor_injury': 'Minor Injury',
                    'major_injury': 'Major Injury',
                    'property_damage': 'Property Damage',
                    'environmental_spill': 'Environmental Spill',
                    'fire_explosion': 'Fire/Explosion'
                }
                return type_map.get(incident_type, incident_type.replace('_', ' ').title())
            
            def get_severity_display(severity):
                severity_map = {
                    'low': 'Low',
                    'medium': 'Medium',
                    'high': 'High',
                    'critical': 'Critical'
                }
                return severity_map.get(severity, severity.title())
            
            def get_status_display(status):
                status_map = {
                    'reported': 'Reported',
                    'investigating': 'Investigating',
                    'corrective_action': 'Corrective Action',
                    'resolved': 'Resolved',
                    'closed': 'Closed'
                }
                return status_map.get(status, status.replace('_', ' ').title())
            
            dashboard_data = {
                'total_incidents': total_incidents,
                'open_incidents': open_incidents,
                'resolved_incidents': total_incidents - open_incidents,
                'incidents_by_type': [
                    {
                        'type': get_incident_type_display(item['incident_type']),
                        'count': item['count']
                    } for item in incidents_by_type
                ],
                'incidents_by_severity': [
                    {
                        'severity': get_severity_display(item['severity']),
                        'count': item['count']
                    } for item in incidents_by_severity
                ],
                'recent_incidents': [
                    {
                        'id': item.id,
                        'title': item.title,
                        'incident_type': get_incident_type_display(item.incident_type),
                        'severity': get_severity_display(item.severity),
                        'status': get_status_display(item.status),
                        'incident_date': item.incident_date
                    } for item in recent_incidents
                ]
            }
            
            return Response(dashboard_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HSEEquipmentViewSet(viewsets.ModelViewSet):
    """HSE Equipment API"""
    permission_classes = [IsAuthenticated]
    queryset = HSEEquipment.objects.all()
    
    def list(self, request):
        """Get equipment with filtering"""
        try:
            status_filter = request.query_params.get('status')
            equipment_type = request.query_params.get('equipment_type')
            location_id = request.query_params.get('location_id')
            
            queryset = self.queryset
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            if equipment_type:
                queryset = queryset.filter(equipment_type=equipment_type)
            
            if location_id:
                queryset = queryset.filter(location_id=location_id)
            
            # Convert choice fields to readable format
            def get_equipment_type_display(equipment_type):
                type_map = {
                    'air_monitor': 'Air Monitor',
                    'water_treatment': 'Water Treatment',
                    'emission_control': 'Emission Control',
                    'waste_management': 'Waste Management',
                    'safety_equipment': 'Safety Equipment',
                    'monitoring_device': 'Monitoring Device'
                }
                return type_map.get(equipment_type, equipment_type.replace('_', ' ').title())
            
            def get_status_display(status):
                status_map = {
                    'operational': 'Operational',
                    'maintenance': 'Maintenance',
                    'out_of_service': 'Out of Service',
                    'calibration_due': 'Calibration Due',
                    'repair_needed': 'Repair Needed'
                }
                return status_map.get(status, status.replace('_', ' ').title())
            
            data = []
            for item in queryset:
                data.append({
                    'id': item.id,
                    'name': item.name,
                    'equipment_type': get_equipment_type_display(item.equipment_type),
                    'status': get_status_display(item.status),
                    'location': {
                        'id': item.location.id,
                        'name': item.location.name
                    } if item.location else None,
                    'manufacturer': item.manufacturer,
                    'model_number': item.model_number,
                    'serial_number': item.serial_number,
                    'installation_date': item.installation_date,
                    'last_maintenance': item.last_maintenance,
                    'next_maintenance': item.next_maintenance,
                    'calibration_due': item.calibration_due,
                    'responsible_person': {
                        'id': item.responsible_person.id,
                        'name': f"{item.responsible_person.first_name} {item.responsible_person.last_name}"
                    } if item.responsible_person else None,
                    'specifications': item.specifications,
                    'performance_metrics': json.loads(item.performance_metrics) if item.performance_metrics else None,
                    'compliance_status': item.compliance_status,
                    'notes': item.notes
                })
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get equipment dashboard data"""
        try:
            # Get equipment statistics
            total_equipment = HSEEquipment.objects.count()
            operational_equipment = HSEEquipment.objects.filter(status='operational').count()
            maintenance_equipment = HSEEquipment.objects.filter(status='maintenance').count()
            calibration_due = HSEEquipment.objects.filter(
                calibration_due__lte=timezone.now().date() + timedelta(days=30)
            ).count()
            
            # Get equipment by type
            equipment_by_type = HSEEquipment.objects.values('equipment_type').annotate(
                count=Count('id')
            )
            
            # Get equipment by status
            equipment_by_status = HSEEquipment.objects.values('status').annotate(
                count=Count('id')
            )
            
            # Get equipment needing attention
            attention_needed = HSEEquipment.objects.filter(
                Q(status='maintenance') | 
                Q(status='calibration_due') | 
                Q(status='repair_needed')
            ).order_by('next_maintenance')[:5]
            
            # Convert choice fields to readable format
            def get_equipment_type_display(equipment_type):
                type_map = {
                    'air_monitor': 'Air Monitor',
                    'water_treatment': 'Water Treatment',
                    'emission_control': 'Emission Control',
                    'waste_management': 'Waste Management',
                    'safety_equipment': 'Safety Equipment',
                    'monitoring_device': 'Monitoring Device'
                }
                return type_map.get(equipment_type, equipment_type.replace('_', ' ').title())
            
            def get_status_display(status):
                status_map = {
                    'operational': 'Operational',
                    'maintenance': 'Maintenance',
                    'out_of_service': 'Out of Service',
                    'calibration_due': 'Calibration Due',
                    'repair_needed': 'Repair Needed'
                }
                return status_map.get(status, status.replace('_', ' ').title())
            
            dashboard_data = {
                'total_equipment': total_equipment,
                'operational_equipment': operational_equipment,
                'maintenance_equipment': maintenance_equipment,
                'calibration_due': calibration_due,
                'equipment_by_type': [
                    {
                        'type': get_equipment_type_display(item['equipment_type']),
                        'count': item['count']
                    } for item in equipment_by_type
                ],
                'equipment_by_status': [
                    {
                        'status': get_status_display(item['status']),
                        'count': item['count']
                    } for item in equipment_by_status
                ],
                'attention_needed': [
                    {
                        'id': item.id,
                        'name': item.name,
                        'equipment_type': get_equipment_type_display(item.equipment_type),
                        'status': get_status_display(item.status),
                        'next_maintenance': item.next_maintenance,
                        'calibration_due': item.calibration_due
                    } for item in attention_needed
                ]
            }
            
            return Response(dashboard_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HSEComplianceViewSet(viewsets.ModelViewSet):
    """HSE Compliance API"""
    permission_classes = [IsAuthenticated]
    queryset = HSECompliance.objects.all()
    
    def list(self, request):
        """Get compliance records with filtering"""
        try:
            status_filter = request.query_params.get('status')
            compliance_type = request.query_params.get('compliance_type')
            business_unit_id = request.query_params.get('business_unit_id')
            
            queryset = self.queryset
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            if compliance_type:
                queryset = queryset.filter(compliance_type=compliance_type)
            
            if business_unit_id:
                queryset = queryset.filter(business_unit_id=business_unit_id)
            
            # Convert choice fields to readable format
            def get_compliance_type_display(compliance_type):
                type_map = {
                    'environmental_permit': 'Environmental Permit',
                    'safety_regulation': 'Safety Regulation',
                    'health_standard': 'Health Standard',
                    'waste_management': 'Waste Management',
                    'emission_control': 'Emission Control',
                    'water_quality': 'Water Quality'
                }
                return type_map.get(compliance_type, compliance_type.replace('_', ' ').title())
            
            def get_status_display(status):
                status_map = {
                    'compliant': 'Compliant',
                    'non_compliant': 'Non-Compliant',
                    'pending_review': 'Pending Review',
                    'under_investigation': 'Under Investigation'
                }
                return status_map.get(status, status.replace('_', ' ').title())
            
            data = []
            for item in queryset:
                data.append({
                    'id': item.id,
                    'title': item.title,
                    'compliance_type': get_compliance_type_display(item.compliance_type),
                    'status': get_status_display(item.status),
                    'business_unit': {
                        'id': item.business_unit.id,
                        'name': item.business_unit.name
                    } if item.business_unit else None,
                    'permit_number': item.permit_number,
                    'issue_date': item.issue_date,
                    'expiry_date': item.expiry_date,
                    'renewal_date': item.renewal_date,
                    'responsible_person': {
                        'id': item.responsible_person.id,
                        'name': f"{item.responsible_person.first_name} {item.responsible_person.last_name}"
                    } if item.responsible_person else None,
                    'requirements': item.requirements,
                    'current_status': item.current_status,
                    'violations': item.violations,
                    'corrective_actions': item.corrective_actions,
                    'last_audit': item.last_audit,
                    'next_audit': item.next_audit
                })
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get compliance dashboard data"""
        try:
            # Get compliance statistics
            total_compliance = HSECompliance.objects.count()
            compliant_records = HSECompliance.objects.filter(status='compliant').count()
            non_compliant_records = HSECompliance.objects.filter(status='non_compliant').count()
            
            # Get expiring permits (within 30 days)
            expiring_soon = HSECompliance.objects.filter(
                expiry_date__lte=timezone.now().date() + timedelta(days=30)
            ).count()
            
            # Get compliance by type
            compliance_by_type = HSECompliance.objects.values('compliance_type').annotate(
                count=Count('id')
            )
            
            # Get compliance by status
            compliance_by_status = HSECompliance.objects.values('status').annotate(
                count=Count('id')
            )
            
            # Get expiring permits
            expiring_permits = HSECompliance.objects.filter(
                expiry_date__lte=timezone.now().date() + timedelta(days=30)
            ).order_by('expiry_date')[:5]
            
            # Convert choice fields to readable format
            def get_compliance_type_display(compliance_type):
                type_map = {
                    'environmental_permit': 'Environmental Permit',
                    'safety_regulation': 'Safety Regulation',
                    'health_standard': 'Health Standard',
                    'waste_management': 'Waste Management',
                    'emission_control': 'Emission Control',
                    'water_quality': 'Water Quality'
                }
                return type_map.get(compliance_type, compliance_type.replace('_', ' ').title())
            
            def get_status_display(status):
                status_map = {
                    'compliant': 'Compliant',
                    'non_compliant': 'Non-Compliant',
                    'pending_review': 'Pending Review',
                    'under_investigation': 'Under Investigation'
                }
                return status_map.get(status, status.replace('_', ' ').title())
            
            dashboard_data = {
                'total_compliance': total_compliance,
                'compliant_records': compliant_records,
                'non_compliant_records': non_compliant_records,
                'compliance_rate': round((compliant_records / total_compliance * 100) if total_compliance > 0 else 0, 2),
                'expiring_soon': expiring_soon,
                'compliance_by_type': [
                    {
                        'type': get_compliance_type_display(item['compliance_type']),
                        'count': item['count']
                    } for item in compliance_by_type
                ],
                'compliance_by_status': [
                    {
                        'status': get_status_display(item['status']),
                        'count': item['count']
                    } for item in compliance_by_status
                ],
                'expiring_permits': [
                    {
                        'id': item.id,
                        'title': item.title,
                        'compliance_type': get_compliance_type_display(item.compliance_type),
                        'expiry_date': item.expiry_date,
                        'days_remaining': (item.expiry_date - timezone.now().date()).days
                    } for item in expiring_permits
                ]
            }
            
            return Response(dashboard_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HSETrainingViewSet(viewsets.ModelViewSet):
    """HSE Training API"""
    permission_classes = [IsAuthenticated]
    queryset = HSETraining.objects.all()
    
    def list(self, request):
        """Get training records with filtering"""
        try:
            status_filter = request.query_params.get('status')
            training_type = request.query_params.get('training_type')
            employee_id = request.query_params.get('employee_id')
            
            queryset = self.queryset
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            if training_type:
                queryset = queryset.filter(training_type=training_type)
            
            if employee_id:
                queryset = queryset.filter(employee_id=employee_id)
            
            # Convert choice fields to readable format
            def get_training_type_display(training_type):
                type_map = {
                    'safety_training': 'Safety Training',
                    'environmental_training': 'Environmental Training',
                    'compliance_training': 'Compliance Training',
                    'equipment_training': 'Equipment Training',
                    'emergency_response': 'Emergency Response'
                }
                return type_map.get(training_type, training_type.replace('_', ' ').title())
            
            def get_status_display(status):
                status_map = {
                    'scheduled': 'Scheduled',
                    'in_progress': 'In Progress',
                    'completed': 'Completed',
                    'overdue': 'Overdue',
                    'cancelled': 'Cancelled'
                }
                return status_map.get(status, status.replace('_', ' ').title())
            
            data = []
            for item in queryset:
                data.append({
                    'id': item.id,
                    'title': item.title,
                    'training_type': get_training_type_display(item.training_type),
                    'status': get_status_display(item.status),
                    'employee': {
                        'id': item.employee.id,
                        'name': f"{item.employee.first_name} {item.employee.last_name}"
                    } if item.employee else None,
                    'trainer': {
                        'id': item.trainer.id,
                        'name': f"{item.trainer.first_name} {item.trainer.last_name}"
                    } if item.trainer else None,
                    'scheduled_date': item.scheduled_date,
                    'completed_date': item.completed_date,
                    'due_date': item.due_date,
                    'duration_hours': float(item.duration_hours) if item.duration_hours else None,
                    'certification_number': item.certification_number,
                    'certification_expiry': item.certification_expiry,
                    'score': float(item.score) if item.score else None,
                    'notes': item.notes
                })
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get training dashboard data"""
        try:
            # Get training statistics
            total_trainings = HSETraining.objects.count()
            completed_trainings = HSETraining.objects.filter(status='completed').count()
            overdue_trainings = HSETraining.objects.filter(status='overdue').count()
            scheduled_trainings = HSETraining.objects.filter(status='scheduled').count()
            
            # Get training by type
            training_by_type = HSETraining.objects.values('training_type').annotate(
                count=Count('id')
            )
            
            # Get training by status
            training_by_status = HSETraining.objects.values('status').annotate(
                count=Count('id')
            )
            
            # Get overdue trainings
            overdue_list = HSETraining.objects.filter(
                due_date__lt=timezone.now()
            ).order_by('due_date')[:5]
            
            # Convert choice fields to readable format
            def get_training_type_display(training_type):
                type_map = {
                    'safety_training': 'Safety Training',
                    'environmental_training': 'Environmental Training',
                    'compliance_training': 'Compliance Training',
                    'equipment_training': 'Equipment Training',
                    'emergency_response': 'Emergency Response'
                }
                return type_map.get(training_type, training_type.replace('_', ' ').title())
            
            def get_status_display(status):
                status_map = {
                    'scheduled': 'Scheduled',
                    'in_progress': 'In Progress',
                    'completed': 'Completed',
                    'overdue': 'Overdue',
                    'cancelled': 'Cancelled'
                }
                return status_map.get(status, status.replace('_', ' ').title())
            
            dashboard_data = {
                'total_trainings': total_trainings,
                'completed_trainings': completed_trainings,
                'overdue_trainings': overdue_trainings,
                'scheduled_trainings': scheduled_trainings,
                'completion_rate': round((completed_trainings / total_trainings * 100) if total_trainings > 0 else 0, 2),
                'training_by_type': [
                    {
                        'type': get_training_type_display(item['training_type']),
                        'count': item['count']
                    } for item in training_by_type
                ],
                'training_by_status': [
                    {
                        'status': get_status_display(item['status']),
                        'count': item['count']
                    } for item in training_by_status
                ],
                'overdue_list': [
                    {
                        'id': item.id,
                        'title': item.title,
                        'training_type': get_training_type_display(item.training_type),
                        'employee': f"{item.employee.first_name} {item.employee.last_name}" if item.employee else 'Unknown',
                        'due_date': item.due_date,
                        'days_overdue': (timezone.now().date() - item.due_date.date()).days
                    } for item in overdue_list
                ]
            }
            
            return Response(dashboard_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HSEReportsViewSet(viewsets.ViewSet):
    """HSE Reports API - Virtual ViewSet for generating reports"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get available reports"""
        try:
            reports = [
                {
                    'id': 1,
                    'title': 'Environmental Compliance Report',
                    'type': 'environmental',
                    'description': 'Monthly environmental compliance summary',
                    'generated_date': timezone.now().date(),
                    'status': 'available'
                },
                {
                    'id': 2,
                    'title': 'Safety Incident Summary',
                    'type': 'safety',
                    'description': 'Quarterly safety incident analysis',
                    'generated_date': timezone.now().date(),
                    'status': 'available'
                },
                {
                    'id': 3,
                    'title': 'Equipment Maintenance Report',
                    'type': 'equipment',
                    'description': 'Monthly equipment status report',
                    'generated_date': timezone.now().date(),
                    'status': 'available'
                }
            ]
            
            return Response(reports, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get reports dashboard data"""
        try:
            # Generate report statistics
            total_reports = 3
            environmental_reports = 1
            safety_reports = 1
            equipment_reports = 1
            
            # Get recent reports
            recent_reports = [
                {
                    'id': 1,
                    'title': 'Environmental Compliance Report',
                    'type': 'Environmental',
                    'generated_date': timezone.now().date(),
                    'status': 'completed'
                },
                {
                    'id': 2,
                    'title': 'Safety Incident Summary',
                    'type': 'Safety',
                    'generated_date': timezone.now().date() - timedelta(days=7),
                    'status': 'completed'
                },
                {
                    'id': 3,
                    'title': 'Equipment Maintenance Report',
                    'type': 'Equipment',
                    'generated_date': timezone.now().date() - timedelta(days=14),
                    'status': 'completed'
                }
            ]
            
            dashboard_data = {
                'total_reports': total_reports,
                'environmental_reports': environmental_reports,
                'safety_reports': safety_reports,
                'equipment_reports': equipment_reports,
                'recent_reports': recent_reports
            }
            
            return Response(dashboard_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HSEAlertsViewSet(viewsets.ViewSet):
    """HSE Alerts API - Virtual ViewSet for alerts"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get HSE alerts"""
        try:
            alerts = [
                {
                    'id': 1,
                    'title': 'High PM2.5 Levels Detected',
                    'type': 'environmental',
                    'severity': 'high',
                    'description': 'PM2.5 levels exceeded threshold at Inspection Point 1',
                    'created_date': timezone.now(),
                    'status': 'active'
                },
                {
                    'id': 2,
                    'title': 'Equipment Calibration Due',
                    'type': 'equipment',
                    'severity': 'medium',
                    'description': 'Air Monitor 3 requires calibration within 7 days',
                    'created_date': timezone.now() - timedelta(hours=2),
                    'status': 'active'
                },
                {
                    'id': 3,
                    'title': 'Safety Training Overdue',
                    'type': 'training',
                    'severity': 'medium',
                    'description': '5 employees have overdue safety training',
                    'created_date': timezone.now() - timedelta(hours=4),
                    'status': 'active'
                }
            ]
            
            return Response(alerts, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get alerts dashboard data"""
        try:
            # Generate alert statistics
            total_alerts = 3
            active_alerts = 3
            resolved_alerts = 0
            
            # Get alerts by type
            alerts_by_type = [
                {'type': 'Environmental', 'count': 1},
                {'type': 'Equipment', 'count': 1},
                {'type': 'Training', 'count': 1}
            ]
            
            # Get alerts by severity
            alerts_by_severity = [
                {'severity': 'High', 'count': 1},
                {'severity': 'Medium', 'count': 2},
                {'severity': 'Low', 'count': 0}
            ]
            
            # Get recent alerts
            recent_alerts = [
                {
                    'id': 1,
                    'title': 'High PM2.5 Levels Detected',
                    'type': 'Environmental',
                    'severity': 'High',
                    'created_date': timezone.now(),
                    'status': 'Active'
                },
                {
                    'id': 2,
                    'title': 'Equipment Calibration Due',
                    'type': 'Equipment',
                    'severity': 'Medium',
                    'created_date': timezone.now() - timedelta(hours=2),
                    'status': 'Active'
                },
                {
                    'id': 3,
                    'title': 'Safety Training Overdue',
                    'type': 'Training',
                    'severity': 'Medium',
                    'created_date': timezone.now() - timedelta(hours=4),
                    'status': 'Active'
                }
            ]
            
            dashboard_data = {
                'total_alerts': total_alerts,
                'active_alerts': active_alerts,
                'resolved_alerts': resolved_alerts,
                'alerts_by_type': alerts_by_type,
                'alerts_by_severity': alerts_by_severity,
                'recent_alerts': recent_alerts
            }
            
            return Response(dashboard_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
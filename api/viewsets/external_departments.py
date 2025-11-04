from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
import requests
import json
from django.conf import settings
from django.utils import timezone
from django.db.models import Max

from inspection_management.models import Evince, ExternalDepartment, ExternalDepartmentAssignment, DataGroup
from api.serializers.external_departments import (
    ExternalDepartmentSerializer,
    ExternalDepartmentAssignmentSerializer
)
from utils.sql_server_connection import SQLServerConnection
from api.mixins import DataGroupFilterMixin
from users.authorization import role_required
from users.models.audit_history import AuditHistory


@method_decorator(role_required(allowed_roles=["Admin"]), name="dispatch")
class ExternalDepartmentViewSet(DataGroupFilterMixin, viewsets.ModelViewSet):
    """ViewSet for managing external departments and their assignments"""
    
    queryset = ExternalDepartment.objects.all()
    serializer_class = ExternalDepartmentSerializer
    permission_classes = [IsAuthenticated]
    data_group_field = 'group'
    apply_to_admin = True
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        
        # Convert group name to ID
        if 'group' in data and isinstance(data['group'], str):
            try:
                group = DataGroup.objects.get(name__iexact=data['group'])
                data['group'] = group.id
            except DataGroup.DoesNotExist:
                return Response(
                    {"group": [f"Data group '{data['group']}' not found"]},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        department = serializer.save(created_by=request.user)

        AuditHistory.objects.create(
            user=request.user, 
            action=f"Created department: {department.name}"
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = request.data.copy()
        
        # Convert group name to ID if provided
        if 'group' in data and isinstance(data['group'], str):
            try:
                group = DataGroup.objects.get(name__iexact=data['group'])
                data['group'] = group.id
            except DataGroup.DoesNotExist:
                return Response(
                    {"group": [f"Data group '{data['group']}' not found"]},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        department = serializer.save()

        AuditHistory.objects.create(
            user=request.user,
            action=f"Updated department: {department.name}"
        )

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        name = instance.name

        AuditHistory.objects.create(
            user=request.user, 
            action=f"Deleted department: {name}"
        )

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'], url_path='fetch-from-lw8')
    def fetch_from_lw8(self, request):
        """Fetch departments from LW8Process database"""
        try:
            # Connect to SQL Server and fetch departments
            sql_conn = SQLServerConnection()
            lw8_departments = sql_conn.fetch_external_departments()
            
            # Sync with local database
            synced_count = 0
            for dept_data in lw8_departments:
                try:
                    dept, created = ExternalDepartment.objects.update_or_create(
                        external_system_id=dept_data['external_system_id'],
                        defaults={
                            'name': dept_data['name'],
                            'department_type': dept_data['department_type'],
                            'description': dept_data['description'],
                            'external_system_url': dept_data.get('external_system_url', ''),
                            'contact_person': dept_data.get('contact_person', ''),
                            'contact_email': dept_data.get('contact_email', ''),
                            'contact_phone': dept_data.get('contact_phone', ''),
                            'capabilities': dept_data.get('capabilities', []),
                            'specializations': dept_data.get('specializations', []),
                            'status': dept_data.get('status', 'ACTIVE'),
                            'is_available': dept_data.get('is_available', True),
                            'max_concurrent_assignments': dept_data.get('max_concurrent_assignments', 5),
                            'created_by': request.user
                        }
                    )
                    if created:
                        synced_count += 1
                except Exception as e:
                    print(f"Error creating department {dept_data['name']}: {str(e)}")
                    continue
            
            return Response({
                'message': f'Successfully synced {synced_count} new departments from LW8Process',
                'total_departments': len(lw8_departments),
                'synced_count': synced_count
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch departments from LW8Process: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='available-for-assignment')
    def available_for_assignment(self, request):
        """Get departments available for new assignments (filtered by user's data groups)"""
        # Use get_queryset() to apply data group filtering automatically
        queryset = self.get_queryset().filter(
            status='ACTIVE',
            is_available=True
        )
        
        # Filter by assignment type if specified
        assignment_type = request.query_params.get('assignment_type')
        if assignment_type:
            queryset = queryset.filter(assignment_type=assignment_type)
        
        # Filter by department type if specified
        dept_type = request.query_params.get('department_type')
        if dept_type:
            queryset = queryset.filter(department_type=dept_type)
        
        # Filter by capabilities if specified
        capability = request.query_params.get('capability')
        if capability:
            queryset = queryset.filter(capabilities__contains=capability)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='users')
    def get_department_users(self, request, pk=None):
        """Get users associated with a specific external department"""
        try:
            department = self.get_object()
            
            # Return department contact information as "users"
            users = []
            if department.contact_person:
                users.append({
                    'id': department.id,
                    'name': department.contact_person,
                    'email': department.contact_email or '',
                    'role': 'Contact Person'
                })
            
            # If department has external_system_id, we could potentially fetch more users
            # from the external system, but for now we'll return the contact person
            
            return Response(users)
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch department users: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='assign-evinces')
    def assign_evinces(self, request, pk=None):
        """Assign multiple evinces to this external department"""
        external_dept = self.get_object()
        
        print(f"🔍 Assignment request received:")
        print(f"  - Department ID: {pk}")
        print(f"  - Department: {external_dept.name}")
        print(f"  - User: {request.user.username}")
        print(f"  - Request data: {request.data}")
        
        # Check if user has manager permissions
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name.upper() not in ['ADMIN', 'MANAGER']:
            return Response(
                {'error': 'Only managers can assign evinces to external departments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        evince_ids = request.data.get('evince_ids', [])
        if not evince_ids:
            return Response(
                {'error': 'evince_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Convert evince_ids to integers if they're strings
        try:
            evince_ids = [int(eid) for eid in evince_ids]
        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Invalid evince_ids format: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get evinces
        evinces = Evince.objects.filter(
            id__in=evince_ids,
            evince_type='hse_risk_management',
            status='RiskValidated'
        )
        
        if not evinces.exists():
            # Check what evinces actually exist for debugging
            all_evinces = Evince.objects.filter(id__in=evince_ids)
            evince_details = []
            for e in all_evinces:
                evince_details.append({
                    'id': e.id,
                    'name': e.name,
                    'evince_type': e.evince_type,
                    'status': e.status
                })
            
            return Response(
                {
                    'error': 'No valid evinces found for assignment. Evinces must have status "RiskValidated" and type "hse_risk_management"',
                    'evince_details': evince_details,
                    'required_status': 'RiskValidated',
                    'required_type': 'hse_risk_management'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse target completion date
        target_completion_date_str = request.data.get('target_completion_date')
        target_completion_date = None
        if target_completion_date_str:
            try:
                print(f"Parsing date: {target_completion_date_str}")
                # Parse ISO 8601 string to datetime
                target_completion_date = timezone.datetime.fromisoformat(target_completion_date_str.replace('Z', '+00:00'))
                print(f"Parsed date: {target_completion_date}")
            except ValueError as e:
                print(f"Date parsing error: {e}")
                return Response(
                    {
                        'error': 'Invalid target_completion_date format. Use ISO 8601 (e.g., 2025-09-20T10:00:00Z)',
                        'received_date': target_completion_date_str,
                        'parsing_error': str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create assignments
        assignments = []
        for evince in evinces:
            # Check if assignment already exists
            # Auto-generate external_task_id if not provided
            external_task_id = request.data.get('external_task_id', '')
            if not external_task_id:
                # Generate sequential mitigation ID
                existing_assignments = ExternalDepartmentAssignment.objects.filter(
                    external_task_id__startswith='Mitigation-EID-'
                ).values_list('external_task_id', flat=True)
                
                max_id = 0
                for task_id in existing_assignments:
                    try:
                        if task_id and task_id.startswith('Mitigation-EID-'):
                            number_str = task_id.replace('Mitigation-EID-', '')
                            number = int(number_str)
                            if number > max_id:
                                max_id = number
                    except (ValueError, AttributeError):
                        continue
                
                external_task_id = f'Mitigation-EID-{max_id + 1}'
                print(f"🔢 Auto-generated external_task_id: {external_task_id}")

            assignment, created = ExternalDepartmentAssignment.objects.get_or_create(
                evince=evince,
                external_department=external_dept,
                defaults={
                    'assigned_by': request.user,
                    'target_completion_date': target_completion_date,
                    'notes': request.data.get('notes', ''),
                    'external_task_id': external_task_id,
                    'priority': request.data.get('priority', 'MEDIUM'),
                    'assigned_user': request.data.get('assigned_user', '')
                }
            )
            
            # Only send to external system if it's a new assignment
            if created:
                # Send assignment to external system (LW8Process)
                external_success = self.send_assignment_to_external_system(assignment, external_dept)
                
                if external_success:
                    # Update status to MitigationInProgress after successful external system upload
                    evince.status = 'MitigationInProgress'
                    evince.assigned_department = external_dept.name
                    evince.save()
                    print(f"Created new assignment for evince {evince.id}, status updated to MitigationInProgress, assigned to {external_dept.name}")
                else:
                    # Keep as RiskValidated if external system upload failed
                    evince.status = 'RiskValidated'
                    evince.assigned_department = external_dept.name
                    evince.save()
                    print(f"Created new assignment for evince {evince.id}, external upload failed, status remains RiskValidated, assigned to {external_dept.name}")
            else:
                print(f"Assignment already exists for evince {evince.id}, skipping external system submission")
            
            assignments.append(assignment)
        
        serializer = ExternalDepartmentAssignmentSerializer(assignments, many=True)
        return Response({
            'message': f'Successfully assigned {len(assignments)} evinces to {external_dept.name}',
            'assignments': serializer.data
        })
    
    @action(detail=True, methods=['post'], url_path='update-mitigation-work')
    def update_mitigation_work(self, request, pk=None):
        """Update mitigation work details for an assignment"""
        assignment = self.get_object()
        
        # Validate that user is assigned for mitigation or has manager permissions
        if (assignment.external_department.contact_person != request.user.username and 
            not hasattr(request.user, 'userprofile') or 
            request.user.userprofile.role.name.upper() not in ['ADMIN', 'MANAGER']):
            return Response(
                {'error': 'Only assigned mitigation user or managers can update mitigation work'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update mitigation fields
        if 'completion_notes' in request.data:
            assignment.completion_notes = request.data['completion_notes']
        
        if 'mitigation_actions' in request.data:
            assignment.mitigation_actions = request.data['mitigation_actions']
        
        if 'evidence_data' in request.data:
            assignment.evidence_data = request.data['evidence_data']
        
        if 'cost_incurred' in request.data:
            assignment.cost_incurred = request.data['cost_incurred']
        
        # Update status
        if 'status' in request.data:
            assignment.status = request.data['status']
        
        assignment.save()
        
        # Update evince status based on assignment status
        evince = assignment.evince
        if assignment.status == 'COMPLETED':
            evince.status = 'LIMSCompleted'
            evince.hse_mitigation_completed = True
            evince.hse_mitigation_evidence = assignment.mitigation_actions
        elif assignment.status == 'IN_PROGRESS':
            evince.status = 'LIMSInProgress'
        
        evince.save()
        
        # Update external system if needed
        self.update_external_system_status(assignment)
        
        serializer = ExternalDepartmentAssignmentSerializer(assignment)
        return Response({
            'message': 'Mitigation work updated successfully',
            'assignment': serializer.data
        })
    
    def update_external_system_status(self, assignment):
        """Update status in external system (SQL Server)"""
        try:
            from utils.sql_server_connection import SQLServerConnection
            
            sql_conn = SQLServerConnection()
            with sql_conn as conn:
                cursor = conn.cursor()
                
                # Update the assignment status in SQL Server
                cursor.execute("""
                    UPDATE IMSAssignments 
                    SET status = ?, 
                        completion_notes = ?,
                        mitigation_actions = ?,
                        evidence_data = ?,
                        cost_incurred = ?
                    WHERE ims_evince_id = ? AND external_department_id = (
                        SELECT id FROM ExternalDepartments 
                        WHERE external_system_id = ?
                    )
                """, (
                    assignment.status,
                    assignment.completion_notes,
                    assignment.mitigation_actions,
                    json.dumps(assignment.evidence_data) if assignment.evidence_data else None,
                    assignment.cost_incurred,
                    assignment.evince.id,
                    assignment.external_department.external_system_id
                ))
                
                conn.commit()
                print(f"Updated external system status for assignment {assignment.id}")
                
        except Exception as e:
            print(f"Error updating external system status: {e}")
            # Don't fail the API call if external system update fails
    
    @action(detail=False, methods=['get'], url_path='fetch-updates-from-lw8')
    def fetch_updates_from_lw8(self, request):
        """Fetch updated mitigation work from LW8Process and sync to local database"""
        try:
            from utils.sql_server_connection import SQLServerConnection
            
            sql_conn = SQLServerConnection()
            with sql_conn as conn:
                cursor = conn.cursor()
                
                # Fetch assignments that have been updated in SQL Server
                cursor.execute("""
                    SELECT 
                        a.id as sql_server_id,
                        a.ims_evince_id,
                        a.status,
                        a.completion_notes,
                        a.mitigation_actions,
                        a.evidence_data,
                        a.cost_incurred,
                        a.target_completion_date,
                        d.external_system_id
                    FROM IMSAssignments a
                    INNER JOIN ExternalDepartments d ON a.external_department_id = d.id
                    WHERE a.status IN ('IN_PROGRESS', 'COMPLETED', 'FAILED')
                    ORDER BY a.id DESC
                """)
                
                columns = [column[0] for column in cursor.description]
                updates = []
                
                for row in cursor.fetchall():
                    update_data = dict(zip(columns, row))
                    if update_data['evidence_data']:
                        try:
                            update_data['evidence_data'] = json.loads(update_data['evidence_data'])
                        except:
                            update_data['evidence_data'] = {}
                    updates.append(update_data)
                
                # Sync updates to local database
                synced_count = 0
                for update in updates:
                    try:
                        # Find the local assignment
                        local_assignment = ExternalDepartmentAssignment.objects.filter(
                            evince_id=update['ims_evince_id'],
                            external_department__external_system_id=update['external_system_id']
                        ).first()
                        
                        if local_assignment:
                            # Update local assignment with SQL Server data
                            local_assignment.status = update['status']
                            local_assignment.completion_notes = update['completion_notes']
                            local_assignment.mitigation_actions = update['mitigation_actions']
                            local_assignment.evidence_data = update['evidence_data']
                            local_assignment.cost_incurred = update['cost_incurred']
                            local_assignment.save()
                            
                            # Update evince status based on assignment status
                            evince = local_assignment.evince
                            if update['status'] == 'COMPLETED':
                                evince.status = 'LIMSCompleted'
                                evince.hse_mitigation_completed = True
                                evince.hse_mitigation_evidence = update['mitigation_actions']
                            elif update['status'] == 'IN_PROGRESS':
                                evince.status = 'LIMSInProgress'
                            elif update['status'] == 'FAILED':
                                evince.status = 'Rejected'
                                evince.hse_risk_rejection_reason = update['completion_notes']
                            
                            evince.save()
                            synced_count += 1
                            
                    except Exception as e:
                        print(f"Error syncing assignment {update['ims_evince_id']}: {e}")
                        continue
                
                return Response({
                    'message': f'Successfully synced {synced_count} assignments from LW8Process',
                    'total_updates': len(updates),
                    'synced_count': synced_count,
                    'updates': updates
                })
                
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch updates from LW8Process: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='manager-review')
    def manager_review(self, request, pk=None):
        """Manager reviews and approves/rejects the mitigation work"""
        assignment = self.get_object()
        
        # Check if user has manager permissions
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name.upper() not in ['ADMIN', 'MANAGER']:
            return Response(
                {'error': 'Only managers can review mitigation work'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate required fields
        if 'approval_status' not in request.data:
            return Response(
                {'error': 'Missing required field: approval_status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approval_status = request.data['approval_status']
        review_notes = request.data.get('review_notes', '')
        
        evince = assignment.evince
        
        if approval_status == 'APPROVED':
            evince.status = 'Approved'
            evince.hse_approved_by = request.user
            evince.hse_approved_at = timezone.now()
            evince.hse_risk_closed = True
        elif approval_status == 'REJECTED':
            evince.status = 'Rejected'
            evince.hse_risk_rejection_reason = review_notes
        else:
            return Response(
                {'error': 'Invalid approval_status. Use APPROVED or REJECTED'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        evince.save()
        
        # Update external system status
        self.update_external_system_status(assignment)
        
        return Response({
            'message': f'Mitigation work {approval_status.lower()} successfully',
            'evince_status': evince.status,
            'assignment_id': assignment.id
        })
    
    @action(detail=True, methods=['get'], url_path='evince-mitigation-details')
    def evince_mitigation_details(self, request, pk=None):
        """Get complete evince and mitigation details for manager review"""
        assignment = self.get_object()
        
        # Check if user has manager permissions
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name.upper() not in ['ADMIN', 'MANAGER']:
            return Response(
                {'error': 'Only managers can view evince mitigation details'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        evince = assignment.evince
        
        # Get parameter results for this evince
        parameter_results = []
        try:
            from inspection_management.models import InspectionResult
            results = InspectionResult.objects.filter(evince=evince).select_related(
                'inspection_test__inspection_analysis'
            )
            for result in results:
                # Get parameter name safely through relationships
                parameter_name = None
                parameter_description = None
                try:
                    # Try to get parameter name from the first parameter in the analysis
                    first_param = result.inspection_test.inspection_analysis.parameter_set.first()
                    if first_param:
                        parameter_name = first_param.name
                        parameter_description = first_param.description
                    else:
                        # Fallback to analysis name if no parameters
                        parameter_name = result.inspection_test.inspection_analysis.name
                except Exception as param_error:
                    print(f"Error getting parameter name for result {result.id}: {param_error}")
                    parameter_name = "Unknown Parameter"
                
                parameter_results.append({
                    'parameter_name': parameter_name,
                    'parameter_description': parameter_description,
                    'entered_value': result.entered_value,
                    'comments': result.comments,
                    'status': result.status,
                    'changed_on': result.changed_on.isoformat() if result.changed_on else None,
                    'inspection_analysis': result.inspection_test.inspection_analysis.name if result.inspection_test.inspection_analysis else None
                })
        except Exception as e:
            print(f"Error fetching parameter results: {e}")
        
        # Get inspection analyses
        inspection_analyses = []
        for analysis in evince.inspection_analyses.all():
            inspection_analyses.append({
                'id': analysis.id,
                'name': analysis.name,
                'description': analysis.description
            })
        
        # Prepare complete response
        response_data = {
            'assignment': {
                'id': assignment.id,
                'assigned_at': assignment.assigned_at.isoformat(),
                'target_completion_date': assignment.target_completion_date.isoformat() if assignment.target_completion_date else None,
                'status': assignment.status,
                'status_display': assignment.get_status_display(),
                'notes': assignment.notes,
                'completion_notes': assignment.completion_notes,
                'mitigation_actions': assignment.mitigation_actions,
                'evidence_data': assignment.evidence_data,
                'cost_incurred': assignment.cost_incurred,
                'external_task_id': assignment.external_task_id,
                'external_status': assignment.external_status,
                'last_sync_at': assignment.last_sync_at.isoformat() if assignment.last_sync_at else None
            },
            'evince': {
                'id': evince.id,
                'name': evince.name,
                'description': evince.description,
                'evince_type': evince.evince_type,
                'evince_type_display': evince.get_evince_type_display(),
                'status': evince.status,
                'status_display': evince.get_status_display(),
                'created_at': evince.changed_on.isoformat(),
                'start_date_time': evince.start_date_time.isoformat() if evince.start_date_time else None,
                'end_date_time': evince.end_date_time.isoformat() if evince.end_date_time else None,
                
                # HSE Risk Assessment details
                'hse_risk_level': evince.hse_risk_level,
                'hse_risk_category': evince.hse_risk_category,
                'hse_risk_notes': evince.hse_risk_notes,
                'hse_observation_details': evince.hse_observation_details,
                'hse_out_of_spec_results': evince.hse_out_of_spec_results,
                'hse_risk_valid': evince.hse_risk_valid,
                'hse_inspection_date': evince.hse_inspection_date.isoformat() if evince.hse_inspection_date else None,
                'hse_mitigation_completed': evince.hse_mitigation_completed,
                'hse_mitigation_evidence': evince.hse_mitigation_evidence,
                'hse_risk_closed': evince.hse_risk_closed,
                'hse_risk_rejection_reason': evince.hse_risk_rejection_reason,
                'hse_approved_at': evince.hse_approved_at.isoformat() if evince.hse_approved_at else None,
                
                # Related objects
                'business_unit': {
                    'id': evince.business_unit.id,
                    'name': evince.business_unit.name,
                    'description': evince.business_unit.description
                } if evince.business_unit else None,
                'inspection_point': {
                    'id': evince.inspection_point.id,
                    'name': evince.inspection_point.name,
                    'description': evince.inspection_point.description
                } if evince.inspection_point else None,
                'assigned_to': {
                    'id': evince.assigned_to.id,
                    'username': evince.assigned_to.username,
                    'first_name': evince.assigned_to.first_name,
                    'last_name': evince.assigned_to.last_name
                } if evince.assigned_to else None,
                'hse_approved_by': {
                    'id': evince.hse_approved_by.id,
                    'username': evince.hse_approved_by.username,
                    'first_name': evince.hse_approved_by.first_name,
                    'last_name': evince.hse_approved_by.last_name
                } if evince.hse_approved_by else None,
                'inspection_analyses': inspection_analyses,
                'parameter_results': parameter_results
            },
            'external_department': {
                'id': assignment.external_department.id,
                'name': assignment.external_department.name,
                'department_type': assignment.external_department.department_type,
                'department_type_display': assignment.external_department.get_department_type_display(),
                'description': assignment.external_department.description,
                'contact_person': assignment.external_department.contact_person,
                'contact_email': assignment.external_department.contact_email,
                'contact_phone': assignment.external_department.contact_phone,
                'capabilities': assignment.external_department.capabilities,
                'specializations': assignment.external_department.specializations,
                'external_system_id': assignment.external_department.external_system_id
            },
            'assigned_by': {
                'id': assignment.assigned_by.id,
                'username': assignment.assigned_by.username,
                'first_name': assignment.assigned_by.first_name,
                'last_name': assignment.assigned_by.last_name
            }
        }
        
        return Response(response_data)
    
    @action(detail=False, methods=['get'], url_path='all-risk-assessments')
    def all_risk_assessments(self, request):
        """Get all HSE Risk Assessment evinces with their mitigation details for manager review"""
        
        # Check if user has manager permissions
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name.upper() not in ['ADMIN', 'MANAGER']:
            return Response(
                {'error': 'Only managers can view all risk assessments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all HSE Risk Assessment evinces
        from inspection_management.models import Evince
        evinces = Evince.objects.filter(evince_type='hse_risk_management').order_by('-changed_on')
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            evinces = evinces.filter(status=status_filter)
        
        # Filter by risk level if provided
        risk_level = request.query_params.get('risk_level')
        if risk_level:
            evinces = evinces.filter(hse_risk_level=risk_level)
        
        # Filter by risk category if provided
        risk_category = request.query_params.get('risk_category')
        if risk_category:
            evinces = evinces.filter(hse_risk_category=risk_category)
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            evinces = evinces.filter(changed_on__date__gte=start_date)
        if end_date:
            evinces = evinces.filter(changed_on__date__lte=end_date)
        
        # Prepare response data
        risk_assessments = []
        
        for evince in evinces:
            # Get external assignments for this evince
            external_assignments = []
            for assignment in evince.external_assignments.all():
                external_assignments.append({
                    'id': assignment.id,
                    'external_department': {
                        'id': assignment.external_department.id,
                        'name': assignment.external_department.name,
                        'department_type': assignment.external_department.department_type,
                        'contact_person': assignment.external_department.contact_person,
                        'contact_email': assignment.external_department.contact_email
                    },
                    'assigned_at': assignment.assigned_at.isoformat(),
                    'target_completion_date': assignment.target_completion_date.isoformat() if assignment.target_completion_date else None,
                    'status': assignment.status,
                    'status_display': assignment.get_status_display(),
                    'completion_notes': assignment.completion_notes,
                    'mitigation_actions': assignment.mitigation_actions,
                    'evidence_data': assignment.evidence_data,
                    'cost_incurred': assignment.cost_incurred,
                    'external_task_id': assignment.external_task_id,
                    'last_sync_at': assignment.last_sync_at.isoformat() if assignment.last_sync_at else None
                })
            
            # Get parameter results for this evince
            parameter_results = []
            try:
                from inspection_management.models import InspectionResult
                results = InspectionResult.objects.filter(evince=evince).select_related(
                    'inspection_test__inspection_analysis'
                )
                for result in results:
                    # Get parameter name safely through relationships
                    parameter_name = None
                    parameter_description = None
                    try:
                        # Try to get parameter name from the first parameter in the analysis
                        first_param = result.inspection_test.inspection_analysis.parameter_set.first()
                        if first_param:
                            parameter_name = first_param.name
                            parameter_description = first_param.description
                        else:
                            # Fallback to analysis name if no parameters
                            parameter_name = result.inspection_test.inspection_analysis.name
                    except Exception as param_error:
                        print(f"Error getting parameter name for result {result.id}: {param_error}")
                        parameter_name = "Unknown Parameter"
                    
                    parameter_results.append({
                        'parameter_name': parameter_name,
                        'parameter_description': parameter_description,
                        'entered_value': result.entered_value,
                        'comments': result.comments,
                        'status': result.status,
                        'changed_on': result.changed_on.isoformat() if result.changed_on else None,
                        'inspection_analysis': result.inspection_test.inspection_analysis.name if result.inspection_test.inspection_analysis else None
                    })
            except Exception as e:
                print(f"Error fetching parameter results for evince {evince.id}: {e}")
            
            # Get inspection analyses
            inspection_analyses = []
            for analysis in evince.inspection_analyses.all():
                inspection_analyses.append({
                    'id': analysis.id,
                    'name': analysis.name,
                    'description': analysis.description
                })
            
            risk_assessment = {
                'evince': {
                    'id': evince.id,
                    'name': evince.name,
                    'description': evince.description,
                    'evince_type': evince.evince_type,
                    'evince_type_display': evince.get_evince_type_display(),
                    'status': evince.status,
                    'status_display': evince.get_status_display(),
                    'created_at': evince.changed_on.isoformat(),
                    'start_date_time': evince.start_date_time.isoformat() if evince.start_date_time else None,
                    'end_date_time': evince.end_date_time.isoformat() if evince.end_date_time else None,
                    
                    # HSE Risk Assessment details
                    'hse_risk_level': evince.hse_risk_level,
                    'hse_risk_category': evince.hse_risk_category,
                    'hse_risk_notes': evince.hse_risk_notes,
                    'hse_observation_details': evince.hse_observation_details,
                    'hse_out_of_spec_results': evince.hse_out_of_spec_results,
                    'hse_risk_valid': evince.hse_risk_valid,
                    'hse_inspection_date': evince.hse_inspection_date.isoformat() if evince.hse_inspection_date else None,
                    'hse_mitigation_completed': evince.hse_mitigation_completed,
                    'hse_mitigation_evidence': evince.hse_mitigation_evidence,
                    'hse_risk_closed': evince.hse_risk_closed,
                    'hse_risk_rejection_reason': evince.hse_risk_rejection_reason,
                    'hse_approved_at': evince.hse_approved_at.isoformat() if evince.hse_approved_at else None,
                    
                    # Related objects
                    'business_unit': {
                        'id': evince.business_unit.id,
                        'name': evince.business_unit.name,
                        'description': evince.business_unit.description
                    } if evince.business_unit else None,
                    'inspection_point': {
                        'id': evince.inspection_point.id,
                        'name': evince.inspection_point.name,
                        'description': evince.inspection_point.description
                    } if evince.inspection_point else None,
                    'assigned_to': {
                        'id': evince.assigned_to.id,
                        'username': evince.assigned_to.username,
                        'first_name': evince.assigned_to.first_name,
                        'last_name': evince.assigned_to.last_name
                    } if evince.assigned_to else None,
                    'hse_approved_by': {
                        'id': evince.hse_approved_by.id,
                        'username': evince.hse_approved_by.username,
                        'first_name': evince.hse_approved_by.first_name,
                        'last_name': evince.hse_approved_by.last_name
                    } if evince.hse_approved_by else None,
                    'inspection_analyses': inspection_analyses,
                    'parameter_results': parameter_results
                },
                'external_assignments': external_assignments,
                'has_external_assignments': len(external_assignments) > 0,
                'total_assignments': len(external_assignments),
                'completed_assignments': len([a for a in external_assignments if a['status'] == 'COMPLETED']),
                'total_cost': sum([a['cost_incurred'] for a in external_assignments if a['cost_incurred']])
            }
            
            risk_assessments.append(risk_assessment)
        
        # Add summary statistics
        summary = {
            'total_risk_assessments': len(risk_assessments),
            'by_status': {},
            'by_risk_level': {},
            'by_risk_category': {},
            'total_cost': sum([ra['total_cost'] for ra in risk_assessments]),
            'assignments_summary': {
                'total_assignments': sum([ra['total_assignments'] for ra in risk_assessments]),
                'completed_assignments': sum([ra['completed_assignments'] for ra in risk_assessments])
            }
        }
        
        # Calculate statistics
        for ra in risk_assessments:
            status = ra['evince']['status']
            risk_level = ra['evince']['hse_risk_level']
            risk_category = ra['evince']['hse_risk_category']
            
            summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
            summary['by_risk_level'][risk_level] = summary['by_risk_level'].get(risk_level, 0) + 1
            summary['by_risk_category'][risk_category] = summary['by_risk_category'].get(risk_category, 0) + 1
        
        return Response({
            'summary': summary,
            'risk_assessments': risk_assessments
        })
    
    def send_assignment_to_external_system(self, assignment, external_dept, is_update=False):
        """Send assignment data to external system (LW8Process)"""
        try:
            # Get complete evince details including parameter results
            evince = assignment.evince
            
            # Fetch parameter results for this evince
            parameter_results = []
            try:
                from inspection_management.models import InspectionResult
                results = InspectionResult.objects.filter(evince=evince)
                for result in results:
                    parameter_results.append({
                        'parameter_name': result.parameter_name,
                        'parameter_description': result.parameter_description,
                        'entered_value': result.entered_value,
                        'comments': result.comments,
                        'status': result.status,
                        'parameter_unit': result.parameter_unit,
                        'parameter_min_value': result.parameter_min_value,
                        'parameter_max_value': result.parameter_max_value
                    })
            except Exception as e:
                print(f"Error fetching parameter results: {str(e)}")
            
            # Prepare complete assignment data
            assignment_data = {
                'ims_evince_id': evince.id,
                'external_department_id': external_dept.external_system_id,  # Pass external_system_id, will be mapped to integer ID in SQL Server
                'assignment_type': 'HSE_RISK_MITIGATION',
                'assigned_by_ims_user_id': assignment.assigned_by.id,
                'assigned_at': assignment.assigned_at.isoformat(),
                'target_completion_date': assignment.target_completion_date.isoformat() if assignment.target_completion_date and hasattr(assignment.target_completion_date, 'isoformat') else None,
                'priority': 'MEDIUM',
                'assignment_data': {
                    # Basic evince info
                    'evince_id': evince.id,
                    'evince_name': evince.name,
                    'description': evince.description,
                    'evince_type': evince.evince_type,
                    'status': evince.status,
                    
                    # Risk assessment details
                    'risk_level': evince.hse_risk_level,
                    'risk_category': evince.hse_risk_category,
                    'observation_details': evince.hse_observation_details,
                    'out_of_spec_results': evince.hse_out_of_spec_results,
                    'risk_valid': evince.hse_risk_valid,
                    
                    # Business context
                    'business_unit': {
                        'id': evince.business_unit.id if evince.business_unit else None,
                        'name': evince.business_unit.name if evince.business_unit else None
                    },
                    'inspection_point': {
                        'id': evince.inspection_point.id if evince.inspection_point else None,
                        'name': evince.inspection_point.name if evince.inspection_point else None
                    },
                    
                    # Assignment details
                    'assigned_to': {
                        'id': evince.assigned_to.id if evince.assigned_to else None,
                        'username': evince.assigned_to.username if evince.assigned_to else None
                    },
                    'reviewed_by': {
                        'id': evince.reviewed_by.id if evince.reviewed_by else None,
                        'username': evince.reviewed_by.username if evince.reviewed_by else None
                    },
                    
                    # Dates
                    'start_date_time': evince.start_date_time.isoformat() if evince.start_date_time else None,
                    'end_date_time': evince.end_date_time.isoformat() if evince.end_date_time else None,
                    'changed_on': evince.changed_on.isoformat() if evince.changed_on else None,
                    
                    # Parameter results
                    'parameter_results': parameter_results,
                    
                    # Additional context
                    'critical_instructions': evince.crtical_instructions,
                    'reassigned': evince.reassigned
                },
                'risk_level': evince.hse_risk_level,
                'risk_category': evince.hse_risk_category,
                'status': 'ASSIGNED'
            }
            
            # Send to SQL Server
            sql_conn = SQLServerConnection()
            
            if is_update:
                # Update existing assignment
                success = sql_conn.update_ims_assignment(assignment_data, evince.id)
                if success:
                    print(f"Successfully updated assignment for {external_dept.name} (Evince ID: {evince.id})")
                    return True
                else:
                    print(f"Failed to update assignment for {external_dept.name} (Evince ID: {evince.id})")
                    return False
            else:
                # Create new assignment
                external_assignment_id = sql_conn.create_ims_assignment(assignment_data)
                
                # Update assignment with external task ID
                assignment.external_task_id = f"TASK_{external_assignment_id}_{external_dept.external_system_id}"
                assignment.external_status = 'ASSIGNED'
                assignment.save()
                
                print(f"Successfully sent assignment to {external_dept.name} (External ID: {external_assignment_id})")
                return True
            
        except Exception as e:
            print(f"Error sending assignment to external system: {str(e)}")
            return False
    
    @action(detail=False, methods=['get'], url_path='fetch-updates-from-lw8')
    def fetch_updates_from_lw8(self, request):
        """Fetch assignment updates from LW8Process database"""
        try:
            # Connect to SQL Server and fetch updates
            sql_conn = SQLServerConnection()
            lw8_updates = sql_conn.fetch_assignment_updates()
            
            updated_count = 0
            for update_data in lw8_updates:
                try:
                    # Find the assignment by external task ID or evince ID
                    assignment = None
                    if update_data.get('external_task_id'):
                        try:
                            assignment = ExternalDepartmentAssignment.objects.get(
                                external_task_id=update_data['external_task_id']
                            )
                        except ExternalDepartmentAssignment.DoesNotExist:
                            pass
                    
                    if not assignment and update_data.get('ims_evince_id'):
                        try:
                            assignment = ExternalDepartmentAssignment.objects.filter(
                                evince_id=update_data['ims_evince_id']
                            ).first()
                        except:
                            pass
                    
                    if not assignment:
                        print(f"Assignment not found for update: {update_data}")
                        continue
                    
                    # Debug: Check manager decision status
                    evince = assignment.evince
                    print(f"🔍 Sync Debug - Evince {evince.id}: current_status={evince.status}, manager_decision_final={evince.hse_manager_decision_final}")
                    
                    # Update assignment
                    assignment.external_status = update_data['status']
                    assignment.last_sync_at = timezone.now()
                    
                    if update_data['status'] == 'COMPLETED':
                        assignment.status = 'COMPLETED'
                        assignment.completion_notes = update_data.get('completion_notes', '')
                        assignment.mitigation_actions = update_data.get('mitigation_actions', '')
                        assignment.evidence_data = update_data.get('evidence_data', '')
                        assignment.cost_incurred = update_data.get('cost_incurred', 0)
                        
                        # Update evince - set to MitigationCompleted for manager review
                        evince = assignment.evince
                        evince.hse_mitigation_actions = update_data.get('mitigation_actions', '')
                        evince.hse_mitigation_evidence = update_data.get('evidence_data', '')
                        evince.hse_mitigation_completed = True
                        
                        # Only update status if manager hasn't made final decision
                        if not evince.hse_manager_decision_final:
                            evince.status = 'MitigationCompleted'
                            print(f"✅ Updated evince {evince.id} status to MitigationCompleted (manager decision pending)")
                        else:
                            print(f"⚠️ Skipped status update for evince {evince.id} - manager has made final decision: {evince.status}")
                        
                        evince.save()
                    elif update_data['status'] == 'IN_PROGRESS':
                        assignment.status = 'IN_PROGRESS'
                        evince = assignment.evince
                        
                        # Only update status if manager hasn't made final decision
                        if not evince.hse_manager_decision_final:
                            evince.status = 'LIMSInProgress'
                            print(f"✅ Updated evince {evince.id} status to LIMSInProgress (manager decision pending)")
                        else:
                            print(f"⚠️ Skipped status update for evince {evince.id} - manager has made final decision: {evince.status}")
                        
                        evince.save()
                    
                    assignment.save()
                    updated_count += 1
                    
                    print(f"Updated assignment {assignment.id} for evince {assignment.evince.id} - Status: {update_data['status']}")
                    
                except Exception as e:
                    print(f"Error updating assignment: {str(e)}")
                    continue
            
            return Response({
                'message': f'Successfully updated {updated_count} assignments from LW8Process',
                'updated_count': updated_count,
                'total_updates': len(lw8_updates)
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch updates from LW8Process: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='get-next-mitigation-id')
    def get_next_mitigation_id(self, request):
        """Get next sequential mitigation ID for HSE Risk Assessment assignments"""
        try:
            # Get all existing mitigation IDs and find the highest number
            assignments = ExternalDepartmentAssignment.objects.filter(
                external_task_id__startswith='Mitigation-EID-'
            ).values_list('external_task_id', flat=True)
            
            max_id = 0
            for task_id in assignments:
                try:
                    # Extract number from "Mitigation-EID-123" format
                    if task_id and task_id.startswith('Mitigation-EID-'):
                        number_str = task_id.replace('Mitigation-EID-', '')
                        number = int(number_str)
                        if number > max_id:
                            max_id = number
                except (ValueError, AttributeError):
                    continue
            
            # If no existing IDs, start from 1, otherwise increment
            next_id = max_id + 1
            
            return Response({
                'next_id': next_id,
                'message': f'Next mitigation ID: {next_id}',
                'existing_count': len(assignments)
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to generate next mitigation ID: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='assignments')
    def get_assignments(self, request):
        """Get existing assignments for a specific evince"""
        try:
            evince_id = request.query_params.get('evince_id')
            if not evince_id:
                return Response(
                    {'error': 'evince_id parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get assignments for the evince
            assignments = ExternalDepartmentAssignment.objects.filter(
                evince_id=evince_id
            ).select_related('external_department', 'assigned_by')
            
            # Serialize the data
            assignment_data = []
            for assignment in assignments:
                assignment_data.append({
                    'id': assignment.id,
                    'external_department': {
                        'id': assignment.external_department.id,
                        'name': assignment.external_department.name,
                        'department_type': assignment.external_department.department_type,
                        'contact_email': assignment.external_department.contact_email,
                        'contact_person': assignment.external_department.contact_person
                    },
                    'target_completion_date': assignment.target_completion_date.isoformat() if assignment.target_completion_date else None,
                    'notes': assignment.notes,
                    'priority': assignment.priority,
                    'external_task_id': assignment.external_task_id,
                    'assigned_user': assignment.assigned_user if assignment.assigned_user and assignment.assigned_user != 'None' else None,
                    'status': assignment.status,
                    'assigned_at': assignment.assigned_at.isoformat() if assignment.assigned_at else None,
                    'assigned_by': {
                        'id': assignment.assigned_by.id,
                        'username': assignment.assigned_by.username,
                        'email': assignment.assigned_by.email
                    },
                    # Add mitigation details
                    'completion_notes': assignment.completion_notes,
                    'mitigation_actions': assignment.mitigation_actions,
                    'evidence_data': assignment.evidence_data,
                    'cost_incurred': assignment.cost_incurred
                })
            
            return Response(assignment_data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch assignments: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

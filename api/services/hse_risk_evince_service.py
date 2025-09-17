from inspection_management.models.evince import Evince
from users.models.user import User
from django.utils import timezone
from django.db import transaction


class HSERiskEvinceService:
    """Service for HSE Risk Management workflow using Evince model"""
    
    # HSE Risk Management workflow states
    HSE_RISK_WORKFLOW_STATES = {
        'Logged': 'Inspection Logged',
        'InspectorReview': 'Inspector Review',
        'RiskValidated': 'Risk Validated',
        'ManagerAssignment': 'Manager Assignment',
        'LIMSInProgress': 'LIMS In Progress',
        'LIMSCompleted': 'LIMS Completed',
        'ManagerApproval': 'Manager Approval',
        'Completed': 'Completed',
        'Rejected': 'Rejected'
    }
    
    # Valid transitions for HSE Risk Management
    HSE_RISK_TRANSITIONS = {
        'Logged': ['InspectorReview', 'Rejected'],
        'InspectorReview': ['RiskValidated', 'Logged', 'Rejected'],
        'RiskValidated': ['ManagerAssignment', 'InspectorReview', 'Rejected'],
        'ManagerAssignment': ['LIMSInProgress', 'RiskValidated', 'Rejected'],
        'LIMSInProgress': ['LIMSCompleted', 'ManagerAssignment'],
        'LIMSCompleted': ['ManagerApproval', 'LIMSInProgress'],
        'ManagerApproval': ['Completed', 'Rejected', 'LIMSCompleted'],
        'Completed': [],
        'Rejected': ['Logged']
    }
    
    @staticmethod
    def create_hse_risk_evince(data, user):
        """Create HSE Risk Management evince"""
        try:
            with transaction.atomic():
                evince = Evince.objects.create(
                    name=data.get('name', ''),
                    description=data.get('description', ''),
                    evince_type='hse_risk_management',
                    business_unit_id=data.get('business_unit_id'),
                    inspection_point_id=data.get('inspection_point_id'),
                    logged_by=user,
                    changed_by=user,
                    reviewed_by_id=data.get('reviewed_by_id'),  # Inspector
                    status='Logged',
                    hse_inspection_date=data.get('inspection_date'),
                    hse_risk_category=data.get('risk_category', 'Safety'),
                    crtical_instructions=data.get('instructions', ''),
                    start_date_time=data.get('start_date_time'),
                    end_date_time=data.get('end_date_time'),
                )
                
                # Generate name if not provided
                if not evince.name:
                    evince.name = f"HSE_Risk_{evince.business_unit.name}_{evince.pk}"
                    evince.save()
                
                return evince
        except Exception as e:
            raise Exception(f"Error creating HSE Risk evince: {str(e)}")
    
    @staticmethod
    def get_hse_risk_evinces(filters=None):
        """Get all HSE Risk Management evinces"""
        queryset = Evince.objects.filter(evince_type='hse_risk_management')
        
        if filters:
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
            if filters.get('business_unit_id'):
                queryset = queryset.filter(business_unit_id=filters['business_unit_id'])
            if filters.get('logged_by_id'):
                queryset = queryset.filter(logged_by_id=filters['logged_by_id'])
            if filters.get('reviewed_by_id'):
                queryset = queryset.filter(reviewed_by_id=filters['reviewed_by_id'])
        
        return queryset.order_by('-changed_on')
    
    @staticmethod
    def can_transition_status(evince, new_status):
        """Check if status transition is valid for HSE Risk Management"""
        if evince.evince_type != 'hse_risk_management':
            return False
        
        current_status = evince.status
        valid_transitions = HSERiskEvinceService.HSE_RISK_TRANSITIONS.get(current_status, [])
        return new_status in valid_transitions
    
    @staticmethod
    def transition_status(evince, new_status, user, comments=None):
        """Transition HSE Risk evince to new status"""
        if not HSERiskEvinceService.can_transition_status(evince, new_status):
            raise ValueError(f"Invalid transition from {evince.status} to {new_status}")
        
        old_status = evince.status
        evince.status = new_status
        evince.changed_by = user
        evince.changed_on = timezone.now()
        
        # Set specific fields based on status
        if new_status == 'InspectorReview':
            evince.reviewed_by = user  # Inspector
        elif new_status == 'RiskValidated':
            pass  # Keep current reviewed_by (inspector)
        elif new_status == 'ManagerAssignment':
            pass  # Manager will assign
        elif new_status == 'LIMSInProgress':
            pass  # Sent to LIMS
        elif new_status == 'LIMSCompleted':
            pass  # LIMS completed
        elif new_status == 'ManagerApproval':
            evince.hse_approved_by = user
            evince.hse_approved_at = timezone.now()
        elif new_status == 'Completed':
            pass  # Final completion
        
        evince.save()
        
        return evince
    
    @staticmethod
    def inspector_review(evince, user, risk_assessment_data):
        """Handle inspector review of HSE Risk evince"""
        if evince.evince_type != 'hse_risk_management':
            raise ValueError("Invalid evince type for HSE Risk review")
        
        if evince.status not in ['Logged', 'InspectorReview']:
            raise ValueError(f"Invalid status for inspector review: {evince.status}")
        
        # Update risk assessment data
        evince.hse_risk_assessment = risk_assessment_data
        evince.hse_risk_notes = risk_assessment_data.get('notes', '')
        evince.hse_risk_valid = risk_assessment_data.get('risk_valid', True)
        evince.reviewed_by = user
        
        # Check for out-of-spec results
        out_of_spec_results = risk_assessment_data.get('out_of_spec_results', [])
        evince.hse_out_of_spec_results = out_of_spec_results
        
        # Check if there are out-of-spec results
        if out_of_spec_results and len(out_of_spec_results) > 0:
            # Out-of-spec results found - set risk level and assign to manager for mitigation
            evince.hse_risk_level = 'HIGH'  # Set risk level for out-of-spec results
            HSERiskEvinceService.transition_status(evince, 'ManagerAssignment', user, 'Out-of-spec results found - assigned to manager for mitigation')
            
            # Try to find a manager for the business unit
            try:
                from users.models.user import User
                from django.contrib.auth.models import Group
                
                # Get the Manager group
                manager_group = Group.objects.filter(name='Manager').first()
                if manager_group:
                    manager = User.objects.filter(
                        userprofile__role=manager_group,
                        userprofile__data_groups__in=[evince.business_unit.group]
                    ).first()
                    
                    if manager:
                        evince.reviewed_by = manager  # Assign to manager for review
                        evince.save()
            except Exception as e:
                print(f"Warning: Could not auto-assign to manager: {e}")
        else:
            # No out-of-spec results - set risk level and stay in InspectorReview for inspector to close
            evince.hse_risk_level = 'No Risk Validated'  # Set risk level for no risk
            HSERiskEvinceService.transition_status(evince, 'InspectorReview', user, 'No out-of-spec results - inspector can close assessment')
        
        return evince
    
    @staticmethod
    def manager_assignment(evince, user, assignment_data):
        """Handle manager assignment of HSE Risk evince"""
        if evince.evince_type != 'hse_risk_management':
            raise ValueError("Invalid evince type for manager assignment")
        
        if evince.status != 'ManagerAssignment':
            raise ValueError(f"Invalid status for manager assignment: {evince.status}")
        
        # Update assignment data
        if assignment_data.get('assigned_to_id'):
            evince.assigned_to_id = assignment_data['assigned_to_id']
        
        # Handle external department assignment
        if assignment_data.get('external_department_id'):
            try:
                from inspection_management.models.external_departments import ExternalDepartment, ExternalDepartmentAssignment
                external_dept = ExternalDepartment.objects.get(id=assignment_data['external_department_id'])
                
                # Update evince with external department assignment
                evince.hse_mitigation_department = external_dept.business_unit
                evince.hse_mitigation_assigned_to = user  # Manager who assigned
                evince.hse_mitigation_actions = assignment_data.get('mitigation_plan', '')
                evince.hse_mitigation_target_date = assignment_data.get('target_date')
                
                # Create external department assignment record
                ExternalDepartmentAssignment.objects.create(
                    evince=evince,
                    external_department=external_dept,
                    assigned_by=user,
                    target_completion_date=assignment_data.get('target_date'),
                    notes=assignment_data.get('mitigation_plan', ''),
                    status='ASSIGNED'
                )
                
                # Transition to LIMSInProgress
                HSERiskEvinceService.transition_status(evince, 'LIMSInProgress', user, f'Assigned to {external_dept.name} for mitigation')
                
            except Exception as e:
                print(f"Error assigning to external department: {e}")
                # Fallback to regular assignment
                HSERiskEvinceService.transition_status(evince, 'LIMSInProgress', user, 'Assigned for investigation')
        else:
            # Regular assignment without external department
            HSERiskEvinceService.transition_status(evince, 'LIMSInProgress', user, 'Assigned for investigation')
        
        return evince
    
    @staticmethod
    def lims_completion(evince, lims_data):
        """Handle LIMS completion callback"""
        if evince.evince_type != 'hse_risk_management':
            raise ValueError("Invalid evince type for LIMS completion")
        
        if evince.status != 'LIMSInProgress':
            raise ValueError(f"Invalid status for LIMS completion: {evince.status}")
        
        # Update LIMS data
        evince.hse_lims_reference_id = lims_data.get('lims_reference_id', '')
        evince.hse_lims_status = lims_data.get('lims_status', 'completed')
        evince.hse_investigation_details = lims_data.get('investigation_details', '')
        evince.hse_mitigation_actions = lims_data.get('mitigation_actions', '')
        
        # Transition to LIMSCompleted
        HSERiskEvinceService.transition_status(evince, 'LIMSCompleted', evince.changed_by, 'LIMS investigation completed')
        
        return evince
    
    @staticmethod
    def manager_approval(evince, user, approval_data):
        """Handle manager approval of LIMS results"""
        if evince.evince_type != 'hse_risk_management':
            raise ValueError("Invalid evince type for manager approval")
        
        if evince.status != 'ManagerApproval':
            raise ValueError(f"Invalid status for manager approval: {evince.status}")
        
        approval_status = approval_data.get('approval_status', 'approved')
        
        if approval_status == 'approved':
            # Transition to Completed
            HSERiskEvinceService.transition_status(evince, 'Completed', user, 'Manager approved LIMS results')
        elif approval_status == 'rejected':
            # Transition to Rejected
            HSERiskEvinceService.transition_status(evince, 'Rejected', user, 'Manager rejected LIMS results')
        
        return evince
    
    @staticmethod
    def get_hse_risk_dashboard_stats():
        """Get dashboard statistics for HSE Risk Management"""
        evinces = Evince.objects.filter(evince_type='hse_risk_management')
        
        stats = {
            'total_risks': evinces.count(),
            'logged': evinces.filter(status='Logged').count(),
            'inspector_review': evinces.filter(status='InspectorReview').count(),
            'risk_validated': evinces.filter(status='RiskValidated').count(),
            'manager_assignment': evinces.filter(status='ManagerAssignment').count(),
            'lims_in_progress': evinces.filter(status='LIMSInProgress').count(),
            'lims_completed': evinces.filter(status='LIMSCompleted').count(),
            'manager_approval': evinces.filter(status='ManagerApproval').count(),
            'completed': evinces.filter(status='Completed').count(),
            'rejected': evinces.filter(status='Rejected').count(),
        }
        
        return stats


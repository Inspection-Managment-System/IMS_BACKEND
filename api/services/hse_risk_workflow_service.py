from django.utils import timezone
from django.db.models import Q
from inspection_management.models import Evince, HSERiskAssessmentResult, ExternalDepartment, ExternalDepartmentAssignment
from users.models.user import User


class HSERiskWorkflowService:
    """Service for managing HSE risk assessment workflow"""
    
    @staticmethod
    def get_manager_risk_assessments(manager_id):
        """Get all HSE risk assessments assigned to a manager for review"""
        try:
            manager = User.objects.get(id=manager_id)
            
            # Get manager's data groups
            manager_data_groups = manager.userprofile.data_groups.all()
            data_group_ids = manager_data_groups.values_list('id', flat=True)
            
            # Get business units that belong to manager's data groups
            from inspection_management.models import BusinessUnit
            business_units = BusinessUnit.objects.filter(group_id__in=data_group_ids)
            business_unit_ids = business_units.values_list('id', flat=True)
            
            # Get risk assessments assigned to manager
            risk_assessments = Evince.objects.filter(
                evince_type='hse_risk_management',
                status__in=['RiskValidated', 'ManagerAssignment', 'LIMSInProgress', 'LIMSCompleted', 'Completed', 'Rejected', 'Reassigned'],
                business_unit_id__in=business_unit_ids
            ).order_by('-changed_on')
            
            return risk_assessments
        except User.DoesNotExist:
            return Evince.objects.none()
    
    @staticmethod
    def assign_risk_to_manager(evince_id, manager_id):
        """Assign HSE risk assessment to manager for review"""
        try:
            evince = Evince.objects.get(id=evince_id)
            manager = User.objects.get(id=manager_id)
            
            # Update evince status and assignment
            evince.status = 'ManagerAssignment'
            evince.reviewed_by = manager
            evince.changed_by = manager
            evince.changed_on = timezone.now()
            evince.save()
            
            return evince
        except (Evince.DoesNotExist, User.DoesNotExist):
            return None
    
    @staticmethod
    def approve_risk_assessment(evince_id, manager_id, approval_notes=None):
        """Manager approves HSE risk assessment"""
        try:
            evince = Evince.objects.get(id=evince_id)
            manager = User.objects.get(id=manager_id)
            
            # Update evince status
            evince.status = 'ManagerApproval'
            evince.hse_approved_by = manager
            evince.hse_approved_at = timezone.now()
            evince.hse_risk_closed = True
            evince.changed_by = manager
            evince.changed_on = timezone.now()
            
            if approval_notes:
                evince.hse_mitigation_actions = approval_notes
            
            evince.save()
            return evince
        except (Evince.DoesNotExist, User.DoesNotExist):
            return None
    
    @staticmethod
    def reject_risk_assessment(evince_id, manager_id, rejection_reason):
        """Manager rejects HSE risk assessment"""
        try:
            evince = Evince.objects.get(id=evince_id)
            manager = User.objects.get(id=manager_id)
            
            # Update evince status
            evince.status = 'InspectorReview'
            evince.hse_risk_rejection_reason = rejection_reason
            evince.hse_risk_valid = False
            evince.changed_by = manager
            evince.changed_on = timezone.now()
            evince.save()
            
            return evince
        except (Evince.DoesNotExist, User.DoesNotExist):
            return None
    
    @staticmethod
    def assign_mitigation_to_external_department(evince_id, external_dept_id, manager_id, mitigation_plan, target_date=None):
        """Assign mitigation work to external department"""
        try:
            evince = Evince.objects.get(id=evince_id)
            external_dept = ExternalDepartment.objects.get(id=external_dept_id)
            manager = User.objects.get(id=manager_id)
            
            # Set target date if not provided
            if not target_date:
                target_date = timezone.now() + timezone.timedelta(days=7)
            
            # Update evince status and assignment
            evince.status = 'LIMSInProgress'
            evince.hse_mitigation_department = external_dept.business_unit
            evince.hse_mitigation_assigned_to = manager  # Manager who assigned
            evince.hse_mitigation_actions = mitigation_plan
            evince.hse_mitigation_target_date = target_date
            evince.changed_by = manager
            evince.changed_on = timezone.now()
            evince.save()
            
            # Create external department assignment
            assignment = ExternalDepartmentAssignment.objects.create(
                evince=evince,
                external_department=external_dept,
                assigned_by=manager,
                target_completion_date=target_date,
                notes=mitigation_plan,
                status='ASSIGNED'
            )
            
            return evince, assignment
        except (Evince.DoesNotExist, ExternalDepartment.DoesNotExist, User.DoesNotExist):
            return None, None
    
    @staticmethod
    def get_available_external_departments():
        """Get all available external departments for assignment"""
        return ExternalDepartment.objects.filter(
            status='ACTIVE',
            is_available=True
        ).order_by('name')
    
    @staticmethod
    def complete_mitigation(evince_id, completion_notes, evidence_data=None):
        """Mark mitigation as completed by external department"""
        try:
            evince = Evince.objects.get(id=evince_id)
            
            # Update evince status
            evince.status = 'LIMSCompleted'
            evince.hse_mitigation_completed = True
            evince.hse_mitigation_evidence = completion_notes
            evince.changed_on = timezone.now()
            evince.save()
            
            # Update external department assignment
            assignment = ExternalDepartmentAssignment.objects.filter(
                evince=evince,
                status='IN_PROGRESS'
            ).first()
            
            if assignment:
                assignment.status = 'COMPLETED'
                assignment.completion_notes = completion_notes
                assignment.mitigation_actions = completion_notes
                if evidence_data:
                    assignment.evidence_data = evidence_data
                assignment.save()
            
            return evince
        except Evince.DoesNotExist:
            return None
    
    @staticmethod
    def verify_mitigation_completion(evince_id, manager_id, verification_notes=None):
        """Manager verifies mitigation completion"""
        try:
            evince = Evince.objects.get(id=evince_id)
            manager = User.objects.get(id=manager_id)
            
            # Update evince status
            evince.status = 'ManagerApproval'
            evince.hse_approved_by = manager
            evince.hse_approved_at = timezone.now()
            evince.hse_risk_closed = True
            evince.changed_by = manager
            evince.changed_on = timezone.now()
            
            if verification_notes:
                evince.hse_mitigation_actions += f"\n\nVerification Notes: {verification_notes}"
            
            evince.save()
            return evince
        except (Evince.DoesNotExist, User.DoesNotExist):
            return None

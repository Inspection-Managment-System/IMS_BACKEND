from inspection_management.models.hse_workflow_models import HSEObservation, HSEWorkflowHistory
from users.models.user import User
from inspection_management.models.business_unit import BusinessUnit


class HSEWorkflowService:
    @staticmethod
    def get_default_manager_for_department(department):
        """Get default manager for a department"""
        try:
            # Find users with MANAGER role in the department
            managers = User.objects.filter(
                role='MANAGER',
                departments__in=[department]
            ).first()
            return managers
        except:
            # Fallback: get any manager
            return User.objects.filter(role='MANAGER').first()
    
    @staticmethod
    def get_available_inspectors():
        """Get available inspectors for assignment"""
        try:
            return User.objects.filter(role='INSPECTOR', is_active=True)
        except:
            return User.objects.filter(is_active=True)
    
    @staticmethod
    def can_validate(user, observation):
        """Check if user can validate the observation"""
        # Admin and Manager can validate
        if user.is_anonymous:
            return True  # For debugging
        return user.role in ['ADMIN', 'MANAGER'] and observation.workflow_state == 'DRAFT'
    
    @staticmethod
    def can_assign(user, observation):
        """Check if user can assign the observation"""
        # Admin and Manager can assign
        if user.is_anonymous:
            return True  # For debugging
        return user.role in ['ADMIN', 'MANAGER'] and observation.workflow_state == 'PENDING_VALIDATION'
    
    @staticmethod
    def can_submit_evidence(user, observation):
        """Check if user can submit evidence"""
        # Admin, Manager, or assigned user can submit evidence
        if user.is_anonymous:
            return True  # For debugging
        return (user.role in ['ADMIN', 'MANAGER'] or user == observation.assigned_to) and observation.workflow_state == 'IN_PROGRESS'
    
    @staticmethod
    def can_close(user, observation):
        """Check if user can close the observation"""
        # Admin and Manager can close
        if user.is_anonymous:
            return True  # For debugging
        return user.role in ['ADMIN', 'MANAGER'] and observation.workflow_state == 'EVIDENCE_SUBMITTED'
    
    @staticmethod
    def can_transition_status(observation, new_status):
        """Check if status transition is valid"""
        valid_transitions = {
            'DRAFT': ['PENDING_VALIDATION'],
            'PENDING_VALIDATION': ['ASSIGNED', 'DRAFT'],
            'ASSIGNED': ['IN_PROGRESS'],
            'IN_PROGRESS': ['EVIDENCE_SUBMITTED', 'ASSIGNED'],
            'EVIDENCE_SUBMITTED': ['CLOSED', 'IN_PROGRESS'],
            'CLOSED': []
        }
        
        current_status = observation.workflow_state
        if current_status in valid_transitions:
            return new_status in valid_transitions[current_status]
        
        return False
    
    @staticmethod
    def transition_state(observation, new_state, user, comments=None):
        """Transition observation to new state and log history"""
        old_state = observation.workflow_state
        observation.workflow_state = new_state
        
        # Auto-assign based on workflow state
        if new_state == 'PENDING_VALIDATION':
            # Auto-assign to department manager
            if observation.affected_department:
                manager = HSEWorkflowService.get_default_manager_for_department(observation.affected_department)
                if manager:
                    observation.validated_by = manager
        
        elif new_state == 'ASSIGNED':
            # Auto-assign to first available inspector if not manually assigned
            if not observation.assigned_to:
                inspector = HSEWorkflowService.get_available_inspectors().first()
                if inspector:
                    observation.assigned_to = inspector
        
        observation.save()
        
        # Log history
        HSEWorkflowHistory.objects.create(
            observation=observation,
            from_state=old_state,
            to_state=new_state,
            action_by=user if not user.is_anonymous else None,
            comments=comments or f'Status changed from {old_state} to {new_state}'
        )
        
        return observation
    
    @staticmethod
    def create_observation_with_workflow(data, user):
        """Create observation with proper workflow initialization"""
        # Set default values
        if 'workflow_state' not in data:
            data['workflow_state'] = 'DRAFT'
        
        if 'risk_category' not in data:
            data['risk_category'] = 'Safety'
        
        # Set created_by
        data['created_by'] = user if not user.is_anonymous else None
        
        # Set affected_department if not provided
        if 'affected_department' not in data:
            default_dept = BusinessUnit.objects.first()
            if default_dept:
                data['affected_department'] = default_dept
        
        # Create the observation
        observation = HSEObservation.objects.create(**data)
        
        # Log initial creation
        HSEWorkflowHistory.objects.create(
            observation=observation,
            from_state='',
            to_state='DRAFT',
            action_by=user if not user.is_anonymous else None,
            comments='Observation created'
        )
        
        return observation

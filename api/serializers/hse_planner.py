from rest_framework import serializers
from inspection_management.models.hse_planner import HSEPlanner
from inspection_management.models import BusinessUnit, InspectionAnalysis, InspectionPoint, Parameter
from users.models.user import User


class SimpleUserSerializer(serializers.ModelSerializer):
    """Simple user serializer for nested representations"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class SimpleParameterSerializer(serializers.ModelSerializer):
    """Simple parameter serializer"""
    unit = serializers.StringRelatedField()
    
    class Meta:
        model = Parameter
        fields = ['id', 'name', 'description', 'unit', 'min_value', 'max_value', 'avg_value']


class HSEPlannerSerializer(serializers.ModelSerializer):
    """Serializer for HSE Planner with nested objects for read operations"""
    business_unit = serializers.CharField(source='evince_business_unit.name', read_only=True)
    inspection_point = serializers.CharField(source='evince_inspection_point.name', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)
    reviewed_by = SimpleUserSerializer(read_only=True)
    assigned_to = SimpleUserSerializer(source='evince_assigned_to', read_only=True)
    inspection_analyses = serializers.StringRelatedField(source='evince_inspection_analyses', many=True, read_only=True)
    parameters = SimpleParameterSerializer(source='evince_parameters', many=True, read_only=True)
    assessment_type_display = serializers.CharField(source='get_assessment_type_display', read_only=True)
    rule_display = serializers.CharField(source='get_rule_display', read_only=True)
    
    # Write fields
    business_unit_id = serializers.IntegerField(write_only=True, source='evince_business_unit')
    inspection_point_id = serializers.IntegerField(write_only=True, source='evince_inspection_point')
    reviewed_by_id = serializers.IntegerField(write_only=True, required=False, allow_null=True, source='reviewed_by')
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True, source='evince_assigned_to')
    inspection_analyses_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False,
        source='evince_inspection_analyses'
    )
    parameters_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False,
        source='evince_parameters'
    )
    
    class Meta:
        model = HSEPlanner
        fields = [
            'id', 'name', 'rule', 'assessment_type', 'evince_description',
            'business_unit', 'inspection_point', 'changed_by_name',
            'reviewed_by', 'assigned_to', 'inspection_analyses', 'parameters',
            'assessment_type_display', 'rule_display',
            'business_unit_id', 'inspection_point_id', 'reviewed_by_id', 'assigned_to_id',
            'inspection_analyses_ids', 'parameters_ids',
            'day_of_week', 'start_date_time', 'end_date_time', 'month', 
            'attachment_name', 'attachment', 'changed_on', 'hse_observation_details'
        ]
        read_only_fields = ['changed_on', 'changed_by']
    
    def create(self, validated_data):
        from inspection_management.models import BusinessUnit, InspectionPoint
        from users.models.user import User
        
        # Extract ManyToMany fields
        inspection_analyses_data = validated_data.pop('evince_inspection_analyses', [])
        parameters_data = validated_data.pop('evince_parameters', [])
        
        # Convert IDs to instances for ForeignKey fields
        if 'evince_business_unit' in validated_data and isinstance(validated_data['evince_business_unit'], int):
            validated_data['evince_business_unit'] = BusinessUnit.objects.get(id=validated_data['evince_business_unit'])
        
        if 'evince_inspection_point' in validated_data and isinstance(validated_data['evince_inspection_point'], int):
            validated_data['evince_inspection_point'] = InspectionPoint.objects.get(id=validated_data['evince_inspection_point'])
        
        if 'reviewed_by' in validated_data and isinstance(validated_data['reviewed_by'], int):
            validated_data['reviewed_by'] = User.objects.get(id=validated_data['reviewed_by'])
        
        if 'evince_assigned_to' in validated_data and isinstance(validated_data['evince_assigned_to'], int):
            validated_data['evince_assigned_to'] = User.objects.get(id=validated_data['evince_assigned_to'])
        
        # Create planner
        planner = HSEPlanner.objects.create(**validated_data)
        
        # Set ManyToMany relationships
        if inspection_analyses_data:
            planner.evince_inspection_analyses.set(inspection_analyses_data)
        if parameters_data:
            planner.evince_parameters.set(parameters_data)
        
        return planner
    
    def update(self, instance, validated_data):
        from inspection_management.models import BusinessUnit, InspectionPoint
        from users.models.user import User
        
        # Extract ManyToMany fields
        inspection_analyses_data = validated_data.pop('evince_inspection_analyses', None)
        parameters_data = validated_data.pop('evince_parameters', None)
        
        # Convert IDs to instances for ForeignKey fields
        if 'evince_business_unit' in validated_data and isinstance(validated_data['evince_business_unit'], int):
            validated_data['evince_business_unit'] = BusinessUnit.objects.get(id=validated_data['evince_business_unit'])
        
        if 'evince_inspection_point' in validated_data and isinstance(validated_data['evince_inspection_point'], int):
            validated_data['evince_inspection_point'] = InspectionPoint.objects.get(id=validated_data['evince_inspection_point'])
        
        if 'reviewed_by' in validated_data and isinstance(validated_data['reviewed_by'], int):
            validated_data['reviewed_by'] = User.objects.get(id=validated_data['reviewed_by'])
        
        if 'evince_assigned_to' in validated_data and isinstance(validated_data['evince_assigned_to'], int):
            validated_data['evince_assigned_to'] = User.objects.get(id=validated_data['evince_assigned_to'])
        
        # Update instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update ManyToMany relationships
        if inspection_analyses_data is not None:
            instance.evince_inspection_analyses.set(inspection_analyses_data)
        if parameters_data is not None:
            instance.evince_parameters.set(parameters_data)
        
        return instance


class HSEPlannerListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    business_unit = serializers.CharField(source='evince_business_unit.name')
    inspection_point = serializers.CharField(source='evince_inspection_point.name')
    changed_by_name = serializers.CharField(source='changed_by.username')
    assigned_to_name = serializers.CharField(source='evince_assigned_to.username', default='-')
    assessment_type_display = serializers.CharField(source='get_assessment_type_display')
    rule_display = serializers.CharField(source='get_rule_display')
    
    class Meta:
        model = HSEPlanner
        fields = [
            'id', 'name', 'rule', 'rule_display', 'assessment_type', 'assessment_type_display',
            'business_unit', 'inspection_point', 'start_date_time', 'end_date_time',
            'changed_by_name', 'assigned_to_name', 'changed_on'
        ]


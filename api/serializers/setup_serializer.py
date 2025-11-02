from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


class SetupSerializer(serializers.Serializer):
    """Serializer for first-time system setup"""
    
    organization_name = serializers.CharField(
        max_length=255,
        required=True,
        help_text="Organization or company name"
    )
    admin_username = serializers.CharField(
        max_length=255,
        required=True,
        help_text="Administrator username"
    )
    admin_name = serializers.CharField(
        max_length=255,
        required=True,
        help_text="Administrator full name"
    )
    admin_email = serializers.EmailField(
        required=True,
        help_text="Administrator email address"
    )
    admin_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Administrator password"
    )
    
    def validate_organization_name(self, value):
        """Validate organization name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Organization name must be at least 2 characters"
            )
        return value.strip()
    
    def validate_admin_password(self, value):
        """Validate password strength"""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate_admin_username(self, value):
        """Validate username is unique"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already taken')
        
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # Check if email is unique
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if User.objects.filter(email=data['admin_email']).exists():
            raise serializers.ValidationError({
                'admin_email': 'This email is already registered'
            })
        
        return data


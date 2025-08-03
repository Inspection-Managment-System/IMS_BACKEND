#!/usr/bin/env python
"""
Test script to verify HSE data is working properly
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ims_backend.settings')
django.setup()

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

def test_hse_data():
    """Test if HSE data exists and is accessible"""
    print("=== HSE Data Test ===")
    
    # Check if data exists
    env_count = HSEEnvironmentalData.objects.count()
    safety_count = HSESafetyIncident.objects.count()
    equipment_count = HSEEquipment.objects.count()
    compliance_count = HSECompliance.objects.count()
    training_count = HSETraining.objects.count()
    
    print(f"Environmental Data: {env_count}")
    print(f"Safety Incidents: {safety_count}")
    print(f"Equipment: {equipment_count}")
    print(f"Compliance: {compliance_count}")
    print(f"Training: {training_count}")
    
    # Check dependencies
    inspection_points = InspectionPoint.objects.count()
    business_units = BusinessUnit.objects.count()
    users = User.objects.count()
    
    print(f"\nDependencies:")
    print(f"Inspection Points: {inspection_points}")
    print(f"Business Units: {business_units}")
    print(f"Users: {users}")
    
    # Test sample data
    if env_count > 0:
        sample_env = HSEEnvironmentalData.objects.first()
        print(f"\nSample Environmental Data:")
        print(f"  ID: {sample_env.id}")
        print(f"  PM2.5: {sample_env.air_quality_pm25}")
        print(f"  PM10: {sample_env.air_quality_pm10}")
        print(f"  Timestamp: {sample_env.timestamp}")
    
    if safety_count > 0:
        sample_safety = HSESafetyIncident.objects.first()
        print(f"\nSample Safety Incident:")
        print(f"  ID: {sample_safety.id}")
        print(f"  Title: {sample_safety.title}")
        print(f"  Type: {sample_safety.incident_type}")
        print(f"  Severity: {sample_safety.severity}")
        print(f"  Status: {sample_safety.status}")
    
    if equipment_count > 0:
        sample_equipment = HSEEquipment.objects.first()
        print(f"\nSample Equipment:")
        print(f"  ID: {sample_equipment.id}")
        print(f"  Name: {sample_equipment.name}")
        print(f"  Type: {sample_equipment.equipment_type}")
        print(f"  Status: {sample_equipment.status}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_hse_data() 
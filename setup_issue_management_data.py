"""
Quick setup script to populate default Issue Management data
Run this after migrations: python setup_issue_management_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ims_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from inspection_management.models import DataGroup, RiskLevel, RiskCategory, HSEObservationType, ExternalDepartment

User = get_user_model()

def setup_issue_management_data():
    print("🔄 Setting up Issue Management default data...")
    
    # Get admin user and data group
    admin = User.objects.filter(is_staff=True).first()
    if not admin:
        print("❌ No admin user found! Please create an admin user first.")
        return
    
    data_group = DataGroup.objects.first()
    if not data_group:
        print("❌ No data group found! Please create a data group first.")
        return
    
    print(f"✅ Using admin: {admin.username}")
    print(f"✅ Using data group: {data_group.name}")
    
    # Create default Risk Levels
    print("\n📊 Creating Risk Levels...")
    risk_levels = [
        {"name": "Low", "value": "LOW", "description": "Minimal risk, routine handling", "order": 1},
        {"name": "Medium", "value": "MEDIUM", "description": "Moderate risk, requires attention", "order": 2},
        {"name": "High", "value": "HIGH", "description": "Significant risk, immediate action", "order": 3},
        {"name": "Critical", "value": "CRITICAL", "description": "Severe risk, emergency response", "order": 4},
    ]
    
    for level_data in risk_levels:
        obj, created = RiskLevel.objects.get_or_create(
            value=level_data["value"],
            group=data_group,
            defaults={
                "name": level_data["name"],
                "description": level_data["description"],
                "order": level_data["order"],
                "changed_by": admin,
            }
        )
        status = "✅ Created" if created else "⏭️  Already exists"
        print(f"  {status}: {obj.name}")
    
    # Create default Risk Categories
    print("\n🏷️  Creating Risk Categories...")
    categories = [
        {"name": "Safety", "value": "Safety", "description": "Safety-related risks", "order": 1},
        {"name": "Environmental", "value": "Environmental", "description": "Environmental impacts", "order": 2},
        {"name": "Equipment", "value": "Equipment", "description": "Equipment-related risks", "order": 3},
        {"name": "Health", "value": "Health", "description": "Health hazards", "order": 4},
        {"name": "Process", "value": "Process", "description": "Process deviations", "order": 5},
    ]
    
    for cat_data in categories:
        obj, created = RiskCategory.objects.get_or_create(
            value=cat_data["value"],
            group=data_group,
            defaults={
                "name": cat_data["name"],
                "description": cat_data["description"],
                "order": cat_data["order"],
                "changed_by": admin,
            }
        )
        status = "✅ Created" if created else "⏭️  Already exists"
        print(f"  {status}: {obj.name}")
    
    # Create default HSE Observation Types
    print("\n👁️  Creating HSE Observation Types...")
    obs_types = [
        {"name": "Slip/Trip Hazard", "value": "slip_trip", "description": "Slipping or tripping hazards", "order": 1},
        {"name": "Equipment Safety Issue", "value": "equipment_safety", "description": "Equipment safety concerns", "order": 2},
        {"name": "Personal Protective Equipment", "value": "ppe", "description": "PPE-related observations", "order": 3},
        {"name": "Emergency Procedure", "value": "emergency", "description": "Emergency response issues", "order": 4},
        {"name": "Chemical Exposure", "value": "chemical", "description": "Chemical handling concerns", "order": 5},
        {"name": "Noise Pollution", "value": "noise", "description": "Excessive noise levels", "order": 6},
        {"name": "Air Quality", "value": "air_quality", "description": "Air quality issues", "order": 7},
        {"name": "Waste Management", "value": "waste", "description": "Waste disposal concerns", "order": 8},
    ]
    
    for obs_data in obs_types:
        obj, created = HSEObservationType.objects.get_or_create(
            value=obs_data["value"],
            group=data_group,
            defaults={
                "name": obs_data["name"],
                "description": obs_data["description"],
                "order": obs_data["order"],
                "changed_by": admin,
            }
        )
        status = "✅ Created" if created else "⏭️  Already exists"
        print(f"  {status}: {obj.name}")
    
    # Create default Departments (Internal)
    print("\n🏢 Creating Departments...")
    departments = [
        {"name": "Internal Maintenance", "type": "MAINTENANCE", "assignment": "INTERNAL", "description": "Internal maintenance department", "order": 1},
        {"name": "Internal Safety Engineering", "type": "SAFETY", "assignment": "INTERNAL", "description": "Internal safety department", "order": 2},
        {"name": "Internal Environmental Services", "type": "ENVIRONMENTAL", "assignment": "INTERNAL", "description": "Internal environmental department", "order": 3},
        {"name": "Internal Quality Control", "type": "QUALITY", "assignment": "INTERNAL", "description": "Internal QC department", "order": 4},
    ]
    
    for dept_data in departments:
        obj, created = ExternalDepartment.objects.get_or_create(
            name=dept_data["name"],
            group=data_group,
            defaults={
                "department_type": dept_data["type"],
                "assignment_type": dept_data["assignment"],
                "description": dept_data["description"],
                "status": "ACTIVE",
                "is_available": True,
                "created_by": admin,
            }
        )
        status_text = "✅ Created" if created else "⏭️  Already exists"
        print(f"  {status_text}: {obj.name}")
    
    print("\n🎉 Issue Management data setup complete!")
    print(f"\n📊 Summary:")
    print(f"  Risk Levels: {RiskLevel.objects.filter(group=data_group).count()}")
    print(f"  Risk Categories: {RiskCategory.objects.filter(group=data_group).count()}")
    print(f"  HSE Observation Types: {HSEObservationType.objects.filter(group=data_group).count()}")
    print(f"  Departments: {ExternalDepartment.objects.filter(group=data_group).count()}")
    print(f"\n✅ You can now manage these from: Sidebar → Issue Management")

if __name__ == "__main__":
    setup_issue_management_data()


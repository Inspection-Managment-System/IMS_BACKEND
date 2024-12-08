from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import timedelta
from inspection_management.models import Equipment

User = get_user_model()

def fetch_all_equipment(user_id):
    user = User.objects.get(id=user_id)  # Convert user_id to User object
    data_groups = user.userprofile.data_groups.all()
    equipment = Equipment.objects.filter(group__in=data_groups).select_related(
        "location", "equipment_type", "group", "operator"
    )

    return [
        {
            "id": equip.id,
            "name": equip.name,
            "type": equip.equipment_type.name if equip.equipment_type else "N/A",
            "description": equip.description,
            "serial_no": equip.serial_no,
            "asset_number": equip.asset_number,
            "location": equip.location.name,
            "business_unit": equip.location.group.name,
            "calibration_date": equip.callibration_date,
            "calibration_expiry_date": equip.callibration_expiry,
            "calibration_status": (
                "Expired" if equip.callibration_expiry < now()
                else "Due Soon" if equip.callibration_expiry <= now() + timedelta(days=30)
                else "Active"
            ),
            "changed_on": equip.changed_on,
            "changed_by": equip.changed_by.username,
            "operator": equip.operator.username if equip.operator else "N/A",
            "group": equip.group.name,
            "attachment_name": equip.attachment_name,
            "attachment": equip.attachment,
        }
        for equip in equipment
    ]


def fetch_equipment_requiring_calibration(user_id):
    user = User.objects.get(id=user_id)  # Convert user_id to User object
    data_groups = user.userprofile.data_groups.all()
    
    # Fetch equipment requiring calibration
    equipment = Equipment.objects.filter(
        group__in=data_groups, callibration_expiry__lte=now()
    ).select_related("location", "equipment_type", "group", "operator")

    # Return all relevant details for each equipment
    return [
        {
            "id": equip.id,
            "name": equip.name,
            "type": equip.equipment_type.name if equip.equipment_type else "N/A",
            "description": equip.description,
            "serial_no": equip.serial_no,
            "asset_number": equip.asset_number,
            "location": equip.location.name,
            "business_unit": equip.location.group.name,
            "calibration_date": equip.callibration_date,
            "calibration_expiry_date": equip.callibration_expiry,
            "calibration_status": "Expired",
            "changed_on": equip.changed_on,
            "changed_by": equip.changed_by.username,
            "operator": equip.operator.username if equip.operator else "N/A",
            "group": equip.group.name,
            "attachment_name": equip.attachment_name,
            "attachment": equip.attachment,
        }
        for equip in equipment
    ]
def fetch_single_equipment_report(user_id, equipment_id):
    user = User.objects.get(id=user_id)  # Convert user_id to User object
    data_groups = user.userprofile.data_groups.all()
    equipment = Equipment.objects.filter(
        id=equipment_id, group__in=data_groups
    ).select_related(
        "location", "equipment_type", "group", "operator"
    ).first()

    if not equipment:
        raise ValueError("Equipment not found or not accessible.")

    return {
        "id": equipment.id,
        "name": equipment.name,
        "type": equipment.equipment_type.name if equipment.equipment_type else "N/A",
        "description": equipment.description,
        "serial_no": equipment.serial_no,
        "asset_number": equipment.asset_number,
        "location": equipment.location.name,
        "business_unit": equipment.location.group.name,
        "calibration_date": equipment.callibration_date,
        "calibration_expiry_date": equipment.callibration_expiry,
        "calibration_status": (
            "Expired" if equipment.callibration_expiry < now()
            else "Due Soon" if equipment.callibration_expiry <= now() + timedelta(days=30)
            else "Active"
        ),
        "changed_on": equipment.changed_on,
        "changed_by": equipment.changed_by.username,
        "operator": equipment.operator.username if equipment.operator else "N/A",
        "group": equipment.group.name,
        "attachment_name": equipment.attachment_name,
        "attachment": equipment.attachment,
    }


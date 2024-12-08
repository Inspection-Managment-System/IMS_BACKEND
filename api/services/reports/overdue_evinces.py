from django.utils.timezone import now
from inspection_management.models import Evince





def fetch_overdue_evinces(inspector_id=None, business_unit_id=None):
 
    filters = {
        "status": "Logged",
        "end_date_time__lt": now(),  
    }

    if inspector_id:
        filters["assigned_to_id"] = inspector_id
    if business_unit_id:
        filters["business_unit_id"] = business_unit_id

    overdue_evinces = Evince.objects.filter(**filters).select_related(
        "business_unit", "inspection_point"
    )

    if not overdue_evinces.exists():
        print("No overdue evinces found.")  

    return [
        {
            "id": evince.id,
            "name": evince.name,
            "description": evince.description,
            "business_unit": evince.business_unit.name,
            "inspection_point": evince.inspection_point.name,
            "start_date_time": evince.start_date_time,
            "end_date_time": evince.end_date_time,
        }
        for evince in overdue_evinces
    ]



def fetch_evince_details(evince_id):

    evince = Evince.objects.select_related(
        "business_unit", "inspection_point", "changed_by", "assigned_to"
    ).get(id=evince_id)

    return {
        "id": evince.id,
        "name": evince.name,
        "description": evince.description,
        "status": evince.status,
        "changed_on": evince.changed_on,
        "logged_by": evince.changed_by.username,
        "business_unit": evince.business_unit.name,
        "inspection_point": evince.inspection_point.name,
        "start_date_time": evince.start_date_time,
        "end_date_time": evince.end_date_time,
        "assigned_to": evince.assigned_to.username if evince.assigned_to else None,
    }

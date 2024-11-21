from datetime import timedelta

from django.db.models import Count, Q
from django.utils.timezone import now

from inspection_management.models import DataGroup, Evince
from users.models import User, UserProfile


def get_evince_status_counts(user_id, time_period="all"):
    try:
        user = User.objects.get(id=user_id)
        user_data_groups = user.userprofile.data_groups.all()

        if not user_data_groups.exists():
            return {
                "error": "No data groups assigned to the user.",
                "total_evinces": 0,
                "status_counts": {
                    status: 0
                    for status in ["Approved", "Rejected", "ResultsEntered", "Logged"]
                },
            }

        evince_filter = Q(business_unit__group__in=user_data_groups)

        end_date = now()
        if time_period.isdigit():
            start_date = end_date - timedelta(days=int(time_period))
            evince_filter &= Q(changed_on__gte=start_date, changed_on__lte=end_date)
        elif time_period == "week":
            start_date = end_date - timedelta(days=7)
            evince_filter &= Q(changed_on__gte=start_date, changed_on__lte=end_date)
        elif time_period == "month":
            start_date = end_date - timedelta(days=30)
            evince_filter &= Q(changed_on__gte=start_date, changed_on__lte=end_date)
        elif time_period == "year":
            start_date = end_date - timedelta(days=365)
            evince_filter &= Q(changed_on__gte=start_date, changed_on__lte=end_date)

        queryset = Evince.objects.filter(evince_filter)
        evince_status_counts = queryset.values("status").annotate(count=Count("id"))

        status_counts = {
            entry["status"]: entry["count"] for entry in evince_status_counts
        }
        all_statuses = ["Approved", "Rejected", "ResultsEntered", "Logged"]
        for status in all_statuses:
            status_counts.setdefault(status, 0)

        total_evinces = sum(status_counts.values())
        status_counts["total_evinces"] = total_evinces

        return status_counts
    except User.DoesNotExist:
        return {"error": f"User with ID {user_id} does not exist."}
    except Exception as e:
        return {"error": str(e)}

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.timezone import now

from inspection_management.models import (
    AnalysisType,
    BusinessUnit,
    Company,
    DataGroup,
    Equipment,
    EquipmentType,
    Evince,
    Facility,
    InspectionAnalysis,
    InspectionPoint,
    Location,
    Parameter,
    Site,
    Suite,
    Unit,
)
from users.models import User, UserProfile


def statistic_cards_data(user_id):
    current_date = now()
    current_month_start = current_date.replace(day=1)

    data_groups = DataGroup.objects.filter(user_profiles__user_id=user_id)

    if data_groups.exists():
        company_queryset = Company.objects.filter(group__in=data_groups)
        business_unit_queryset = BusinessUnit.objects.filter(group__in=data_groups)
        site_queryset = Site.objects.filter(group__in=data_groups)
    else:
        company_queryset = Company.objects.none()
        business_unit_queryset = BusinessUnit.objects.none()
        site_queryset = Site.objects.none()

    total_users = User.objects.count()
    users_this_month = User.objects.filter(date_joined__gte=current_month_start).count()

    total_companies = company_queryset.count()
    companies_this_month = company_queryset.filter(
        changed_on__gte=current_month_start
    ).count()

    total_business_units = business_unit_queryset.count()
    business_units_this_month = business_unit_queryset.filter(
        changed_on__gte=current_month_start
    ).count()

    total_sites = site_queryset.count()
    sites_this_month = site_queryset.filter(changed_on__gte=current_month_start).count()

    return {
        "total_users": {"count": total_users, "this_month": users_this_month},
        "total_companies": {
            "count": total_companies,
            "this_month": companies_this_month,
        },
        "total_business_units": {
            "count": total_business_units,
            "this_month": business_units_this_month,
        },
        "total_sites": {"count": total_sites, "this_month": sites_this_month},
    }

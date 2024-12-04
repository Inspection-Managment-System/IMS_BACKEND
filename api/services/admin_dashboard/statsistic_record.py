from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Count, Q
from django.utils import timezone

from inspection_management.models import (AnalysisType, BusinessUnit, Company,
                                          DataGroup, Equipment, EquipmentType,
                                          Evince, Facility, InspectionAnalysis,
                                          InspectionPoint, Location, Parameter,
                                          Site, Suite, Unit)
from users.models import User, UserProfile


def statistic_cards_data():
    current_date = timezone.now()
    current_month_start = current_date.replace(day=1)
    total_users = User.objects.count()
    users_this_month = User.objects.filter(date_joined__gte=current_month_start).count()
    total_companies = Company.objects.count()
    companies_this_month = Company.objects.filter(
        changed_on__gte=current_month_start
    ).count()
    total_business_units = BusinessUnit.objects.count()
    business_units_this_month = BusinessUnit.objects.filter(
        changed_on__gte=current_month_start
    ).count()

    total_sites = Site.objects.count()
    sites_this_month = Site.objects.filter(changed_on__gte=current_month_start).count()

    return {
        "total_users": {"count": total_users, "this_month": users_this_month},
        "total_companies": {
            "count": total_companies,
            "this_month": companies_this_month,
        },
        "total_business_unit": {
            "count": total_business_units,
            "this_month": business_units_this_month,
        },
        "totalsites": {"count": total_sites, "this_month": sites_this_month},
    }

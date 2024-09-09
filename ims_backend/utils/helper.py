from inspection_management.models import *
from users.models import *


def get_related_sites_from_company(company_name):
    company_id = Company.objects.get(name=company_name).id
    sites = Site.objects.filter(company=company_id)
    return sites


def get_related_business_units_from_site(site_name):
    site_id = Site.objects.get(name=site_name).id
    business_units = BusinessUnit.objects.filter(site=site_id)
    return business_units


def get_related_inspection_points_from_business_unit(business_unit_name):
    business_unit_id = BusinessUnit.objects.get(name=business_unit_name).id
    inspection_points = InspectionPoint.objects.filter(business_unit=business_unit_id)
    return inspection_points


def get_related_inspection_analyses_from_analysis_type(analysis_type_name):
    analysis_type_id = AnalysisType.objects.get(name=analysis_type_name).id
    inspection_analyses = InspectionAnalysis.objects.filter(
        analysis_type=analysis_type_id
    )
    return inspection_analyses


def get_user_groups(user_id):
    user_object = User.objects.get(id=user_id)
    return list(user_object.userprofile.data_groups.values_list("id", flat=True))


def get_user_through_role(role):
    user_profiles = UserProfile.objects.filter(role__name=role)
    return [userprofile.user for userprofile in user_profiles]

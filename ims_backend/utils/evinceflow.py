from inspection_management.models import InspectionResult, InspectionTest


def create_evince_instance(evince_instance, data):
    evince_instance.changed_by = data.get("changed_by")
    evince_instance.save()

    for inspection_analysis in evince_instance.inspection_analyses.all():
        inspection_test = InspectionTest.objects.create(
            evince=evince_instance,
            inspection_analysis=inspection_analysis,
            changed_by=data.get("changed_by"),
        )
        
        # Create one InspectionResult per parameter in the analysis
        parameters = inspection_analysis.parameter_set.all()
        for parameter in parameters:
            InspectionResult.objects.create(
                evince=evince_instance,
                inspection_test=inspection_test,
                parameter=parameter,
                changed_by=data.get("changed_by"),
            )

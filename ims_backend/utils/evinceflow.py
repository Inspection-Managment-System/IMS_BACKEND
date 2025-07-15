from inspection_management.models import InspectionResult, InspectionTest


def create_evince_instance(evince_instance, data):
    evince_instance.changed_by = data.get("changed_by")
    evince_instance.save()

    for inspection_analysis in evince_instance.inspection_analyses.all():
        InspectionTest.objects.create(
            evince=evince_instance,
            inspection_analysis=inspection_analysis,
            changed_by=data.get("changed_by"),
        )

    inspection_tests = InspectionTest.objects.filter(evince=evince_instance)

    for inspection_test in inspection_tests:
        InspectionResult.objects.create(
            evince=evince_instance,
            inspection_test=inspection_test,
            changed_by=data.get("changed_by"),
        )

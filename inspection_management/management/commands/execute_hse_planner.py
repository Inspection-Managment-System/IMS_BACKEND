import zoneinfo
from datetime import datetime, timedelta, timezone
from time import sleep

from django.core.management.base import BaseCommand
from inspection_management.models import Evince
from inspection_management.models.hse_planner import HSEPlanner


class Command(BaseCommand):
    help = "Create HSE Risk Assessment Evinces based on HSE Planner rules"

    def add_arguments(self, parser):
        parser.add_argument(
            "--timezone",
            type=str,
            help="Timezone (IANA, e.g. Asia/Dubai, Europe/London). Defaults to UTC.",
            default="UTC",
        )

    def create_hse_evince(self, planner):
        """Create HSE Risk Assessment evince from planner"""
        evince = Evince(
            description=planner.evince_description,
            business_unit=planner.evince_business_unit,
            inspection_point=planner.evince_inspection_point,
            changed_by=planner.changed_by,
            reviewed_by=planner.reviewed_by,
            assigned_to=planner.evince_assigned_to,
            start_date_time=planner.start_date_time,
            end_date_time=planner.end_date_time,
            status="Logged",
            evince_type="hse_risk_management",  # Set as HSE Risk Assessment
            hse_risk_trigger_type="observation" if planner.assessment_type == "observation" else "parameter",
            hse_has_parameters=planner.assessment_type == "parameter",
            hse_observation_details=planner.hse_observation_details if planner.assessment_type == "observation" else None,
        )
        evince.save()

        # For parameter-based assessments
        if planner.assessment_type == "parameter":
            evince.inspection_analyses.set(planner.evince_inspection_analyses.all())
            
            selected_parameters = planner.evince_parameters.all()
            
            if selected_parameters.exists():
                from inspection_management.models import InspectionTest, InspectionResult
                
                print(f"Creating HSE evince with {selected_parameters.count()} parameters")
                
                for inspection_analysis in evince.inspection_analyses.all():
                    inspection_test = InspectionTest.objects.create(
                        evince=evince,
                        inspection_analysis=inspection_analysis,
                        changed_by=planner.changed_by,
                    )
                    
                    for parameter in selected_parameters:
                        if parameter.inspection_analysis == inspection_analysis:
                            InspectionResult.objects.create(
                                evince=evince,
                                inspection_test=inspection_test,
                                parameter=parameter,
                                changed_by=planner.changed_by,
                            )
                            print(f"Created result for parameter: {parameter.name}")
        
        print(f"Created HSE Risk Assessment: {evince.name} (Type: {planner.assessment_type})")

    def handle(self, *args, **options):
        tz_name = options["timezone"]
        try:
            local_tz = zoneinfo.ZoneInfo(tz_name)
        except Exception:
            self.stderr.write(f"Invalid timezone '{tz_name}'. Using UTC.")
            local_tz = zoneinfo.ZoneInfo("UTC")

        self.stdout.write(f"Using timezone: {local_tz}")
        last_execution = {}

        while True:
            now_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)
            now = now_utc.astimezone(local_tz)
            self.stdout.write(f"Now (local): {now}")

            for planner in HSEPlanner.objects.all():
                start_time = planner.start_date_time.astimezone(local_tz).replace(second=0, microsecond=0)
                end_time = planner.end_date_time.astimezone(local_tz).replace(second=0, microsecond=0)

                if now < start_time or now >= end_time:
                    continue
                
                today_str = now.strftime("%Y-%m-%d")
                planner_key = f"{planner.id}_{today_str}"

                if (
                    planner.rule == "Daily"
                    and now.time() >= start_time.time()
                    and now.time() <= (start_time + timedelta(minutes=1)).time()
                ):
                    if planner_key in last_execution:
                        continue
                    
                    self.stdout.write("Creating HSE Evince (Daily).")
                    self.create_hse_evince(planner)
                    last_execution[planner_key] = now

                elif (
                    planner.rule == "Weekly"
                    and now.time() >= start_time.time()
                    and now.time() <= (start_time + timedelta(minutes=1)).time()
                ):
                    if now.strftime("%A") in planner.day_of_week.split(","):
                        if planner_key in last_execution:
                            continue
                        
                        self.stdout.write("Creating HSE Evince (Weekly).")
                        self.create_hse_evince(planner)
                        last_execution[planner_key] = now

                elif (
                    planner.rule == "Monthly"
                    and now.time() >= start_time.time()
                    and now.time() <= (start_time + timedelta(minutes=1)).time()
                ):
                    if now.strftime("%A") in planner.day_of_week.split(",") and now.strftime("%b-%Y") in planner.month.split(","):
                        if planner_key in last_execution:
                            continue
                        
                        self.stdout.write("Creating HSE Evince (Monthly).")
                        self.create_hse_evince(planner)
                        last_execution[planner_key] = now

            sleep(60)


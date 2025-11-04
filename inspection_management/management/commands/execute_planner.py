import zoneinfo
from datetime import datetime, timedelta, timezone
from time import sleep

from django.core.management.base import BaseCommand

from ims_backend.utils.evinceflow import create_evince_instance
from inspection_management.models import Evince, Planner


class Command(BaseCommand):
    help = "Create Evince objects based on Planner rules"

    def add_arguments(self, parser):
        parser.add_argument(
            "--timezone",
            type=str,
            help="Timezone name (IANA, e.g. Asia/Dubai, Europe/London). Defaults to UTC.",
            default="UTC",
        )

    def to_local_naive(self, dt_utc, local_tz):
        """Convert UTC datetime to local timezone"""
        return dt_utc.astimezone(local_tz)

    def create_evince(self, planner):
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
        )
        evince.save()
        evince.inspection_analyses.set(planner.evince_inspection_analyses.all())
        
        # Get the parameters that were selected in the planner
        selected_parameters = planner.evince_parameters.all()
        
        if selected_parameters.exists():
            # Create inspection tests and results only for selected parameters
            from inspection_management.models import InspectionTest, InspectionResult
            
            print(f"Creating evince with {selected_parameters.count()} selected parameters")
            
            for inspection_analysis in evince.inspection_analyses.all():
                inspection_test = InspectionTest.objects.create(
                    evince=evince,
                    inspection_analysis=inspection_analysis,
                    changed_by=planner.changed_by,
                )
                
                # Only create results for parameters that were selected in the planner
                for parameter in selected_parameters:
                    if parameter.inspection_analysis == inspection_analysis:
                        InspectionResult.objects.create(
                            evince=evince,
                            inspection_test=inspection_test,
                            parameter=parameter,
                            changed_by=planner.changed_by,
                        )
                        print(f"Created result for parameter: {parameter.name}")
        else:
            # If no parameters were specifically selected, create all (old behavior)
            data = {"changed_by": planner.changed_by}
            create_evince_instance(evince, data)

    def handle(self, *args, **options):
        tz_name = options["timezone"]
        try:
            local_tz = zoneinfo.ZoneInfo(tz_name)
        except Exception:
            self.stderr.write(f"Invalid timezone '{tz_name}'. Falling back to UTC.")
            local_tz = zoneinfo.ZoneInfo("UTC")

        self.stdout.write(f"Using timezone: {local_tz}")
        
        # Track last execution time for each planner to prevent duplicate creation
        last_execution = {}

        while True:
            now_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)
            now = now_utc.astimezone(local_tz)
            self.stdout.write(f"Now (local): {now}")

            for planner in Planner.objects.all():
                # Convert UTC times to local timezone properly
                start_time = planner.start_date_time.astimezone(local_tz).replace(second=0, microsecond=0)
                end_time = planner.end_date_time.astimezone(local_tz).replace(second=0, microsecond=0)

                self.stdout.write(
                    f"Planner ID {planner.id} - Start (local): {start_time}, End (local): {end_time}"
                )

                if now < start_time or now >= end_time:
                    self.stdout.write("Not in range yet..")
                    continue
                
                # Create a unique key for tracking this planner's last execution
                today_str = now.strftime("%Y-%m-%d")
                planner_key = f"{planner.id}_{today_str}"

                if (
                    planner.rule == "Daily"
                    and now.time() >= start_time.time()
                    and now.time() <= (start_time + timedelta(minutes=1)).time()
                ):
                    # Check if we already created an evince today for this planner
                    if planner_key in last_execution:
                        self.stdout.write(f"Already created evince today for Planner {planner.id}. Skipping.")
                        continue
                    
                    self.stdout.write("Creating Evince now (Daily).")
                    self.create_evince(planner)
                    last_execution[planner_key] = now  # Mark as executed

                elif (
                    planner.rule == "Weekly"
                    and now.time() >= start_time.time()
                    and now.time() <= (start_time + timedelta(minutes=1)).time()
                ):
                    if now.strftime("%A") in planner.day_of_week.split(","):
                        # Check if we already created an evince today for this planner
                        if planner_key in last_execution:
                            self.stdout.write(f"Already created evince today for Planner {planner.id}. Skipping.")
                            continue
                        
                        self.stdout.write("Creating Evince now (Weekly).")
                        self.create_evince(planner)
                        last_execution[planner_key] = now  # Mark as executed

                elif (
                    planner.rule == "Monthly"
                    and now.time() >= start_time.time()
                    and now.time() <= (start_time + timedelta(minutes=1)).time()
                ):
                    if now.strftime("%A") in planner.day_of_week.split(
                        ","
                    ) and now.strftime("%b-%Y") in planner.month.split(","):
                        # Check if we already created an evince today for this planner
                        if planner_key in last_execution:
                            self.stdout.write(f"Already created evince today for Planner {planner.id}. Skipping.")
                            continue
                        
                        self.stdout.write("Creating Evince now (Monthly).")
                        self.create_evince(planner)
                        last_execution[planner_key] = now  # Mark as executed

            sleep(60)

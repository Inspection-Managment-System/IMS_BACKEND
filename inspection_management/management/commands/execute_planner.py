from datetime import datetime, timedelta, timezone
from time import sleep

from django.core.management.base import BaseCommand

from ims_backend.utils.evinceflow import create_evince_instance
from inspection_management.models import Evince, Planner


class Command(BaseCommand):
    help = "Create Evince objects based on Planner rules"

    def create_evince(self, planner):
        evince = Evince(
            description=planner.evince_description,
            business_unit=planner.evince_business_unit,
            inspection_point=planner.evince_inspection_point,
            changed_by=planner.changed_by,
            reviewed_by=planner.reviewed_by,
            start_date_time=planner.start_date_time,
            end_date_time=planner.end_date_time,
            status="Logged",
        )
        evince.save()
        data = {"changed_by": planner.changed_by}
        evince.inspection_analyses.set(planner.evince_inspection_analyses.all())
        create_evince_instance(evince, data)

    def handle(self, *args, **options):
        print("Planner Running...")
        while True:
            # Make 'now' timezone-aware
            now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
            print("Now: ", now)

            for planner in Planner.objects.all():
                start_time = planner.start_date_time.replace(second=0, microsecond=0)
                end_time = planner.end_date_time.replace(second=0, microsecond=0)

                print("Start: ", start_time)
                print("End: ", end_time)

                if now < start_time or now >= end_time:
                    print("Not in range yet..")
                    continue

                # Time-based logic for rule matching
                if (
                    planner.rule == "Daily"
                    and now.time() >= start_time.time()
                    and now.time() <= (start_time + timedelta(minutes=1)).time()
                ):
                    print("Creating Evince now (Daily).")
                    self.create_evince(planner)

                elif (
                    planner.rule == "Weekly"
                    and now.time() >= start_time.time()
                    and now.time() <= (start_time + timedelta(minutes=1)).time()
                ):
                    if now.strftime("%A") in planner.day_of_week.split(","):
                        print("Creating Evince now (Weekly).")
                        self.create_evince(planner)

                elif (
                    planner.rule == "Monthly"
                    and now.time() >= start_time.time()
                    and now.time() <= (start_time + timedelta(minutes=1)).time()
                ):
                    if now.strftime("%A") in planner.day_of_week.split(
                        ","
                    ) and now.strftime("%b-%Y") in planner.month.split(","):
                        print("Creating Evince now (Monthly).")
                        self.create_evince(planner)

            sleep(60)

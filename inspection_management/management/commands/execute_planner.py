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
            '--timezone',
            type=str,
            help='Timezone name (IANA, e.g. Asia/Dubai, Europe/London). Defaults to UTC.',
            default='UTC'
        )

    def to_local_naive(self, dt_utc, local_tz):
        naive = dt_utc.replace(tzinfo=None)
        return naive.replace(tzinfo=local_tz)

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
        tz_name = options['timezone']
        try:
            local_tz = zoneinfo.ZoneInfo(tz_name)
        except Exception:
            self.stderr.write(f"Invalid timezone '{tz_name}'. Falling back to UTC.")
            local_tz = zoneinfo.ZoneInfo("UTC")

        self.stdout.write(f"Using timezone: {local_tz}")

        while True:
            now_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)
            now = now_utc.astimezone(local_tz)
            self.stdout.write(f"Now (local): {now}")

            for planner in Planner.objects.all():
                start_time = self.to_local_naive(planner.start_date_time, local_tz).replace(second=0, microsecond=0)
                end_time = self.to_local_naive(planner.end_date_time, local_tz).replace(second=0, microsecond=0)

                self.stdout.write(f"Planner ID {planner.id} - Start (local naive): {start_time}, End (local naive): {end_time}")

                if now < start_time or now >= end_time:
                    self.stdout.write("Not in range yet..")
                    continue

                if (
                    planner.rule == "Daily"
                    and now.time() >= start_time.time()
                    and now.time() <= (start_time + timedelta(minutes=1)).time()
                ):
                    self.stdout.write("Creating Evince now (Daily).")
                    self.create_evince(planner)

                elif (
                    planner.rule == "Weekly"
                    and now.time() >= start_time.time()
                    and now.time() <= (start_time + timedelta(minutes=1)).time()
                ):
                    if now.strftime("%A") in planner.day_of_week.split(","):
                        self.stdout.write("Creating Evince now (Weekly).")
                        self.create_evince(planner)

                elif (
                    planner.rule == "Monthly"
                    and now.time() >= start_time.time()
                    and now.time() <= (start_time + timedelta(minutes=1)).time()
                ):
                    if now.strftime("%A") in planner.day_of_week.split(",") and now.strftime("%b-%Y") in planner.month.split(","):
                        self.stdout.write("Creating Evince now (Monthly).")
                        self.create_evince(planner)

            sleep(60)

from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from collections import defaultdict
import calendar
import json
import time
from apps.core.utils.api_clients import CarbonIntensityService


class Command(BaseCommand):
    help = "Collect monthly generation mix data and store in JSON format"

    def add_arguments(self, parser):
        parser.add_argument(
            "--start-date",
            type=str,
            default="2022-11",
            help="Start date in YYYY-MM format (default: 2022-11)",
        )
        parser.add_argument(
            "--output",
            type=str,
            default="monthly_generation_averages.json",
            help="Output JSON file path (default: monthly_generation_averages.json)",
        )

    def handle(self, *args, **options):
        client = CarbonIntensityService()
        monthly_data = defaultdict(
            lambda: defaultdict(lambda: {"sum": defaultdict(float), "count": 0})
        )

        # Parse start date
        start_year, start_month = map(int, options["start_date"].split("-"))
        current_date = datetime.now()
        year, month = start_year, start_month

        self.stdout.write(
            f"Starting data collection from {year}-{month:02d} to {current_date.year}-{current_date.month:02d}..."
        )

        while True:
            # Calculate month parameters
            is_current_month = year == current_date.year and month == current_date.month

            if is_current_month:
                end_day = current_date.day
            else:
                end_day = calendar.monthrange(year, month)[1]

            start_date = datetime(year, month, 1)
            end_date = datetime(year, month, end_day, 23, 59, 59)
            current_chunk_start = start_date

            self.stdout.write(f"\nProcessing {year}-{month:02d}...")

            # Split month into 14-day chunks
            while current_chunk_start <= end_date:
                current_chunk_end = current_chunk_start + timedelta(days=13)

                # Adjust chunk end if it exceeds month end
                if current_chunk_end > end_date:
                    current_chunk_end = end_date
                else:
                    current_chunk_end = current_chunk_end.replace(
                        hour=23, minute=59, second=59
                    )

                self.stdout.write(
                    f"Fetching {current_chunk_start.date()} to {current_chunk_end.date()}..."
                )

                try:
                    response = client.get_regional_intensity_range(
                        current_chunk_start, current_chunk_end
                    )
                except Exception as e:
                    self.stderr.write(
                        f"Error fetching {current_chunk_start}-{current_chunk_end}: {str(e)}"
                    )
                    current_chunk_start = current_chunk_end + timedelta(seconds=1)
                    continue

                if not response.get("data"):
                    self.stdout.write(
                        f"No data for {current_chunk_start}-{current_chunk_end}"
                    )
                    current_chunk_start = current_chunk_end + timedelta(seconds=1)
                    continue

                # Process each 30-minute interval
                for interval in response["data"]:
                    for region in interval["regions"]:
                        region_id = region["regionid"]
                        for fuel_data in region["generationmix"]:
                            monthly_data[(year, month)][region_id]["sum"][
                                fuel_data["fuel"]
                            ] += fuel_data["perc"]
                        monthly_data[(year, month)][region_id]["count"] += 1

                current_chunk_start = current_chunk_end + timedelta(seconds=1)
                time.sleep(1)  # Rate limiting between API calls

            # Break after processing current month
            if is_current_month:
                break

            # Move to next month
            month += 1
            if month > 12:
                month = 1
                year += 1

        # Calculate averages and format results
        result = {}
        for (year, month), regions in monthly_data.items():
            month_key = f"{year}-{month:02d}"
            result[month_key] = {}
            for region_id, data in regions.items():
                count = data["count"]
                if count == 0:
                    continue
                result[month_key][str(region_id)] = {
                    fuel: round(total / count, 1) for fuel, total in data["sum"].items()
                }

        # Save to JSON file
        output_path = options["output"]
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully saved data to {output_path}")
        )

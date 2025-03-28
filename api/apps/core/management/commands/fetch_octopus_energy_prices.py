import json
import requests
import calendar
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = "Fetch energy prices for all GSPs and save as JSON with monthly averages"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            type=str,
            default="energy_data",
            help="Directory to save JSON files",
        )

    def handle(self, *args, **options):
        # Create output directory if it doesn't exist
        output_dir = options["output_dir"]
        os.makedirs(output_dir, exist_ok=True)

        gsps = [chr(ord("C") + i) for i in range(14)]  # A-P
        all_data = {gsp: {} for gsp in gsps}

        for gsp in gsps:
            self.stdout.write(f"Processing GSP {gsp}...")
            gsp_data = self.process_gsp(gsp)

            # Save individual GSP file
            filename = os.path.join(output_dir, f"energy_prices_gsp_{gsp}.json")
            with open(filename, "w") as f:
                json.dump(gsp_data, f, indent=2)

            all_data[gsp] = gsp_data

        # Save combined data
        combined_filename = os.path.join(output_dir, "energy_prices_all_gsps.json")
        with open(combined_filename, "w") as f:
            json.dump(all_data, f, indent=2)

        self.stdout.write(self.style.SUCCESS("Data collection complete!"))

    def process_gsp(self, gsp):
        gsp_data = {}
        current_year = 2022
        current_month = 11
        end_year = 2025
        end_month = 1

        while True:
            if (current_year > end_year) or (
                current_year == end_year and current_month > end_month
            ):
                break

            year_month = f"{current_year}-{str(current_month).zfill(2)}"
            month_data = {"days": {}, "average": None}
            monthly_values = []

            days_in_month = calendar.monthrange(current_year, current_month)[1]

            for day in range(1, days_in_month + 1):
                try:
                    period_from = datetime(current_year, current_month, day)
                except ValueError:
                    break

                period_to = period_from + timedelta(days=1)
                date_key = period_from.strftime("%Y-%m-%d")

                try:
                    data = self.fetch_day_data(gsp, period_from, period_to)
                    if data:
                        month_data["days"][date_key] = data
                        monthly_values.extend(
                            [entry["value_exc_vat"] for entry in data]
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error fetching {date_key} for GSP {gsp}: {str(e)}"
                        )
                    )

            if monthly_values:
                month_data["average"] = round(
                    sum(monthly_values) / len(monthly_values), 2
                )

            gsp_data[year_month] = month_data

            # Move to next month
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        return gsp_data

    def fetch_day_data(self, gsp, period_from, period_to):
        url = (
            "https://api.octopus.energy/v1/products/AGILE-FLEX-22-11-25/"
            f"electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-{gsp}/standard-unit-rates/"
        )
        params = {
            "period_from": period_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "period_to": period_to.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return [
                {
                    "valid_from": entry["valid_from"],
                    "valid_to": entry["valid_to"],
                    "value_exc_vat": entry["value_exc_vat"],
                }
                for entry in data.get("results", [])
            ]
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.WARNING(
                    f"API request failed for GSP {gsp} ({period_from}): {str(e)}"
                )
            )
            return None

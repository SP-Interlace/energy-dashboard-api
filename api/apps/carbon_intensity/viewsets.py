from datetime import datetime, timedelta
from dataclasses import asdict
import json
import os
from pathlib import Path
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime
from django.core.exceptions import ValidationError
from .models import (
    CarbonIntensity,
    CarbonIntensityData,
    Region,
    GenerationMix,
    CarbonIntensityStats,
    CarbonIntensityStatistics,
)
from .serializers import (
    CarbonIntensitySerializer,
    RegionSerializer,
    GenerationMixSerializer,
    CarbonIntensityStatsSerializer,
)

from apps.core.utils.api_clients import CarbonIntensityService


class CarbonIntensityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CarbonIntensitySerializer

    def get_queryset(self):
        params = self.request.query_params
        print(params)
        from_dt = parse_datetime(
            params.get(
                "from", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            )
        )
        to_dt = parse_datetime(params.get("to", datetime.now().strftime("%Y-%m-%d")))
        region_id = params.get("region_id")
        postcode = params.get("postcode")

        if not from_dt or not to_dt:
            raise ValidationError("Both 'from' and 'to' datetime parameters required")

        queryset = CarbonIntensity.objects.get_for_period(from_dt, to_dt, region_id)

        if postcode:
            queryset = queryset.filter(postcode_prefix=postcode[:4])

        return queryset

    @action(detail=False, methods=["get"], url_path="latest")
    def latest(self, request):
        """Take latest stored national intensity (from Django DB)."""
        instance = CarbonIntensity.objects.latest_national_intensity()
        if not instance:
            return Response(
                {"detail": "No data available"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # National Intensity Endpoints
    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        """Gets current national intensity."""
        service = CarbonIntensityService()
        response = service.get_current_intensity()
        return self._handle_intensity_response(response)

    @action(detail=False, methods=["get"], url_path="regional")
    def regional(self, request):
        """Gets current regional intensity."""
        service = CarbonIntensityService()
        response = service.get_regional_current()
        print(response)
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def today(self, request):
        """Gets today's national intensity."""
        service = CarbonIntensityService()
        response = service.get_intensity_today()
        return self._handle_intensity_response(response)

    @action(detail=False, methods=["get"], url_path="date/(?P<date>[^/.]+)")
    def intensity_date(self, request, date=None):
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date().isoformat()
        except ValueError:
            raise ValidationError("Invalid date format. Use YYYY-MM-DD.")
        service = CarbonIntensityService()
        response = service.get_intensity_date(parsed_date)
        return self._handle_intensity_response(response)

    @action(detail=False, methods=["get"], url_path="quarterly-generationmix")
    def quarterly(self, request):
        """Gets quarterly generation mix."""
        year = request.query_params.get("year")
        quarter = request.query_params.get("quarter")
        if not year or not quarter:
            return Response(
                {"error": "Year and quarter are required parameters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        module_path = Path(__file__).resolve().parent.parent.parent
        file_path = os.path.join(
            module_path, "data/generationmix/monthly_generation_averages.json"
        )
        # Check if the file exists
        if not os.path.exists(file_path):
            return Response(
                {"error": "Data file not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Load the data from the JSON file
        with open(file_path, "r") as f:
            data = json.load(f)

        # Filter the data for the specified quarter and year
        filtered_data = {}
        for month, regions in data.items():
            month_date = datetime.strptime(month, "%Y-%m")
            if month_date.year == int(year) and (month_date.month - 1) // 3 + 1 == int(
                quarter
            ):
                filtered_data[month] = regions

        return Response(filtered_data)

    @action(
        detail=False,
        methods=["get"],
        url_path="stats/(?P<from_time>[^/]+)/(?P<to_time>[^/]+)",
    )
    def stats(self, request, from_time=None, to_time=None):
        from_dt = parse_datetime(from_time)
        to_dt = parse_datetime(to_time)
        if not from_dt or not to_dt:
            raise ValidationError("Valid 'from' and 'to' datetimes required.")
        service = CarbonIntensityService()
        response = service.get_statistics(from_dt, to_dt)
        return self._handle_stats_response(response, from_dt, to_dt)

    def _handle_intensity_response(self, response):
        if not response or "data" not in response:
            return Response(
                {"detail": "No data available"}, status=status.HTTP_404_NOT_FOUND
            )

        # Save data to CarbonIntensity model
        data = response["data"]
        if isinstance(data, list):
            entries = data
        else:
            entries = [data]

        saved_instances = []
        for entry in entries:
            intensity = entry.get("intensity", {})
            ci_data = CarbonIntensityData(
                from_datetime=parse_datetime(entry["from"]),
                to_datetime=parse_datetime(entry["to"]),
                actual=intensity.get("actual"),
                forecast=intensity.get("forecast"),
                index=intensity.get("index", "moderate"),
            )
            obj, created = CarbonIntensity.objects.update_or_create(
                from_datetime=ci_data.from_datetime,
                to_datetime=ci_data.to_datetime,
                defaults=asdict(ci_data),
            )
            saved_instances.append(obj)

        serializer = self.get_serializer(saved_instances, many=True)
        return Response(serializer.data)

    def _handle_stats_response(self, response, from_dt, to_dt):
        if not response or "data" not in response:
            return Response(
                {"detail": "No data available"}, status=status.HTTP_404_NOT_FOUND
            )

        # Save stats data
        stats_data = CarbonIntensityStatistics(
            from_datetime=from_dt,
            to_datetime=to_dt,
            min_intensity=response["data"]["min"],
            max_intensity=response["data"]["max"],
            average_intensity=response["data"]["average"],
        )
        stats_obj = CarbonIntensityStats.from_dataclass(stats_data)
        stats_obj.save()

        serializer = CarbonIntensityStatsSerializer(stats_obj)
        return Response(serializer.data)


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    lookup_field = "region_id"


class GenerationMixViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GenerationMixSerializer

    def get_queryset(self):
        params = self.request.query_params
        from_dt = parse_datetime(params.get("from"))
        to_dt = parse_datetime(params.get("to"))

        if from_dt and to_dt:
            return GenerationMix.objects.filter(
                from_datetime__gte=from_dt, to_datetime__lte=to_dt
            )
        return GenerationMix.objects.all()

    @action(detail=False, methods=["get"])
    def latest(self, request):
        instance = GenerationMix.objects.get_latest_mix()
        if not instance:
            return Response(
                {"detail": "No data available"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CarbonIntensityStatsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CarbonIntensityStatsSerializer

    def get_queryset(self):
        params = self.request.query_params
        from_dt = parse_datetime(params.get("from"))
        to_dt = parse_datetime(params.get("to"))

        if not from_dt or not to_dt:
            raise ValidationError("Both 'from' and 'to' datetime parameters required")

        return CarbonIntensityStats.objects.get_stats(from_dt, to_dt)

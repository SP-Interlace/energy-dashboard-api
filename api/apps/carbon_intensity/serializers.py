from rest_framework import serializers
from .models import CarbonIntensity, Region, GenerationMix, CarbonIntensityStats


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ["region_id", "name", "postcode_prefix", "short_name"]


class CarbonIntensitySerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)
    index = serializers.CharField(source="get_index_display")

    class Meta:
        model = CarbonIntensity
        fields = [
            "from_datetime",
            "to_datetime",
            "actual",
            "forecast",
            "index",
            "region",
            "postcode_prefix",
        ]


class GenerationMixSerializer(serializers.ModelSerializer):
    fuel_mix = serializers.JSONField(binary=True)

    class Meta:
        model = GenerationMix
        fields = ["from_datetime", "to_datetime", "fuel_mix"]


class CarbonIntensityStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbonIntensityStats
        fields = "__all__"

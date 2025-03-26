from django.db import models
from django.core.cache import cache
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, Optional
import json
import logging

from apps.core.utils.api_clients import CarbonIntensityService

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_TTL = 60 * 15  # 15 minutes


class CarbonIntensityManager(models.Manager):
    """Custom manager for CarbonIntensity model with caching."""

    def get_for_period(
        self, from_dt: datetime, to_dt: datetime, region_id: int = None
    ) -> models.QuerySet:
        cache_key = f"carbon_intensity_{from_dt}_{to_dt}_{region_id}".replace(
            " ", "_"
        ).replace(":", "-")
        cached = cache.get(cache_key)

        if cached:
            logger.debug("Returning cached carbon intensity data")
            return cached

        qs = self.filter(from_datetime__gte=from_dt, to_datetime__lte=to_dt)

        if not qs.exists():
            # Trigger service directly if celery hasn't updated the data
            service = CarbonIntensityService()
            response = service.get_intensity_between(from_dt, to_dt)
            if response and "data" in response:
                for entry in response["data"]:
                    intensity = entry.get("intensity", {})
                    ci_data = CarbonIntensityData(
                        from_datetime=entry["from"],
                        to_datetime=entry["to"],
                        actual=intensity.get("actual"),
                        forecast=intensity.get("forecast"),
                        index=intensity.get("index", "moderate"),
                    )
                    CarbonIntensity.from_dataclass(ci_data).save()

            qs = self.filter(from_datetime__gte=from_dt, to_datetime__lte=to_dt)

        if region_id:
            qs = qs.filter(region_id=region_id)
        else:
            qs = qs.filter(region__isnull=True)

        qs = qs.order_by("from_datetime")
        cache.set(cache_key, qs, CACHE_TTL)
        return qs

    def latest_national_intensity(self) -> Optional["CarbonIntensity"]:
        cache_key = "latest_national_intensity"
        cached = cache.get(cache_key)

        if cached:
            return cached

        instance = self.filter(region__isnull=True).order_by("-from_datetime").first()
        cache.set(cache_key, instance, 60)  # 1 minute cache for latest data
        return instance


class Region(models.Model):
    """Represents a geographical region with carbon intensity data"""

    region_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    postcode_prefix = models.CharField(max_length=4, null=True, blank=True, unique=True)
    short_name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["postcode_prefix"]),
            models.Index(fields=["short_name"]),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.region_id})"


@dataclass
class CarbonIntensityData:
    """Dataclass for validating and converting carbon intensity data"""

    from_datetime: datetime
    to_datetime: datetime
    actual: Optional[int] = None
    forecast: Optional[int] = None
    index: str = "moderate"
    region_id: Optional[int] = None
    postcode_prefix: Optional[str] = None

    def to_model(self) -> "CarbonIntensity":
        """Converts dataclass to Django model instance"""
        return CarbonIntensity.from_dataclass(self)


class CarbonIntensity(models.Model):
    """Stores carbon intensity data for national and regional levels"""

    INTENSITY_INDEXES = [
        ("very low", "Very Low"),
        ("low", "Low"),
        ("moderate", "Moderate"),
        ("high", "High"),
        ("very high", "Very High"),
    ]

    from_datetime = models.DateTimeField()
    to_datetime = models.DateTimeField()
    actual = models.IntegerField(null=True, blank=True)
    forecast = models.IntegerField(null=True, blank=True)
    index = models.CharField(
        max_length=20, choices=INTENSITY_INDEXES, default="moderate"
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="intensity_data",
    )
    postcode_prefix = models.CharField(max_length=4, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = CarbonIntensityManager()

    class Meta:
        indexes = [
            models.Index(fields=["from_datetime", "to_datetime"]),
            models.Index(fields=["postcode_prefix"]),
            models.Index(fields=["index"]),
        ]
        ordering = ["-from_datetime"]
        unique_together = [
            ("from_datetime", "to_datetime", "region", "postcode_prefix"),
        ]

    def __str__(self):
        location = self.region or self.postcode_prefix or "National"
        return f"Carbon Intensity for {location} at {self.from_datetime}"

    @classmethod
    def from_dataclass(cls, data: CarbonIntensityData) -> "CarbonIntensity":
        """Create model instance from dataclass"""
        return cls(**asdict(data))

    def save(self, *args, **kwargs):
        """Override save to handle cache invalidation and duplicates"""
        # Check for existing data before saving
        exists = CarbonIntensity.objects.filter(
            from_datetime=self.from_datetime,
            to_datetime=self.to_datetime,
            region=self.region,
            postcode_prefix=self.postcode_prefix,
        ).exists()

        if exists:
            logger.warning("Duplicate carbon intensity data detected")
            return

        super().save(*args, **kwargs)
        # Invalidate relevant caches
        cache.delete_many(
            [
                "latest_national_intensity",
                f"carbon_intensity_{self.from_datetime}_{self.to_datetime}",
            ]
        )


class GenerationMixManager(models.Manager):
    """Custom manager for GenerationMix model with caching"""

    def get_latest_mix(self) -> Optional["GenerationMix"]:
        cache_key = "latest_generation_mix"
        cached = cache.get(cache_key)

        if cached:
            return cached

        instance = self.order_by("-from_datetime").first()
        cache.set(cache_key, instance, 60)  # 1 minute cache
        return instance


@dataclass
class GenerationMixData:
    """Dataclass for validating and converting generation mix data"""

    from_datetime: datetime
    to_datetime: datetime
    fuel_mix: Dict[str, float]  # {fuel_type: percentage}

    def to_model(self) -> "GenerationMix":
        """Converts dataclass to Django model instance"""
        return GenerationMix.from_dataclass(self)


class GenerationMix(models.Model):
    """Stores electricity generation mix percentages by fuel type"""

    from_datetime = models.DateTimeField()
    to_datetime = models.DateTimeField()
    fuel_mix = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = GenerationMixManager()

    class Meta:
        verbose_name_plural = "Generation Mixes"
        ordering = ["-from_datetime"]
        unique_together = [
            ("from_datetime", "to_datetime"),
        ]

    def __str__(self):
        return f"Generation Mix from {self.from_datetime} to {self.to_datetime}"

    @classmethod
    def from_dataclass(cls, data: GenerationMixData) -> "GenerationMix":
        """Create model instance from dataclass"""
        return cls(
            from_datetime=data.from_datetime,
            to_datetime=data.to_datetime,
            fuel_mix=json.dumps(data.fuel_mix),
        )

    def save(self, *args, **kwargs):
        """Override save to handle cache invalidation"""
        super().save(*args, **kwargs)
        cache.delete("latest_generation_mix")


class CarbonIntensityStatsManager(models.Manager):
    """Custom manager for statistical data with caching"""

    def get_stats(self, from_dt: datetime, to_dt: datetime) -> models.QuerySet:
        cache_key = f"carbon_stats_{from_dt}_{to_dt}"
        cached = cache.get(cache_key)

        if cached:
            return cached

        qs = self.filter(from_datetime=from_dt, to_datetime=to_dt).order_by("-created")

        cache.set(cache_key, qs, CACHE_TTL)
        return qs


@dataclass
class CarbonIntensityStatistics:
    """Dataclass for carbon intensity statistics"""

    from_datetime: datetime
    to_datetime: datetime
    min_intensity: int
    max_intensity: int
    average_intensity: float
    block_hours: Optional[int] = None

    def to_model(self) -> "CarbonIntensityStats":
        """Converts dataclass to Django model instance"""
        return CarbonIntensityStats.from_dataclass(self)


class CarbonIntensityStats(models.Model):
    """Stores statistical data about carbon intensity"""

    from_datetime = models.DateTimeField()
    to_datetime = models.DateTimeField()
    min_intensity = models.IntegerField()
    max_intensity = models.IntegerField()
    average_intensity = models.FloatField()
    block_hours = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = CarbonIntensityStatsManager()

    class Meta:
        verbose_name_plural = "Carbon Intensity Statistics"
        ordering = ["-from_datetime"]
        unique_together = [
            ("from_datetime", "to_datetime", "block_hours"),
        ]

    def __str__(self):
        return f"Stats from {self.from_datetime} to {self.to_datetime}"

    @classmethod
    def from_dataclass(cls, data: CarbonIntensityStatistics) -> "CarbonIntensityStats":
        """Create model instance from dataclass"""
        return cls(**asdict(data))

    def save(self, *args, **kwargs):
        """Override save to handle cache invalidation"""
        super().save(*args, **kwargs)
        cache.delete(f"carbon_stats_{self.from_datetime}_{self.to_datetime}")

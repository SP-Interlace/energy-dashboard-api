# tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger
from .models import CarbonIntensity, GenerationMix
from apps.core.utils.api_clients import CarbonIntensityService
from .models import (
    CarbonIntensityData,
    GenerationMixData,
)  # Dataclasses for storing API response data

logger = get_task_logger(__name__)


@shared_task
def update_intensity_data():
    service = CarbonIntensityService()
    try:
        # Update national data
        national_data = service.get_current_intensity()
        process_intensity_response(national_data)

        # Update regional data
        regional_data = service.get_regional_current()
        process_regional_response(regional_data)

        logger.info("Successfully updated intensity data")
    except Exception as e:
        logger.error(f"Error updating intensity data: {str(e)}")
        raise


@shared_task
def update_generation_mix():
    service = CarbonIntensityService()
    try:
        response = service.get_current_generation()
        if response and "data" in response:
            for entry in response["data"]:
                mix_data = GenerationMixData(
                    from_datetime=entry["from"],
                    to_datetime=entry["to"],
                    fuel_mix={
                        item["fuel"]: item["perc"] for item in entry["generationmix"]
                    },
                )
                GenerationMix.from_dataclass(mix_data).save()
        logger.info("Successfully updated generation mix")
    except Exception as e:
        logger.error(f"Error updating generation mix: {str(e)}")
        raise


def process_intensity_response(response):
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


def process_regional_response(response):
    if response and "data" in response:
        for region in response["data"].get("regions", []):
            intensity = region.get("intensity", {})
            ci_data = CarbonIntensityData(
                from_datetime=region["from"],
                to_datetime=region["to"],
                actual=intensity.get("actual"),
                forecast=intensity.get("forecast"),
                index=intensity.get("index", "moderate"),
                region_id=region.get("regionid"),
            )
            CarbonIntensity.from_dataclass(ci_data).save()

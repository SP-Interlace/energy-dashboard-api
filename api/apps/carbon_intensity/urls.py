from rest_framework.routers import SimpleRouter

from . import viewsets

router = SimpleRouter()

router.register(
    "carbon-intensity", viewsets.CarbonIntensityViewSet, basename="carbon-intensity"
)
router.register("region", viewsets.RegionViewSet, basename="region")
router.register(
    "generation-mix", viewsets.GenerationMixViewSet, basename="generation-mix"
)

urlpatterns = router.urls

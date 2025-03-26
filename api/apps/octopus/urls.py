from rest_framework.routers import SimpleRouter

from . import viewsets

router = SimpleRouter()

router.register(
    "grid-supply-point", viewsets.GridSupplyPointViewSet, basename="grid-supply-point"
)
router.register(
    "grid-supply-point-price",
    viewsets.GSPPriceViewSet,
    basename="grid-supply-point-price",
)

urlpatterns = router.urls

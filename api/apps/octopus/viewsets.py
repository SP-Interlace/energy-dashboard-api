from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.core.utils.api_clients import OctopusService
from .serializers import GridSupplyPointSerializer, GSPPriceSerializer
from datetime import datetime


class GridSupplyPointViewSet(viewsets.ViewSet):
    """
    ViewSet for Grid Supply Points (GSPs).
    """

    def list(self, request):
        service = OctopusService()
        gsp_data = service.get_grid_supply_points(format="json")
        serializer = GridSupplyPointSerializer(gsp_data.get("results", []), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="by-postcode")
    def by_postcode(self, request):
        postcode = request.query_params.get("postcode", "SW1A1AA")
        service = OctopusService()
        group_id = service.get_grid_supply_point_by_postcode(postcode=postcode)
        return Response({"group_id": group_id})


class GSPPriceViewSet(viewsets.ViewSet):
    """
    ViewSet for GSP-specific energy prices.
    """

    gsp_conversion_table = {
        1: "A",
        2: "B",
        3: "C",
        4: "D",
        5: "E",
        6: "F",
        7: "G",
        8: "H",
        9: "J",
        10: "K",
        11: "L",
        12: "M",
        13: "N",
        14: "P",
    }

    def list(self, request):
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        from_date = datetime.strptime(from_date, "%Y-%m-%dT%H:%MZ").isoformat()
        to_date = datetime.strptime(to_date, "%Y-%m-%dT%H:%MZ").isoformat()

        gsp = request.query_params.get("gsp", 1)
        # Convert GSP to alphabetical format (GSP Group ID)
        if gsp in self.gsp_conversion_table:
            gsp = self.gsp_conversion_table[gsp]

        # Validate dates
        try:
            from_date = datetime.fromisoformat(from_date) if from_date else None
            to_date = datetime.fromisoformat(to_date) if to_date else None
        except ValueError:
            return Response(
                {
                    "error": "Invalid date format. Use ISO format (e.g., 2024-05-30T00:00:00Z)"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = OctopusService()
        print("Okay all good up to here")
        price_data = service.get_gsp_price_today(gsp)
        serializer = GSPPriceSerializer(price_data.get("results", []), many=True)
        return Response(serializer.data)

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.core.utils.api_clients import OctopusService
from .serializers import GridSupplyPointSerializer, GSPPriceSerializer
from datetime import datetime

import os
import json


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

    inv_gsp_conversion_table = {v: k for k, v in gsp_conversion_table.items()}

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
        price_data = service.get_gsp_price(gsp, from_date, to_date)
        serializer = GSPPriceSerializer(price_data.get("results", []), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="aggregated-prices")
    def aggregated_prices(self, request):
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        from_date = datetime.strptime(from_date, "%Y-%m-%dT%H:%MZ").isoformat()
        to_date = datetime.strptime(to_date, "%Y-%m-%dT%H:%MZ").isoformat()

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

        results = {}
        for gsp in self.gsp_conversion_table.values():
            results[self.inv_gsp_conversion_table[gsp]] = GSPPriceSerializer(
                service.get_gsp_price(gsp, from_date, to_date).get("results", []),
                many=True,
            ).data

        return Response(results)

    @action(detail=False, methods=["get"], url_path="quarterly-prices")
    def quarterly_prices_by_region(self, request):
        quarter = request.query_params.get("quarter")
        year = request.query_params.get("year")
        if not quarter or not year:
            return Response(
                {"error": "Quarter and year are required parameters."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            quarter = int(quarter)
            year = int(year)
        except ValueError:
            return Response(
                {"error": "Quarter and year must be integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if quarter < 1 or quarter > 4:
            return Response(
                {"error": "Quarter must be between 1 and 4."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate the start and end dates for the quarter
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2
        start_date = datetime(year, start_month, 1)
        end_date = datetime(year, end_month, 1)

        # Get data from api/data/octopus_prices
        # get module path to avoid missing file error
        module_path = os.path.dirname(__file__)
        file_path = os.path.join(
            module_path, "../../data/octopus_prices/energy_prices_gsp_quarters.json"
        )
        # Check if the file exists
        print(file_path)
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
        for region, prices in data.items():
            filtered_prices = []
            for month, price in prices.items():
                month_date = datetime.strptime(month, "%Y-%m")
                if start_date <= month_date <= end_date:
                    print(month_date, start_date, end_date)
                    filtered_prices.append(price)
            if filtered_prices:
                print(region)
                print(self.inv_gsp_conversion_table.keys())
                print(self.inv_gsp_conversion_table[region])
                filtered_data[self.inv_gsp_conversion_table[region]] = filtered_prices
        # Return the filtered data
        return Response(filtered_data)

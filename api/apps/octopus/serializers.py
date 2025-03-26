from rest_framework import serializers


class GridSupplyPointSerializer(serializers.Serializer):
    group_id = serializers.CharField()
    # Add other fields from the API response as needed


class GSPPriceSerializer(serializers.Serializer):
    value_exc_vat = serializers.FloatField()
    value_inc_vat = serializers.FloatField()
    valid_from = serializers.DateTimeField()
    valid_to = serializers.DateTimeField()

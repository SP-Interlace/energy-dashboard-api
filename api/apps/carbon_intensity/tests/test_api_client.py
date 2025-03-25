from django.test import TestCase
from unittest.mock import Mock, patch
from apps.core.utils.api_clients import CarbonIntensityService


class CarbonIntensityTests(TestCase):
    def setUp(self):
        self.service = CarbonIntensityService()
        self.mock_get = patch.object(self.service.session, "get").start()
        self.mock_response = Mock()
        self.mock_response.json.return_value = {"data": "dummy"}
        self.mock_get.return_value = self.mock_response
        self.addCleanup(patch.stopall)

    # Carbon Intensity - National tests
    def test_get_current_intensity(self):
        result = self.service.get_current_intensity()
        self.mock_get.assert_called_once_with(f"{self.service.base_url}intensity")
        self.assertEqual(result, {"data": "dummy"})

    def test_get_intensity_today(self):
        result = self.service.get_intensity_today()
        self.mock_get.assert_called_once_with(f"{self.service.base_url}intensity/date")
        self.assertEqual(result, {"data": "dummy"})

    def test_get_intensity_date(self):
        date = "2023-10-01"
        result = self.service.get_intensity_date(date)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}intensity/date/{date}"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_intensity_date_period(self):
        date = "2023-10-01"
        period = 1
        result = self.service.get_intensity_date_period(date, period)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}intensity/date/{date}/{period}"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_intensity_factors(self):
        result = self.service.get_intensity_factors()
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}intensity/factors"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_intensity_from(self):
        from_time = "2023-10-01T12:00Z"
        result = self.service.get_intensity_from(from_time)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}intensity/{from_time}"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_intensity_fw24h(self):
        from_time = "2023-10-01T12:00Z"
        result = self.service.get_intensity_fw24h(from_time)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}intensity/{from_time}/fw24h"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_intensity_fw48h(self):
        from_time = "2023-10-01T12:00Z"
        result = self.service.get_intensity_fw48h(from_time)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}intensity/{from_time}/fw48h"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_intensity_pt24h(self):
        from_time = "2023-10-01T12:00Z"
        result = self.service.get_intensity_pt24h(from_time)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}intensity/{from_time}/pt24h"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_intensity_between(self):
        from_time = "2023-10-01T12:00Z"
        to_time = "2023-10-02T12:00Z"
        result = self.service.get_intensity_between(from_time, to_time)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}intensity/{from_time}/{to_time}"
        )
        self.assertEqual(result, {"data": "dummy"})

    # Statistics - National tests
    def test_get_statistics(self):
        from_time = "2023-10-01"
        to_time = "2023-10-02"
        result = self.service.get_statistics(from_time, to_time)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}intensity/stats/{from_time}/{to_time}"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_statistics_block(self):
        from_time = "2023-10-01"
        to_time = "2023-10-02"
        block = 24
        result = self.service.get_statistics_block(from_time, to_time, block)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}intensity/stats/{from_time}/{to_time}/{block}"
        )
        self.assertEqual(result, {"data": "dummy"})

    # Generation Mix - Nationalbeta tests
    def test_get_current_generation(self):
        result = self.service.get_current_generation()
        self.mock_get.assert_called_once_with(f"{self.service.base_url}generation")
        self.assertEqual(result, {"data": "dummy"})

    def test_get_generation_pt24h(self):
        from_time = "2023-10-01T12:00Z"
        result = self.service.get_generation_pt24h(from_time)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}generation/{from_time}/pt24h"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_generation_range(self):
        from_time = "2023-10-01T12:00Z"
        to_time = "2023-10-02T12:00Z"
        result = self.service.get_generation_range(from_time, to_time)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}generation/{from_time}/{to_time}"
        )
        self.assertEqual(result, {"data": "dummy"})

    # Carbon Intensity - Regionalbeta tests
    def test_get_regional_current(self):
        result = self.service.get_regional_current()
        self.mock_get.assert_called_once_with(f"{self.service.base_url}regional")
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_england(self):
        result = self.service.get_regional_england()
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/england"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_scotland(self):
        result = self.service.get_regional_scotland()
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/scotland"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_wales(self):
        result = self.service.get_regional_wales()
        self.mock_get.assert_called_once_with(f"{self.service.base_url}regional/wales")
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_postcode(self):
        postcode = "SW1A"
        result = self.service.get_regional_postcode(postcode)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/postcode/{postcode}"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_regionid(self):
        regionid = 1
        result = self.service.get_regional_regionid(regionid)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/regionid/{regionid}"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_intensity_fw24h(self):
        from_time = "2023-10-01T12:00Z"
        result = self.service.get_regional_intensity_fw24h(from_time)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/intensity/{from_time}/fw24h"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_intensity_fw24h_postcode(self):
        from_time = "2023-10-01T12:00Z"
        postcode = "EC1A"
        result = self.service.get_regional_intensity_fw24h_postcode(from_time, postcode)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/intensity/{from_time}/fw24h/postcode/{postcode}"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_intensity_fw24h_regionid(self):
        from_time = "2023-10-01T12:00Z"
        regionid = 2
        result = self.service.get_regional_intensity_fw24h_regionid(from_time, regionid)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/intensity/{from_time}/fw24h/regionid/{regionid}"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_intensity_fw48h(self):
        from_time = "2023-10-01T12:00Z"
        result = self.service.get_regional_intensity_fw48h(from_time)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/intensity/{from_time}/fw48h"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_intensity_fw48h_postcode(self):
        from_time = "2023-10-01T12:00Z"
        postcode = "EC1A"
        result = self.service.get_regional_intensity_fw48h_postcode(from_time, postcode)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/intensity/{from_time}/fw48h/postcode/{postcode}"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_intensity_fw48h_regionid(self):
        from_time = "2023-10-01T12:00Z"
        regionid = 2
        result = self.service.get_regional_intensity_fw48h_regionid(from_time, regionid)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/intensity/{from_time}/fw48h/regionid/{regionid}"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_intensity_pt24h(self):
        from_time = "2023-10-01T12:00Z"
        result = self.service.get_regional_intensity_pt24h(from_time)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/intensity/{from_time}/pt24h"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_intensity_pt24h_postcode(self):
        from_time = "2023-10-01T12:00Z"
        postcode = "EC1A"
        result = self.service.get_regional_intensity_pt24h_postcode(from_time, postcode)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/intensity/{from_time}/pt24h/postcode/{postcode}"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_intensity_pt24h_regionid(self):
        from_time = "2023-10-01T12:00Z"
        regionid = 2
        result = self.service.get_regional_intensity_pt24h_regionid(from_time, regionid)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/intensity/{from_time}/pt24h/regionid/{regionid}"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_intensity_range(self):
        from_time = "2023-10-01T12:00Z"
        to_time = "2023-10-02T12:00Z"
        result = self.service.get_regional_intensity_range(from_time, to_time)
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/intensity/{from_time}/{to_time}"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_intensity_range_postcode(self):
        from_time = "2023-10-01T12:00Z"
        to_time = "2023-10-02T12:00Z"
        postcode = "EC1A"
        result = self.service.get_regional_intensity_range_postcode(
            from_time, to_time, postcode
        )
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/intensity/{from_time}/{to_time}/postcode/{postcode}"
        )
        self.assertEqual(result, {"data": "dummy"})

    def test_get_regional_intensity_range_regionid(self):
        from_time = "2023-10-01T12:00Z"
        to_time = "2023-10-02T12:00Z"
        regionid = 2
        result = self.service.get_regional_intensity_range_regionid(
            from_time, to_time, regionid
        )
        self.mock_get.assert_called_once_with(
            f"{self.service.base_url}regional/intensity/{from_time}/{to_time}/regionid/{regionid}"
        )
        self.assertEqual(result, {"data": "dummy"})

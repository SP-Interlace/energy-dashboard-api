# from django.test import TestCase
# from apps.core.utils.api_clients import fetch_carbon_intensity_data
# # pprint
# from pprint import pprint

# class TestCarbonIntensityAPI(TestCase):
#     def test_api_format(self):
#         data = fetch_carbon_intensity_data()
#         self.assertIsInstance(data, dict)
#         self.assertIn('data', data)
#         self.assertIsInstance(data['data'], list)
#         self.assertIsInstance(data['data'][0], dict)
#         self.assertIn('regions', data['data'][0])
#         self.assertIsInstance(data['data'][0]['regions'], list)
#         self.assertIsInstance(data['data'][0]['regions'][0], dict)

#         pprint(data)

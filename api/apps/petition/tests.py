import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import Petition

"""
THESE ARE AI WRITTEN TESTS
"""


class CreatePetitionAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("create_petition_api")

    def test_valid_post_request(self):
        """Test a valid POST request creates a new Petition and returns a success response."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "mailing_list": "true",  # Test string conversion to boolean
        }
        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

        # Verify the petition was created correctly in the database.
        petition = Petition.objects.last()
        self.assertEqual(petition.name, "John Doe")
        self.assertEqual(petition.email, "john@example.com")
        self.assertTrue(petition.mailing_list)

    def test_invalid_method(self):
        """Test that GET requests are rejected with a 400 status code."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content, {"error": "Only POST requests are allowed."}
        )

    def test_invalid_json(self):
        """Test that an invalid JSON payload returns a 400 status code."""
        response = self.client.post(
            self.url, data="This is not JSON", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        # Check that the error message mentions invalid JSON.
        error_response = response.json()
        self.assertIn("Invalid JSON payload", error_response.get("error", ""))

    def test_missing_required_fields(self):
        """Test that missing name or email returns a 400 status code with the proper error message."""
        # Example payload missing email:
        data = {"name": "John Doe"}
        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {"error": "Missing required fields: name and email are required."},
        )

    def test_mailing_list_boolean_conversion(self):
        """Test that mailing_list values provided as strings are correctly converted to booleans."""
        data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "mailing_list": "on",  # should be interpreted as True
        }
        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        petition = Petition.objects.last()
        self.assertTrue(petition.mailing_list)

        # Also test a false value
        data["mailing_list"] = "off"  # not in ["true", "1", "on"] so should be False
        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        petition = Petition.objects.last()
        self.assertFalse(petition.mailing_list)

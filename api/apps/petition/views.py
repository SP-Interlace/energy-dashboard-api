import os
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Petition


@csrf_exempt
def create_petition_api(request):
    """
    Endpoint for front end mailing list

    Used to create new entry in db, now sends to brevo
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return JsonResponse(
            {"error": "Missing required fields: name and email are required."},
            status=400,
        )

    # Split name into first and last
    name_parts = name.strip().split()
    fname = name_parts[0]
    lname = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

    # Also add to django table
    mailing_list = data.get("mailing_list", False)
    if isinstance(mailing_list, str):
        mailing_list = mailing_list.lower() in ["true", "1", "on"]

    Petition.objects.create(name=name, email=email, mailing_list=mailing_list)

    if mailing_list is False:
        return JsonResponse({"success": True}, status=200)

    brevo_payload = {
        "attributes": {"FNAME": fname, "LNAME": lname},
        "updateEnabled": False,
        "email": email,
    }

    # Brevo API key
    api_key = os.getenv("BREVO_API_KEY")
    if not api_key:
        return JsonResponse({"error": "API key not found."}, status=500)

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": api_key,
    }

    try:
        response = requests.post(
            "https://api.brevo.com/v3/contacts",
            headers=headers,
            json=brevo_payload,
            timeout=60,
        )
        if response.status_code in (200, 201):
            return JsonResponse({"success": True}, status=200)
        else:
            return JsonResponse(
                {
                    "error": "Failed to add contact to Brevo.",
                    "details": response.json(),
                },
                status=response.status_code,
            )
    except requests.RequestException as e:
        return JsonResponse(
            {"error": "Request to Brevo failed.", "details": str(e)}, status=500
        )

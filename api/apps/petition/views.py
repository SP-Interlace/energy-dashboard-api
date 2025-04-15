import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Petition


@csrf_exempt
def create_petition_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed."}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    name = data.get("name")
    email = data.get("email")
    mailing_list = data.get("mailing_list", False)

    if not name or not email:
        return JsonResponse(
            {"error": "Missing required fields: name and email are required."},
            status=400,
        )

    if isinstance(mailing_list, str):
        mailing_list = mailing_list.lower() in ["true", "1", "on"]

    Petition.objects.create(name=name, email=email, mailing_list=mailing_list)

    return JsonResponse({"success": True}, status=200)

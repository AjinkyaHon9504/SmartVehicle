from rest_framework.decorators import api_view
from rest_framework.response import Response

from firebase_admin import db


@api_view(["GET"])
def dashboard_stats(request):

    parking = db.reference("parking").get() or {}

    logs = db.reference("logs").get() or {}

    total_entries = len(logs)

    unauthorized = 0

    for key, value in logs.items():

        if value["status"] == "NOT_AUTHORIZED":
            unauthorized += 1

    return Response({

        "total_slots": parking.get("total_slots", 0),

        "occupied_slots": parking.get("occupied_slots", 0),

        "available_slots":
            parking.get("total_slots", 0)
            - parking.get("occupied_slots", 0),

        "total_entries": total_entries,

        "unauthorized_entries": unauthorized
    })
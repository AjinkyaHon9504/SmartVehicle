from rest_framework.decorators import api_view
from rest_framework.response import Response

from firebase_admin import db


@api_view(["GET"])
def recent_logs(request):

    logs = db.reference("logs").get() or {}

    logs_list = []

    for key, value in logs.items():

        logs_list.append(value)

    logs_list.reverse()

    return Response(logs_list[:20])
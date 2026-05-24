from rest_framework.decorators import api_view
from rest_framework.response import Response

from .pipeline import process_image


@api_view(["POST"])
def upload_image(request):

    image = request.FILES.get("image")

    if not image:
        return Response({
            "error": "No image uploaded"
        })

    result = process_image(image)

    return Response(result)


from rest_framework.decorators import api_view
from rest_framework.response import Response
import threading




running = False

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .vehicle_pipeline import service


@api_view(["GET"])
def start_detection(request):

    service.start()

    return Response({
        "status": "LIVE detection started"
    })


@api_view(["GET"])
def stop_detection(request):

    service.stop()

    return Response({
        "status": "Detection stopped"
    })
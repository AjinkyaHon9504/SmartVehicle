from django.urls import path

from .views import upload_image, start_detection, stop_detection
from .dashboard_views import *

urlpatterns = [

    # ---------------- API ----------------
    path("upload/", upload_image, name="upload_image"),

    # ---------------- DASHBOARD ----------------
    path("", dashboard_home, name="dashboard"),

    path("vehicles/", vehicles_page, name="vehicles"),

    path("vehicles/add/", add_vehicle, name="add_vehicle"),

    path("vehicles/delete/<str:plate>/", delete_vehicle, name="delete_vehicle"),

    path("logs/", logs_page, name="logs"),

    path("slots/", slots_page, name="slots"),

    path("vehicles/detect/start/", start_detection),
    path("vehicles/detect/stop/", stop_detection),
]
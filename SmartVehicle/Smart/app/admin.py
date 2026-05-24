from django.contrib import admin
from .models import AuthorizedPlate, ParkingConfig

admin.site.register(AuthorizedPlate)
admin.site.register(ParkingConfig)
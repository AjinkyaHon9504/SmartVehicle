from django.db import models


class AuthorizedPlate(models.Model):
    plate = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.plate


class ParkingConfig(models.Model):
    total_slots = models.IntegerField(default=50)
    occupied_slots = models.IntegerField(default=0)
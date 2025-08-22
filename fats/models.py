from django.db import models
from doctrines.models import Doctrine

# Create your models here.
class fleet(models.Model):
    name = models.CharField(max_length=200)

class Fats(models.Model):
    name = models.CharField(max_length=200)
    fleetType = models.ForeignKey(fleet, on_delete=models.DO_NOTHING, related_name="fats_fleetType")
    doctrine = models.ForeignKey(Doctrine, on_delete=models.DO_NOTHING, related_name="fats_doctrine")
    solarSystem = models.CharField(max_length=200)
    ship = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)


from django.db import models
from doctrines.models import Doctrine
from sso.models import EveCharater

# Create your models here.
class FleetType(models.Model):
    name = models.CharField(max_length=200,default="")

class Fats(models.Model):
    name = models.CharField(max_length=200, default="")
    characterFC = models.ForeignKey(EveCharater, on_delete=models.DO_NOTHING, related_name="fats_characterFC")
    character = models.ForeignKey(EveCharater, on_delete=models.DO_NOTHING, related_name="fats_character")
    fleetType = models.ForeignKey(FleetType, on_delete=models.DO_NOTHING, related_name="fats_fleetType")
    doctrine = models.ForeignKey(Doctrine, on_delete=models.DO_NOTHING, related_name="fats_doctrine")
    solarSystem = models.CharField(max_length=200)
    ship = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)

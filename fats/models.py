from django.db import models
from doctrines.models import Doctrine
from sso.models import EveCharater

class FleetType(models.Model):
    name = models.CharField(max_length=200,default="")

    def __str__(self):
        return self.name

class Fats(models.Model):
    name = models.CharField(max_length=200, default="")
    characterFC = models.ForeignKey(EveCharater, on_delete=models.DO_NOTHING, related_name="fats_characterFC")
    character = models.ForeignKey(EveCharater, on_delete=models.DO_NOTHING, related_name="fats_character")
    fleetType = models.ForeignKey(FleetType, on_delete=models.DO_NOTHING, related_name="fats_fleetType")
    doctrine = models.ForeignKey(Doctrine, on_delete=models.DO_NOTHING, related_name="fats_doctrine")
    solarSystem = models.CharField(max_length=200)
    ship = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.characterFC.name} - {self.date}"

class SRP(models.Model):
    srp_id = models.CharField(max_length=10, default="", unique=True)
    status = models.IntegerField(default=0)
    srp_cost = models.BigIntegerField(default= 0)
    fleet = models.ForeignKey(Fats, on_delete=models.DO_NOTHING, related_name="SRP_Fleet")

    def __str__(self):
        return f"SRP {self.srp_id} - Fleet: {self.fleet.name} - Status: {self.status}"
    
class SRPShips(models.Model):
    pilot = models.ForeignKey(EveCharater, on_delete=models.DO_NOTHING, related_name="SRP_Pilot")
    zkill_id =models.BigIntegerField(default=0)
    ship_id = models.BigIntegerField(default=0)
    ship_name = models.CharField(max_length=200, default="")
    srp = models.ForeignKey(SRP, on_delete=models.DO_NOTHING, related_name="SRP_Ship")
    zkill_value = models.BigIntegerField(default=0)
    srp_cost = models.BigIntegerField(default=0)
    status = models.IntegerField(default=0)

    def __str__(self):
        return f"SRP Ship {self.ship_name} - Pilot: {self.pilot.name} - Status: {self.status}"

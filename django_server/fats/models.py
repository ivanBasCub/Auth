from django.db import models
from doctrines.models import Doctrine
from sso.models import Eve_Character

class FleetType(models.Model):
    name = models.CharField(max_length=200,default="")

    def __str__(self):
        return self.name

class Fleet(models.Model):
    name = models.CharField(max_length=200, default="")
    character_FC_name = models.CharField(max_length=200, default="")
    type = models.ForeignKey(FleetType, on_delete=models.CASCADE, related_name="fats_fleetType")
    doctrine = models.ForeignKey(Doctrine, on_delete=models.CASCADE, related_name="fats_doctrine")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.character_FC_name} - {self.date}"
    
class Fat_Character(models.Model):
    fleet = models.ForeignKey(Fleet, on_delete=models.CASCADE, related_name="fleet")
    character = models.ForeignKey(Eve_Character, on_delete=models.CASCADE, related_name="player_character")
    ship = models.CharField(max_length=200)
    solar_system = models.CharField(max_length=200)

class SRP(models.Model):
    srp_id = models.CharField(max_length=10, default="", unique=True)
    status = models.IntegerField(default=0)
    srp_cost = models.BigIntegerField(default= 0)
    fleet = models.ForeignKey(Fleet, on_delete=models.CASCADE, related_name="SRP_Fleet")

    def __str__(self):
        return f"SRP {self.srp_id} - Fleet: {self.fleet.name} - Status: {self.status}"
    
class SRP_Ship(models.Model):
    character = models.ForeignKey(Eve_Character, on_delete=models.CASCADE, related_name="SRP_Pilot")
    zkill_id =models.BigIntegerField(default=0)
    ship_id = models.BigIntegerField(default=0)
    ship_name = models.CharField(max_length=200, default="")
    srp = models.ForeignKey(SRP, on_delete=models.CASCADE, related_name="SRP_Ship")
    zkill_value = models.BigIntegerField(default=0)
    srp_cost = models.BigIntegerField(default=0)
    status = models.IntegerField(default=0)

    def __str__(self):
        return f"SRP Ship {self.ship_name} - Pilot: {self.character.name} - Status: {self.status}"
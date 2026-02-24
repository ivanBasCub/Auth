from django.db import models
from sso.models import Eve_Character

# Create your models here.
class Skillplan(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(default="")
    skills = models.JSONField(default=dict)

class Skillplan_CheckList(models.Model):
    skillPlan = models.ManyToManyField(Skillplan, related_name="skillplan_name")
    character = models.ManyToManyField(Eve_Character, related_name="character_skillplan")
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.skillPlan.all().first().name} for {self.character.all().first().character_name} - Status: {self.status}"

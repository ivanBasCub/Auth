from django.db import models
from sso.models import EveCharater

# Create your models here.
class Skillplan(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(default="")
    skills = models.JSONField(default=dict)

class Skillplan_CheckList(models.Model):
    Skillplan = models.ManyToManyField(Skillplan, related_name="skillplan_name")
    character = models.ManyToManyField(EveCharater, related_name="character_skillplan")
    status = models.BooleanField(default=False)

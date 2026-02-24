from django.db import models
from django.contrib.auth.models import User

class Eve_Character(models.Model):
    character_id = models.BigIntegerField(default=0)
    character_name = models.CharField(max_length=150)
    access_token = models.TextField(default="")
    refresh_token = models.CharField(max_length=100)
    expiration = models.TimeField(null=True, blank=True)
    corp_id = models.BigIntegerField(default=0)
    corp_name = models.CharField(max_length=150,default="")
    alliance_id = models.BigIntegerField(default=0)
    alliance_name = models.CharField(max_length=150,default="")
    money = models.BigIntegerField(default=0)
    skill_points = models.BigIntegerField(default=0)
    skills = models.JSONField(default=dict)
    main = models.BooleanField(default=False)
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING, related_name="evepj")
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.character_name} - {self.user}"
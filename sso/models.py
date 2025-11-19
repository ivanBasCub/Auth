from django.db import models
from django.contrib.auth.models import User

class EveCharater(models.Model):
    characterId = models.BigIntegerField(default=0)
    characterName = models.CharField(max_length=150)
    accessToken = models.TextField(default="")
    refreshToken = models.CharField(max_length=100)
    expiration = models.TimeField(null=True, blank=True)
    corpId = models.BigIntegerField(default=0)
    corpName = models.CharField(max_length=150,default="")
    allianceId = models.BigIntegerField(default=0)
    allianceName = models.CharField(max_length=150,default="")
    walletMoney = models.BigIntegerField(default=0)
    totalSkillPoints = models.BigIntegerField(default=0)
    skills = models.JSONField(default=dict)
    main = models.BooleanField(default=False)
    user_character = models.ForeignKey(User,on_delete=models.DO_NOTHING, related_name="evepj")

    def __str__(self):
        return f"{self.characterName} - {self.user_character}"
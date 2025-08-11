from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class EveCharater(models.Model):
    characterId = models.BigIntegerField(default=0)
    characterName = models.CharField(max_length=150)
    accessToken = models.TextField(default="")
    refreshToken = models.CharField(max_length=100)
    expiration = models.TimeField(null=True, blank=True)
    main = models.BooleanField(default=False)
    user_character = models.ForeignKey(User,on_delete=models.DO_NOTHING, related_name="evepj")

    def __str__(self):
        return f"{self.characterName} - {self.user_character}"
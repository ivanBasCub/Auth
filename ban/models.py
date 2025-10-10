from django.db import models
from django.contrib.auth.models import User
from sso.models import EveCharater
from django.utils import timezone

class BanCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class BannedCharacter(models.Model):
    character_id = models.BigIntegerField(default=0, unique=True)
    character_name = models.CharField(max_length=255, default="")
    ban_category = models.ForeignKey(BanCategory, on_delete=models.SET_NULL, null=True, blank=True)
    banned_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="banned_by")
    reason = models.TextField()
    ban_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.character_name} (ID: {self.character_id}) - Banned by {self.banned_by}"
    
class SuspiciousNotification(models.Model):
    character = models.ForeignKey(EveCharater, on_delete=models.SET_NULL, null=True, blank=True)
    target = models.TextField(default="")
    date = models.DateField(default=timezone.now)
    amount = models.BigIntegerField(default=0)
    
    def __str__(self):
        return f"{self.character.characterName} - {self.target} - amount: {self.amount}"

    
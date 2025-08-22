from django.db import models
from django.contrib.auth.models import User

# Create your models here.
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
    

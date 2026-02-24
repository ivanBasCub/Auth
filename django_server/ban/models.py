from django.db import models
from django.contrib.auth.models import User
from sso.models import Eve_Character

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Character(models.Model):
    character = models.ForeignKey(Eve_Character, on_delete=models.CASCADE, related_name="ban")
    ban_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    banned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="banned_by")
    reason = models.TextField()
    ban_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.character.characterId} (ID: {self.character.characterName}) - Banned by {self.banned_by}"
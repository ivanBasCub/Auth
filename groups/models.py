from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.
class GroupNotifications(models.Model):
    group = models.ManyToManyField(Group, related_name = "SolitudGrupo")
    user = models.ManyToManyField(User, related_name="userNotification")
    status = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)

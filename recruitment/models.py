from django.db import models
from django.contrib.auth.models import User

class Applications_access(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date = models.DateField(auto_now_add=True)
    totalSP = models.BigIntegerField(default=0)
    cynoCovert = models.BooleanField(default=False)
    msg = models.TextField(default="")
    application_type = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.date}"
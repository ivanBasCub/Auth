from django.db import models

class Categories(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Doctrine(models.Model):
    title = models.CharField(max_length=200)
    desc = models.TextField(default="")
    doCategory = models.ForeignKey(Categories, on_delete=models.DO_NOTHING, related_name="DoctrineCategory")

    def __str__(self):
        return self.title

class FitShip(models.Model):
    fitId = models.BigIntegerField(default=0)
    shipId = models.BigIntegerField(default=0)
    nameFit = models.CharField(max_length=200)
    desc = models.TextField(default="")
    items = models.JSONField(default=dict)
    fitCategory = models.ForeignKey(Categories, on_delete=models.DO_NOTHING, related_name="fitCategory")
    fitDoctrine = models.ForeignKey(Doctrine, on_delete=models.DO_NOTHING, related_name="fitDoctrine")
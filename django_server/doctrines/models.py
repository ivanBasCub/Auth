from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200)
    type = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Doctrine(models.Model):
    title = models.CharField(max_length=200)
    desc = models.TextField(default="")
    category = models.ManyToManyField(
        'Category',
        related_name="DoctrineCategory"
    )

    def __str__(self):
        return self.title

class Fit(models.Model):
    fit_id = models.BigIntegerField(default=0)
    ship_id = models.BigIntegerField(default=0)
    ship_name = models.CharField(max_length=100, default="")
    name_fit = models.CharField(max_length=200)
    desc = models.TextField(default="")
    items = models.JSONField(default=dict)
    min_skills = models.JSONField(default=dict)
    category = models.ManyToManyField('Category', related_name="fitCategory")
    doctrine = models.ManyToManyField('Doctrine', related_name="fitDoctrine")

    def __str__(self):
        return self.nameFit
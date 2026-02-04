from django.db import models
from sso.models import EveCharater

class Item(models.Model):
    eve_id = models.PositiveBigIntegerField(default=0)
    name = models.CharField(max_length=254)
    
    def __str__(self):
        return self.name
    
class Location(models.Model):
    eve_id = models.PositiveBigIntegerField(default=0)
    name = models.TextField(default="")
    
    def __str__(self):
        return self.name
    
class Asset(models.Model):
    character = models.ForeignKey(EveCharater, on_delete=models.CASCADE, related_name="assets")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="assets")
    quantity = models.PositiveBigIntegerField(default=1)
    loc_flag = models.CharField(max_length=254)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="assets")
    
    def __str__(self):
        return f"{self.character.characterName} - {self.quantity} - {self.item.name} - {self.location}"
    
# Member Transactions
class Transaction(models.Model):
    character = models.ForeignKey(EveCharater, on_delete=models.CASCADE, related_name="transsactions")
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    balance = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.TextField(default="")
    context = models.CharField(max_length=254)
    ref = models.CharField(max_length=254)
    target = models.CharField(max_length=254)
    date = models.DateField(blank=True, null=True)
    
    def __str__(self): 
        return f"{self.character} - {self.amount}"

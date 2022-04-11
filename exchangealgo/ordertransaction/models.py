from django.db import models
from django.contrib.auth.models import User
from djongo.models.fields import ObjectIdField
from accounts.models import Profile



class Order(models.Model):
    CHOICES = (("BUY", "BUY"), ("SELL", "SELL"))

    _id = ObjectIdField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    position = models.CharField(max_length=8, choices=CHOICES, default="BUY")
    status = models.Field(default="open")
    price = models.FloatField()
    quantity_max_insert = models.FloatField()
    datetime = models.DateTimeField(auto_now_add=True)
    order_number = models.IntegerField()



class Transaction(models.Model):

    _id = ObjectIdField()
    call = models.ForeignKey(User, related_name="call", on_delete=models.CASCADE)
    put = models.ForeignKey(User, related_name="put", on_delete=models.CASCADE)
    quantity = models.FloatField()
    price = models.FloatField()
    datetime = models.DateTimeField(auto_now_add=True)

class OrderManager(models.Model):

    last_order_number = models.IntegerField(default=0)

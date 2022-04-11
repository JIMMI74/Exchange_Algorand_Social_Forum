from django.db import models
from django.contrib.auth.models import User
from djongo.models.fields import ObjectIdField
from .coinmarketcap import algoValue
import random


class Profile(models.Model):
    _id = ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.CASCADE,  related_name='profile')
    ips = models.Field(default=[])
    subprofiles = models.Field(default={})
    n = random.randint(1, 10)
    ALGO_Wallet = models.FloatField(default=n)
    USD_wallet = models.FloatField(default=1000)
    profit = models.FloatField(default=0)
    ALGO_Pending_Wallet = models.FloatField(default=0)
    USD_Pending_Wallet = models.FloatField(default=0)

    class Meta:
        ordering = ['profile']

    def __str__(self):
        return "profile for user {}".format(self.user.username)

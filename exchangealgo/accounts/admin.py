from django.contrib import admin
from accounts.models import Profile
from coinmarketalgo.models import Purchase
from ordertransaction.models import Order, Transaction

admin.site.register([Profile, Purchase, Order, Transaction])

from accounts.coinmarketcap import algoValue
from django import forms
from .models import Purchase



class PurchaseForm(forms.ModelForm):
    price = algoValue()

    class Meta:
        model = Purchase
        fields = ['max_spend_usd']

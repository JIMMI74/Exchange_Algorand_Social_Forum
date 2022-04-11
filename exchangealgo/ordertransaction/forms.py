from django import forms
from .models import Order
from accounts.coinmarketcap import algoValue



class OrderForm(forms.ModelForm):
    price = algoValue()

    class Meta:
        model = Order
        fields = ['position', 'quantity_max_insert', 'price']
        labels = {'position': 'BUY/SELL', 'quantity_max_insert': 'n_coin_ALGO'}
        widgets = {
            "quantity": forms.TextInput(attrs={"placeholder": "insert the quantity"}),
            "price": forms.TextInput(attrs={"placeholder": "insert your price"})
        }

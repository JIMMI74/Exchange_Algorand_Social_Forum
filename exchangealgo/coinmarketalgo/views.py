from django.shortcuts import render, redirect
from accounts.coinmarketcap import algoValue
from .forms import PurchaseForm
from django.contrib import messages
from accounts.models import Profile
from django.http import HttpResponseBadRequest
from .models import PrincipalHome





def buyalgomkt(request):
    new_price = algoValue()
    if request.method == "POST":
        form = PurchaseForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.instance.profile = Profile.objects.get(user=request.user)
            form.instance.purchased_price = new_price
            if (
                form.instance.profile.USD_wallet > 0
                and form.instance.max_spend_usd < form.instance.profile.USD_wallet
            ):
                form.instance.purchased_coin = form.instance.max_spend_usd / new_price
                buyer = Profile.objects.get(user=request.user)
                buyer.ALGO_Wallet += form.instance.purchased_coin
                buyer.USD_wallet -= form.instance.max_spend_usd

                form.save()
                buyer.save()
                messages.success(request, "Your purchase has been placed and processed")
            else:
                messages.warning(request, "You do not have enough money")
            return redirect("purchase")

        else:
            return HttpResponseBadRequest()

    else:
        form = PurchaseForm()

    return render(
        request, "coinmarketalgo/purchase.html", {"form": form, "new_price": new_price}
    )



def HomePrincipalView(request):
    obj = PrincipalHome.objects.all()
    context = {'obj': obj}
    return render(request, 'coinmarketalgo/homepage.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from .forms import OrderForm
from accounts.models import Profile
from accounts.coinmarketcap import algoValue
from .models import Order, Transaction
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import OrderManager
from django.views.generic import ListView


@login_required
def placeOrders(request):
    price_traded_on_exchange = algoValue()
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            ordermanager = OrderManager.objects.all()[0]   # incremented each order by 1 that will be initially inserted by the admin
            order_number = ordermanager.last_order_number
            order_number += 1
            form.instance.order_number = order_number
            ordermanager.last_order_number = order_number
            ordermanager.save()
            form.save(commit=False)
            form.instance.profile = Profile.objects.get(user=request.user)
            decision = form.instance.position
            #  retrieving the list of the user's open orders
            open_orders = Order.objects.filter(status='open', profile=form.instance.profile)
            print('open_orders:', open_orders)
            # only order BUY
            open_status_buyer = open_orders.filter(position='BUY')
            # only order SELL
            print('open_status_buyer', open_status_buyer)
            open_status_sellers = open_orders.filter(position='SELL')

            # interrupt if it is a BUY order but there is already an open in SELL
            if decision == 'BUY' and open_status_sellers.count() > 0:
                messages.warning(request,
                                 "Attention, order cannot be processed, you already have an open order pending in SELL!")
                return redirect('/buy_sell_dex/')
                                                        # otherwise I proceed with the verification of other open orders in the same position
            elif open_status_buyer.count() > 0:
                lower_price = None
                for order in open_status_buyer:
                    price = order.price
                    if lower_price == None:
                        lower_price = price
                    elif price < lower_price:
                        lower_price = price
                                                            # if the amount is lower than other open buys, it stop
                if form.instance.price < lower_price:
                    messages.warning(request,
                                     "Attention, order cannot be processed, you placed an order at a higher price!")
                    return redirect('/buy_sell_dex/')
                # same logic in reverse

            if decision == 'SELL' and open_status_buyer.count() > 0:
                messages.warning(request,
                                 "Attention, order cannot be processed, you already have an open order pending in BUY!")
                return redirect('/buy_sell_dex/')
                                                            # altrimenti procedo con la verifica di altri ordini open nella stessa posizione
            elif open_status_sellers.count() > 0:
                high_price = None
                for order in open_status_sellers:
                    price = order.price
                    if high_price == None:
                        high_price = price
                    elif price > high_price:
                        high_price = price
                if form.instance.price > high_price:
                    messages.warning(request,
                                     "Attention, order cannot be processed, you already have an open order pending!")
                    return redirect('/buy_sell_dex/')
                                                                    # condition buy/sell of user

            if form.instance.price < 0 or form.instance.quantity_max_insert < 0:
                messages.warning(request, 'Add money !')
                return redirect('/buy_sell_dex/')
            if decision == 'BUY':
                if (form.instance.price * form.instance.quantity_max_insert) > form.instance.profile.USD_wallet:
                    messages.warning(request, 'you do not have enough funds to complete the operation!')
                    return redirect('/buy_sell_dex/')
                else:
                    form.instance.profile.USD_wallet -= form.instance.price * form.instance.quantity_max_insert
                    form.instance.profile.USD_Pending_Wallet += form.instance.price * form.instance.quantity_max_insert
                    print('BUY', 'USD_wallet:', form.instance.profile.USD_wallet, 'USD_Pending_Wallet:',
                          form.instance.profile.USD_Pending_Wallet)
            if decision == 'SELL':
                if form.instance.quantity_max_insert > form.instance.profile.ALGO_Wallet:
                    messages.warning(request, 'You cannot sell more Coin than you have!')
                    return redirect('/buy_sell_dex/')
                else:
                    form.instance.profile.ALGO_Wallet -= form.instance.quantity_max_insert
                    form.instance.profile.ALGO_Pending_Wallet += form.instance.quantity_max_insert
                    print('SELL')
            form.instance.profile.save()
            orders = form.save()
            messages.success(request,
                             'Your Order has been created successfully...'
                             'go to the Public buy/sell and check its status !')
            print(str(orders.profile) + "+" + str(orders.quantity_max_insert))
            open_buyers = Order.objects.filter(position='BUY', status='open').exclude(profile=orders.profile).\
                order_by('-price')

            open_sellers = Order.objects.filter(position='SELL', status='open').exclude(profile=orders.profile).\
                order_by('price')

            if orders.position == 'BUY' and open_sellers.count() > 0:
                for sell in open_sellers:
                    if sell.price <= orders.price:
                        put_trader = sell.profile
                        call_trader = orders.profile

                        if sell.quantity_max_insert <= orders.quantity_max_insert:
                            call_trader.USD_Pending_Wallet -= (sell.price * sell.quantity_max_insert)
                            call_trader.ALGO_Wallet += sell.quantity_max_insert
                            put_trader.USD_wallet += (sell.price * sell.quantity_max_insert)
                            put_trader.ALGO_Pending_Wallet -= sell.quantity_max_insert
                            print('BUY: if', put_trader.ALGO_Pending_Wallet)
                            orders.quantity_max_insert -= sell.quantity_max_insert
                            if orders.quantity_max_insert == 0.0:
                                orders.status = 'closed'
                            Transaction.objects.create(call=call_trader.user, put=put_trader.user,
                                                       price=sell.price, quantity=sell.quantity_max_insert)
                            put_trader.profit += (sell.price * sell.quantity_max_insert)
                            call_trader.profit -= (sell.price * sell.quantity_max_insert)

                            sell.status = 'closed'
                            sell.quantity_max_insert = 0.0

                        else:

                            call_trader.USD_Pending_Wallet -= (sell.price * orders.quantity_max_insert)
                            call_trader.ALGO_Wallet += orders.quantity_max_insert
                            put_trader.USD_wallet += (sell.price * orders.quantity_max_insert)
                            put_trader.ALGO_Pending_Wallet -= orders.quantity_max_insert
                            print('BUY: else', put_trader.ALGO_Pending_Wallet)

                            sell.quantity_max_insert -= orders.quantity_max_insert

                            Transaction.objects.create(call=orders.profile.user, put=put_trader.user,
                                                       quantity=orders.quantity_max_insert, price=sell.price)

                            call_trader.profit -= (sell.price * orders.quantity_max_insert)
                            put_trader.profit += (sell.price * orders.quantity_max_insert)

                            orders.status = 'closed'
                            orders.quantity_max_insert = 0.0

                        put_trader.save()
                        call_trader.save()
                        orders.save()
                        sell.save()
                        form.instance.profile.save()

            if orders.position == 'SELL' and open_buyers.count() > 0:  # position Sell
                for buy in open_buyers:
                    if buy.price >= orders.price:
                        call_trader = buy.profile
                        put_trader = orders.profile

                        if buy.quantity_max_insert <= orders.quantity_max_insert:
                            call_trader.USD_Pending_Wallet -= (buy.price * buy.quantity_max_insert)
                            call_trader.ALGO_Wallet += buy.quantity_max_insert
                            put_trader.USD_wallet += (buy.price * buy.quantity_max_insert)
                            put_trader.ALGO_Pending_Wallet -= buy.quantity_max_insert
                            print('PUT: IF', put_trader.ALGO_Pending_Wallet)
                            orders.quantity_max_insert -= buy.quantity_max_insert
                            if orders.quantity_max_insert == 0.0:
                                orders.status = 'closed'


                            Transaction.objects.create(call=call_trader.user, put=put_trader.user,
                                                       quantity=buy.quantity_max_insert, price=buy.price)
                            call_trader.profit -= (buy.price * buy.quantity_max_insert)
                            put_trader.profit += (buy.price * buy.quantity_max_insert)
                            buy.status = 'closed'
                            buy.quantity_max_insert = 0.0
                        else:
                            call_trader.USD_Pending_Wallet -= (buy.price * orders.quantity_max_insert)
                            call_trader.ALGO_Wallet += orders.quantity_max_insert
                            put_trader.USD_wallet += (buy.price * orders.quantity_max_insert)
                            put_trader.ALGO_Pending_Wallet -= orders.quantity_max_insert
                            print('PUT: else', put_trader.ALGO_Pending_Wallet)
                            buy.quantity_max_insert -= orders.quantity_max_insert

                            Transaction.objects.create(call=call_trader.user, put=put_trader.user,
                                                       quantity=orders.quantity_max_insert, price=buy.price)

                            call_trader.profit -= (orders.price * orders.quantity_max_insert)
                            put_trader.profit += (orders.price * orders.quantity_max_insert)


                            orders.status = 'closed'
                            orders.quantity_max_insert = 0.0

                        put_trader.save()
                        call_trader.save()
                        buy.save()
                        orders.save()
                        form.instance.profile.save()
                        messages.success(request, 'great, your transaction was successful!')

            return redirect("match_orders")
    else:
        form = OrderForm()

    return render(request, "ordertransaction/match_orders.html", {'form': form,
                                                                  'price_traded_on_exchange': price_traded_on_exchange})


@login_required
def activeOrders(request):
    response = []
    ord_active = Order.objects.filter(status='open')
    for data in ord_active:
        response.append(
            {
                'price': data.price,
                'position': data.position,
                "quantity_max_insert": data.quantity_max_insert,
                "datetime": data.datetime,
            }
        )
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    user_current = Profile.objects.filter(user=request.user)[0]
    user_current.ips.append(ip)
    user_current.save(update_fields=['ips'])

    return JsonResponse(response, safe=False)



def gain_loss(request):
    response = []
    profiles = Profile.objects.all()
    for profile in profiles:
        response.append(
            {
                "user": profile.user.username,
                "ALGO_Wallet": profile.ALGO_Wallet,
                "USD_wallet": profile.USD_wallet,
                "profit/losses": profile.profit,
            }
        )
    return JsonResponse(response, safe=False)

@login_required
def order_status_book_view(request):  # with view
    orders = Order.objects.all().order_by('-datetime')
    order_paginator = Paginator(orders, 10)
    page_num = request.GET.get("page")
    page = order_paginator.get_page(page_num)
    context = {'orders': orders, 'count': order_paginator.count, 'page': page}
    return render(request, 'ordertransaction/match_status.html', context)


def transaction_user(request):  # with json
    response = []
    operations = Transaction.objects.filter(Q(call=request.user) | Q(put=request.user))
    for transdone in operations:
        response.append(
            {

                "quantity": transdone.quantity,
                "price": transdone.price,
                "datetime": transdone.datetime,
                "buyer": transdone.call.username,
                "seller": transdone.put.username,
            }
        )

    return JsonResponse(response, safe=False)



class ListOrder(ListView):
    model = Order
    template_name = 'ordertransaction/status.html'
    ordering = ['datetime']




def deleteOrder(request, n):
    order = get_object_or_404(Order, order_number=n)
    if request.method == "POST":

        if order.position == 'BUY':
            print(order.quantity_max_insert)
            quantity_usd_pending = order.quantity_max_insert * order.price
            order.profile.USD_wallet += quantity_usd_pending
            order.profile.USD_Pending_Wallet -= quantity_usd_pending
        else:
            quantity_coin_pending = order.quantity_max_insert
            order.profile.ALGO_Wallet += quantity_coin_pending
            order.profile.ALGO_Pending_Wallet -= quantity_coin_pending
        order.profile.save()
        order.delete()
        messages.success(request, "Your order has been deleted successfully!")

        return redirect("status")
    return render(request, 'ordertransaction/order_confirm_delete.html')










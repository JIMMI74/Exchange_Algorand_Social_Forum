from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import RegistrationForm, UserEditForm
from .models import Profile
from .coinmarketcap import algoValue, algo_perc24h, algo_vol24h, algo_marketCap
from django.contrib import messages
from coinmarketalgo.models import Purchase
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from forum.models import Discussion, Post, HomepageSection
from django.db.models import Q
from ordertransaction.models import Transaction, Order


def registration_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]
            User.objects.create_user(username=username, password=password, email=email)
            user = authenticate(username=username, password=password)
            Profile.objects.create(user=user)
            profile = Profile.objects.get(user=user)
            login(request, user)
            messages.success(request,
                             f'Your Account has been created successfully, you have received {profile.ALGO_Wallet} '
                             f'ALGO '
                             f'and {profile.USD_wallet}$  for registering. See in your wallet!')
            return redirect("social_page")
    else:
        form = RegistrationForm()
    context = {"form": form}
    return render(request, "accounts/registration.html", context)


def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    algowallet = profile.ALGO_Wallet
    pending_ALGO = profile.ALGO_Pending_Wallet
    pending_USD = profile.USD_Pending_Wallet
    print(profile.USD_Pending_Wallet)
    price = algoValue()
    market_cap = algo_marketCap()
    vol24h = algo_perc24h()
    percent_24h = algo_vol24h()
    orders = Order.objects.filter(profile=profile).order_by('datetime')
    orders_transactions = Transaction.objects.filter(Q(call=request.user) | Q(put=request.user)).order_by('-datetime')
    purchase = Purchase.objects.filter(profile=profile)
    algo_usd = round(profile.ALGO_Wallet * algoValue(), 3)
    remaining_balance = round(profile.USD_wallet, 6)
    profit = round(profile.profit)
    context = {'user': user, 'algo_usd': algo_usd, 'remaining_balance': remaining_balance, 'purchase': purchase,
               'profit': profit, 'price': price, 'market_cap': market_cap, 'vol24h': vol24h, 'percent_24h': percent_24h,
               'orders_transactions': orders_transactions, 'orders': orders,
               'algowallet': algowallet, 'pending_USD':  pending_USD, 'pending_ALGO': pending_ALGO}
    return render(request, 'accounts/user_profile.html', context)


def edit_profile(request):
    if request.method == 'POST':
        userform = UserEditForm(data=request.POST, instance=request.user)
        if userform.is_valid():
            userform.save()
            messages.success(request, ('You just edited your profile'))
            return redirect('/')
        else:
            messages.error(request, 'Check your data')
    else:
        print(request.user)
        print(request.user.profile)
        userform = UserEditForm(instance=request.user)

    context = {'userform': userform}
    return render(request, 'accounts/edit_profile.html', context)


class UserListViewCBV(ListView):
    model = Profile
    template_name = "accounts/list_user.html"



class SocialPage(ListView):
    queryset = HomepageSection.objects.all()
    template_name = 'accounts/social_page.html'
    context_object_name = "list_section"


class UserList(LoginRequiredMixin, ListView):
    model = User
    template_name = 'accounts/users.html'


def user_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    discussion_user = Discussion.objects.filter(author_discussion=user).order_by("-pk")
    context = {"user": user, "discussion_user": discussion_user}
    return render(request, 'accounts/user_profile_social.html', context)

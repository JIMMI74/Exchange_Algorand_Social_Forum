"""exchangealgo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from coinmarketalgo.views import buyalgomkt, HomePrincipalView
from ordertransaction.views import placeOrders, activeOrders, gain_loss, order_status_book_view,\
    transaction_user, ListOrder, deleteOrder
from django.conf.urls.static import static
from django.conf import settings




urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('buycoin/', buyalgomkt, name='purchase'),
    path('buy_sell_dex/', placeOrders, name='match_orders'),
    path('activeOrders/', activeOrders, name='activeOrders'),
    path('gain_loss/', gain_loss, name='gain_loss'),
    path('orderbook/', order_status_book_view, name='orderbook'),
    path('trasaction_jeson/', transaction_user, name='trasaction_jeson'),
    path('forum/', include('forum.urls')),
    path('', HomePrincipalView, name='homepage'),
    path('status/', ListOrder.as_view(), name='status'),
    path('status/<int:n>/remove', deleteOrder, name="delete_orders")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

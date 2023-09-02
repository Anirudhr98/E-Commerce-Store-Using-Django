
from django.contrib import admin
from django.urls import path
from .views import login_view,logout_view,signup_view,store_view,add_to_cart_view,cart_view,remove_item_from_cart,remove_all_items_from_cart,create_checkout_session,orders,stripe_webhook,order_message,seed_data,product
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',store_view,name = "store"),
    path('login/',login_view,name = "login"),
    path('logout/',logout_view,name = "logout"),
    path('signup/',signup_view,name = "signup"),
    path('addtocart/',add_to_cart_view,name="add_to_cart"),
    path('cart/',cart_view),
    path('cart/remove/<product_id>/', remove_item_from_cart),
    path('cart/removeallitemsfromcart/',remove_all_items_from_cart),
    path('product/<int:product_id>',product),
    path('create_checkout_session/',create_checkout_session),
    path('orders/',orders),
    path('stripe_webhook/',stripe_webhook),
    path('order_message/',order_message),
    path('seed_data',seed_data),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
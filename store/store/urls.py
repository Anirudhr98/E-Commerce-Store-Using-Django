
from django.contrib import admin
from django.urls import path
from .views import login_view,logout_view,signup_view,store_view,add_to_cart_view,cart_view,remove_item_from_cart,remove_all_items_from_cart,final_cart_update,create_order,create_checkout_session,orders,stripe_webhook,order_message
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
    path('cart/finalcartupdate/',final_cart_update),
    path('create_order/',create_order),
    path('create_checkout_session/',create_checkout_session),
    path('orders/',orders),
    path('stripe_webhook/',stripe_webhook),
    path('order_message/',order_message),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
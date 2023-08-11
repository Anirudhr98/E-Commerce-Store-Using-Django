
from django.contrib import admin
from django.urls import path
from .views import login_view,logout_view,signup_view,store_view,add_to_cart_view,cart_view,remove_item_from_cart,remove_all_items_from_cart
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
    path('cart/remove/<int:product_id>/', remove_item_from_cart),
    path('cart/removeallitemsfromcart',remove_all_items_from_cart),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
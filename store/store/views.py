from django.shortcuts import redirect,render,HttpResponse
from .models import User,Product,Cart
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from django.core.paginator import Paginator
import json


def store_view(request):
    # Logging in user
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            cart_items = get_cart(request)
            messages.success(request,"You have been logged in!")
            return redirect("/")
        else:
            messages.info(request,"Please enter valid credentials!")  
            return redirect("/login/")

# Pulling items from database
    items = Product.objects.all()
    items_per_page = 6
    paginator = Paginator(items,items_per_page)
    current_page_number = request.GET.get('page')
    current_page_items = paginator.get_page(current_page_number)

    cart_items = get_cart(request)
    return render(request, 'store.html', {'current_page_items': current_page_items,"cart_items": cart_items})

    
def login_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        address = request.POST.get("address")
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if password!=confirm_password:
            messages.info(request,"Passwords do not match!")
            return redirect("/signup/",)
        try:
            hashed_password = make_password(password)
            user = User(name = name,email=email,username=username,address=address,phone_number=phone_number,password=hashed_password)
            user.save()
            messages.success(request,"You have been successfully signed up!")
            return redirect('/login/')
        except IntegrityError:
            messages.info(request,"Username or Email already exists! Please choose another one.")
            return redirect('/signup/')

    return render(request,"login.html")

def logout_view(request):
    logout(request)
    request.session.pop("cartItems","None")
    messages.success(request,"You have been logged out!")
    return redirect("/")

def signup_view(request):
    return render(request,"signup.html")

def add_to_cart_view(request):
    if request.method == "POST":
        new_cart_items = json.loads(request.POST.get('cartItems'))
        userId = request.POST.get('userId')
        user = User.objects.get(pk = userId)
        print("Cart Items are ",new_cart_items)
        for item in new_cart_items:
            cart_item = Cart(user=user,product_id = item["productId"],product_name = item["productName"],product_price = item["productPrice"])
            cart_item.save()
        return redirect("/")   

def cart_view(request):
    cart_items = Cart.objects.filter(user_id=request.user.id)
    cart_numbers = [i for i in range(1,11)]
    context = {
        'cart_items': cart_items,
        'cart_numbers': cart_numbers
    }
    return render(request, "cart.html", context)

def get_cart(request):
    user = request.user
    cart_items = Cart.objects.filter(user_id = user.id)
    return cart_items

def remove_item_from_cart(request,product_id):
    if request.method == "POST":
        user = request.user
        print("Product Id is ",product_id)
        try:
            Cart.objects.filter(user_id = user.id,product_id = product_id).delete()
            return redirect('/cart/')
        
        except Cart.DoesNotExist:
            return redirect('/cart/')
 
def remove_all_items_from_cart(request):
    user = request.user
    Cart.objects.filter(user_id=user.id).delete()
    messages.info(request, "Your cart is now empty!")
    return HttpResponse("")

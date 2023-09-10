from django.shortcuts import redirect,render,HttpResponse
from django.http import JsonResponse
from .models import Product,Cart,Order,CustomUser
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.paginator import Paginator
import threading
import requests
from decouple import config
import json
import stripe




def store_view(request):
    # Logging in user
    if request.method == "POST":
        if not request.user.is_authenticated:
            email = request.POST.get("email")
            password = request.POST.get("password")
            user = authenticate(request,email=email,password=password)
            if user is not None:
                login(request,user)
                cart_items = get_cart(request)
                messages.success(request,"You have been logged in!")
                return redirect("/")
            else:
                messages.info(request,"Please enter valid credentials!")  
                return redirect("/login/")
        else:
            messages.info(request,"Please logout and then re-login!")     
            return redirect("/")   

    unique_categories = Product.objects.values('category').distinct()
    unique_categories = [item["category"] for item in unique_categories]

    # Initialize with all products
    items = Product.objects.all()

    # Retrieve the filter and sort parameters from the GET request
    category = request.GET.get('category')
    sort_by = request.GET.get('sort_by')

    # Apply filtering based on the category parameter
    if (category and category!="None"):
        items = items.filter(category=category)

    # Apply sorting based on the sort_by parameter
    if (sort_by and sort_by!="None"):
        items = items.order_by(sort_by)

    # Pagination
    items_per_page = 6
    paginator = Paginator(items, items_per_page)
    current_page_number = request.GET.get('page')
    current_page_items = paginator.get_page(current_page_number)


    items_to_add_to_cookie = []
    if request.user.is_authenticated:
        cart_items = get_cart(request)
        if cart_items:
            cookie = json.loads(request.COOKIES.get('cartItems', '[]'))
            for item in cart_items:
                item.product_price = str(item.product_price)
                if not any(int(existing_item['productId']) == item.product_id for existing_item in cookie):
                    items_to_add_to_cookie.append({'productId': item.product_id, 'productName': item.product_name, 'productPrice': item.product_price})
    return render(request, 'store.html', {'current_page_items': current_page_items,"items_to_add_to_cookie":json.dumps(items_to_add_to_cookie),"unique_categories":unique_categories,"category":category,"sort_by":sort_by})

    
def login_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        address = request.POST.get("address")
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if password!=confirm_password:
            messages.info(request,"Passwords do not match!")
            return redirect("/signup/",)
        try:
            user = CustomUser(name = name, email = email, address = address,phone_number=phone_number)
            user.set_password(password)
            user.save()
            messages.success(request,"You have been successfully signed up!")
            return redirect('/login/')
        except IntegrityError:
            messages.info(request,"Username or Email already exists! Please choose another one.")
            return redirect('/signup/')

    return render(request,"login.html")

@login_required
def logout_view(request):
    response = redirect("/")
    response.set_cookie("cartItems", "", expires="Thu, 01 Jan 1970 00:00:00 GMT")
    messages.success(request, "You have been logged out!")
    logout(request)  
    return response

def signup_view(request):
    return render(request,"signup.html")

@login_required
def add_to_cart_view(request):
    if request.method == "POST":
        new_cart_items = json.loads(request.POST.get('cartItems'))
        userId = request.POST.get('userId')
        user = CustomUser.objects.get(pk=userId)
        existing_cart_items = Cart.objects.filter(user=user)
        for item in new_cart_items:
            if not any(str(existing_item.product_id) == item["productId"] for existing_item in existing_cart_items):
                cart_item = Cart(user=user, product_id=item["productId"], product_name=item["productName"], product_price=item["productPrice"])
                cart_item.save()
        return redirect('/')

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user_id=request.user.id)
    cart_numbers = [i for i in range(1,11)]
    user_address = cart_items[0].user.address if cart_items and cart_items[0].user.address else None
    user_phone_number = cart_items[0].user.phone_number if cart_items and cart_items[0].user.phone_number else None
    context = {
        'cart_items': cart_items,
        'cart_numbers': cart_numbers,
        'user_address': user_address,
        'user_phone_number':user_phone_number,
    }
    return render(request, "cart.html", context)

@login_required
def get_cart(request):
    user = request.user
    cart_items = Cart.objects.filter(user_id = user.id)
    return cart_items

@login_required
def remove_item_from_cart(request,product_id):
    if request.method == "POST":
        user = request.user
        try:
            Cart.objects.filter(user_id = user.id,product_id = product_id).delete()
            return redirect('/cart/')
        
        except Cart.DoesNotExist:
            return redirect('/cart/')
 
@login_required
def remove_all_items_from_cart(request):
    user = request.user
    Cart.objects.filter(user_id=user.id).delete()
    messages.info(request, "Your cart is now empty!")
    return HttpResponse("")

@login_required
def create_checkout_session(request):
    if request.method == "POST":
        final_cart_items = json.loads(request.body.decode('utf-8')).get('final_cart_items')
        personal_details = json.loads(request.body.decode('utf-8')).get('personal_details')
        stripe.api_key = config('STRIPE_SECRET_KEY')
        data_to_be_passed_to_stripe = get_final_cart_items(request, final_cart_items)
        
        metadata = {
            "user_id" : str(request.user.id),
            "address" : str(personal_details[0]["address"]),
            "phone_number" : str(personal_details[0]["phone_number"]),
            "alternate_phone_number" : str(personal_details[0]["alternate_phone_number"]),
            "items" : json.dumps([
                {
                'product_id':   str(item["productId"]),
                "product_name": str(item["product_name"]),
                "quantity": str(item["quantity"]),
                "product_price": str(item["product_price"]), 
                }
                for item in data_to_be_passed_to_stripe])
        }
        
        line_items = []
        for item in data_to_be_passed_to_stripe:
            line_item = {
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': item["product_name"],
                    },
                    'unit_amount': int(item["product_price"] * 100),  # Convert price to cents
                },
                'quantity': item["quantity"],
            }
            line_items.append(line_item)

        payment_method_types = ["card"]    
           
        # Create a Checkout session
        session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            payment_intent_data={
                'metadata': metadata,
            },
            success_url = 'http://127.0.0.1:8000/order_message',
            payment_method_types = payment_method_types,
        )
        return JsonResponse({'session_id': session.id})
    return JsonResponse({'message': 'GET request received'})

@login_required
def get_final_cart_items(request,final_cart_items):
    items = []
    for item in final_cart_items:
        cart_item = Cart.objects.filter(user_id = request.user.id,product_id = item["productId"]).first()
        if cart_item:
            items.append({'productId': item["productId"],'quantity': item["quantity"], 'product_price':cart_item.product_price,'product_name':cart_item.product_name})
    return items    

@login_required
def orders(request):
    orders = Order.objects.filter(user_id=request.user.id)  
    return render(request, 'orders.html', { "orders": orders})


@csrf_exempt
def stripe_webhook(request):
    if request.method == 'POST':
        webhook_secret = config('WEBHOOK_KEY')
        payload = request.body.decode('utf-8')
        try:
            event = stripe.Webhook.construct_event(
                payload, request.META['HTTP_STRIPE_SIGNATURE'], webhook_secret
            )
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({'error': str(e)}, status=400)

        if event.type == 'payment_intent.succeeded':
            payment_intent =event.data.object
            user = CustomUser.objects.get(id = payment_intent.metadata["user_id"])
            alternate_phone_number_str = payment_intent["metadata"]["alternate_phone_number"]
            if alternate_phone_number_str:
                alternate_phone_number = int(alternate_phone_number_str)
            else:
                alternate_phone_number = 1
            products_ordered =payment_intent["metadata"]["items"]

            # Handling Concurrency and placing order
            lock = threading.Lock()
            with lock:
                if can_order():
                    order = Order.objects.create(
                        user = user,
                        webhook_event_id = payment_intent["id"],
                        order_status='Payment Completed',
                        total_amount = int((payment_intent.amount_received)/100),
                        address = payment_intent["metadata"]["address"],
                        phone_number = int(payment_intent["metadata"]["phone_number"]),
                        alternate_phone_number = alternate_phone_number,
                        products_ordered = products_ordered,
                    )
                    order.save()
                    Cart.objects.filter(user_id = payment_intent["metadata"]["user_id"],).delete().save()
                else:
                    payment_intent_id = payment_intent["id"]
                    refund_amount = payment_intent.amount_received
                    refund = stripe.Refund.create(payment_intent=payment_intent_id,amount=refund_amount,reason='requested_by_customer')
                    messages.info(request,"Payment deducted from your bank account has been refunded!")
                    return JsonResponse({'status': 'refund_successfull'})
            return JsonResponse({'status': 'order_successfull'})
        else:
            return JsonResponse({'status': 'order_failure'})
    return JsonResponse({'status':'None'})

def can_order():
    # Check if the order can be placed 
    return True    

@login_required
def order_message(request):
    return render(request,"order_message.html")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def seed_data(request):
    url = "https://fakestoreapi.com/products"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for item in data:
            price=item.get('price', 0.0)
            product = Product.objects.create(
                id=item.get('id'),
                name=item.get('title', ''),
                image=item.get('image', ''),
                price = price*87,
                description=item.get('description', ''),
                category=item.get('category', ''),
                rating=item.get('rating', {}).get('rate', 0.0),
                count_rating=item.get('rating', {}).get('count', 0)
            )
            product.save()
        return HttpResponse("Product Items Seeded")
    else:
        return HttpResponse(f"Failed to fetch data. Status code: {response.status_code}")
    

def product(request,product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'product_page.html', {'product': product})
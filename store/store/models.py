from django.db import models
from django.db.models import UniqueConstraint
from decimal import Decimal
import json
import uuid

class Cart(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='carts',null=True)  
    product_id = models.CharField(max_length=128,default="")
    product_name = models.CharField(max_length=128, default="")
    quantity = models.IntegerField(default=1)
    product_price = models.DecimalField(decimal_places=2, max_digits=10)
    total_price = models.DecimalField(decimal_places=2, max_digits=10,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_price = Decimal(self.quantity) * Decimal(self.product_price)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Product Name: {self.product_name}, User: {self.user.username}"

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'product_id'], name='unique_cart_item')
        ]


class User(models.Model):
    name = models.CharField(max_length=128)
    username = models.CharField(max_length=128, unique=True, null=False)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=1000)
    phone_number = models.IntegerField(null=False, default=1234567890)
    password = models.CharField(max_length=128, default='')
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_cart') 

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    description = models.CharField(max_length=10000)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return self.name


class Order(models.Model):
    order_id = models.AutoField(primary_key=True, unique = True)   
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user')
    order_date = models.DateField(auto_now_add=True)
    order_status = models.CharField(max_length=100)
    webhook_event_id = models.CharField(max_length=100,null=False)
    products_ordered = models.TextField()
    total_amount = models.IntegerField()
    address = models.CharField(max_length=100)
    phone_number = models.IntegerField()
    alternate_phone_number = models.IntegerField()

    def __str__(self):
        return f" Order Id :{self.order_id} User :{self.user_id} Order Status :{self.order_status}"
    
    def get_products_ordered(self):
        try:
            return json.loads(self.products_ordered)
        except json.JSONDecodeError as e:
            return []


    



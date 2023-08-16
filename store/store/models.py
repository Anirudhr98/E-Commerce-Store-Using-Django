from django.db import models
from django.db.models import UniqueConstraint

class Cart(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='carts',null=True)  
    product_id = models.IntegerField(unique=True)
    product_name = models.CharField(max_length=128, default="")
    quantity = models.IntegerField(default=1)
    product_price = models.DecimalField(decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def price_total(self):
        return self.quantity * self.product_price

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
    name = models.CharField(max_length=128)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    description = models.CharField(max_length=10000)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return self.name

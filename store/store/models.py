from django.db import models
from django.db.models import UniqueConstraint
from decimal import Decimal
import json
from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin
from django.utils import timezone

class Cart(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='carts',null=True)  
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=128, default="")
    quantity = models.IntegerField(default=1)
    product_price = models.DecimalField(decimal_places=2, max_digits=10)
    total_price = models.DecimalField(decimal_places=2, max_digits=10,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_price = Decimal(self.quantity) * Decimal(self.product_price)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Product Name: {self.product_name}, User: {self.user.name}"

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'product_id'], name='unique_cart_item')
        ]



class Product(models.Model):
    id = models.IntegerField(default=None,primary_key=True,db_index=True)
    name = models.CharField(max_length=128)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    description = models.CharField(max_length=10000)
    category = models.CharField(max_length=1000)
    image = models.URLField()
    rating = models.IntegerField()
    count_rating = models.IntegerField()
    
    def __str__(self):
        return self.name


class Order(models.Model):
    order_id = models.AutoField(primary_key=True, unique = True)   
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE,related_name='user')
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

    
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_cart') 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='customuser_set',  
        related_query_name='user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='customuser_set',  
        related_query_name='user'
    )
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']


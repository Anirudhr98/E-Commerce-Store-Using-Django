from django.contrib import admin
from .models import CustomUser,Product,Cart,Order
from django.contrib.auth.admin import UserAdmin

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = (
        (None, {'fields': ('name','email', 'password')}),
        (('Personal info'), {'fields': ('address','phone_number','cart')}),
        (('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('name','email','phone_number')
    search_fields = ('name','email','phone_number')
    list_filter = ()
    ordering = ()
admin.site.register(CustomUser,CustomUserAdmin)

# Generated by Django 3.2.20 on 2023-08-30 14:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_alter_cart_product_id'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='cart',
            name='unique_cart_item',
        ),
    ]
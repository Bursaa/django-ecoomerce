# Generated by Django 4.2.3 on 2023-08-22 08:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0004_product_description_alter_customer_name"),
    ]

    operations = [
        migrations.RemoveField(model_name="product", name="digital",),
    ]

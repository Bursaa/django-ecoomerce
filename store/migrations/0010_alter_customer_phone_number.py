# Generated by Django 4.2.3 on 2023-08-24 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0009_customer_phone_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="phone_number",
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
    ]

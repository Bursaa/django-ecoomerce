# Generated by Django 4.2.3 on 2023-08-22 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0005_remove_product_digital"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="allegro_append",
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="ebay_append",
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="olx_append",
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="vintedo_append",
            field=models.BooleanField(default=False, null=True),
        ),
    ]
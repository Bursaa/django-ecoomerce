# Generated by Django 4.2.3 on 2023-08-24 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0008_remove_subcategory_category_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="phone_number",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

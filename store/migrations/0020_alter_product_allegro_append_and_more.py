# Generated by Django 4.2.3 on 2023-09-04 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0019_category_allegro_id_subcategory_allegro_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="allegro_append",
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="olx_append",
            field=models.BooleanField(null=True),
        ),
    ]

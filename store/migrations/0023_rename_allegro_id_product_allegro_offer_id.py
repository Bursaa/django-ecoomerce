# Generated by Django 4.2.3 on 2023-09-05 15:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0022_remove_product_allegro_product_allegro_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product", old_name="allegro_id", new_name="allegro_offer_id",
        ),
    ]
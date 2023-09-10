# Generated by Django 4.2.3 on 2023-09-08 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0025_token_delete_tokens"),
    ]

    operations = [
        migrations.AddField(
            model_name="token",
            name="authorizated",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="token",
            name="access_token",
            field=models.CharField(blank=True, default="", max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name="token",
            name="refresh_token",
            field=models.CharField(blank=True, default="", max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name="token",
            name="time_of_invalidation",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]

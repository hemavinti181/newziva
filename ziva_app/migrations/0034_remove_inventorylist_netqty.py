# Generated by Django 4.1.4 on 2022-12-27 13:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ziva_app', '0033_inventorylist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventorylist',
            name='netqty',
        ),
    ]

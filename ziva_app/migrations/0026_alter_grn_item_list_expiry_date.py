# Generated by Django 4.1.4 on 2022-12-27 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ziva_app', '0025_alter_grn_item_list_expiry_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grn_item_list',
            name='expiry_date',
            field=models.DateField(blank=True, default='0000-00-00', null=True),
        ),
    ]

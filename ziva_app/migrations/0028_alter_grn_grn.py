# Generated by Django 4.1.4 on 2022-12-27 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ziva_app', '0027_grn_alter_grn_item_list_expiry_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grn',
            name='grn',
            field=models.CharField(max_length=50),
        ),
    ]

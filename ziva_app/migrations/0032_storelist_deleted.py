# Generated by Django 4.1.4 on 2022-12-27 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ziva_app', '0031_storelist_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='storelist',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]

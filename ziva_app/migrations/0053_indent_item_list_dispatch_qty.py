# Generated by Django 4.1.4 on 2022-12-30 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ziva_app', '0052_indent_item_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='indent_item_list',
            name='dispatch_qty',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]

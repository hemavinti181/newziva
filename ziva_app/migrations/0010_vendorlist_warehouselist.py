# Generated by Django 4.1.4 on 2022-12-22 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ziva_app', '0009_filter_itemlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vendor_code', models.CharField(max_length=50)),
                ('vendor_name', models.CharField(max_length=50)),
                ('pan', models.CharField(max_length=50)),
                ('gst', models.CharField(max_length=50)),
                ('contact_name', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=50)),
                ('contact_no', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='WarehouseList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_code', models.CharField(max_length=50)),
                ('item_name', models.CharField(max_length=50)),
                ('hsn', models.CharField(max_length=50)),
                ('gst', models.CharField(max_length=50)),
                ('category', models.CharField(max_length=50)),
                ('manufacture', models.CharField(max_length=50)),
                ('uom', models.CharField(max_length=50)),
            ],
        ),
    ]

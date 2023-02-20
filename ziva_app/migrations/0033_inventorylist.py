# Generated by Django 4.1.4 on 2022-12-27 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ziva_app', '0032_storelist_deleted'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cp_sno', models.IntegerField()),
                ('itemcode', models.CharField(blank=True, max_length=50, null=True)),
                ('itemname', models.CharField(blank=True, max_length=50, null=True)),
                ('qty', models.IntegerField()),
                ('freeqty', models.IntegerField()),
                ('netqty', models.IntegerField()),
                ('manufacturername', models.CharField(blank=True, max_length=50, null=True)),
                ('batchcode', models.CharField(blank=True, max_length=50, null=True)),
                ('expirydate', models.DateField(auto_now=True, null=True)),
                ('displayexpiry', models.DateField(auto_now=True, null=True)),
                ('mrp', models.IntegerField()),
                ('margin', models.IntegerField()),
            ],
        ),
    ]

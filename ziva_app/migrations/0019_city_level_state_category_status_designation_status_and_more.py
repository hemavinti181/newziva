# Generated by Django 4.1.4 on 2022-12-26 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ziva_app', '0018_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.CharField(max_length=50, primary_key='True', serialize=False)),
                ('code', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=10)),
                ('status', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.CharField(max_length=50, primary_key='True', serialize=False)),
                ('code', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=10)),
                ('status', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.CharField(max_length=50, primary_key='True', serialize=False)),
                ('code', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=10)),
                ('status', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='category',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='designation',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='role',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='uom',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]

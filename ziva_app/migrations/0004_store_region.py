# Generated by Django 4.1.4 on 2022-12-19 12:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ziva_app', '0003_region'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='depo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='regions', to='ziva_app.depo'),
        ),
    ]

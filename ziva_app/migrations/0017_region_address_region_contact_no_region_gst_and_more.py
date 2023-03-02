# Generated by Django 4.1.4 on 2022-12-26 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ziva_app', '0016_remove_warehouse_gst_image_remove_warehouse_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='depo',
            name='address',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='depo',
            name='contact_no',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='depo',
            name='gst',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='depo',
            name='gst_image',
            field=models.ImageField(default=1, upload_to=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='depo',
            name='image',
            field=models.ImageField(default=1, upload_to=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='depo',
            name='lic_image',
            field=models.ImageField(default=1, upload_to=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='depo',
            name='licence',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='depo',
            name='region_manager',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]

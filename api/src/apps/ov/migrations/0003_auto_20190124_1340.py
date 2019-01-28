# Generated by Django 2.1.5 on 2019-01-24 12:40

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ov', '0002_auto_20190124_1054'),
    ]

    operations = [
        migrations.AddField(
            model_name='ovkv6',
            name='geo_location',
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=28992),
        ),
        migrations.AlterField(
            model_name='ovkv6',
            name='userstopcode',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
# Generated by Django 4.1 on 2023-12-12 16:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bingentity',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2023, 12, 12, 0, 0)),
            preserve_default=False,
        ),
    ]

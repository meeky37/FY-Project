# Generated by Django 4.1 on 2024-01-19 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nlp_processor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoundErrors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bound_start', models.IntegerField()),
                ('bound_end', models.IntegerField()),
                ('left_segment', models.TextField()),
                ('mention_segment', models.TextField()),
                ('right_segment', models.TextField()),
                ('error_message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
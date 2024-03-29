# Generated by Django 4.1 on 2024-02-06 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_app', '0022_alter_article_headline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='headline',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='url',
            field=models.CharField(max_length=500, unique=True),
        ),
    ]

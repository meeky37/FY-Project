# Generated by Django 4.1 on 2023-12-29 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_app', '0008_remove_article_similar_article_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='similar_articles',
            field=models.ManyToManyField(blank=True, to='profiles_app.article'),
        ),
    ]
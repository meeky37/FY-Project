# Generated by Django 4.1 on 2023-12-29 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_app', '0007_remove_article_similar_articles_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='similar_article',
        ),
        migrations.AddField(
            model_name='article',
            name='similar_articles',
            field=models.ManyToManyField(blank=True, null=True, to='profiles_app.article'),
        ),
    ]

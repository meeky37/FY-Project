# Generated by Django 4.1 on 2023-12-29 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_app', '0005_remove_article_minhash_signature_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='similar_articles',
            field=models.ManyToManyField(blank=True, to='profiles_app.article'),
        ),
    ]
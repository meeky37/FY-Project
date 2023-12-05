# Generated by Django 4.1 on 2023-12-03 00:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entity',
            name='source_article_id',
        ),
        migrations.AddField(
            model_name='entity',
            name='source_article',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.PROTECT, to='profiles_app.article'),
            preserve_default=False,
        ),
    ]
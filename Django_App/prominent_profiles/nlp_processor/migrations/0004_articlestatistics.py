# Generated by Django 4.1 on 2024-01-25 20:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_app', '0020_entityhistory_delete_entitymergelog'),
        ('nlp_processor', '0003_rename_bounderrors_bounderror'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleStatistics',
            fields=[
                ('article', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='profiles_app.article')),
                ('fuzzy_hash', models.CharField(max_length=64, null=True)),
                ('word_count', models.IntegerField(blank=True, null=True)),
                ('terms_count', models.IntegerField(blank=True, null=True)),
                ('vocd', models.FloatField(blank=True, null=True)),
                ('yulek', models.FloatField(blank=True, null=True)),
                ('simpsond', models.FloatField(blank=True, null=True)),
                ('the_count', models.IntegerField(blank=True, null=True)),
                ('and_count', models.IntegerField(blank=True, null=True)),
                ('is_count', models.IntegerField(blank=True, null=True)),
                ('of_count', models.IntegerField(blank=True, null=True)),
                ('in_count', models.IntegerField(blank=True, null=True)),
                ('to_count', models.IntegerField(blank=True, null=True)),
                ('it_count', models.IntegerField(blank=True, null=True)),
                ('that_count', models.IntegerField(blank=True, null=True)),
                ('with_count', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]

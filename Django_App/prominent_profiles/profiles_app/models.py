from django.db import models

# profiles_app/models.py
from django.db import models


class Article(models.Model):
    headline = models.CharField(max_length=255, null=True)
    url = models.CharField(max_length=255, unique=True)
    image_url = models.CharField(max_length=255, null=True)
    date_added = models.DateTimeField(auto_now_add=True)


class Entity(models.Model):
    source_article = models.ForeignKey(Article, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, null=True)


class BingEntity(models.Model):
    entity_id = models.ForeignKey('Entity', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.CharField(max_length=255)
    web_search_url = models.CharField(max_length=255)
    bing_id = models.CharField(max_length=255)
    contractual_rules = models.JSONField()
    entity_type_display_hint = models.CharField(max_length=255)
    entity_type_hints = models.JSONField()


class BoundMention(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    bound_start = models.IntegerField()
    bound_end = models.IntegerField()
    avg_neutral = models.DecimalField(max_digits=5, decimal_places=2)
    avg_positive = models.DecimalField(max_digits=5, decimal_places=2)
    avg_negative = models.DecimalField(max_digits=5, decimal_places=2)
    bound_text = models.TextField()


class OverallSentiment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    num_bound = models.IntegerField()
    linear_neutral = models.DecimalField(max_digits=5, decimal_places=2)
    linear_positive = models.DecimalField(max_digits=5, decimal_places=2)
    linear_negative = models.DecimalField(max_digits=5, decimal_places=2)
    exp_neutral = models.DecimalField(max_digits=5, decimal_places=2)
    exp_positive = models.DecimalField(max_digits=5, decimal_places=2)
    exp_negative = models.DecimalField(max_digits=5, decimal_places=2)

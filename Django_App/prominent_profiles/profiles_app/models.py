from django.db import models

# profiles_app/models.py
from django.db import models

class Entity(models.Model):
    source_article_id = models.IntegerField()
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, null=True)

class Article(models.Model):
    headline = models.CharField(max_length=255, null=True)
    url = models.CharField(max_length=255, unique=True)
    image_url = models.CharField(max_length=255, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

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

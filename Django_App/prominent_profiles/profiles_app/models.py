from django.conf import settings
from django.db import models


class Article(models.Model):
    headline = models.CharField(max_length=255, null=True)
    url = models.CharField(max_length=255, unique=True)
    image_url = models.CharField(max_length=255, null=True, blank=True)
    publication_date = models.DateTimeField(null=True, blank=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    site_name = models.CharField(max_length=255, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)


class Entity(models.Model):
    source_article = models.ForeignKey(Article, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, null=True, blank=True)
    app_visible = models.BooleanField(
        default=False)  # So web admins can filter live entities on app.
    view_count = models.IntegerField(default=0)

    @property
    def article_count(self):
        return OverallSentiment.objects.filter(entity=self).count()


class IgnoreEntitySimilarity(models.Model):
    entity_a = models.ForeignKey('Entity', related_name='ignore_relationships_a',
                                 on_delete=models.CASCADE)
    entity_b = models.ForeignKey('Entity', related_name='ignore_relationships_b',
                                 on_delete=models.CASCADE)

    class Meta:
        unique_together = ('entity_a', 'entity_b')

    def __str__(self):
        return f"Ignore Relationship: '{self.entity_a.name}' <-> '{self.entity_b.name}'"


class EntityHistory(models.Model):
    name = models.CharField(max_length=255)
    merged_into = models.ForeignKey('Entity', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                             blank=True)

    def __str__(self):
        if self.merged_into is not None:
            return f'Merge Log: {self.merged_into.name} <- {self.name}'
        else:
            # Handle cases where EntityHistory was (by mistake) not included in merge steps
            return f'Merge Log: No merge information available for {self.name}'



class EntityView(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    view_dt = models.DateField(auto_now_add=True)
    view_time = models.TimeField(auto_now_add=True)


class BingEntity(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.CharField(max_length=255)
    web_search_url = models.CharField(max_length=255)
    bing_id = models.CharField(max_length=255)
    contractual_rules = models.JSONField()
    entity_type_display_hint = models.CharField(max_length=255)
    entity_type_hints = models.JSONField()
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

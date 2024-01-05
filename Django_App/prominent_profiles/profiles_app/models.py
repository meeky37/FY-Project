# profiles_app/models.py
from django.db import models
from django.utils import timezone


class Article(models.Model):
    headline = models.CharField(max_length=255, null=True)
    url = models.CharField(max_length=255, unique=True)
    image_url = models.CharField(max_length=255, null=True, blank=True)
    publication_date = models.DateTimeField(null=True, blank=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    site_name = models.CharField(max_length=255, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

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


    # def get_article_count(self):
    #     # Making sortable in admin portal
    #     return self.article_count
    # get_article_count.admin_order_field = 'article_count'


#
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

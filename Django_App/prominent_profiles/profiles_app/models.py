from django.conf import settings
from django.db import models


class Article(models.Model):
    """
    Represents an article collected from various sources with metadata including its headline,
    URL, publication details, and processing status.
    NLP Job success can be inferred from this model as an article should always be marked
    processed (i.e. it went through article_processor.py) or a similar reject as a
    SimilarEntityPair was created during the job.
    """
    headline = models.CharField(max_length=255, null=True)
    url = models.CharField(max_length=500, unique=True)
    image_url = models.CharField(max_length=500, null=True, blank=True)
    publication_date = models.DateTimeField(null=True, blank=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    site_name = models.CharField(max_length=255, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    similar_rejection = models.BooleanField(default=False)
    source_file = models.ForeignKey('nlp_processor.ProcessedFile', on_delete=models.DO_NOTHING,
                                    default=None, null=True, blank=True)


class Entity(models.Model):
    """
    Represents an entity identified within articles, with a visibility flag and article count to
    help admins to make visibility decisions.
    These are the 'Profiles' at the core of the 'Prominent Profiles' web app.
    """
    source_article = models.ForeignKey(Article, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, null=True, blank=True)
    app_visible = models.BooleanField(
        default=False)  # So web admins can filter live entities on app.
    view_count = models.IntegerField(default=0)

    @property
    def article_count(self):
        """
        Property to compute the number of articles associated with this entity via the
        OverallSentiment model.

        :return: (int) The count of articles associated with this entity.
        """
        return OverallSentiment.objects.filter(entity=self).count()

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"


class IgnoreEntitySimilarity(models.Model):
    """
    Defines a relationship to explicitly ignore the similarity between two entities, so they are
    not suggested by the admins' Merge Review page as candidates for a merge.
    """
    entity_a = models.ForeignKey('Entity', related_name='ignore_relationships_a',
                                 on_delete=models.CASCADE)
    entity_b = models.ForeignKey('Entity', related_name='ignore_relationships_b',
                                 on_delete=models.CASCADE)

    class Meta:
        unique_together = ('entity_a', 'entity_b')
        verbose_name = "Ignore entity similarity"
        verbose_name_plural = "Ignore entity similarities"

    def __str__(self):
        """
        String representation of the ignore similarity relationship between two entities.
        Quicker, more logical representation than the default Django approach.
        """
        return f"Ignore Relationship: '{self.entity_a.name}' <-> '{self.entity_b.name}'"



class EntityHistory(models.Model):
    """
    Logs the history of entity modifications, specifically tracking entity merges as well as the
    admin user account that made the change for accountability purposes.
    """
    name = models.CharField(max_length=255)
    merged_into = models.ForeignKey('Entity', on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                             blank=True)

    def __str__(self):
        """
        Overrides the default django admin representation with a more logical <- to show the
        change made.
        """
        if self.merged_into is not None:
            return f'Merge Log: {self.merged_into.name} <- {self.name}'
        else:
            # Handle cases where EntityHistory was (by mistake) not included in merge steps
            return f'Merge Log: No merge information available for {self.name}'

    class Meta:
        verbose_name = "Entity history"
        verbose_name_plural = "Entity histories"


class SimilarEntityPair(models.Model):
    """
    Represents a pair of entities with a calculated similarity score, useful for identifying
    potentially related entities. Previously, these were not stored in the database and made for
    an unresponsive admin user experience.
    """
    entity_a = models.ForeignKey(Entity, related_name='similarity_pair_a', on_delete=models.CASCADE)
    entity_b = models.ForeignKey(Entity, related_name='similarity_pair_b', on_delete=models.CASCADE)
    similarity_score = models.FloatField()

    class Meta:
        unique_together = ('entity_a', 'entity_b')
        indexes = [
            models.Index(fields=['entity_a', 'entity_b']),
            models.Index(fields=['entity_b', 'entity_a']),
        ]

    def __str__(self):
        return f"{self.entity_a.name} - {self.entity_b.name}: {self.similarity_score}"


class EntityView(models.Model):
    """
    Tracks views of entities, logging each view with a date and time stamp for the
    TrendingEntityCards on the apps home page www.prominentprofiles.com
    """
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    view_dt = models.DateField(auto_now_add=True)
    view_time = models.TimeField(auto_now_add=True)


class BingEntity(models.Model):
    """
    Stores info gathered from bing entity for display on front-end to enrich the UX.
    Additionally, contractual rules and dates are kept to fairly attribute photos and
    descriptions shown.
    """
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.CharField(max_length=255)
    improved_image_url = models.CharField(max_length=255, null=True)
    web_search_url = models.CharField(max_length=255)
    bing_id = models.CharField(max_length=255)
    contractual_rules = models.JSONField()
    entity_type_display_hint = models.CharField(max_length=255)
    entity_type_hints = models.JSONField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bing entity"
        verbose_name_plural = "Bing entities"


class BoundMention(models.Model):
    """
    Represents a specific mention of an entity within an article
    including its textual context (typically a sentence) and average NewsSentiment scores.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    bound_start = models.IntegerField()
    bound_end = models.IntegerField()
    avg_neutral = models.DecimalField(max_digits=5, decimal_places=2)
    avg_positive = models.DecimalField(max_digits=5, decimal_places=2)
    avg_negative = models.DecimalField(max_digits=5, decimal_places=2)
    bound_text = models.TextField()


class OverallSentiment(models.Model):
    """
    Represents the results of aggregating and scaling bound mentions of an entity across an
    article text to provide a holistic/summative view for web app users.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    num_bound = models.IntegerField()
    linear_neutral = models.DecimalField(max_digits=5, decimal_places=2)
    linear_positive = models.DecimalField(max_digits=5, decimal_places=2)
    linear_negative = models.DecimalField(max_digits=5, decimal_places=2)
    exp_neutral = models.DecimalField(max_digits=5, decimal_places=2)
    exp_positive = models.DecimalField(max_digits=5, decimal_places=2)
    exp_negative = models.DecimalField(max_digits=5, decimal_places=2)

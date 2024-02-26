from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponseBadRequest
from django.urls import path
from django.shortcuts import render
from rapidfuzz import fuzz
from django.http import HttpResponse

from .models import Article, BoundMention, OverallSentiment, BingEntity, EntityView, \
    IgnoreEntitySimilarity, Entity, EntityHistory


class BoundMentionInline(admin.TabularInline):
    model = BoundMention
    fields = ('entity', 'name_display', 'bound_start', 'bound_end', 'avg_neutral', 'avg_positive',
                       'avg_negative', 'bound_text')
    readonly_fields = ('entity', 'name_display', 'bound_start', 'bound_end', 'avg_neutral',
                       'avg_positive', 'avg_negative', 'bound_text')
    can_delete = False
    max_num = 0

    def name_display(self, instance):
        return instance.entity.name
    name_display.short_description = "Entity Name"


class OverallSentimentInlineForArticle(admin.TabularInline):
    model = OverallSentiment
    fields = ('name_display', 'num_bound', 'linear_neutral', 'linear_positive',
                       'linear_negative',
                       'exp_positive', 'exp_neutral', 'exp_negative',)
    readonly_fields = ('name_display', 'num_bound', 'linear_neutral', 'linear_positive',
                       'linear_negative',
                       'exp_positive', 'exp_neutral', 'exp_negative')
    can_delete = False
    max_num = 0

    def name_display(self, instance):
        return instance.entity.name
    name_display.short_description = "Entity Name"


class OverallSentimentInlineForEntity(admin.TabularInline):
    model = OverallSentiment
    fields = ('article', 'headline_display', 'num_bound', 'linear_neutral', 'linear_positive',
              'linear_negative',
              'exp_positive', 'exp_neutral', 'exp_negative',)
    readonly_fields = (
    'article', 'headline_display', 'num_bound', 'linear_neutral', 'linear_positive',
    'linear_negative',
    'exp_positive', 'exp_neutral', 'exp_negative')
    can_delete = False
    max_num = 0

    def headline_display(self, instance):
        return instance.article.headline
    headline_display.short_description = "Article Headline"


class EntityInline(admin.TabularInline):
    model = Entity
    fields = ('Entity', 'name_display')
    readonly_fields = ('Entity', 'name_display')
    can_delete = False
    max_num = 0

    def name_display(self, instance):
        return instance.entity.name
    name_display.short_description = "Entity Name"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'processed', 'similar_rejection', 'headline', 'url', 'image_url',
    'date_added','publication_date', 'site_name', 'author')
    readonly_fields = (
    'headline', 'url', 'image_url', 'publication_date', 'author', 'site_name', 'processed',
    'similar_rejection')

    inlines = [BoundMentionInline, OverallSentimentInlineForArticle]


def get_similar_entities(entities, ignored_entity_pairs, app_visible_entities, threshold):
    """Utilise rapid fuzzy matching on pairs that haven't been added to the ignore table.
       Process can be reduced significantly by considering only entities that are visible on app
       frontend (i.e most important)"""
    similar_entities = []

    ignored_pairs = set()

    if ignored_entity_pairs:
        for ignore_relationship in ignored_entity_pairs:
            ignored_pairs.add((ignore_relationship.entity_a, ignore_relationship.entity_b))
            ignored_pairs.add((ignore_relationship.entity_b, ignore_relationship.entity_a))

    if app_visible_entities is not None:
        considered_entities = app_visible_entities
    else:
        considered_entities = entities

    for entity in considered_entities:
        similar_entities_for_current = [
            other_entity for other_entity in entities
            if other_entity != entity
               and (entity, other_entity) not in ignored_pairs
               and fuzz.ratio(entity.name, other_entity.name) >= threshold
        ]

        if len(similar_entities_for_current) > 1:
            similar_entities.append((entity, similar_entities_for_current))

    return similar_entities


def update_and_merge_entities(master_entity, secondary_entity, request):
    """
    Update references, perform master entity inheritance, and delete secondary entity.

    - master_entity: The entity to which secondary_entity is being merged.
    - secondary_entity: The entity being merged into master_entity.
    """

    with transaction.atomic():
        # Update references
        BoundMention.objects.filter(entity=secondary_entity).update(entity=master_entity)
        OverallSentiment.objects.filter(entity=secondary_entity).update(entity=master_entity)
        BingEntity.objects.filter(entity=secondary_entity).update(entity=master_entity)
        EntityHistory.objects.filter(merged_into=secondary_entity).update(merged_into=master_entity)

        # Master entity inheritance
        master_entity.name = f"{master_entity.name}"
        master_entity.type = master_entity.type or secondary_entity.type
        master_entity.app_visible = master_entity.app_visible or secondary_entity.app_visible

        # Save changes and create EntityHistory record
        master_entity.save()
        EntityHistory.objects.create(
            name=secondary_entity.name,
            merged_into=master_entity,
            user=request.user
        )

        # Delete the secondary entity
        secondary_entity.delete()


class EntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'app_visible', 'view_count', 'display_article_count_numeric')
    list_filter = ('app_visible',)
    list_per_page = 1000
    search_fields = ['name']
    inlines = [OverallSentimentInlineForEntity]

    def get_queryset(self, request):
        queryset = Entity.objects.annotate(overallsentiment__count=Count('overallsentiment__id'))
        return queryset

    def display_article_count_numeric(self, obj):
        return obj.overallsentiment__count

    display_article_count_numeric.short_description = 'Article Count (Numeric)'

    def merge_entities_primary_higher(self, request, queryset):
        """Merges two checkbox selected entities in standard django entity table view.
            The entity selected higher in the table ordering is retained."""
        queryset = queryset.annotate(article_count_numeric=Count('overallsentiment'))
        if queryset.count() == 2:
            master_entity = queryset.first()
            secondary_entity = queryset.last()
            update_and_merge_entities(master_entity, secondary_entity, request)

            self.message_user(request, "Entities merged successfully.", level='INFO')
        else:
            self.message_user(request, "Please select exactly two entities for merging.",
                              level='ERROR')

    def merge_entities_primary_lower(self, request, queryset):
        """As above except the entity lower in the table is retained (opposite to above)"""
        queryset = queryset.annotate(article_count_numeric=Count('overallsentiment'))
        if queryset.count() == 2:
            master_entity = queryset.last()
            secondary_entity = queryset.first()
            update_and_merge_entities(master_entity, secondary_entity, request)

            self.message_user(request, "Entities merged successfully.", level='INFO')
        else:
            self.message_user(request, "Please select exactly two entities for merging.",
                              level='ERROR')

    def reset_view_count(self, request, queryset):
        queryset = queryset.order_by('id')
        queryset.update(view_count=0)

    def make_app_visible(self, request, queryset):
        queryset = queryset.order_by('id')
        queryset.update(app_visible=True)

    make_app_visible.short_description = "Mark selected entities as app visible"
    merge_entities_primary_lower.short_description = ("Merge HIGHER entity into LOWER entity in "
                                                      "table")
    merge_entities_primary_higher.short_description = ("Merge LOWER entity into HIGHER entity in "
                                                       "table")
    make_app_visible.short_description = 'Make App Visible'
    reset_view_count.short_description = 'Reset View Count'
    display_article_count_numeric.admin_order_field = 'overallsentiment__count'

    actions = [merge_entities_primary_higher, merge_entities_primary_lower, make_app_visible,
               reset_view_count]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('merge_review/', self.admin_site.admin_view(self.merge_review),
                 name='merge_review'),
            path('merge_review/app_visible/', self.admin_site.admin_view(
                self.merge_review_app_visible_only),
                 name='merge_review_app_visible_only'),
            path('merge_entities_admin/', self.admin_site.admin_view(self.merge_entities_admin),
                 name='merge_entities_admin'),
            path('ignore_entities_admin/', self.admin_site.admin_view(self.ignore_entities_admin),
                 name='ignore_entities_admin'),
        ]
        return custom_urls + urls

    def merge_review(self, request):
        """Collect entity pairings to be ignored, all entities in database, set a moderate
        threshold then process using get_similar_entities.
        Sort in alphabetical order for user display"""
        ignore_entity_pairs = IgnoreEntitySimilarity.objects.all()
        entities = Entity.objects.all()
        threshold = 78
        similar_entities = get_similar_entities(entities, ignore_entity_pairs, None, threshold)
        merge_pairs = sorted(similar_entities, key=lambda x: x[0].name)
        return render(request, 'admin/merge_review.html', {'merge_pairs': merge_pairs})

    def merge_review_app_visible_only(self, request):
        """As above but also obtains app_visible = True entities to provide similar_entities with a
        smaller pool of fuzzy match comparisons to make"""
        ignore_entity_pairs = IgnoreEntitySimilarity.objects.all()
        entities = Entity.objects.all()
        app_visible_entities = Entity.objects.filter(app_visible=True)
        threshold = 65
        similar_entities = get_similar_entities(entities, ignore_entity_pairs,
                                                app_visible_entities, threshold)
        merge_pairs = sorted(similar_entities, key=lambda x: x[0].name)
        return render(request, 'admin/merge_review.html', {'merge_pairs': merge_pairs})

    def merge_entities_admin(self, request):
        """Handles merge request made in the admin site by checking the form is actually a merge
        request and that secondary entities have been selected.
        Then merges secondaries into primary iteratively then return an appropriate response"""
        if request.method == 'POST':
            merge_option = request.POST.get('merge')

            if merge_option == 'yes':
                selected_entities = request.POST.getlist('secondary_entities')

                if len(selected_entities) > 0:
                    primary_entity_id = request.POST.get('primary_entity_id')
                    primary_entity_name = request.POST.get('primary_entity_name')

                    try:
                        with transaction.atomic():
                            primary_entity = self.get_object(request, primary_entity_id)
                            for entity_id in selected_entities:
                                master_entity = primary_entity
                                secondary_entity = self.get_object(request, entity_id)
                                update_and_merge_entities(master_entity, secondary_entity, request)
                            messages.success(request,
                                             f"Entities merged successfully. Primary: {primary_entity_name}")

                        return HttpResponse(status=200)

                    except Exception as e:
                        print(f"Error during merge: {str(e)}")

                        messages.error(request, "An error occurred during the merge process.")
                        return HttpResponseBadRequest("An error occurred during the merge process.")

        return HttpResponseBadRequest("Invalid request.")

    def ignore_entities_admin(self, request):
        """Handles merge request made in the admin site by checking the form is actually a merge
        request and that secondary entities have been selected.
        Then merges secondaries into primary iteratively then return an appropriate response"""
        if request.method == 'POST':
            ignore_option = request.POST.get('ignore')

            if ignore_option == 'yes':
                selected_entities = request.POST.getlist('secondary_entities')

                if len(selected_entities) > 0:
                    primary_entity_id = request.POST.get('primary_entity_id')
                    primary_entity_name = request.POST.get('primary_entity_name')

                    try:
                        with transaction.atomic():
                            primary_entity = self.get_object(request, primary_entity_id)

                            for entity_id in selected_entities:
                                secondary_entity = self.get_object(request, entity_id)
                                IgnoreEntitySimilarity.objects.create(entity_a=primary_entity,
                                                                      entity_b=secondary_entity)

                            messages.success(request,
                                             f"Entity fuzzy match exceptions created "
                                             f"successfully. "
                                             f"Primary:"
                                             f" {primary_entity_name}")

                        return HttpResponse(status=200)

                    except Exception as e:
                        print(f"Error during exception creation: {str(e)}")

                        messages.error(request, "An error occurred during the merge process.")
                        return HttpResponseBadRequest("An error occurred during the merge process.")

        return HttpResponseBadRequest("Invalid request.")


class BingEntityAdmin(admin.ModelAdmin):
    list_display = ('id', 'entity', 'name', 'description', 'image_url',
                    'improved_image_url', 'web_search_url', 'bing_id',
                    'contractual_rules', 'entity_type_display_hint', 'entity_type_hints',
                    'date_added')


class EntityViewAdmin(admin.ModelAdmin):
    list_display = ('entity', 'get_entity_name', 'view_dt', 'view_time')
    list_filter = ('entity', 'view_dt', 'view_time')
    search_fields = ('entity__name',)

    def get_entity_name(self, obj):
        return obj.entity.name

    get_entity_name.short_description = 'Entity Name'
    get_entity_name.admin_order_field = 'entity__name'


class OverallSentimentAdmin(admin.ModelAdmin):
    list_display = (
    'article_id', 'entity_id', 'get_article_headline', 'get_entity_name', 'num_bound',
    'linear_neutral', 'linear_positive', 'linear_negative', 'exp_neutral', 'exp_positive',
    'exp_negative')
    search_fields = ('article__id',)
    readonly_fields = ['get_article_headline', 'get_entity_name']

    def get_article_headline(self, obj):
        return obj.article.headline

    get_article_headline.short_description = 'Article Headline'
    get_article_headline.admin_order_field = 'article__headline'

    def get_entity_name(self, obj):
        return obj.entity.name

    get_entity_name.short_description = 'Entity Name'
    get_entity_name.admin_order_field = 'entity__name'

class BoundMentionAdmin(admin.ModelAdmin):
    list_display = (
        'article_id', 'entity_id', 'get_entity_name', 'bound_start', 'bound_end', 'avg_neutral',
        'avg_positive', 'avg_negative', 'bound_text')

    def get_entity_name(self, obj):
        return obj.entity.name

    get_entity_name.short_description = 'Entity Name'
    get_entity_name.admin_order_field = 'entity__name'


admin.site.register(Entity, EntityAdmin)
admin.site.register(IgnoreEntitySimilarity)
admin.site.register(EntityHistory)
admin.site.register(EntityView, EntityViewAdmin)
admin.site.register(BingEntity, BingEntityAdmin)
admin.site.register(BoundMention, BoundMentionAdmin)
admin.site.register(OverallSentiment, OverallSentimentAdmin)

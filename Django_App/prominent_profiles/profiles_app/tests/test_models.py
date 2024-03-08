import json
from datetime import datetime
from decimal import Decimal

from accounts.models import CustomUser
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from nlp_processor.models import ProcessedFile
from profiles_app.models import (Article, Entity, IgnoreEntitySimilarity, EntityHistory,
                                 SimilarEntityPair, \
                                 EntityView, BingEntity, BoundMention, OverallSentiment)


class ArticleTest(TestCase):
    def setUp(self):
        self.processed_file = ProcessedFile.objects.create(
            file_name="uob+student+blogs_no_dup_articles_loop_29-06-2022-11:45.json")

    def test_article_flags_modification(self):
        # Check processed and similar rejection updates without error
        naive_datetime = datetime.strptime("Jun. 29, 2022", "%b. %d, %Y")
        publication_date = timezone.make_aware(naive_datetime)

        current_date = timezone.now()
        date_added = timezone.make_aware(
            datetime(current_date.year, current_date.month, current_date.day))

        article = Article.objects.create(headline="Day in the Life of a Computer Science Student",
                                         url="https://blog.bham.ac.uk/epsstudentblogs/2022/06/29/day-in-the-life-of-a-computer-science-student/",
                                         image_url="https://blog.bham.ac.uk/epsstudentblogs/wp-content/uploads/sites/59/2020/05/Untitled-design.png",
                                         publication_date=publication_date,
                                         author="Guest Blogger",
                                         date_added=date_added,
                                         processed=False,
                                         similar_rejection=False,
                                         source_file=None
                                         )
        article.processed = True
        article.similar_rejection = True
        article.save()

        updated_article = Article.objects.get(id=article.id)
        self.assertTrue(updated_article.processed)
        self.assertTrue(updated_article.similar_rejection)

    def test_article_with_processed_file(self):
        naive_datetime = datetime.strptime("Jun. 29, 2022", "%b. %d, %Y")
        publication_date = timezone.make_aware(naive_datetime)

        current_date = timezone.now()
        date_added = timezone.make_aware(
            datetime(current_date.year, current_date.month, current_date.day))

        article = Article.objects.create(headline="Day in the Life of a Computer Science Student",
                                         url="https://blog.bham.ac.uk/epsstudentblogs/2022/06/29/day-in-the-life-of-a-computer-science-student/",
                                         image_url="https://blog.bham.ac.uk/epsstudentblogs/wp-content/uploads/sites/59/2020/05/Untitled-design.png",
                                         publication_date=publication_date,
                                         author="Guest Blogger",
                                         date_added=date_added,
                                         processed=False,
                                         similar_rejection=False,
                                         source_file=self.processed_file
                                         )

        article.save()

        self.assertEqual(article.headline, "Day in the Life of a Computer Science Student")
        self.assertEqual(article.url,
                         "https://blog.bham.ac.uk/epsstudentblogs/2022/06/29/day-in-the-life-of-a-computer-science-student/")
        self.assertEqual(article.image_url,
                         "https://blog.bham.ac.uk/epsstudentblogs/wp-content/uploads/sites/59/2020/05/Untitled-design.png")
        self.assertEqual(article.publication_date, publication_date)
        self.assertEqual(article.author, "Guest Blogger")
        self.assertEqual(article.date_added.date(), timezone.now().date())
        self.assertEqual(article.source_file, self.processed_file)
        self.assertFalse(article.processed)
        self.assertFalse(article.similar_rejection)

    def test_article_creation_missing_url(self):
        # Ensuring article creation with missing required url is rejected
        with self.assertRaises(ValidationError):
            # Attempt to create an article without providing a required field like 'url'.
            Article.objects.create(headline="Missing URL").full_clean()

    def test_article_unique_url(self):
        # Testing the unique constraint on the 'url' field prevents 2 obvious duplicates being
        # added.
        Article.objects.create(
            headline="Original Article",
            url="https://example.com/original",
            source_file=self.processed_file
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                # Attempt to create another article with the same URL
                Article.objects.create(
                    headline="Duplicate Article",
                    url="https://example.com/original",
                    source_file=self.processed_file
                )

    def test_article_delete_cascades(self):
        # Test the deletion of an Article and check cascade works on models using an article key.
        article = Article.objects.create(
            headline="Penny Mordaunt defends Michelle Donelan after taxpayers foot £15,000 legal bill",
            url="https://www.bbc.com/news/uk-politics-68503255.amp",
            source_file=self.processed_file
        )

        entity = Entity.objects.create(
            source_article=article,
            name="Penny Mordaunt"
        )

        bound_mention = BoundMention.objects.create(
            article=article,
            entity=entity,
            bound_start=100,
            bound_end=10,
            avg_neutral=0.0,
            avg_positive=0.72,
            avg_negative=0.0,
            bound_text="Ms Mordaunt said she was confident the payment had been 'justified'."
        )

        overall_sentiment = OverallSentiment.objects.create(
            article=article,
            entity=entity,
            num_bound=1,
            linear_neutral=0.0,
            linear_positive=0.72,
            linear_negative=0.0,
            exp_neutral=0.0,
            exp_positive=0.373,
            exp_negative=0.0
        )

        article_id = article.id
        article.delete()

        with self.assertRaises(Article.DoesNotExist):
            Article.objects.get(id=article_id)

        self.assertFalse(Entity.objects.filter(id=entity.id).exists())
        self.assertFalse(BoundMention.objects.filter(id=bound_mention.id).exists())
        self.assertFalse(OverallSentiment.objects.filter(id=overall_sentiment.id).exists())


class EntityTest(TestCase):
    def setUp(self):
        self.article = Article.objects.create(
            headline="<b>Prince Harry</b>&#39;s wildest confessions - from getting naked in Vegas to &#39;wild&#39; partying",
            url="https://www.ok.co.uk/royal/prince-harrys-wildest-confessions-getting-32291851",
            publication_date=timezone.now(),
            processed=True
        )

    def test_create_entity(self):
        # Test creating an entity and linking it with the article
        entity = Entity.objects.create(
            source_article=self.article,
            name="Prince Harry",
            type=None,
            app_visible=True,
            view_count=0
        )

        self.assertEqual(entity.source_article, self.article)
        self.assertEqual(entity.name, "Prince Harry")
        self.assertEqual(entity.type, None)
        self.assertTrue(entity.app_visible)
        self.assertEqual(entity.view_count, 0)

    def test_visibility_toggle(self):
        # Test toggling false to true for entity visibility
        entity = Entity.objects.create(
            source_article=self.article,
            name="Prince Harry",
            app_visible=False
        )

        self.assertFalse(entity.app_visible)
        entity.app_visible = True
        entity.save()

        updated_entity = Entity.objects.get(id=entity.id)
        self.assertTrue(updated_entity.app_visible)

    def test_cascade_delete(self):
        # Checking entity is deleted by source article cascade
        entity = Entity.objects.create(
            source_article=self.article,
            name="Prince Harry",
        )

        self.article.delete()
        with self.assertRaises(Entity.DoesNotExist):
            Entity.objects.get(id=entity.id)


class IgnoreEntitySimilarityTest(TestCase):

    def setUp(self):
        # Set up two articles to be associated with entities
        self.article1 = Article.objects.create(
            headline="A brief, lonely presence at a major family occasion...A &#39;spare&#39; "
                     "who&#39;s been openly critical of his family...Does <b>Prince</b> Joachim&#39;s"
                     " solo trip to see his brother made King of ...",
            url="https://www.dailymail.co.uk/femail/article-12952097/Solo-family-occasion-critical"
                "-royals-remind.html",
            publication_date=timezone.now(),
            processed=True
        )

        self.article2 = Article.objects.create(
            headline="The fairytale story of how Princess Mary of Denmark met her <b>prince</b> at"
                     " a bar",
            url="https://evoke.ie/2024/01/05/royal/the-fairytale-story-of-how-princess-mary-of-"
                "denmark-met-her-prince-during-the-olympics",
            publication_date=timezone.now(),
            processed=True
        )

        # Create two entities for testing
        self.entity1 = Entity.objects.create(
            source_article=self.article1,
            name="Princess Marie"
        )

        self.entity2 = Entity.objects.create(
            source_article=self.article2,
            name="Princess Mary"
        )

    def test_create_ignore_entity_similarity(self):
        # Test an ignore relationship can be created between two entities
        ignore_relationship = IgnoreEntitySimilarity.objects.create(
            entity_a=self.entity1,
            entity_b=self.entity2
        )

        self.assertEqual(ignore_relationship.entity_a, self.entity1)
        self.assertEqual(ignore_relationship.entity_b, self.entity2)

    def test_duplicate_prevention(self):
        # Unique together should block a duplicate relationship - testing here.
        IgnoreEntitySimilarity.objects.create(
            entity_a=self.entity1,
            entity_b=self.entity2
        )

        with self.assertRaises(IntegrityError):
            IgnoreEntitySimilarity.objects.create(
                entity_a=self.entity1,
                entity_b=self.entity2
            )

    def test_str_method(self):
        ignore_relationship = IgnoreEntitySimilarity.objects.create(
            entity_a=self.entity1,
            entity_b=self.entity2
        )

        # Verifying clearer string representation for admin console is returned
        expected_str = f"Ignore Relationship: '{self.entity1.name}' <-> '{self.entity2.name}'"
        self.assertEqual(str(ignore_relationship), expected_str)

    def test_cascade_delete(self):
        # If entity is deleted the ignore similarity object is no longer required.
        IgnoreEntitySimilarity.objects.create(
            entity_a=self.entity1,
            entity_b=self.entity2
        )

        self.entity1.delete()
        with self.assertRaises(IgnoreEntitySimilarity.DoesNotExist):
            IgnoreEntitySimilarity.objects.get(entity_a=self.entity1, entity_b=self.entity2)


class EntityHistoryTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(email='info@prominentprofiles.com',
                                                   password='nope101')

        self.article1 = Article.objects.create(
            headline="Sunak Rishi Sunk Ship",
            url="https://www.fakenewssssss.co.uk/130218038",
            publication_date=timezone.now(),
            processed=True
        )

        self.entity1 = Entity.objects.create(
            source_article=self.article1,
            name="Rishi Sunak"
        )

        self.entity2 = Entity.objects.create(
            source_article=self.article1,
            name="Sunak Rishi Sunak"
        )

    def test_create_entity_history_with_merge(self):
        # Test creating an EntityHistory with a merge
        entity_history = EntityHistory.objects.create(
            name=self.entity1.name,
            merged_into=self.entity2,
            user=self.user
        )

        self.assertEqual(entity_history.name, self.entity1.name)
        self.assertEqual(entity_history.merged_into, self.entity2)
        self.assertEqual(entity_history.user, self.user)
        self.assertIsNotNone(entity_history.timestamp)

    def test_str_method(self):
        # Verify the string returned is correct when merged_into is set
        entity_history_with_merge = EntityHistory.objects.create(
            name=self.entity1.name,
            merged_into=self.entity2,
            user=self.user
        )
        self.assertEqual(str(entity_history_with_merge),
                         f'Merge Log: {self.entity2.name} <- {self.entity1.name}')

        # Verify the string returned is correct when merged_into is None
        entity_history_without_merge = EntityHistory.objects.create(
            name=self.entity1.name,
            user=self.user
        )
        self.assertEqual(str(entity_history_without_merge),
                         f'Merge Log: No merge information available for {self.entity1.name}')


class SimilarEntityPairTest(TestCase):

    def setUp(self):
        self.article1 = Article.objects.create(
            headline="The Idea Of You – Release Date, Trailer And The Book It’s Based On",
            url="https://www.capitalfm.com/news/tv-film/the-idea-of-you-release-date-trailer-book-"
                "harry-styles/"
        )
        self.entity1 = Entity.objects.create(
            source_article=self.article1,
            name="Harry Edward Styles"
        )
        self.entity2 = Entity.objects.create(
            source_article=self.article1,
            name="Harry Styles"
        )

    def test_create_similar_entity_pair(self):
        # Test similar entity pair creation
        pair = SimilarEntityPair.objects.create(
            entity_a=self.entity1,
            entity_b=self.entity2,
            similarity_score=0.8
        )
        self.assertEqual(pair.entity_a, self.entity1)
        self.assertEqual(pair.entity_b, self.entity2)
        self.assertAlmostEqual(pair.similarity_score, 0.8)

    def test_duplicate_prevention(self):
        # Ensure that the unique_together constraint prevents entity a and b.
        SimilarEntityPair.objects.create(
            entity_a=self.entity1,
            entity_b=self.entity2,
            similarity_score=0.8
        )
        with self.assertRaises(IntegrityError):
            SimilarEntityPair.objects.create(
                entity_a=self.entity1,
                entity_b=self.entity2,
                similarity_score=0.8
            )

    def test_str_method(self):
        # Test the __str__ method for correct formatting
        pair = SimilarEntityPair.objects.create(
            entity_a=self.entity1,
            entity_b=self.entity2,
            similarity_score=0.85
        )
        expected_str = f"{self.entity1.name} - {self.entity2.name}: {pair.similarity_score}"
        self.assertEqual(str(pair), expected_str)


class EntityViewTest(TestCase):
    def setUp(self):
        self.article1 = Article.objects.create(
            headline="The Idea Of You – Release Date, Trailer And The Book It’s Based On",
            url="https://www.capitalfm.com/news/tv-film/the-idea-of-you-release-date-trailer-book-"
                "harry-styles/"
        )
        self.entity1 = Entity.objects.create(
            source_article=self.article1,
            name="Harry Styles"
        )

    def test_entity_view_logging(self):
        # Test creating an EntityView and ensure fields are set correctly
        entity_view = EntityView.objects.create(
            entity=self.entity1,
        )

        self.assertEqual(entity_view.entity, self.entity1)
        self.assertAlmostEqual(entity_view.view_dt, timezone.localdate())

    def test_auto_population_of_date_and_time(self):
        # Similar to the above but focuses on the auto nature of the fields
        entity_view = EntityView.objects.create(
            entity=self.entity1,
        )

        now = timezone.now()
        self.assertEqual(entity_view.view_dt, now.date())
        self.assertIsNotNone(entity_view.view_time)


class BingEntityTest(TestCase):

    def setUp(self):
        self.article = Article.objects.create(
            headline="&#39;When I Stand Up, You Sit Down&#39;: Commons Speaker Brutally Slaps Down"
                     " Rishi Sunak",
            url="https://uk.sports.yahoo.com/news/stand-sit-down-commons-speaker-143959533.html"
        )
        self.entity = Entity.objects.create(
            source_article=self.article,
            name="Lindsay Hoyle"
        )

    def test_create_bing_entity_lindsay_hoyle(self):
        # Lindsay Hoyle bing entity creation test
        contractual_rules_example = json.dumps([
            {"_type": "ContractualRules/LicenseAttribution", "license":
                {"url": "http://creativecommons.org/licenses/by-sa/3.0/", "name": "CC-BY-SA"},
             "licenseNotice": "Text under CC-BY-SA license", "targetPropertyName": "description",
             "mustBeCloseToContent": True},
            {"url": "https://en.wikipedia.org/wiki/Lindsay_Hoyle", "text": "Wikipedia",
             "_type": "ContractualRules/LinkAttribution", "targetPropertyName": "description",
             "mustBeCloseToContent": True},
            {"url": "https://en.wikipedia.org/wiki/Lindsay_Hoyle", "_type":
                "ContractualRules/MediaAttribution", "targetPropertyName": "image",
             "mustBeCloseToContent": True}
        ])
        entity_type_hints_example = json.dumps(["Person"])

        bing_entity = BingEntity.objects.create(
            entity=self.entity,
            name="Lindsay Hoyle",
            description="Sir Lindsay Harvey Hoyle is a British politician who has served as Speaker"
                        " of the House of Commons since 2019 and as Member of Parliament for "
                        "Chorley since 1997. Before his election as Speaker, he was a member of "
                        "the Labour Party.",
            image_url="http://www.bing.com/th?id=OSK.7e1a3f9dbaa6289489126577abe1b209&w=110&h=110&c=7",
            improved_image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Official"
                               "_portrait_of_Rt_Hon_Sir_Lindsay_Hoyle_MP_crop_2.jpg/250px-Official"
                               "_portrait_of_Rt_Hon_Sir_Lindsay_Hoyle_MP_crop_2.jpg",
            web_search_url="https://www.bing.com/entityexplore?q=Lindsay+Hoyle&filters=sid:%22a1389"
                           "397-b793-f883-b4fb-387ae2158b39%22&elv=AXXfrEiqqD9r3GuelwApulrmELBPcwv"
                           "yWC8s65HOj6PdRs42E6U6dT5TpGGjtmbq4BDdpsQEq7cRRJx8OLQve4Poi4s1lHZptsqpq"
                           "nufVw4i",
            bing_id="a1389397-b793-f883-b4fb-387ae2158b39",
            contractual_rules=contractual_rules_example,
            entity_type_display_hint="British politician",
            entity_type_hints=entity_type_hints_example,
        )

        self.assertEqual(bing_entity.entity, self.entity)
        self.assertEqual(bing_entity.name, "Lindsay Hoyle")
        self.assertTrue("Sir Lindsay Harvey Hoyle" in bing_entity.description)
        self.assertTrue("http://www.bing.com/th?id=OSK.7e1a3f9dbaa6289489126577abe1b209&w=110&h=11"
                        "0&c=7" in bing_entity.image_url)
        self.assertTrue(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Official_portrait"
            "_of_Rt_Hon_Sir_Lindsay_Hoyle_MP_crop_2.jpg/250px-Official_portrait_of_Rt_"
            "Hon_Sir_Lindsay_Hoyle_MP_crop_2.jpg" in bing_entity.improved_image_url)
        self.assertEqual(bing_entity.contractual_rules, contractual_rules_example)
        self.assertEqual(bing_entity.entity_type_display_hint, "British politician")
        self.assertEqual(bing_entity.entity_type_hints, entity_type_hints_example)

    def test_cascade_delete(self):
        # Check when an entity is deleted the bing entity associated is deleted too (cascade)
        bing_entity = BingEntity.objects.create(
            entity=self.entity,
            name="DELETE",
            description="Delete me when my entity is deleted",
            image_url="www.images.com/test.png",
            web_search_url="www.search.com/deleteme",
            bing_id="7981274",
            contractual_rules=json.dumps({}),
            entity_type_display_hint="Cascade Expected",
            entity_type_hints=json.dumps([]),
        )

        # Entity delete then verify bing entity is deleted too.
        self.entity.delete()
        with self.assertRaises(BingEntity.DoesNotExist):
            BingEntity.objects.get(id=bing_entity.id)


class BoundMentionModelTest(TestCase):

    def setUp(self):
        self.article = Article.objects.create(
            headline="Emmanuel Macron warns West of threat from Russian breakthrough in Ukraine",
            url="https://exampleArticle.com"
        )
        self.entity = Entity.objects.create(
            source_article=self.article,
            name="Emmanuel Macron"
        )

        self.bound_mention_data = {
            'article': self.article,
            'entity': self.entity,
            'bound_start': 1483,
            'bound_end': 1671,
            'avg_neutral': Decimal('0.00'),
            'avg_positive': Decimal('0.75'),
            'avg_negative': Decimal('0.00'),
            'bound_text': "On Thursday, some party leaders said Mr Macron advocated a “no limits” "
                          "approach to counter the Russian president as part of his theory of "
                          "“strategic ambivalence” – keeping Moscow guessing."
        }

    def test_create_bound_mention(self):
        # Test creating a BoundMention and asserting all the fields
        bound_mention = BoundMention.objects.create(**self.bound_mention_data)

        self.assertEqual(bound_mention.article, self.article)
        self.assertEqual(bound_mention.entity, self.entity)
        self.assertEqual(bound_mention.bound_start, 1483)
        self.assertEqual(bound_mention.bound_end, 1671)
        self.assertEqual(bound_mention.avg_neutral, Decimal('0.00'))
        self.assertEqual(bound_mention.avg_positive, Decimal('0.75'))
        self.assertEqual(bound_mention.avg_negative, Decimal('0.00'))
        self.assertEqual(bound_mention.bound_text,
                         "On Thursday, some party leaders said Mr Macron advocated a “no limits” "
                         "approach to counter the Russian president as part of his theory of "
                         "“strategic ambivalence” – keeping Moscow guessing.")

    def test_cascade_delete_entity(self):
        # Entity delete then verify bound_mention is deleted too.
        bound_mention = BoundMention.objects.create(**self.bound_mention_data)
        self.entity.delete()
        # Ensure the related BoundMention instance is deleted
        self.assertFalse(BoundMention.objects.filter(pk=bound_mention.pk).exists())

    def test_cascade_delete_article(self):
        # Article delete then verify bound_mention is deleted too.
        bound_mention = BoundMention.objects.create(**self.bound_mention_data)
        self.article.delete()
        self.assertFalse(BoundMention.objects.filter(pk=bound_mention.pk).exists())


class OverallSentimentTest(TestCase):

    def setUp(self):
        self.article = Article.objects.create(
            headline="Emmanuel Macron warns West of threat from Russian breakthrough in Ukraine",
            url="https://exampleArticle.com"
        )
        self.entity = Entity.objects.create(
            source_article=self.article,
            name="Emmanuel Macron"
        )

        self.overall_sentiment_data = {
            'article': self.article,
            'entity': self.entity,
            'num_bound': 10,
            'linear_neutral': Decimal('0.10'),
            'linear_positive': Decimal('0.70'),
            'linear_negative': Decimal('0.20'),
            'exp_neutral': Decimal('0.10'),
            'exp_positive': Decimal('0.70'),
            'exp_negative': Decimal('0.20')
        }

    def test_create_overall_sentiment(self):
        # Test creating an OverallSentiment and asserting all fields
        overall_sentiment = OverallSentiment.objects.create(**self.overall_sentiment_data)

        self.assertEqual(overall_sentiment.article, self.article)
        self.assertEqual(overall_sentiment.entity, self.entity)
        self.assertEqual(overall_sentiment.num_bound, 10)
        self.assertEqual(overall_sentiment.linear_neutral, Decimal('0.10'))
        self.assertEqual(overall_sentiment.linear_positive, Decimal('0.70'))
        self.assertEqual(overall_sentiment.linear_negative, Decimal('0.20'))
        self.assertEqual(overall_sentiment.exp_neutral, Decimal('0.10'))
        self.assertEqual(overall_sentiment.exp_positive, Decimal('0.70'))
        self.assertEqual(overall_sentiment.exp_negative, Decimal('0.20'))

    def test_cascade_delete_entity(self):
        # Entity delete then verify overall_sentiment is deleted too.
        overall_sentiment = OverallSentiment.objects.create(**self.overall_sentiment_data)
        self.entity.delete()
        # Ensure the related OverallSentiment instance is deleted
        self.assertFalse(OverallSentiment.objects.filter(pk=overall_sentiment.pk).exists())

    def test_cascade_delete_article(self):
        # Article delete then verify overall_sentiment is deleted too.
        overall_sentiment = OverallSentiment.objects.create(**self.overall_sentiment_data)
        self.article.delete()
        self.assertFalse(OverallSentiment.objects.filter(pk=overall_sentiment.pk).exists())

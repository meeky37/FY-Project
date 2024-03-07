import unittest
from datetime import datetime
from decimal import Decimal
from unittest import mock
from unittest.mock import Mock, patch

from django.test import TestCase
from django.utils import timezone

from nlp_processor.models import ArticleStatistics, SimilarArticlePair, ProcessedFile, BoundError
from profiles_app.models import Article as ArticleModel, Entity, BoundMention, OverallSentiment
from nlp_processor.article_processor import Article
from datetime import datetime

from nlp_processor.article_update import calculate_all_percentage_differences
from nlp_processor.sentiment_resolver import (scaling, average_array, round_array_to_1dp,
                                              percentage_contribution)
from nlp_processor.sentiment_resolver import SentimentAnalyser

from nlp_processor.utils import DatabaseUtils

from nlp_processor.article_utils import *
from spacy.tokens import Token

"""
The following tests focus on the success of nlp_processor models interacting with profiles app 
models, object creation, and that of statistics calculation, percentage difference and similarity 
detection in the NLP pipeline"""


class ProcessedFileTest(TestCase):
    def setUp(self):
        self.processed_file_data = {
            "search_term": "keir starmer",
            "file_name": "keir+starmer_no_dup_articles_loop_11-12-2023-20:56.json",
            "media_path": "api_articles/keir+starmer",
            "nlp_applied": False,
        }
        self.processed_file = ProcessedFile.objects.create(**self.processed_file_data)

    def test_processed_file_creation(self):
        # Test the ProcessedFile object was created properly.
        self.assertTrue(isinstance(self.processed_file, ProcessedFile))
        self.assertEqual(self.processed_file.search_term, self.processed_file_data["search_term"])
        self.assertEqual(self.processed_file.file_name, self.processed_file_data["file_name"])
        self.assertEqual(self.processed_file.media_path, self.processed_file_data["media_path"])
        self.assertFalse(self.processed_file.nlp_applied)


class ArticleModelTest(TestCase):
    def setUp(self):
        naive_datetime = datetime.strptime("Dec. 11, 2023", "%b. %d, %Y")
        publication_date = timezone.make_aware(naive_datetime)
        self.article_1_data = {
            "headline": "Eat Out To Help Out ‘a mistake', says son whose father died with Covid-19",
            "url": "https://www.irishnews.com/news/uknews/2023/12/11/news/eat_out_to_help_out_a_mistake_says_son_whose_father_died_with_covid-19-3841086/",
            "image_url": "https://www.irishnews.com/resizer/v2/2MA3VA3ZPBPJHPF26ETAK5BLBU.jpg?smart=true&auth=cb38d4fd0baddad649316411ca4f82b60ea0957801edec0adc8267240c5ab470&width=1200&height=630",
            "publication_date": publication_date,
            "author": "Max McLean; Hannah Cottrell; PA",
            "site_name": "The Irish News",
            "processed": True,
            "similar_rejection": False,
        }
        self.article_1 = ArticleModel.objects.create(**self.article_1_data)

        # Create an instance of ArticleStatistics associated with article_1
        ArticleStatistics.objects.create(
            article=self.article_1,
            fuzzy_hash="96:12HDzrYGnhcA+bfWRgCOchuVMwnoTJdzn8GU:0HDpwSRccgXUJdzn8GU",
            word_count=694,
            terms_count=264,
            vocd=91.01118535891062,
            yulek=112.75614366729678,
            simpsond=0.011295258294197849,
            the_count=34,
            and_count=11,
            is_count=0,
            of_count=7,
            in_count=14,
            to_count=19,
            it_count=9,
            that_count=11,
            with_count=8
        )

        naive_datetime = datetime.strptime("Dec. 11, 2023", "%b. %d, %Y")
        publication_date = timezone.make_aware(naive_datetime)
        self.article_2_data = {
            "headline": "Eat Out To Help Out ‘a mistake’, says son whose father died with Covid-19",
            "url": "https://www.andoveradvertiser.co.uk/news/national/23983163.eat-help-a-mistake-says-son-whose-father-died-covid-19/",
            "image_url": "https://www.andoveradvertiser.co.uk/resources/images/17538776/?type=og-image",
            "publication_date": publication_date,
            "author": "PA News Agency",
            "site_name": "Andover Advertiser",
            "processed": True,
            "similar_rejection": False,  # In December, similar rejection wasn't in the pipeline.
        }
        self.article_2 = ArticleModel.objects.create(**self.article_2_data)

        # Create an instance of ArticleStatistics associated with article_2
        ArticleStatistics.objects.create(
            article=self.article_2,
            fuzzy_hash="96:12HDzrYGnhcA+bfWRgCOchuVMwnoTJdzn8GJFU+t:0HDpwSRccgXUJdzn8G35",
            word_count=768,
            terms_count=296,
            vocd=99.02204350574443,
            yulek=104.59665907951083,
            simpsond=0.010475932884479778,
            the_count=36,
            and_count=14,
            is_count=2,
            of_count=8,
            in_count=14,
            to_count=21,
            it_count=10,
            that_count=13,
            with_count=9
        )

    def test_article_creation(self):
        # Test the article object is created properly.
        self.assertTrue(isinstance(self.article_1, ArticleModel))
        self.assertEqual(self.article_1.headline, self.article_1_data["headline"])
        self.assertEqual(self.article_1.url, self.article_1_data["url"])
        self.assertEqual(self.article_1.image_url, self.article_1_data["image_url"])
        self.assertEqual(self.article_1.publication_date, self.article_1_data["publication_date"])
        self.assertEqual(self.article_1.author, self.article_1_data["author"])
        self.assertEqual(self.article_1.site_name, self.article_1_data["site_name"])
        self.assertTrue(self.article_1.processed)
        self.assertFalse(self.article_1.similar_rejection)


class ArticleClass_ModelTest(TestCase):
    def setUp(self):
        naive_datetime = datetime.strptime("Dec. 11, 2023", "%b. %d, %Y")
        publication_date = timezone.make_aware(naive_datetime)
        self.article_1_data = {
            "headline": "Eat Out To Help Out ‘a mistake', says son whose father died with Covid-19",
            "url": "https://www.irishnews.com/news/uknews/2023/12/11/news/eat_out_to_help_out_a_mistake_says_son_whose_father_died_with_covid-19-3841086/",
            "image_url": "https://www.irishnews.com/resizer/v2/2MA3VA3ZPBPJHPF26ETAK5BLBU.jpg?smart=true&auth=cb38d4fd0baddad649316411ca4f82b60ea0957801edec0adc8267240c5ab470&width=1200&height=630",
            "publication_date": publication_date,
            "author": "Max McLean; Hannah Cottrell; PA",
            "site_name": "The Irish News",
            "processed": True,
            "similar_rejection": False,
        }
        self.article_1 = ArticleModel.objects.create(**self.article_1_data)

        # Create an instance of ArticleStatistics associated with article_1
        ArticleStatistics.objects.create(
            article=self.article_1,
            fuzzy_hash="96:12HDzrYGnhcA+bfWRgCOchuVMwnoTJdzn8GU:0HDpwSRccgXUJdzn8GU",
            word_count=694,
            terms_count=264,
            vocd=91.01118535891062,
            yulek=112.75614366729678,
            simpsond=0.011295258294197849,
            the_count=34,
            and_count=11,
            is_count=0,
            of_count=7,
            in_count=14,
            to_count=19,
            it_count=9,
            that_count=11,
            with_count=8
        )

        # Now we try to add similar article and will see if it is detected as similar later
        naive_datetime = datetime.strptime("2023-12-11", "%Y-%m-%d")
        publication_date = timezone.make_aware(naive_datetime)
        linguistic_stats = {
            "fuzzy_hash": "96:12HDzrYGnhcA+bfWRgCOchuVMwnoTJdzn8GJFU+t:0HDpwSRccgXUJdzn8G35",
            "word_count": 768,
            "terms_count": 296,
            "vocd": 99.02204350574443,
            "yulek": 104.59665907951083,
            "simpsond": 0.010475932884479778,
            "the_count": 36,
            "and_count": 14,
            "is_count": 2,
            "of_count": 8,
            "in_count": 14,
            "it_count": 10,
            "that_count": 13,
            "to_count": 21,
            "with_count": 9,
        }

        self.processed_file_data = {
            "search_term": "keir starmer",
            "file_name": "keir+starmer_no_dup_articles_loop_11-12-2023-20:56.json",
            "media_path": "api_articles/keir+starmer",
            "nlp_applied": False,
        }
        self.processed_file = ProcessedFile.objects.create(**self.processed_file_data)

        # def __init__(self, url, headline, text_body, NER, date, author, site_name, source_file):
        self.article_instance = Article(
            url="https://www.andoveradvertiser.co.uk/news/national/23983163.eat-help-a-mistake-says-son-whose-father-died-covid-19/",
            headline="Eat Out To Help Out ‘a mistake’, says son whose father died with Covid-19",
            text_body=None,
            NER=None,
            date=publication_date,
            author="PA News Agency",
            site_name="Andover Advertiser",
            source_file=self.processed_file
        )

        self.article_instance.image_url = \
            "https://www.andoveradvertiser.co.uk/resources/images/17538776/?type=og-image"
        self.article_instance.linguistic_stats = linguistic_stats

    def test_save_to_database_method(self):
        """Tests if article_processor.py correctly saves the article instance to the database and
         check its associated ArticleStatistics were stored correctly"""
        # Call the save_to_database method
        self.article_instance.save_to_database()

        # Assertions to ensure the article was saved correctly
        saved_article = ArticleModel.objects.get(url=self.article_instance.url)
        self.assertIsNotNone(saved_article)
        self.assertEqual(saved_article.headline, self.article_instance.headline)
        self.assertEqual(saved_article.image_url, self.article_instance.image_url)
        self.assertEqual(saved_article.publication_date, self.article_instance.publication_date)
        self.assertEqual(saved_article.author, self.article_instance.author)
        self.assertEqual(saved_article.site_name, self.article_instance.site_name)
        # Ensure the processed and similar_rejection flags are set as False to begin with
        self.assertFalse(saved_article.processed)
        self.assertFalse(saved_article.similar_rejection)

        # Assertions to ensure the article statistics were saved correctly
        saved_stats = ArticleStatistics.objects.get(article=saved_article)
        self.assertIsNotNone(saved_stats)
        self.assertEqual(saved_stats.fuzzy_hash,
                         self.article_instance.linguistic_stats["fuzzy_hash"])
        self.assertEqual(saved_stats.word_count,
                         self.article_instance.linguistic_stats["word_count"])
        self.assertEqual(saved_stats.terms_count,
                         self.article_instance.linguistic_stats["terms_count"])
        self.assertEqual(saved_stats.vocd, self.article_instance.linguistic_stats["vocd"])
        self.assertEqual(saved_stats.yulek, self.article_instance.linguistic_stats["yulek"])
        self.assertEqual(saved_stats.simpsond, self.article_instance.linguistic_stats["simpsond"])
        self.assertEqual(saved_stats.the_count, self.article_instance.linguistic_stats["the_count"])
        self.assertEqual(saved_stats.and_count, self.article_instance.linguistic_stats["and_count"])
        self.assertEqual(saved_stats.is_count, self.article_instance.linguistic_stats["is_count"])
        self.assertEqual(saved_stats.of_count, self.article_instance.linguistic_stats["of_count"])
        self.assertEqual(saved_stats.in_count, self.article_instance.linguistic_stats["in_count"])
        self.assertEqual(saved_stats.to_count, self.article_instance.linguistic_stats["to_count"])
        self.assertEqual(saved_stats.it_count, self.article_instance.linguistic_stats["it_count"])
        self.assertEqual(saved_stats.that_count,
                         self.article_instance.linguistic_stats["that_count"])
        self.assertEqual(saved_stats.with_count,
                         self.article_instance.linguistic_stats["with_count"])

        # Unique identifier check
        self.assertIsNotNone(self.article_instance.database_id)

    def test_article_similarity(self):
        """Checks the functionality of the similarity check method to determine if two articles
        are similar."""
        self.article_instance.save_to_database()
        is_similar = self.article_instance.check_similarity()
        self.assertTrue(is_similar)


class SimilarArticlesTest(TestCase):
    """Here we use Tales of Two Cities by Charles Dickens in original and a modified variant to
    test the linguistics values, their difference calculations and the expected similarity=True
    outcome"""

    def setUp(self):
        current_date = timezone.now()
        publication_date = timezone.make_aware(
            datetime(current_date.year, current_date.month, current_date.day))

        self.processed_file_data = {
            "search_term": "test articles",
            "file_name": "test+articles_no_dup_articles_loop_11-12-2023-20:56.json",
            "media_path": "api_articles/test+articles",
            "nlp_applied": False,
        }
        self.processed_file = ProcessedFile.objects.create(**self.processed_file_data)

        text_body = ("It was the best of times, it was the worst of times, it was the age of "
                     "wisdom, it was the age of foolishness, it was the epoch of belief, "
                     "it was the epoch of incredulity, it was the season of Light, it was the "
                     "season of Darkness, it was the spring of hope, it was the winter of "
                     "despair, we had everything before us, we had nothing before us,  we were "
                     "all going direct to Heaven, we were all going direct the other way – in "
                     "short the period was so far like the present period, that some of its "
                     "noisiest authorities insisted on its being received, for good or for evil, "
                     "in the superlative degree of comparison only.")

        self.article_instance_1 = Article(
            url="https://classic-literature.fandom.com/wiki/A_Tale_of_Two_Cities",
            headline="It was the best of times, it was the worst of times",
            text_body=text_body,
            NER=None,
            date=publication_date,
            author="Charles Dickens",
            site_name="Dickens World",
            source_file=self.processed_file
        )

        text_body_2 = ("It was the worst of times, it was the best of times, it was the age of "
                       "wisdom, it was the age of foolishness, it was the epoch of belief, "
                       "it was the epoch of incredulity, it was the season of Light, it was the "
                       "season of Darkness, it was the spring of hope, it was the winter of "
                       "despair, we had everything before us, we had nothing before us,  we were "
                       "all going direct to Heaven, we were all going direct the other way – in "
                       "short the period was so far like the present period, that some of its "
                       "noisiest authorities insisted on its being received, for good or for evil, "
                       "in the superlative degree of comparison only.")

        self.article_instance_2 = Article(
            url="https://en.wikipedia.org/wiki/A_Tale_of_Two_Cities",
            headline="It was the worst of times, it was the best of times",
            text_body=text_body_2,
            NER=None,
            date=publication_date,
            author="Charles Dickens",
            site_name="Dickens World",
            source_file=self.processed_file
        )

    def test_article_similarity(self):
        """Checks article_update methods determine linguistic statistics that correctly lead to
            a True similarity flag"""
        self.article_instance_1.get_statistics()
        self.article_instance_1.save_to_database()
        self.article_instance_2.get_statistics()
        self.article_instance_2.save_to_database()
        is_similar = self.article_instance_2.check_similarity()
        self.assertTrue(is_similar)

    def test_statistics_calculation(self):
        """Confirms the accurate calc. + storage of linguistic and count-based statistics for
        article instances."""
        expected_statistics = {
            'word_count': 137,
            'terms_count': 58,
            'vocd': 24.12504499685439,
            'yulek': 392.6276392910105,
            'simpsond': 0.039595499216635806,
            'the_count': 14,
            'and_count': 0,
            'is_count': 0,
            'of_count': 12,
            'in_count': 2,
            'it_count': 9,
            'that_count': 1,
            'to_count': 1,
            'with_count': 0
        }

        # Calculate statistics using article_processor and article_update methods
        self.article_instance_1.get_statistics()
        self.article_instance_2.get_statistics()

        # Save Articles to the database (should create ArticleStatistics entries)
        self.article_instance_1.save_to_database()
        self.article_instance_2.save_to_database()

        # Retrieve ArticleStatistics objects associated with the articles
        stats_article_1 = ArticleStatistics.objects.get(article=self.article_instance_1.database_id)
        stats_article_2 = ArticleStatistics.objects.get(article=self.article_instance_2.database_id)

        # Compare the retrieved statistics with expected values
        self.assertEqual(stats_article_1.word_count, expected_statistics['word_count'])
        self.assertEqual(stats_article_1.terms_count, expected_statistics['terms_count'])
        self.assertAlmostEqual(stats_article_1.vocd, expected_statistics['vocd'], places=6)
        self.assertAlmostEqual(stats_article_1.yulek, expected_statistics['yulek'], places=6)
        self.assertAlmostEqual(stats_article_1.simpsond, expected_statistics['simpsond'], places=6)
        self.assertEqual(stats_article_1.the_count, expected_statistics['the_count'])
        self.assertEqual(stats_article_1.and_count, expected_statistics['and_count'])
        self.assertEqual(stats_article_1.is_count, expected_statistics['is_count'])
        self.assertEqual(stats_article_1.of_count, expected_statistics['of_count'])
        self.assertEqual(stats_article_1.in_count, expected_statistics['in_count'])
        self.assertEqual(stats_article_1.it_count, expected_statistics['it_count'])
        self.assertEqual(stats_article_1.that_count, expected_statistics['that_count'])
        self.assertEqual(stats_article_1.to_count, expected_statistics['to_count'])
        self.assertEqual(stats_article_1.with_count, expected_statistics['with_count'])

        self.assertEqual(stats_article_2.word_count, expected_statistics['word_count'])
        self.assertEqual(stats_article_2.terms_count, expected_statistics['terms_count'])
        self.assertAlmostEqual(stats_article_2.vocd, expected_statistics['vocd'], places=6)
        self.assertAlmostEqual(stats_article_2.yulek, expected_statistics['yulek'], places=6)
        self.assertAlmostEqual(stats_article_2.simpsond, expected_statistics['simpsond'], places=6)
        self.assertEqual(stats_article_2.the_count, expected_statistics['the_count'])
        self.assertEqual(stats_article_2.and_count, expected_statistics['and_count'])
        self.assertEqual(stats_article_2.is_count, expected_statistics['is_count'])
        self.assertEqual(stats_article_2.of_count, expected_statistics['of_count'])
        self.assertEqual(stats_article_2.in_count, expected_statistics['in_count'])
        self.assertEqual(stats_article_2.it_count, expected_statistics['it_count'])
        self.assertEqual(stats_article_2.that_count, expected_statistics['that_count'])
        self.assertEqual(stats_article_2.to_count, expected_statistics['to_count'])
        self.assertEqual(stats_article_2.with_count, expected_statistics['with_count'])

    #

    def test_percentage_difference_calculation(self):
        """Tests the calculation of percentage differences in linguistic statistics
        between similar articles, including a custom summary statistic avg_count that ignores
        extreme % differences when calculating the avg of % differences."""
        self.article_instance_1.get_statistics()
        self.article_instance_1.save_to_database()
        self.article_instance_2.get_statistics()
        self.article_instance_2.save_to_database()

        stats_article_1 = ArticleStatistics.objects.get(article=self.article_instance_1.database_id)
        stats_article_2 = ArticleStatistics.objects.get(article=self.article_instance_2.database_id)

        similarity_score = 96

        pair = SimilarArticlePair(article1=stats_article_1,
                                  article2=stats_article_2,
                                  hash_similarity_score=similarity_score)
        pair.save()

        calculate_all_percentage_differences(pair)
        saved_pair = SimilarArticlePair.objects.get(pk=pair.id)

        # Assert the calculated differences
        self.assertEqual(saved_pair.words_diff, 0.0)
        self.assertEqual(saved_pair.terms_diff, 0.0)
        self.assertEqual(saved_pair.vocd_diff, 0.0)
        self.assertEqual(saved_pair.yulek_diff, 0.0)
        self.assertEqual(saved_pair.simpsond_diff, 0.0)
        self.assertEqual(saved_pair.the_diff, 0.0)
        self.assertEqual(saved_pair.and_diff, 100)
        self.assertEqual(saved_pair.is_diff, 100)
        self.assertEqual(saved_pair.of_diff, 0.0)
        self.assertEqual(saved_pair.in_diff, 0.0)
        self.assertEqual(saved_pair.to_diff, 0.0)
        self.assertEqual(saved_pair.it_diff, 0.0)
        self.assertEqual(saved_pair.that_diff, 0.0)
        self.assertEqual(saved_pair.with_diff, 100)

        # Tests method declared within the SimilarArticlePair model (ignore > 50 diff tested here)
        self.assertEqual(saved_pair.avg_count_diff, 0.0)


class NoSimilarityTest(TestCase):
    """Here we use Tales of Two Cities by Charles Dickens and a completely unrelated real news
    article to test the linguistics values, their difference calculations and the expected
    similarity=False outcome"""

    def setUp(self):
        naive_datetime = datetime.strptime("Dec. 11, 2023", "%b. %d, %Y")
        publication_date = timezone.make_aware(naive_datetime)
        self.article_1_data = {
            "headline": "Eat Out To Help Out ‘a mistake', says son whose father died with Covid-19",
            "url": "https://www.irishnews.com/news/uknews/2023/12/11/news/eat_out_to_help_out_a_mistake_says_son_whose_father_died_with_covid-19-3841086/",
            "image_url": "https://www.irishnews.com/resizer/v2/2MA3VA3ZPBPJHPF26ETAK5BLBU.jpg?smart=true&auth=cb38d4fd0baddad649316411ca4f82b60ea0957801edec0adc8267240c5ab470&width=1200&height=630",
            "publication_date": publication_date,
            "author": "Max McLean; Hannah Cottrell; PA",
            "site_name": "The Irish News",
            "processed": True,
            "similar_rejection": False,
        }
        self.article_1 = ArticleModel.objects.create(**self.article_1_data)

        # Create an instance of ArticleStatistics associated with article_1
        ArticleStatistics.objects.create(
            article=self.article_1,
            fuzzy_hash="96:12HDzrYGnhcA+bfWRgCOchuVMwnoTJdzn8GU:0HDpwSRccgXUJdzn8GU",
            word_count=694,
            terms_count=264,
            vocd=91.01118535891062,
            yulek=112.75614366729678,
            simpsond=0.011295258294197849,
            the_count=34,
            and_count=11,
            is_count=0,
            of_count=7,
            in_count=14,
            to_count=19,
            it_count=9,
            that_count=11,
            with_count=8
        )

        current_date = timezone.now()
        publication_date = timezone.make_aware(
            datetime(current_date.year, current_date.month, current_date.day))

        self.processed_file_data = {
            "search_term": "test articles",
            "file_name": "test+articles_no_dup_articles_loop_11-12-2023-20:56.json",
            "media_path": "api_articles/test+articles",
            "nlp_applied": False,
        }
        self.processed_file = ProcessedFile.objects.create(**self.processed_file_data)

        text_body = ("It was the best of times, it was the worst of times, it was the age of "
                     "wisdom, it was the age of foolishness, it was the epoch of belief, "
                     "it was the epoch of incredulity, it was the season of Light, it was the "
                     "season of Darkness, it was the spring of hope, it was the winter of "
                     "despair, we had everything before us, we had nothing before us,  we were "
                     "all going direct to Heaven, we were all going direct the other way – in "
                     "short the period was so far like the present period, that some of its "
                     "noisiest authorities insisted on its being received, for good or for evil, "
                     "in the superlative degree of comparison only.")

        self.article_instance_1 = Article(
            url="https://classic-literature.fandom.com/wiki/A_Tale_of_Two_Cities",
            headline="It was the best of times, it was the worst of times",
            text_body=text_body,
            NER=None,
            date=publication_date,
            author="Charles Dickens",
            site_name="Dickens World",
            source_file=self.processed_file
        )

    def test_article_similarity(self):
        """Checks article_update methods determine linguistic statistics, but this time the
        article text is nothing alike between the two stored articles and their related
        statistics"""
        self.article_instance_1.get_statistics()
        self.article_instance_1.save_to_database()
        is_similar = self.article_instance_1.check_similarity()
        self.assertFalse(is_similar)


"""Sentiment Resolver Specific Tests"""


class SentimentResolverHelper(TestCase):
    def setUp(self):
        self.avg_array_list = [[0.2, 0.5, 0.3]]
        self.avg_array_list_2 = [[0.1, 0.3, 0.6], [0.2, 0.8, 0.1]]
        self.k_exponential = 3

        # Probabilities for average_array method tests
        self.probabilities_mixed = [
            {'class_prob': 0.2, 'class_label': 'neutral'},
            {'class_prob': 0.3, 'class_label': 'positive'},
            {'class_prob': 0.5, 'class_label': 'negative'}
        ]
        self.probabilities_single = [{'class_prob': 0.5, 'class_label': 'positive'}]

        self.probabilities_positive_only = [
            {'class_prob': 0.5, 'class_label': 'positive'},
            {'class_prob': 0.1, 'class_label': 'positive'},
            {'class_prob': 0.8, 'class_label': 'positive'}
        ]

        # Array for round_array_to_1dp method tests
        self.array_to_round = [20.5555555555554, 30.322222221, 49.811111111111]
        self.array_1dp_100 = [20.1, 40.9, 39.0]
        self.array_large_adj = [20.0, 30.0, 49.0]
        self.array_similar_in = [33.333, 33.333, 33.334]

        # Elements for percentage_contribution method tests
        self.elements_even_distribution = [100, 100, 100]
        self.elements_single_dom = [0, 0, 300]
        self.elements_zero_sum = [0, 0, 0]
        self.elements_varied = [10, 20, 70]

    # scaling tests
    def test_scaling_linear(self):
        # Test linear scaling of sentiment scores.
        expected_output = [20.0, 50.0, 30.0]
        output = scaling(self.avg_array_list, linear=True)
        self.assertEqual(output, expected_output)

    def test_scaling_exponential(self):
        # Test exponential scaling with the default value of k.
        expected_output = [0.8, 12.5, 2.7]
        output = scaling(self.avg_array_list, linear=False)
        tolerance = 1e-5
        self.assertTrue(all(abs(a - b) < tolerance for a, b in zip(output, expected_output)))

    def test_scaling_exponential(self):
        # Ensure custom k values are properly applied in exponential scaling.
        expected_output = [4.0, 25.0, 9.0]
        output = scaling(self.avg_array_list, k=2, linear=False)
        tolerance = 1e-5
        self.assertTrue(all(abs(a - b) < tolerance for a, b in zip(output, expected_output)))

    def test_scaling_multiple_array(self):
        # Verify handling and correctly scale multiple sentiment score arrays.
        expected_output = [0.9, 53.9, 21.7]
        output = scaling(self.avg_array_list_2)
        tolerance = 1e-5
        self.assertTrue(all(abs(a - b) < tolerance for a, b in zip(output, expected_output)))

    # average_array tests
    def test_average_array_single(self):
        # Test with a single probability entry.
        expected_output = [0.0, 0.5, 0.0]
        output = average_array(self.probabilities_single)
        self.assertEqual(output, expected_output)

    def test_average_array_mixed_sentiments(self):
        # Test averaging with mixed sentiment labels.
        expected_output = [(0.2 / 3), (0.3 / 3), (0.5 / 3)]
        output = average_array(self.probabilities_mixed)
        self.assertEqual(output, expected_output)

    def test_average_array_positive_sentiments(self):
        # Test averaging when all entries have the same label
        expected_output = [0, (1.4 / 3), 0]
        output = average_array(self.probabilities_positive_only)
        self.assertEqual(output, expected_output)

    def test_average_array_empty_list(self):
        # Check the edge case of an empty probability list is handled gracefully
        expected_output = [0, 0, 0]
        output = average_array([])
        self.assertEqual(output, expected_output)

    # round_array_to_1dp tests

    def test_round_array_to_1dp_standard(self):
        # Test rounding array elements to one decimal place and sum to 100
        expected_output = [20.6, 30.3, 49.1]
        output = round_array_to_1dp(self.array_to_round)
        self.assertEqual(output, expected_output)

    def test_round_array_to_1dp_no_change_req(self):
        """Test rounding array elements to one decimal place and sum to 100 with an array that
        needs no changes"""
        expected_output = [20.1, 40.9, 39.0]
        output = round_array_to_1dp(self.array_1dp_100)
        self.assertEqual(output, expected_output)

    def test_round_array_to_1dp_large_adj(self):
        """Ensure correct adjustment when the last element requires significant change to ensure
        a 100% sum."""
        expected_output = [20.0, 30.0, 50.0]
        output = round_array_to_1dp(self.array_large_adj)
        self.assertEqual(output, expected_output)

    def test_round_array_to_1dp_similar_inputs(self):
        # Test when all elements are the (nearly-) same and need rounding.
        expected_output = [33.3, 33.3, 33.4]
        output = round_array_to_1dp(self.array_similar_in)
        self.assertEqual(output, expected_output)

    # percentage_contribution tests

    def test_percentage_contribution_even_distribution(self):
        # Test percentage contribution calculation with evenly distributed elements
        expected_output = [33.3, 33.3, 33.4]
        output = percentage_contribution(self.elements_even_distribution)
        self.assertEqual(output, expected_output)

    def test_percentage_contribution_single_dom(self):
        # Test percentage contribution calculation with evenly distributed elements
        expected_output = [0.0, 0.0, 100.0]
        output = percentage_contribution(self.elements_single_dom)
        self.assertEqual(output, expected_output)

    def test_percentage_contribution_zero_sum(self):
        # Stress test percentage contribution calculation with all zero entries
        expected_output = [0.0, 0.0, 0.0]
        output = percentage_contribution(self.elements_zero_sum)
        self.assertEqual(output, expected_output)

    def test_percentage_contribution_varied_values(self):
        # Test percentage contribution calculation with varied values i.e. typical input
        expected_output = [10.0, 20.0, 70.0]
        output = percentage_contribution(self.elements_varied)
        self.assertEqual(output, expected_output)



"""The following tests check methods in Database Utils in utils.py"""


class EntityDatabaseUtilsTests(TestCase):
    def setUp(self):
        self.article_1_data = {
            "headline": "Eat Out To Help Out ‘a mistake', says son whose father died with Covid-19",
            "url": "https://www.irishnews.com/news/uknews/2023/12/11/news/eat_out_to_help_out_a_mistake_says_son_whose_father_died_with_covid-19-3841086/",
            "image_url": "https://www.irishnews.com/resizer/v2/2MA3VA3ZPBPJHPF26ETAK5BLBU.jpg?smart=true&auth=cb38d4fd0baddad649316411ca4f82b60ea0957801edec0adc8267240c5ab470&width=1200&height=630",
            "publication_date": timezone.now(),
            "author": "Max McLean; Hannah Cottrell; PA",
            "site_name": "The Irish News",
            "processed": False,
            "similar_rejection": False,
        }
        self.article_1 = ArticleModel.objects.create(**self.article_1_data)

        self.article_2_data = {
            "headline": "Eat Out To Help Out ‘a mistake’, says son whose father died with Covid-19",
            "url": "https://www.andoveradvertiser.co.uk/news/national/23983163.eat-help-a-mistake-says-son-whose-father-died-covid-19/",
            "image_url": "https://www.andoveradvertiser.co.uk/resources/images/17538776/?type=og-image",
            "publication_date": timezone.now(),
            "author": "PA News Agency",
            "site_name": "Andover Advertiser",
            "processed": False,
            "similar_rejection": False,
        }
        self.article_2 = ArticleModel.objects.create(**self.article_2_data)

    def test_insert_new_entity(self):
        # Test inserting a new entity associated with an article.
        entity_name = "Rishi Sunak"
        source_article_id = self.article_1.id
        entity_id = DatabaseUtils.insert_entity(entity_name, source_article_id)
        self.assertIsNotNone(entity_id)
        self.assertTrue(Entity.objects.filter(id=entity_id).exists())
        entity = Entity.objects.get(id=entity_id)
        self.assertEqual(entity.name, entity_name)
        self.assertEqual(entity.source_article.id, source_article_id)

    #
    def test_prevent_duplicate_entity(self):
        # Ensure that inserting a duplicate entity name does not create a new entity.
        entity_name = "Rishi Sunak"
        source_article_id = self.article_1.id

        # Then many articles later we encounter the same entity_name
        source_article_id_2 = self.article_2.id

        # Insert the entity first time and then simulating an equivalent name mention later
        first_insert_id = DatabaseUtils.insert_entity(entity_name, source_article_id)
        second_insert_id = DatabaseUtils.insert_entity(entity_name, source_article_id_2)
        print(first_insert_id)
        print(second_insert_id)

        self.assertEqual(first_insert_id, second_insert_id)
        self.assertEqual(Entity.objects.filter(name=entity_name).count(), 1)

    def test_reject_insert_entity_without_article(self):
        """Test that attempting to insert an entity without associating it with an article is rejected.
           Else we open the door to first-time entity inserts with no source article id.
           Consistently insert entity should ALWAYS be called with a source article id!"""

        entity_name = "Dr Mark Lee"
        entity_id = DatabaseUtils.insert_entity(entity_name)
        self.assertIsNone(entity_id)


class BoundMentionTests(TestCase):
    def setUp(self):
        self.article_1_data = {
            "headline": "Eat Out To Help Out ‘a mistake', says son whose father died with Covid-19",
            "url": "https://www.irishnews.com/news/uknews/2023/12/11/news/eat_out_to_help_out_a_mistake_says_son_whose_father_died_with_covid-19-3841086/",
            "image_url": "https://www.irishnews.com/resizer/v2/2MA3VA3ZPBPJHPF26ETAK5BLBU.jpg?smart=true&auth=cb38d4fd0baddad649316411ca4f82b60ea0957801edec0adc8267240c5ab470&width=1200&height=630",
            "publication_date": timezone.now(),
            "author": "Max McLean; Hannah Cottrell; PA",
            "site_name": "The Irish News",
            "processed": False,
            "similar_rejection": False,
        }
        self.article = ArticleModel.objects.create(**self.article_1_data)

        self.entity_1_data = {
            "name": "Boris Johnson",
            "source_article_id": self.article.id,
            "type": None,
            "app_visible": True,
            "view_count": 0
        }
        self.entity = Entity.objects.create(**self.entity_1_data)

    def test_successful_insertion_of_bound_mention_data(self):
        # Test typical bound mention is correctly inserted
        entity_name = "Boris Johnson"
        article_id = self.article.id
        entity_db_id = self.entity.id
        scores = (0.0, 0.9, 0.0)
        text = ("The PM and Chancellor deliberately kept the deadly plan under wraps until the "
                "last possible moment")
        bounds_keys = (102, 200)

        DatabaseUtils.insert_bound_mention_data(entity_name, article_id, entity_db_id, scores, text,
                                                bounds_keys)

        self.assertEqual(BoundMention.objects.count(), 1)
        bound_mention = BoundMention.objects.first()
        self.assertEqual(bound_mention.entity.name, entity_name)
        self.assertEqual(bound_mention.article.id, article_id)
        self.assertEqual(bound_mention.bound_start, bounds_keys[0])
        self.assertEqual(bound_mention.bound_end, bounds_keys[1])

    def test_duplicate_rejection_bound_mention(self):
        # Test duplicate bound mention rejection
        entity_name = "Boris Johnson"
        article_id = self.article.id
        entity_db_id = self.entity.id
        scores = (0.0, 0.9, 0.0)
        text = ("The PM and Chancellor deliberately kept the deadly plan under wraps until the "
                "last possible moment")
        bounds_keys = (102, 200)

        DatabaseUtils.insert_bound_mention_data(entity_name, article_id, entity_db_id, scores,
                                                text,
                                                bounds_keys)

        DatabaseUtils.insert_bound_mention_data(entity_name, article_id, entity_db_id, scores,
                                                text,
                                                bounds_keys)

        self.assertEqual(BoundMention.objects.count(), 1)


class OverallSentimentDatabaseUtilsTests(TestCase):
    def setUp(self):
        self.article_1_data = {
            "headline": "Eat Out To Help Out ‘a mistake', says son whose father died with Covid-19",
            "url": "https://www.irishnews.com/news/uknews/2023/12/11/news/eat_out_to_help_out_a_mistake_says_son_whose_father_died_with_covid-19-3841086/",
            "image_url": "https://www.irishnews.com/resizer/v2/2MA3VA3ZPBPJHPF26ETAK5BLBU.jpg?smart=true&auth=cb38d4fd0baddad649316411ca4f82b60ea0957801edec0adc8267240c5ab470&width=1200&height=630",
            "publication_date": timezone.now(),
            "author": "Max McLean; Hannah Cottrell; PA",
            "site_name": "The Irish News",
            "processed": False,
            "similar_rejection": False,
        }
        self.article = ArticleModel.objects.create(**self.article_1_data)

        self.entity_1_data = {
            "name": "Boris Johnson",
            "source_article_id": self.article.id,
            "type": None,
            "app_visible": True,
            "view_count": 0
        }
        self.entity = Entity.objects.create(**self.entity_1_data)

    def test_successful_insertion_of_overall_sentiment(self):
        # Test that overall sentiment data is correctly inserted into the database
        article_id = self.article.id
        entity_id = self.entity.id
        num_bound = 5
        linear_scores = (Decimal('0.1'), Decimal('0.3'), Decimal('0.6'))
        exp_scores = (Decimal('0.05'), Decimal('0.25'), Decimal('0.7'))

        DatabaseUtils.insert_overall_sentiment(article_id, entity_id, num_bound,
                                               *linear_scores, *exp_scores)

        self.assertEqual(OverallSentiment.objects.count(), 1)
        overall_sentiment = OverallSentiment.objects.first()
        self.assertEqual(overall_sentiment.article.id, article_id)
        self.assertEqual(overall_sentiment.entity.id, entity_id)
        self.assertEqual(overall_sentiment.num_bound, num_bound)
        self.assertEqual((overall_sentiment.linear_neutral, overall_sentiment.linear_positive,
                          overall_sentiment.linear_negative), linear_scores)
        self.assertEqual((overall_sentiment.exp_neutral, overall_sentiment.exp_positive,
                          overall_sentiment.exp_negative), exp_scores)

    def test_prevent_duplicate_overall_sentiment_entries(self):
        """Checking that no duplicate OverallSentiment entries are created for identical
        article-entity pairs"""
        article_id = self.article.id
        entity_id = self.entity.id
        num_bound = 5
        linear_scores = (Decimal('0.1'), Decimal('0.3'), Decimal('0.6'))
        exp_scores = (Decimal('0.05'), Decimal('0.25'), Decimal('0.7'))

        # Insert 1
        DatabaseUtils.insert_overall_sentiment(article_id, entity_id, num_bound,
                                               *linear_scores, *exp_scores)
        # Insert again with exact same data
        DatabaseUtils.insert_overall_sentiment(article_id, entity_id, num_bound,
                                               *linear_scores, *exp_scores)

        # Verify that a duplicate entry was not created
        self.assertEqual(OverallSentiment.objects.count(), 1)

    def test_overall_sentiment_data_for_different_entities(self):
        """Verify that inserting the same overall sentiment outcomes except the entity differs is
        not prevented (rare but possible case)"""
        # Setup for a second entity
        entity_2 = Entity.objects.create(name="Test Entity 2", source_article=self.article)

        num_bound = 5

        linear_scores = (Decimal('0.4'), Decimal('0.2'), Decimal('0.2'))
        exp_scores = (Decimal('0.55'), Decimal('0.1'), Decimal('0.1'))

        # Insert overall sentiment for the 1st entity
        DatabaseUtils.insert_overall_sentiment(self.entity.id, self.article.id, num_bound,
                                               *linear_scores, *exp_scores)
        # Insert overall sentiment for the 2nd entity
        DatabaseUtils.insert_overall_sentiment(entity_2.id, self.article.id, num_bound,
                                               *linear_scores, *exp_scores)

        # Seeking two distinct overall sentiments
        self.assertEqual(OverallSentiment.objects.count(), 2)


"""The following tests check methods which help article_processor in creating bound mentions for 
evaluations from extracted/raw article text in utils.py"""


class ArticleUtilsExternalLinkTests(unittest.TestCase):
    def test_allowed_url(self):
        # Known URL that is allowed to be fetched
        url = "https://www.birmingham.ac.uk/schools/computer-science"
        self.assertTrue(can_fetch_url(url))

    def test_invalid_url(self):
        # Invalid URL that will raise an error"""
        url = "https://www.birmingham.ac.ukkkkkkk/schools/computer-science"
        self.assertFalse(can_fetch_url(url))

    # def test_disallowed_url(self):
    #     # Known URL that is not allowed to be fetched"""
    #     url = None # could be added if determined in pipeline runs
    #     self.assertFalse(can_fetch_url(url))

    def get_preview_image_url_timeout_check(self):
        url = ('https://www.itv.com/news/2024-03-06/donald-trumps-last-rival-nikki-'
               'haley-drops-out-of-presidential-race')  # Main content on itv tends to be video
        self.assertIsNone(get_preview_image_url(url))


class TestMergePositions(unittest.TestCase):
    def test_merge_same_entity_type(self):
        # Testing positions for same given entity are merged together correctly
        entities = {}

        entity1 = Mock(text="Kate Middleton", label_="PERSON", start_char=0, end_char=10)
        entity2 = Mock(text="Kate Middleton", label_="PERSON", start_char=11, end_char=20)

        entities = merge_positions(entities, entity1)
        entities = merge_positions(entities, entity2)
        # Check merged entities
        self.assertEqual(len(entities), 1)
        self.assertIn('kate middletonperson', entities)
        self.assertEqual(entities['kate middletonperson'],
                         ['Kate Middleton', [[0, 10], [11, 20]], 'PERSON'])

    #
    def test_no_merge_different_entity_type(self):
        # Testing positions for same given entity are NOT merged together
        entities = {}

        entity1 = Mock(text="Prince Harry", label_="PERSON", start_char=0, end_char=10)
        entity2 = Mock(text="Sussex Royal", label_="ORG", start_char=11, end_char=20)

        entities = merge_positions(entities, entity1)
        entities = merge_positions(entities, entity2)

        self.assertEqual(len(entities), 2)
        self.assertIn('prince harryperson', entities)
        self.assertIn('sussex royalorg', entities)
        self.assertEqual(entities['prince harryperson'], ['Prince Harry', [[0, 10]], 'PERSON'])
        self.assertEqual(entities['sussex royalorg'], ['Sussex Royal', [[11, 20]], 'ORG'])


class ClusterText(unittest.TestCase):
    def test_stopword_removal(self):
        # Providing cluster text with many stop words then tests if they were correctly removed
        cluster_text = ['I', 'saw', 'Saltburn', 'last', 'night,', 'and', 'it', 'was', 'his',
                        'favorite;', 'he', 'said', 'that', 'they', 'enjoyed', 'it', 'too,',
                        'but', 'this', 'is', 'not', 'the', 'one', 'she', 'wanted,', 'so',
                        'those', 'are', 'the', 'ones', 'we', 'will', 'watch', 'later,',
                        'with', 'a', 'bag', 'of', 'popcorn.']
        expected_result = ['saw', 'Saltburn', 'last', 'night,', 'and', 'was', 'favorite;', 'said',
                           'enjoyed', 'too,', 'but', 'is', 'not', 'one', 'wanted,', 'so', 'are',
                           'ones', 'we', 'will', 'watch', 'later,', 'with', 'bag', 'popcorn.']
        cleansed_text = cleanse_cluster_text(cluster_text)
        self.assertEqual(cleansed_text, expected_result)

    def test_no_stopwords(self):
        # Providing cluster text with no stop words then tests the input remains unmodified
        cluster_text = ['saw', 'Saltburn', 'last', 'night,', 'and', 'was', 'favorite;',
                        'said',
                        'enjoyed', 'too,', 'but', 'is', 'not', 'one', 'wanted,', 'so', 'are',
                        'ones', 'we', 'will', 'watch', 'later,', 'with', 'bag', 'popcorn.']
        expected_result = ['saw', 'Saltburn', 'last', 'night,', 'and', 'was', 'favorite;',
                           'said',
                           'enjoyed', 'too,', 'but', 'is', 'not', 'one', 'wanted,', 'so', 'are',
                           'ones', 'we', 'will', 'watch', 'later,', 'with', 'bag', 'popcorn.']
        cleansed_text = cleanse_cluster_text(cluster_text)
        self.assertEqual(cleansed_text, expected_result)

    def test_empty(self):
        # Checking empty cluster text input is well-behaved
        cluster_text = []
        expected_result = []
        cleansed_text = cleanse_cluster_text(cluster_text)
        self.assertEqual(cleansed_text, expected_result)


#
class TestRemoveTitles(unittest.TestCase):
    def test_remove_title_at_start(self):
        # Checking removing title at the start of the entity
        entity_with_title_at_start = "Sir Keir Starmer"
        expected_result = "Keir Starmer"
        result = remove_titles(entity_with_title_at_start)
        self.assertEqual(result, expected_result)

    def test_remove_title_at_end(self):
        # Checking removing title at the end of the entity
        entity_with_title_at_end = "Hugo Keith KC"
        expected_result = "Hugo Keith"
        result = remove_titles(entity_with_title_at_end)
        self.assertEqual(result, expected_result)

    def test_remove_title_both_ends(self):
        # Checking removing title both sides of the entity
        entity_with_title_at_end = "Mr Hugo Keith KC"
        expected_result = "Hugo Keith"
        result = remove_titles(entity_with_title_at_end)
        self.assertEqual(result, expected_result)

    def test_no_title(self):
        # Checking remove title at the start of the entity
        entity_without_title = "Sadiq Khan"
        expected_result = "Sadiq Khan"
        result = remove_titles(entity_without_title)
        self.assertEqual(result, expected_result)


class TestInsertIntervals(unittest.TestCase):
    def test_insert_new_values(self):
        # Check new values correctly split the bounds supporting custom tokenisation
        initial_list = [(0, 50), (51, 100), (101, 150)]
        new_values = [75, 120]
        expected_result = [(0, 50), (51, 75), (76, 100), (101, 120), (121, 150)]
        result = insert_intervals(initial_list, new_values)
        self.assertEqual(result, expected_result)

    def test_no_new_values(self):
        # Check initial list is returned without no new values
        initial_list = [(0, 50), (51, 100), (101, 150)]
        new_values = []
        result = insert_intervals(initial_list, new_values)
        self.assertEqual(result, initial_list)

    def test_insert_values_outside_intervals(self):
        # Check new values outside of initial list don't throw an error that impacts result
        initial_list = [(0, 50), (51, 100), (101, 150)]
        new_values = [-10, 200]
        result = insert_intervals(initial_list, new_values)
        self.assertEqual(result, initial_list)


class TestIsSubstring(unittest.TestCase):
    def test_entity1_substring_of_entity2(self):
        # Test when entity1 is a substring of entity2
        entity1 = "Joe"
        entity2 = "Joe Biden"
        self.assertTrue(is_substring(entity1, entity2))

    def test_entity2_substring_of_entity1(self):
        # Test when entity2 is a substring of entity1
        entity1 = "Lee Anderson"
        entity2 = "Lee"
        self.assertTrue(is_substring(entity1, entity2))

    def test_entities_equal(self):
        # Test when entity1 and entity2 are equal
        entity1 = "Valdimar Putin"
        entity2 = "Valdimar Putin"
        self.assertTrue(is_substring(entity1, entity2))

    def test_no_substring(self):
        # Test when neither entity is a substring of the other
        entity1 = "Jeremy Hunt"
        entity2 = "Jeremy Clarkson"
        self.assertFalse(is_substring(entity1, entity2))

    def test_case_insensitivity(self):
        # Test case insensitivity
        entity1 = "farage"
        entity2 = "FARAGE"
        self.assertTrue(is_substring(entity1, entity2))


class TestCombineEntities(unittest.TestCase):
    def test_combine_entities_success(self):
        """Test providing two entities and a cluster text where they are seen together in context
        are combined"""
        entities = ["David", "Cameron"]
        cluster_text = ("David Cameron is a British politician who has served as Foreign Secretary "
                        "since 2023.")
        combined_entity = combine_entities(entities, cluster_text)
        self.assertEqual(combined_entity, "David Cameron")

    def test_combine_entities_no_combo(self):
        """Test providing two entities and a cluster text where they are not seen together in
        context are not combined"""
        entities = ["James", "Gray"]
        cluster_text = ("James Cleverly was appointed Secretary of State for the Home Department "
                        "on 13 November 2023.")
        combined_entity = combine_entities(entities, cluster_text)
        self.assertEqual(combined_entity, None)

    #
    def test_case_insensitivity(self):
        """
        Test that the method is set up to be case-sensitive
        NB: There is an argument to make this method case-insensitive, but news articles
        *should* be well written.
        """
        entities = ["Joe", "Bidden"]
        cluster_text = "joe bidden confuses Gaza with Ukraine in airdrop announcement."
        combined_entity = combine_entities(entities, cluster_text)
        self.assertIsNone(combined_entity)


class TestUpdateEntityName(unittest.TestCase):
    def test_update_entity_name(self):
        # Test updating the entity name when it is a substring of a two-word cluster text entry
        entry = {
            'Entity Name': 'Johnson',
            'Cluster Info': {'Cluster Text': ['Boris Johnson']}
        }
        updated_entry = update_entity_name(entry)
        self.assertEqual(updated_entry['Entity Name'], 'Boris Johnson')

    def test_no_update_needed(self):
        # Test when the entity name does not need updating
        entry = {
            'Entity Name': 'Johnson',
            'Cluster Info': {'Cluster Text': ['Boris']}
        }
        updated_entry = update_entity_name(entry)
        self.assertEqual(updated_entry['Entity Name'], 'Johnson')

    def test_entity_name_as_substring_of_longer_cluster_text(self):
        # Test when the entity name is a substring of a longer cluster text entry
        entry = {
            'Entity Name': 'Johnson',
            'Cluster Info': {'Cluster Text': ['Boris Johnson is a politician']}
        }
        updated_entry = update_entity_name(entry)
        self.assertEqual(updated_entry['Entity Name'], 'Johnson')

    def test_entity_name_with_space_before_apostrophe(self):
        """Test when there is a space between 'e' and apostrophe in the entity name (seen examples
          of this in articles)"""
        entry = {
            'Entity Name': "Megan Markle '",
            'Cluster Info': {'Cluster Text': ["Megan Markle is a Duchess"]}
        }
        updated_entry = update_entity_name(entry)
        self.assertEqual(updated_entry['Entity Name'], "Megan Markle '")

    def test_case_insensitivity(self):
        """
        Test that the method is set up to be case-sensitive
        NB: There is an argument to make this method case-insensitive, but news articles
        *should* be well written.
        """
        entry = {
            'Entity Name': 'johnson',
            'Cluster Info': {'Cluster Text': ['Boris Johnson']}
        }
        updated_entry = update_entity_name(entry)
        self.assertNotEqual(updated_entry['Entity Name'], 'Boris Johnson')


class TestCleanUpSubstrings(unittest.TestCase):
    def test_no_substrings(self):
        """Test when there are no substrings within each cluster ID but there are substrings
           across them so changes shouldn't be made but could be
           if the method isn't well sorted"""
        clustered_entities = [
            {'Entity Name': 'Nicola Sturgeon', 'Cluster Info': {'Cluster ID': 1}},
            {'Entity Name': 'Nicola', 'Cluster Info': {'Cluster ID': 2}}
        ]
        cleaned_entities = clean_up_substrings_revised(clustered_entities)
        self.assertEqual(len(cleaned_entities), 2)
        self.assertListEqual(cleaned_entities, clustered_entities)

    def test_single_substring(self):
        # Test when there is only one substring within each cluster ID
        clustered_entities = [
            {'Entity Name': 'Donald', 'Cluster Info': {'Cluster ID': 1}},
            {'Entity Name': 'Donald Trump', 'Cluster Info': {'Cluster ID': 1}},
            {'Entity Name': 'Joe', 'Cluster Info': {'Cluster ID': 2}},
            {'Entity Name': 'Joe Bidden', 'Cluster Info': {'Cluster ID': 2}}
        ]
        cleaned_entities = clean_up_substrings_revised(clustered_entities)
        self.assertEqual(len(cleaned_entities), 2)
        self.assertIn({'Entity Name': 'Donald Trump', 'Cluster Info': {'Cluster ID': 1}},
                      cleaned_entities)
        self.assertIn({'Entity Name': 'Joe Bidden', 'Cluster Info': {'Cluster ID': 2}},
                      cleaned_entities)

    #
    def test_multiple_substrings(self):
        # Test when there are multiple substrings within each cluster ID
        clustered_entities = [
            {'Entity Name': 'Rishi', 'Cluster Info': {'Cluster ID': 1}},
            {'Entity Name': 'Rishi Sunak', 'Cluster Info': {'Cluster ID': 1}},
            {'Entity Name': 'Sunak', 'Cluster Info': {'Cluster ID': 1}},
            {'Entity Name': 'Kate', 'Cluster Info': {'Cluster ID': 2}},
            {'Entity Name': 'Kate Middleton', 'Cluster Info': {'Cluster ID': 2}},
            {'Entity Name': 'Middleton', 'Cluster Info': {'Cluster ID': 2}}
        ]
        cleaned_entities = clean_up_substrings_revised(clustered_entities)
        self.assertEqual(len(cleaned_entities), 2)
        self.assertIn({'Entity Name': 'Rishi Sunak', 'Cluster Info': {'Cluster ID': 1}},
                      cleaned_entities)
        self.assertIn({'Entity Name': 'Kate Middleton', 'Cluster Info': {'Cluster ID': 2}},
                      cleaned_entities)

    def test_empty_input(self):
        # Test when the input list is empty
        clustered_entities = []
        cleaned_entities = clean_up_substrings_revised(clustered_entities)
        self.assertEqual(len(cleaned_entities), 0)


class TestCreateEntityEntry(unittest.TestCase):

    def setUp(self):
        self.entity_creator = create_entity_entry

    def test_personA_basic(self):
        self.assertEqual(
            self.entity_creator("personA", [[11664, 11669]], "People", 1),
            {'Entity Name': 'personA', 'Positions': [[11664, 11669]], 'Label': 'People',
             'Num Positions': 1, 'Cluster Info': []}
        )

    def test_personB_empty_label(self):
        self.assertEqual(
            self.entity_creator("personB",
                                [[12301, 12306], [14453, 14458], [15005, 15010], [15286, 15291]],
                                "", 4),
            {'Entity Name': 'personB',
             'Positions': [[12301, 12306], [14453, 14458], [15005, 15010], [15286, 15291]],
             'Label': '', 'Num Positions': 4, 'Cluster Info': []}
        )

    def test_personC_zero_positions(self):
        self.assertEqual(
            self.entity_creator("personC", [], "People", 0),
            {'Entity Name': 'personC', 'Positions': [], 'Label': 'People', 'Num Positions': 0,
             'Cluster Info': []}
        )

    def test_personD_negative_positions(self):
        self.assertEqual(
            self.entity_creator("personD", [[-123, -120]], "People", 1),
            {'Entity Name': 'personD', 'Positions': [[-123, -120]], 'Label': 'People',
             'Num Positions': 1, 'Cluster Info': []}
        )


"""The following integration tests check more complex methods in the NLP pipeline in
article_processor.py and sentiment_resolver.py"""


class AverageSentimentResultsDBCheck(TestCase):

    def setUp(self):
        naive_datetime = datetime.strptime("Dec. 11, 2023", "%b. %d, %Y")
        publication_date = timezone.make_aware(naive_datetime)
        self.article_1_data = {
            "headline": "Eat Out To Help Out ‘a mistake', says son whose father died with Covid-19",
            "url": "https://www.irishnews.com/news/uknews/2023/12/11/news/eat_out_to_help_out_a_mistake_says_son_whose_father_died_with_covid-19-3841086/",
            "image_url": "https://www.irishnews.com/resizer/v2/2MA3VA3ZPBPJHPF26ETAK5BLBU.jpg?smart=true&auth=cb38d4fd0baddad649316411ca4f82b60ea0957801edec0adc8267240c5ab470&width=1200&height=630",
            "publication_date": publication_date,
            "author": "Max McLean; Hannah Cottrell; PA",
            "site_name": "The Irish News",
            "processed": False,
            "similar_rejection": False,
        }
        self.article_1 = ArticleModel.objects.create(**self.article_1_data)

        self.bounds_sentiment = {(0, 167): {'Keir Starmer': {1: [{'class_id': 0, 'class_label':
            'negative', 'class_prob': 0.9354697465896606}]},
                                            'Tory': {2: [{'class_id': 1, 'class_label': 'neutral',
                                                          'class_prob':
                                                              0.6213993430137634}]}},
                                 (168, 315): {
                                     'Keir Starmer': {1: [{'class_id': 0, 'class_label': 'negative',
                                                           'class_prob': 0.8984778523445129}]},
                                     'Lindsay Hoyle': {3: [{'class_id': 1, 'class_label': 'neutral',
                                                            'class_prob': 0.74396151304245}]},
                                     'Tory': {2: [
                                         {'class_id': 0, 'class_label': 'negative', 'class_prob':
                                             0.5514150261878967}]}},
                                 (564, 659): {
                                     'Keir Starmer': {1: [{'class_id': 0, 'class_label': 'negative',
                                                           'class_prob': 0.9571385383605957},
                                                          {'class_id': 0, 'class_label': 'negative',
                                                           'class_prob': 0.8608132600784302}]}}}
        self.article_text = "test " * 500

        source_article_id = 1
        DatabaseUtils.insert_entity('Keir Starmer', source_article_id)
        DatabaseUtils.insert_entity('Tory', source_article_id)
        DatabaseUtils.insert_entity('Linday Hoyle', source_article_id)

    @mock.patch('nlp_processor.utils.DatabaseUtils.insert_overall_sentiment')
    @mock.patch('nlp_processor.utils.DatabaseUtils.insert_bound_mention_data')
    def test_average_sentiment_results_bound_mentions(self, mock_insert_bound_mention_data,
                                                      mock_insert_overall_sentiment):
        source_article_id = self.article_1.id

        SentimentAnalyser.average_sentiment_results(source_article_id,
                                                    self.bounds_sentiment, self.article_text)

        # Count the number of expected insertions based on the bounds_sentiment dictionary
        expected_insertions = sum(len(mentions) for mentions in self.bounds_sentiment.values())

        # Was insert_bound_mention_data function was called the expected number of times?
        self.assertEqual(mock_insert_bound_mention_data.call_count, expected_insertions)

        # No matter how many bounds sentiments there are we expect overall_sentiments to equal
        # the number of entities provided
        unique_entities = {entity for bounds in self.bounds_sentiment.values() for entity in bounds}
        expected_overall_insertions = len(unique_entities)

        # Was insert_bound_mention_data function was called the expected number of times?
        self.assertEqual(mock_insert_overall_sentiment.call_count, expected_overall_insertions)

        # Going deeper and checking the contents was as expected
        actual_calls = mock_insert_bound_mention_data.call_args_list

        # Expected values for first call related to "Keir Starmer"
        expected_entity_name_1, expected_source_article_id_1, expected_entity_db_id_1, expected_scores_1, expected_bounds_keys_1 = (
            "Keir Starmer", 1, 1, [0.0, 0.0, 0.9354697465896606], (0, 167)
        )

        # Expected values for fourth call related to "Keir Starmer"
        expected_entity_name_4, expected_source_article_id_4, expected_entity_db_id_4, expected_scores_4, expected_bounds_keys_4 = (
            "Lindsay Hoyle", 1, 3, [0.74396151304245, 0.0, 0.0], (168, 315)
        )

        # Assert the expected values match the actual calls
        actual_call_1 = actual_calls[0][0]
        self.assertEqual((actual_call_1[0], actual_call_1[1], actual_call_1[2], actual_call_1[3],
                          actual_call_1[5]), (expected_entity_name_1, expected_source_article_id_1,
                                              expected_entity_db_id_1, expected_scores_1,
                                              expected_bounds_keys_1),
                         "Mismatch in call 1 for Keir Starmer")

        actual_call_4 = actual_calls[5][0]
        self.assertEqual((actual_call_4[0], actual_call_4[1], actual_call_4[2], actual_call_4[3],
                          actual_call_4[5]), (expected_entity_name_4, expected_source_article_id_4,
                                              expected_entity_db_id_4, expected_scores_4,
                                              expected_bounds_keys_4),
                         "Mismatch in call 4 for Lindsay Hoyle")

        overall_calls = mock_insert_overall_sentiment.call_args_list

        # Expected values for the overall sentiment calls
        expected_call_1 = (1, 1, 3, 0.0, 0.0, 100.0, 0.0, 0.0, 100.0)
        expected_call_2 = (1, 2, 2, 53.0, 0.0, 47.0, 58.9, 0.0, 41.1)
        expected_call_3 = (1, 3, 1, 100.0, 0.0, 0.0, 100.0, 0.0, 0.0)

        # Assert the expected values match the actual calls
        self.assertEqual(overall_calls[0][0], expected_call_1,
                         "Mismatch in call 1 for overall sentiment")
        self.assertEqual(overall_calls[1][0], expected_call_2,
                         "Mismatch in call 2 for overall sentiment")
        self.assertEqual(overall_calls[2][0], expected_call_3,
                         "Mismatch in call 3 for overall sentiment")


class TestDetermineSentences(unittest.TestCase):
    MENTION_REQ_PER = 0.20

    def setUp(self):
        # Sample article text with scenarios to test including custom \n- one.
        self.article_text = ("This is the 1st sentence? This is the 2nd sentence!\n-This is "
                             "the 3rd sentence, following a newline and hyphen. This is the 4th "
                             "sentence.")

        self.article = Article(
            text_body=self.article_text,
            url=None,
            headline=None,
            NER=None,
            date=None,
            author=None,
            site_name=None,
            source_file=None
        )

    def test_determine_sentences_normal(self):
        expected_sentences = 4
        expected_bounds = [(0, 25), (26, 51), (52, 110), (111, 136)]
        expected_threshold = 0  # Based on MENTION_REQ_PER and the number of sentences provided

        self.article.determine_sentences()

        self.assertEqual(len(self.article.sentence_bounds), expected_sentences,
                         "Incorrect number of sentences detected.")
        self.assertEqual(self.article.sentence_bounds, expected_bounds,
                         "Sentence bounds do not match expected values.")
        self.assertEqual(self.article.mention_threshold, expected_threshold,
                         "Incorrect mention threshold calculated.")


class TestEntityClusterMapping(unittest.TestCase):
    def setUp(self):
        self.instance = Article(
            text_body=None,
            url=None,
            headline=None,
            NER=None,
            date=None,
            author=None,
            site_name=None,
            source_file=None
        )
        self.instance.coref_clusters = [
            (0, (["Labour's", 'the Opposition party', 'Labour’s', 'Labour', 'Labour', 'Labour',
                  'his Party', 'Labour', 'Labour', 'Labour', 'Labour'],
                 [(78, 86), (146, 166), (230, 238), (373, 379), (439, 445), (963, 969),
                  (1042, 1051), (1240, 1246), (1767, 1773), (1895, 1901), (2163, 2169)], 11)),
            (1, (
                ['Tory', 'the Tories', 'the Conservatives', 'Tory', 'the Conservatives', 'Tory',
                 'Tory',
                 'Tory', 'the party’s'], [(47, 51), (249, 259), (403, 420),
                                          (2005, 2009), (2046, 2063), (2107, 2111), (2557, 2561),
                                          (2579, 2583), (2712, 2723)], 9)),
            (2, (['Hoyle', 'Speaker Sir Lindsay Hoyle', 'the Speaker', 'Hoyle', 'Sir Lindsay', 'he',
                  'Sir Lindsay', 'he', 'his'],
                 [(224, 229), (1064, 1089), (1197, 1208), (1324, 1329), (1734, 1745), (1751, 1753),
                  (1824, 1835), (1866, 1868), (1961, 1964)], 9)),
            (3, (["Sir Keir Starmer's", 'Keir Starmer', 'Sir Keir Starmer', 'his', 'his',
                  'the Labour leader', 'his', 'Sir Keir'], [(0, 18), (168, 180),
                                                            (574, 590), (600, 603), (900, 903),
                                                            (959, 976), (1042, 1045), (1385, 1393)],
                 8)),
            (4, (['Lee Anderson MP, who lost the Tory whip', 'The former Tory deputy chairman',
                  'Mr Anderson', 'his', 'the MP’s'],
                 [(2527, 2566), (2568, 2599), (2691, 2702), (2740, 2743), (2822, 2830)], 5)),
            (5, (
                ['a fresh poll', 'A survey by Redfield & Wilton Strategies from Sunday',
                 'the survey',
                 'The new survey'],
                [(302, 314), (316, 368), (2078, 2088), (2171, 2185)], 4)),
            (6, (['Redfield & Wilton Strategies', 'the company’s', 'Redfield & Wilton Strategies',
                  'our'],
                 [(328, 356), (515, 528), (2275, 2303), (2371, 2374)], 4)),
            (7, (['us', 'Our', 'us', 'our'],
                 [(710, 712), (725, 728), (807, 809), (814, 817)], 4)),
            (8, (['Rishi Sunak’s', 'Sunak', 'Mr Sunak', 'he'],
                 [(2202, 2215), (2344, 2349), (2677, 2685), (2799, 2801)], 4)),
            (9, (['comments made by Lee Anderson MP, who lost the Tory whip', 'said',
                  'the MP’s comments'], [(2510, 2566), (2600, 2604), (2822, 2839)], 3)),
            (
                10,
                (["Sir Keir Starmer's popularity", "Labour's popularity"], [(0, 29), (78, 97)], 2)),
            (11, (['put', 'This'], [(369, 372), (429, 433)], 2)),
            (12, (['pressured', 'This'], [(1213, 1222), (1272, 1276)], 2)),
            (13, (['the motion', 'the SNP motion'], [(1260, 1270), (1288, 1302)], 2)),
            (14, (['the SNP’s', 'SNP'], [(1099, 1108), (1292, 1295)], 2)),
            (15, (['intimidated', 'the incident'], [(1052, 1063), (1365, 1377)], 2)),
            (16, (['allegations', 'the claims'], [(1025, 1163), (1421, 1431)], 2)),
            (17, (['selected', 'his move'], [(1754, 1762), (1961, 1969)], 2)),
            (18, (['2019', '2019'], [(2000, 2004), (2102, 2106)], 2)),
            (19, (['Some 18% of 2019 Tory voters', 'they'], [(2090, 2118), (2124, 2128)], 2)),
            (20, (['Reform', 'Reform UK'], [(71, 77), (2140, 2149)], 2)),
            (21, (['Rishi Sunak’s approval rating', 'it'], [(2202, 2231), (2309, 2311)], 2)),
            (22, (['The Prime Minister', 'his'], [(2441, 2459), (2494, 2497)], 2)),
            (23, (['London', 'our capital city'], [(2605, 2611), (2640, 2656)], 2)),
            (24, (['London mayor Sadiq Khan', 'his'], [(2605, 2628), (2665, 2668)], 2)),
            (25, (['his “choice of words', 'it'], [(2740, 2760), (2780, 2782)], 2))]

    @patch('nlp_processor.article_utils.cleanse_cluster_text')
    @patch('nlp_processor.article_utils.remove_titles')
    def test_process_clusters_for_keir_starmer(self, mock_remove_titles, mock_cleanse_cluster_text):
        mock_cleanse_cluster_text.side_effect = lambda x: x
        mock_remove_titles.side_effect = lambda x: x

        entity_entry = {'Entity Name': 'Keir Starmer',
                        'Positions': [[4, 16], [168, 180], [578, 590]], 'Label': 'PERSON',
                        'Num Positions': 3}
        entity_name = 'Keir Starmer'

        self.instance.process_clusters_for_entity(entity_entry, entity_name)

        expected_cluster_info = {
            'Cluster ID': 4,
            'Cluster Text': ["Sir Keir Starmer's", 'Keir Starmer', 'Sir Keir Starmer',
                             'the Labour leader', 'Sir Keir'],
            'Cluster Positions': [(0, 18), (168, 180), (574, 590), (600, 603), (900, 903),
                                  (959, 976), (1042, 1045), (1385, 1393)]
        }

        self.assertEqual(entity_entry.get('Cluster Info'), expected_cluster_info)

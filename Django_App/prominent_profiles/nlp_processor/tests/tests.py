from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from nlp_processor.models import ArticleStatistics, SimilarArticlePair, ProcessedFile, BoundError
from profiles_app.models import Article as ArticleModel
from nlp_processor.article_processor import Article
from datetime import datetime

from nlp_processor.article_update import calculate_all_percentage_differences

from nlp_processor.sentiment_resolver import (scaling, average_array, round_array_to_1dp,
                                              percentage_contribution)

"""
The following tests focus on the success of nlp_processor models interacting with profiles app 
models, object creation, and that of statistics calculation, percentage difference and similarity 
detection in the NLP pipeline"""
class ProcessedFileTest(TestCase):
    def setUp(self):
        # Set up data for the whole TestCase
        self.processed_file_data = {
            "search_term": "keir starmer",
            "file_name": "keir+starmer_no_dup_articles_loop_11-12-2023-20:56.json",
            "media_path": "api_articles/keir+starmer",
            "nlp_applied": False,
        }
        self.processed_file = ProcessedFile.objects.create(**self.processed_file_data)

    def test_processed_file_creation(self):
        """Test the ProcessedFile object was created properly."""
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
        """Test the article object is created properly."""
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
        """Checks the functionality of the similarity check method to determine if two articles are similar."""
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
        """Test linear scaling of sentiment scores."""
        expected_output = [20.0, 50.0, 30.0]
        output = scaling(self.avg_array_list, linear=True)
        self.assertEqual(output, expected_output)

    def test_scaling_exponential(self):
        """Test exponential scaling with the default value of k."""
        expected_output = [0.8, 12.5, 2.7]
        output = scaling(self.avg_array_list, linear=False)
        tolerance = 1e-5
        self.assertTrue(all(abs(a - b) < tolerance for a, b in zip(output, expected_output)))

    def test_scaling_exponential(self):
        """Ensure custom k values are properly applied in exponential scaling."""
        expected_output = [4.0, 25.0, 9.0]
        output = scaling(self.avg_array_list, k=2, linear=False)
        tolerance = 1e-5
        self.assertTrue(all(abs(a - b) < tolerance for a, b in zip(output, expected_output)))

    def test_scaling_multiple_array(self):
        """Verify handling and correctly scale multiple sentiment score arrays"""
        expected_output = [0.9, 53.9, 21.7]
        output = scaling(self.avg_array_list_2)
        print(output)
        tolerance = 1e-5
        self.assertTrue(all(abs(a - b) < tolerance for a, b in zip(output, expected_output)))

    # average_array tests
    def test_average_array_single(self):
        """Test with a single probability entry."""
        expected_output = [0.0, 0.5, 0.0]
        output = average_array(self.probabilities_single)
        self.assertEqual(output, expected_output)

    def test_average_array_mixed_sentiments(self):
        """Test averaging with mixed sentiment labels"""
        expected_output = [(0.2/3), (0.3/3), (0.5/3)]
        output = average_array(self.probabilities_mixed)
        self.assertEqual(output, expected_output)

    def test_average_array_positive_sentiments(self):
        """ Test averaging when all entries have the same label"""
        expected_output = [0, (1.4/3), 0]
        output = average_array(self.probabilities_positive_only)
        self.assertEqual(output, expected_output)

    def test_average_array_empty_list(self):
        """Check the edge case of an empty probability list is handled gracefully"""
        expected_output = [0, 0, 0]
        output = average_array([])
        self.assertEqual(output, expected_output)

    # round_array_to_1dp tests

    def test_round_array_to_1dp_standard(self):
        """Test rounding array elements to one decimal place and sum to 100"""
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
        """Test when all elements are the (nearly-) same and need rounding."""
        expected_output = [33.3, 33.3, 33.4]
        output = round_array_to_1dp(self.array_similar_in)
        self.assertEqual(output, expected_output)

    # percentage_contribution tests

    def test_percentage_contribution_even_distribution(self):
        """Test percentage contribution calculation with evenly distributed elements"""
        expected_output = [33.3, 33.3, 33.4]
        output = percentage_contribution(self.elements_even_distribution)
        self.assertEqual(output, expected_output)

    def test_percentage_contribution_single_dom(self):
        """Test percentage contribution calculation with evenly distributed elements"""
        expected_output = [0.0, 0.0, 100.0]
        output = percentage_contribution(self.elements_single_dom)
        self.assertEqual(output, expected_output)

    def test_percentage_contribution_zero_sum(self):
        """Stress test percentage contribution calculation with all zero entries"""
        expected_output = [0.0, 0.0, 0.0]
        output = percentage_contribution(self.elements_zero_sum)
        self.assertEqual(output, expected_output)

    def test_percentage_contribution_varied_values(self):
        """Stress test percentage contribution calculation with varied values i.e. typical input"""
        expected_output = [10.0, 20.0, 70.0]
        output = percentage_contribution(self.elements_varied)
        self.assertEqual(output, expected_output)


"""The following tests concern checking Database Utils in utils.py"""
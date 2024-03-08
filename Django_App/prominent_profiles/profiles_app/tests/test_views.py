import json

from django.urls import reverse
from django.utils import timezone
from profiles_app.models import Entity, Article, OverallSentiment, BingEntity
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


class ProfilesViewsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.test_article = Article.objects.create(headline="Test Article", url="http://test.com",
                                                   publication_date=timezone.now())
        self.test_article.save()

        self.test_entity = Entity.objects.create(name="Lindsay Hoyle",
                                                 source_article=self.test_article,
                                                 app_visible=True)

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

        self.bing_entity = BingEntity.objects.create(
            entity=self.test_entity,
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

        self.test_entity.save()

        self.not_visible_entity = Entity.objects.create(name="Hidden Entity",
                                                        source_article=self.test_article,
                                                        app_visible=False)
        self.not_visible_entity.save()

        self.test_overall_sentiment = OverallSentiment.objects.create(article=self.test_article,
                                                                      entity=self.test_entity,
                                                                      num_bound=1,
                                                                      linear_neutral=0.5,
                                                                      linear_positive=0.3,
                                                                      linear_negative=0.2,
                                                                      exp_neutral=0.4,
                                                                      exp_positive=0.1,
                                                                      exp_negative=0.15)
        self.test_overall_sentiment.save()

    def test_visible_entities_view(self):
        url = reverse('visible_entities')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_visible_entities_view(self):
        # Testing the visible entity is in the response and the non_visible one isn't.
        url = reverse('visible_entities')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        visible_entity_ids = [entity['id'] for entity in response_data]

        self.assertIn(self.test_entity.id, visible_entity_ids, "Visible entity not returned by API")
        self.assertNotIn(self.not_visible_entity.id, visible_entity_ids,
                         "Not visible entity was returned by API")
        self.assertTrue(all(['name' in entity and 'id' in entity for entity in response_data]),
                        "Response data does not contain expected 'name' or 'id' fields.")

    def test_bing_entity_detail_view(self):
        url = reverse('bing_entity_detail', args=[self.test_entity.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(response_data['id'], self.bing_entity.id)
        self.assertEqual(response_data['name'], self.bing_entity.name)
        self.assertEqual(response_data['description'], self.bing_entity.description)
        self.assertEqual(response_data['image_url'], self.bing_entity.improved_image_url)
        self.assertEqual(response_data['web_search_url'], self.bing_entity.web_search_url)
        self.assertEqual(response_data['bing_id'], self.bing_entity.bing_id)
        self.assertEqual(response_data['contractual_rules'], self.bing_entity.contractual_rules)
        self.assertEqual(response_data['entity_type_display_hint'],
                         self.bing_entity.entity_type_display_hint)
        self.assertEqual(response_data['entity_type_hints'], self.bing_entity.entity_type_hints)

    def test_bing_entity_mini_view(self):
        url = reverse('bing_entity_mini', args=[self.test_entity.id])
        response = self.client.get(url)
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('name', response_data)
        self.assertIn('image_url', response_data)

        # Don't want long description in mini response.
        self.assertNotIn('description', response_data)
        self.assertEqual(response_data['id'], self.bing_entity.id)

        self.assertEqual(response_data['name'], self.bing_entity.name, "Name doesn't match.")
        self.assertEqual(response_data['image_url'], self.bing_entity.improved_image_url)
        self.assertEqual(response_data['contractual_rules'], self.bing_entity.contractual_rules)
        self.assertEqual(response_data['display_hint'], self.bing_entity.entity_type_display_hint)

    def test_overall_sentiment_exp_view(self):
        url = reverse('exp_overall', args=[self.test_entity.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertIn('data', response_data)
        self.assertIsInstance(response_data['data'], list)

        if response_data['data']:
            self.assertIn('id', response_data['data'][0])
            self.assertIn('entity_id', response_data['data'][0])
            self.assertIn('headline', response_data['data'][0])
            self.assertIn('url', response_data['data'][0])
            self.assertIn('image_url', response_data['data'][0])
            self.assertIn('publication_date', response_data['data'][0])
            self.assertIn('author', response_data['data'][0])
            self.assertIn('neutral', response_data['data'][0])
            self.assertIn('positive', response_data['data'][0])
            self.assertIn('negative', response_data['data'][0])

        for entry in response_data['data']:
            self.assertEqual(entry['id'], self.test_overall_sentiment.article.id)
            self.assertEqual(entry['entity_id'], self.test_overall_sentiment.entity.id)
            self.assertAlmostEqual(float(entry['neutral']), self.test_overall_sentiment.exp_neutral,
                                   places=2)
            self.assertAlmostEqual(float(entry['positive']),
                                   self.test_overall_sentiment.exp_positive, places=2)
            self.assertAlmostEqual(float(entry['negative']),
                                   self.test_overall_sentiment.exp_negative, places=2)

    def test_overall_sentiment_linear_view(self):
        url = reverse('lin_overall', args=[self.test_entity.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertIn('data', response_data)
        self.assertIsInstance(response_data['data'], list)

        if response_data['data']:
            self.assertIn('id', response_data['data'][0])
            self.assertIn('entity_id', response_data['data'][0])
            self.assertIn('headline', response_data['data'][0])
            self.assertIn('url', response_data['data'][0])
            self.assertIn('image_url', response_data['data'][0])
            self.assertIn('publication_date', response_data['data'][0])
            self.assertIn('author', response_data['data'][0])
            self.assertIn('neutral', response_data['data'][0])
            self.assertIn('positive', response_data['data'][0])
            self.assertIn('negative', response_data['data'][0])

        for entry in response_data['data']:
            self.assertEqual(entry['id'], self.test_overall_sentiment.article.id)
            self.assertEqual(entry['entity_id'], self.test_overall_sentiment.entity.id)
            self.assertAlmostEqual(float(entry['neutral']),
                                   self.test_overall_sentiment.linear_neutral,
                                   places=2)
            self.assertAlmostEqual(float(entry['positive']),
                                   self.test_overall_sentiment.linear_positive, places=2)
            self.assertAlmostEqual(float(entry['negative']),
                                   self.test_overall_sentiment.linear_negative, places=2)

    def test_article_overall_sentiment_exp_view(self):
        article_id = self.test_article.id
        url = reverse('exp_article_overall', args=[article_id, self.test_entity.id])
        response = self.client.get(url)
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response_data)
        self.assertEqual(response_data[0]['id'], self.test_article.id)
        self.assertEqual(response_data[0]['headline'], self.test_article.headline)
        self.assertEqual(response_data[0]['url'], self.test_article.url)
        self.assertAlmostEqual(float(response_data[0]['neutral']),
                               self.test_overall_sentiment.exp_neutral, places=2)
        self.assertAlmostEqual(float(response_data[0]['positive']),
                               self.test_overall_sentiment.exp_positive, places=2)
        self.assertAlmostEqual(float(response_data[0]['negative']),
                               self.test_overall_sentiment.exp_negative, places=2)
        exp_pub_date = self.test_article.publication_date.strftime(
            '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        self.assertEqual(response_data[0]['publication_date'], exp_pub_date)

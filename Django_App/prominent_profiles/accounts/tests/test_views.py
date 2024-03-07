from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from profiles_app.models import Entity, Article
from accounts.models import Subscription

"""Making test API Calls to check for expected responses"""

User = get_user_model()


class AccountsViewsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # User will be for authentication tests
        self.test_user = User.objects.create_user(email='newStudent@student.bham.ac.uk',
                                                  password='SellyOak70',
                                                  phone_number='1234567890')
        self.test_user.save()

        self.test_article = Article.objects.create(headline="API Test Article")
        self.test_entity = Entity.objects.create(name="API Test Entity",
                                                 source_article=self.test_article)
        self.test_entity.save()

    def test_register_user(self):
        url = reverse('register_user')
        data = {
            'email': 'newStudent@student.bham.com',
            'password': 'SellyOak70',
            'phone_number': '0123456789',
            'date_of_birth': '2001-03-19'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('success' in response.data)

    def test_toggle_sub_authenticated(self):
        self.client.force_authenticate(user=self.test_user)
        url = reverse('toggle_sub',
                      args=[self.test_entity.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.json())

    def test_get_sub_status_authenticated(self):
        self.client.force_authenticate(user=self.test_user)
        url = reverse('get_sub_status', args=[self.test_entity.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.json())

    def test_get_user_data(self):
        self.client.force_authenticate(user=self.test_user)
        url = reverse('get_user_data')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], self.test_user.first_name)

    def test_get_sub_list(self):
        self.client.force_authenticate(user=self.test_user)

        Subscription.objects.create(user=self.test_user, entity=self.test_entity)

        url = reverse('get_sub_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('subscribed_entities', response.json())
        entities_list = response.json()['subscribed_entities']

        # Expecting a subscription in the list hence True check.
        self.assertTrue(entities_list)

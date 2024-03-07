from accounts.models import CustomUser, Subscription
from accounts.serializers import CustomUserSerializer
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.test import TestCase
from profiles_app.models import Entity, Article
from rest_framework.exceptions import ValidationError

"""Checking accounts models follow expected business logic through these tests"""


class CustomUserSerializerTest(TestCase):
    def setUp(self):
        # User data to use for initial user and flexible for use in tests of CustomUser
        self.user_data = {
            'email': 'test@example.com',
            'phone_number': '1111111111',
            'date_of_birth': '2015-07-01',
            'location': 'United Kingdom',
            'first_name': 'Dexter',
            'last_name': 'Meek',
            'password': 'ILoveTreats'
        }
        self.user = CustomUser.objects.create_user(**self.user_data)

    def test_validate_phone_number_uniqueness(self):
        duplicate_phone_data = self.user_data.copy()  # Same phone number as set up (should be rejected)
        duplicate_phone_data[
            'email'] = 'new@example.com'  # Change the email to avoid email uniqueness violation.
        serializer = CustomUserSerializer(data=duplicate_phone_data)

        # Fail expectation as phone number won't be unique.
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_user_creation(self):
        # Creation of user with same details but different phone number and email (permitted use)
        new_user_data = self.user_data.copy()
        new_user_data['email'] = 'newuser@example.com'
        new_user_data['phone_number'] = '0987654321'

        serializer = CustomUserSerializer(data=new_user_data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, new_user_data['email'])
        self.assertEqual(user.phone_number, new_user_data['phone_number'])


class CustomUserModelTest(TestCase):
    def test_create_user(self):
        user = CustomUser.objects.create_user(email='test@example.com', password='ILoveTreats',
                                              phone_number='1111111111', date_of_birth='2015-07-01',
                                              location='United Kingdom', first_name='Dexter',
                                              last_name='Meek')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('ILoveTreats'))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        superuser = CustomUser.objects.create_superuser(email='admin@prominentprofiles.com',
                                                        password='theBestAdmin')
        self.assertEqual(superuser.email, 'admin@prominentprofiles.com')
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)


class SubscriptionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user and entity for subscription model checks
        cls.user = CustomUser.objects.create_user(email='user@example.com', password='userpass123')
        cls.test_article = Article.objects.create(
            headline="Test Article",
        )
        cls.entity = Entity.objects.create(source_article=cls.test_article, name="David "
                                                                                 "Attenborough")

    def test_create_subscription(self):
        subscription = Subscription.objects.create(user=self.user, entity=self.entity)
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.entity, self.entity)

    def test_subscription_uniqueness(self):
        Subscription.objects.create(user=self.user, entity=self.entity)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Subscription.objects.create(user=self.user, entity=self.entity)

        # Checking only 1 sub exists i.e, the extra duplicate sub was rejected
        subscription_count = Subscription.objects.filter(user=self.user, entity=self.entity).count()
        self.assertEqual(subscription_count, 1)

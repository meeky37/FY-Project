from django.http import HttpResponse
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.middleware import UserActivityMiddleware

User = get_user_model()

"""Simulating authenticated requests to check middleware keeping track of last visit that isn't 
today - key to supporting dynamic Subscription Dashboard contents"""


class UserActivityMiddlewareTest(TestCase):
    def setUp(self):
        def get_response(request):
            return HttpResponse()

        self.factory = RequestFactory()
        self.user = User.objects.create_user(email='newStudent@student.bham.ac.uk',
                                             password='SellyOak70')
        self.middleware = UserActivityMiddleware(get_response)

    def test_authenticated_request_updates_last_visit(self):
        request = self.factory.get('/some-path')
        request.user = self.user
        self.middleware.process_request(request)
        self.user.refresh_from_db()

        # Would still expect `last_visit_excluding_today` to be None for new user
        self.assertIsNotNone(self.user.last_visit)
        self.assertIsNone(self.user.last_visit_excluding_today)  # No previous visit to set

    def test_consecutive_requests_same_day(self):
        # e.g. sign up date - 1st request
        first_request_time = timezone.now()
        self.user.last_visit = first_request_time - timezone.timedelta(days=5)
        self.user.save()

        # e.g. few days later returns to prominent profiles
        request = self.factory.get('/another-path')
        request.user = self.user
        self.middleware.process_request(request)
        self.user.refresh_from_db()

        # e.g. uses the site again that same day
        request = self.factory.get('/another-path')
        request.user = self.user
        self.middleware.process_request(request)
        self.user.refresh_from_db()

        # e.g. and again
        request = self.factory.get('/another-path')
        request.user = self.user
        self.middleware.process_request(request)
        self.user.refresh_from_db()

        self.assertNotEqual(self.user.last_visit, first_request_time)
        self.assertEqual(self.user.last_visit_excluding_today.date(), (timezone.now() -
                                                                       timezone.timedelta(
                                                                           days=5)).date())

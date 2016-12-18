# Django
from django.test import TestCase
from django.contrib.auth.models import User

# Core
from core.models import Profile


class ProfileTestCase(TestCase):
    fixtures = ['fixtures/services.yaml']

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='qwe123123',
            email='testuser@localhost')

    def tearDown(self):
        del self.user

    def test_user_name(self):
        self.assertEqual(self.user.username, 'testuser')

    def test_user_email(self):
        self.assertEqual(self.user.email, 'testuser@localhost')

    def test_user_password(self):
        self.assertIsNotNone(self.user.check_password('qwe123123'))

    def test_user_profile_presence(self):
        self.assertIsNotNone(self.user.profile)

    def test_user_profile_instance(self):
        from core.models import Profile
        self.assertIsInstance(self.user.profile, Profile)

    def test_user_profile_service(self):
        from core.models import Service, CAPACITY_CHOICES
        self.assertIsInstance(self.user.profile.service, Service)
        self.assertEqual(self.user.profile.service.capacity, CAPACITY_CHOICES[0][0])

    def test_user_profile_language(self):
        from django.conf import settings
        self.assertEqual(self.user.profile.language, settings.LANGUAGE_CODE)

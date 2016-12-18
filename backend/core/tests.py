# Django
from django.test import TestCase

# Core
from core.models import Service


class ServiceTestCase(TestCase):

    def setUp(self):
        self.service_512mb = Service.objects.create(
            name='test service 512mb',
            price=0,
            capacity=536870912)
        self.service_1gb = Service.objects.create(
            name='test service 1gb',
            price=0,
            capacity=1073741824)

    def tearDown(self):
        del self.service_512mb
        del self.service_1gb

    def test_service_capacity(self):
        self.assertEqual(self.service_512mb.capacity, 536870912)
        self.assertEqual(self.service_1gb.capacity, 1073741824)

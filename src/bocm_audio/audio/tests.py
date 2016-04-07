#--coding:utf-8--
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from audio.models import Organization

from django.utils import unittest

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

# tests.py
class ViewTest(TestCase):
	def test(self):
		response = self.client.get('/test')
		self.failUnlessEqual('abc', response.content)

class OrganizationTestCase(TestCase):
	def setUp(self):
		Organization.objects.create(name="上海分行",parent=1,link="1_2_")
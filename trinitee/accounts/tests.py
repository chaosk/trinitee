from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client
from django.utils import unittest
from accounts.models import UserProfile


class AccountsTestCase(unittest.TestCase):
	def setUp(self):
		self.user1, c = User.objects.get_or_create(username="AnneM",
			email="anne@moore.com")
		self.user2, c = User.objects.get_or_create(username="JohnD",
			email="john@doe.com")
		self.client = Client()

	def testViewProfileSuccess(self):
		response = self.client.get(reverse('profile', args=[self.user1.id]))
		self.assertEqual(response.status_code, 200)

	def testViewProfileFailure(self):
		# User with that PK doesn't exist
		response = self.client.get(reverse('profile', args=[10000]))
		self.assertEqual(response.status_code, 404)

	def testViewRegisterPrepare(self):
		response = self.client.get(reverse('register'))
		self.assertEqual(response.status_code, 200)

	def testViewRegisterSuccess(self):
		response = self.client.post(reverse('register'),
			{'username': "JackB", 'email1': "jack24@aol.com",
			'email2': "jack24@aol.com", 'password1': "wearenotalone",
			'password2': "wearenotalone"},
			follow=True)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(bool(len(response.redirect_chain)))
		self.assertTrue(response.context['user'].is_authenticated())
		self.assertEqual(response.context['user'].username, "JackB")

	def testViewRegisterFailure(self):
		# Send no POST data
		response = self.client.post(reverse('register'))
		self.assertEqual(response.status_code, 200)

		# Send incomplete POST data
		response = self.client.post(reverse('register'),
			{'username': "JackB"})
		self.assertEqual(response.status_code, 200)

		# Send POST data with non-unique username
		response = self.client.post(reverse('register'),
			{'username': "AnneM", 'email1': "jack24@aol.com",
			'email2': "jack24@aol.com", 'password1': "wearenotalone",
			'password2': "wearenotalone"})
		self.assertEqual(response.status_code, 200)

		# Send POST data with mistyped second email
		response = self.client.post(reverse('register'),
			{'username': "JackB", 'email1': "jack24@aol.com",
			'email2': "jack25@aol.com", 'password1': "wearenotalone",
			'password2': "wearenotalone"})
		self.assertEqual(response.status_code, 200)

		# Send POST data with mistyped second password
		response = self.client.post(reverse('register'),
			{'username': "JackB", 'email1': "jack24@aol.com",
			'email2': "jack24@aol.com", 'password1': "wearenotalone",
			'password2': "wearealone"})
		self.assertEqual(response.status_code, 200)

	def testViewList(self):
		response = self.client.get(reverse('userlist'))
		self.assertEqual(response.status_code, 200)

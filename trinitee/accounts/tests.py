from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client
from lib.unittest import TestCase
from accounts.models import UserProfile


class AccountsTestCase(TestCase):
	def setUp(self):
		if not User.objects.all().exists():
			self.user1 = User.objects.create_user(username="AnneM",
				password='topsecret', email="anne@moore.com")
			self.user2 = User.objects.create_user(username="JohnD",
				password='dupa.8', email="john@doe.com")
			# dupa.8 is kinda epic password in polish internet
			# not that anyone cares, just explaining how it got here
		else:
			self.user1 = User.objects.get(pk=1)
			self.user2 = User.objects.get(pk=2)
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
		self.assertMessageCount(response, 1)
		self.assertHasMessage(response, "Welcome aboard, JackB.")

	def testViewRegisterFailure(self):
		# Send no POST data
		response = self.client.post(reverse('register'))
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['form'].errors)

		# Send incomplete POST data
		response = self.client.post(reverse('register'),
			{'username': "JackB"})
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['form'].errors)

		# Send POST data with non-unique username
		response = self.client.post(reverse('register'),
			{'username': "AnneM", 'email1': "jack24@aol.com",
			'email2': "jack24@aol.com", 'password1': "wearenotalone",
			'password2': "wearenotalone"})
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['form'].errors)

		# Send POST data with mistyped second email
		response = self.client.post(reverse('register'),
			{'username': "JackB", 'email1': "jack24@aol.com",
			'email2': "jack25@aol.com", 'password1': "wearenotalone",
			'password2': "wearenotalone"})
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['form'].errors)

		# Send POST data with mistyped second password
		response = self.client.post(reverse('register'),
			{'username': "JackB", 'email1': "jack24@aol.com",
			'email2': "jack24@aol.com", 'password1': "wearenotalone",
			'password2': "wearealone"})
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['form'].errors)

		# Try to register while being logged in already
		self.client.login(username=self.user1.username,
			password='topsecret')
		response = self.client.post(reverse('register'),
			{'username': "JackB", 'email1': "jack24@aol.com",
			'email2': "jack24@aol.com", 'password1': "wearenotalone",
			'password2': "wearenotalone"},
			follow=True)
		self.assertEqual(response.status_code, 200)
		self.assertIn(reverse('home'), response.redirect_chain[0][0])
		self.assertTrue(response.context['user'].is_authenticated())
		self.assertNotEqual(response.context['user'].username, "JackB")

	def testViewLoginPrepare(self):
		response = self.client.get(reverse('login'))
		self.assertEqual(response.status_code, 200)

	def testViewLoginSuccess(self):
		response = self.client.post(reverse('login'),
			{'username': self.user1.username,
			'password': 'topsecret'},
			follow=True)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(bool(len(response.redirect_chain)))
		self.assertTrue(response.context['user'].is_authenticated())
		self.assertEqual(response.context['user'].username,
			self.user1.username)
		self.assertMessageCount(response, 1)
		self.assertHasMessage(response, "Hello, {0}."
			.format(self.user1.username))

	def testViewLoginFailure(self):
		# Send no POST data
		response = self.client.post(reverse('login'))
		self.assertEqual(response.status_code, 200)
		self.assertFalse(response.context['user'].is_authenticated())
		self.assertTrue(response.context['form'].errors)

		# Send incomplete POST data
		response = self.client.post(reverse('login'),
			{'username': self.user1.username})
		self.assertEqual(response.status_code, 200)
		self.assertFalse(response.context['user'].is_authenticated())
		self.assertTrue(response.context['form'].errors)

		# Send incorrect POST data
		response = self.client.post(reverse('login'),
			{'username': self.user1.username,
			'password': 'topsecretwrong'})
		self.assertEqual(response.status_code, 200)
		self.assertFalse(response.context['user'].is_authenticated())
		self.assertTrue(response.context['form'].errors)

		# Try to login as disabled user
		self.user1.is_active = False
		self.user1.save()
		self.assertEqual(response.status_code, 200)
		self.assertFalse(response.context['user'].is_authenticated())
		self.assertTrue(response.context['form'].errors)
		self.user1.is_active = True
		self.user1.save()

		# Try to login while being logged in already
		self.client.login(username=self.user1.username,
			password='topsecret')
		response = self.client.post(reverse('login'),
			{'username': self.user2.username,
			'password': 'dupa.8'},
			follow=True)
		self.assertEqual(response.status_code, 200)
		self.assertIn(reverse('home'), response.redirect_chain[0][0])
		self.assertTrue(response.context['user'].is_authenticated())
		self.assertNotEqual(response.context['user'].username,
			self.user2.username)

	def testViewLogoutSuccess(self):
		self.client.login(username=self.user1.username,
			password='topsecret')
		response = self.client.get(reverse('logout'), follow=True)
		self.assertEqual(response.status_code, 200)
		self.assertIn(reverse('home'), response.redirect_chain[0][0])
		self.assertFalse(response.context['user'].is_authenticated())

	def testViewList(self):
		response = self.client.get(reverse('userlist'))
		self.assertEqual(response.status_code, 200)

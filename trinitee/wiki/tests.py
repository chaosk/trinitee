from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import Client
from lib.unittest import TestCase
from reversion.models import Version
from wiki.models import WikiPage

INVALID_SLUG = '_invalidslug'

class WikiTestCase(TestCase):
	fixtures = ['accounts_tests', 'wiki_tests']

	def setUp(self):
		self.page1 = WikiPage.objects.get(pk=1)
		self.page2 = WikiPage.objects.get(pk=2)
		self.user1 = User.objects.get(pk=1)
		self.user2 = User.objects.get(pk=2)
		self.client = Client()

	def testViewIndex(self):
		response = self.client.get(reverse('wiki_index'))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['page'].title, u"Index")

	def testViewDetailSuccess(self):
		response = self.client.get(reverse('wiki_detail',
			args=[self.page1.slug]))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['page'].title, self.page1.title)

	def testViewDetailFailure(self):
		response = self.client.get(reverse('wiki_detail',
			args=[INVALID_SLUG]))
		self.assertEqual(response.status_code, 404)

	def testViewCreatePrepareSuccess(self):
		self.client.login(username=self.user1.username,
			password='topsecret')
		response = self.client.get(reverse('wiki_new'))
		self.assertEqual(response.status_code, 200)

	def testViewCreatePrepareFailure(self):
		# Missing permissions
		response = self.client.get(reverse('wiki_new'))
		self.assertEqual(response.status_code, 403)

	def testViewCreateSuccess(self):
		self.client.login(username=self.user1.username,
			password='topsecret')
		response = self.client.post(reverse('wiki_new'),
			{'title': u"Test page", 'content': "Lorem ipsum"},
			follow=True)
		self.assertEqual(response.status_code, 200)
		self.assertMessageCount(response, 1)
		self.assertHasMessage(response, "New page has been added to the wiki.")
		
		final = response.redirect_chain[0]
		self.assertEqual(final[1], 302)
		self.assertEqual(final[0], 'http://testserver/wiki/Test_page')

	def testViewCreateFailure(self):
		self.client.login(username=self.user1.username,
			password='topsecret')

		# Send no POST data
		response = self.client.post(reverse('wiki_new'))
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['form'].errors)
		
		# Send incomplete POST data
		response = self.client.post(reverse('wiki_new'),
			{'title': u"Test page"})
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['form'].errors)

		# Send POST data with non-unique title
		response = self.client.post(reverse('wiki_new'),
			{'title': self.page1.title, 'content': "Test content"})
		self.assertEqual(response.status_code, 200)

		self.client.logout()

		# Send POST data with missing permissions
		response = self.client.post(reverse('wiki_new'),
			{'title': u"Test page", 'content': "Lorem ipsum"})
		self.assertEqual(response.status_code, 403)


	def testViewEditPrepareSuccess(self):
		self.client.login(username=self.user1.username,
			password='topsecret')
		response = self.client.get(reverse('wiki_edit',
			args=[self.page1.slug]))
		self.assertEqual(response.status_code, 200)

	def testViewEditPrepareFailure(self):
		# Missing permissions
		response = self.client.get(reverse('wiki_edit',
			args=[self.page1.slug]))
		self.assertEqual(response.status_code, 403)

		self.client.login(username=self.user1.username,
			password='topsecret')

		# Nonexistent page
		response = self.client.get(reverse('wiki_edit',
			args=[INVALID_SLUG]))
		self.assertEqual(response.status_code, 404)

	def testViewEditSuccess(self):
		self.client.login(username=self.user1.username,
			password='topsecret')
		new_content = "Page 1! Edited!"
		response = self.client.post(reverse('wiki_edit',
			args=[self.page1.slug]), {'content': new_content,
				'comment': "Slightly updated"}, follow=True)
		self.assertEqual(response.status_code, 200)
		self.assertIn(self.page1.get_absolute_url(), response.redirect_chain[0][0])
		self.assertMessageCount(response, 1)
		self.assertHasMessage(response, "Successfully updated \"{0}\" page."
			.format(self.page1.title))
		self.assertEqual(response.context['page'].content, new_content)

	def testViewEditFailure(self):
		self.client.login(username=self.user1.username,
			password='topsecret')

		# Send no POST data
		response = self.client.post(reverse('wiki_edit',
			args=[self.page1.slug]))
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['form'].errors)

		# Try to edit a nonexistent Page
		response = self.client.post(reverse('wiki_edit',
			args=[INVALID_SLUG]))
		self.assertEqual(response.status_code, 404)

		self.client.logout()

		# Send POST data with missing permissions
		response = self.client.post(reverse('wiki_edit',
			args=[self.page1.slug]),
			{'comment': u"Slightly updated", 'content': "Page 1! Edited!"})
		self.assertEqual(response.status_code, 403)

	def testViewDeletePrepareSuccess(self):
		self.client.login(username=self.user1.username,
			password='topsecret')
		response = self.client.get(reverse('wiki_delete',
			args=[self.page2.slug]))
		self.assertEqual(response.status_code, 200)

	def testViewDeletePrepareFailure(self):
		# Missing permissions
		response = self.client.get(reverse('wiki_delete',
			args=[self.page1.slug]))
		self.assertEqual(response.status_code, 403)

		self.client.login(username=self.user1.username,
			password='topsecret')

		# Nonexistent page
		response = self.client.get(reverse('wiki_delete',
			args=[INVALID_SLUG]))
		self.assertEqual(response.status_code, 404)

	def testViewDeleteSuccess(self):
		self.client.login(username=self.user1.username,
			password='topsecret')
		response = self.client.post(reverse('wiki_delete',
			args=[self.page2.slug]), follow=True)
		self.assertEqual(response.status_code, 200)
		self.assertIn(reverse('wiki_index'), response.redirect_chain[0][0])
		self.assertMessageCount(response, 1)
		self.assertHasMessage(response, "Successfully removed \"{0}\" page."
			.format(self.page2.title))		
		self.assertRaises(WikiPage.DoesNotExist, WikiPage.objects.get, pk=2)

	def testViewDeleteFailure(self):
		# Missing permissions
		response = self.client.post(reverse('wiki_delete',
			args=[self.page1.slug]))
		self.assertEqual(response.status_code, 403)

		self.client.login(username=self.user1.username,
			password='topsecret')

		# Try to delete a nonexistent Page
		response = self.client.post(reverse('wiki_delete',
			args=[INVALID_SLUG]))
		self.assertEqual(response.status_code, 404)

	def testViewList(self):
		response = self.client.get(reverse('wiki_list'))
		self.assertEqual(response.status_code, 200)

	def testViewHistory(self):
		response = self.client.get(reverse('wiki_history',
			args=[self.page1.slug]))
		self.assertEqual(response.status_code, 200)

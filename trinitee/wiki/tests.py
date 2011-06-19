from django.core.urlresolvers import reverse
from django.test import Client
from django.utils import unittest
from reversion.models import Version
from wiki.models import WikiPage

INVALID_SLUG = '_invalidslug'

class WikiTestCase(unittest.TestCase):
	def setUp(self):
		self.page1, c = WikiPage.objects.get_or_create(slug="Page_1", defaults={
			'title': u"Page 1",
			'content': "Page 1!"})
		self.page2, c = WikiPage.objects.get_or_create(slug="Page_2", defaults={
			'title': u"Page 2",
			'content': "Page _2_!"})
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

	def testViewCreatePrepare(self):
		response = self.client.get(reverse('wiki_new'))
		self.assertEqual(response.status_code, 200)

	def testViewCreateSuccess(self):
		response = self.client.post(reverse('wiki_new'),
			{'title': u"Test page", 'content': "Lorem ipsum"},
			follow=True)
		
		self.assertEqual(response.status_code, 200)
		
		final = response.redirect_chain[0]
		self.assertEqual(final[1], 302)
		self.assertEqual(final[0], 'http://testserver/wiki/Test_page')

	def testViewCreateFailure(self):
		# Send no POST data
		response = self.client.post(reverse('wiki_new'))
		self.assertEqual(response.status_code, 200)
		
		# Send incomplete POST data
		response = self.client.post(reverse('wiki_new'),
			{'title': u"Test page"})
		self.assertEqual(response.status_code, 200)

		# Send POST data with non-unique title
		response = self.client.post(reverse('wiki_new'),
			{'title': u"Page 1", 'content': "Test content"})
		self.assertEqual(response.status_code, 200)

	def testViewEditPrepareSuccess(self):
		response = self.client.get(reverse('wiki_edit',
			args=[self.page1.slug]))
		self.assertEqual(response.status_code, 200)

	def testViewEditPrepareFailure(self):
		response = self.client.get(reverse('wiki_edit',
			args=[INVALID_SLUG]))
		self.assertEqual(response.status_code, 404)

	def testViewEditSuccess(self):
		new_content = "Page 1! Edited!"
		response = self.client.post(reverse('wiki_edit',
			args=[self.page1.slug]), {'content': new_content,
				'comment': "Slightly updated"}, follow=True)
		self.assertEqual(response.status_code, 200)
		self.assertIn(self.page1.get_absolute_url(), response.redirect_chain[0][0])
		self.assertEqual(response.context['page'].content, new_content)

	def testViewEditFailure(self):
		# Send no POST data
		response = self.client.post(reverse('wiki_edit',
			args=[self.page1.slug]))
		self.assertEqual(response.status_code, 200)

		# Try to edit a nonexistent Page
		response = self.client.post(reverse('wiki_edit',
			args=[INVALID_SLUG]))
		self.assertEqual(response.status_code, 404)

	def testViewDeletePrepareSuccess(self):
		response = self.client.get(reverse('wiki_delete',
			args=[self.page2.slug]))
		self.assertEqual(response.status_code, 200)

	def testViewDeletePrepareFailure(self):
		response = self.client.get(reverse('wiki_delete',
			args=[INVALID_SLUG]))
		self.assertEqual(response.status_code, 404)

	def testViewDeleteSuccess(self):
		response = self.client.post(reverse('wiki_delete',
			args=[self.page2.slug]), follow=True)
		self.assertEqual(response.status_code, 200)
		self.assertIn(reverse('wiki_index'), response.redirect_chain[0][0])
		self.assertRaises(WikiPage.DoesNotExist, WikiPage.objects.get, pk=2)

	def testViewDeleteFailure(self):
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
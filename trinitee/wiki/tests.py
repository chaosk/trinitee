from django.core.urlresolvers import reverse
from django.test import Client
from django.utils import unittest
from reversion.models import Version
from wiki.models import WikiPage


class WikiTestCase(unittest.TestCase):
	def setUp(self):
		self.page1, c = WikiPage.objects.get_or_create(title=u"Page 1",
			content="Page 1!")
		
		self.page2, c = WikiPage.objects.get_or_create(title=u"Page 2",
			content="Page _2_!")
		self.client = Client()

	def testViewDetailSuccess(self):
		response = self.client.get(reverse('wiki_detail',
			args=[self.page1.slug]))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['page'].title, self.page1.title)

	def testViewDetailFailure(self):
		response = self.client.get(reverse('wiki_detail',
			args=['_impossibleslug']))
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

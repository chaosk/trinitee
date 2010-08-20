from django.test import TestCase
from django.contrib.auth.models import User
from forums.models import Post, Topic, Forum

class TopicTestCase(TestCase):
	fixtures = ['forum_tests']

	def setUp(self):
		self.user = User.objects.get(username="user")
		self.admin = User.objects.get(username="admin")
		self.forum = Forum.objects.get(id=1)
		#self.topic = Topic.objects.create(title="Test topic", sound="meow")
		#self.post = Post.objects.create(topic=self.topic, sound="roar")

	def testCreateSuccess(self):
		topic = Topic.objects.create(title="Test topic", author=self.user,
			forum=self.forum)
		retrieved = Topic.objects.get(id=topic.id)
		self.assertEquals(topic.title, "Test topic")


class KarmaTestCase(TestCase):
	fixtures = ['forum_tests']

	def setUp(self):
		self.user = User.objects.get(username="user")
		self.admin = User.objects.get(username="admin")
		self.topic = Topic.objects.get(id=1)
		self.post_admin = Post.objects.get(id=1)
		self.post_user = Post.objects.get(id=2)

	def testUserVotesNotOwnPostSuccess(self):
		post = self.post_admin
		user = self.user
		returned = post.vote_up(user)
		self.assertTrue(returned)

	def testAdminVotesNotOwnPostSuccess(self):
		post = self.post_user
		user = self.admin
		returned = post.vote_up(user)
		self.assertTrue(returned)

	def testUserVotesOwnPostFailure(self):
		post = self.post_user
		user = self.user
		returned = post.vote_up(user)
		self.assertFalse(returned)

	def testAdminVotesOwnPostSuccess(self):
		post = self.post_admin
		user = self.admin
		returned = post.vote_up(user)
		self.assertTrue(returned)

from django.test import TestCase as DjTestCase

"""
Based on http://stackoverflow.com/questions/2897609/#4934325
"""

class TestCase(DjTestCase):
	def assertMessageCount(self, response, expect_num):
		"""
		Asserts that exactly the given number of messages have been sent.
		"""

		actual_num = len(response.context['messages'])
		if actual_num != expect_num:
			self.fail('Message count was %d, expected %d' %
				(actual_num, expect_num))

	def assertHasMessage(self, response, text, level=None):
		"""
		Asserts that there a message with the given text.
		"""

		messages = response.context['messages']
		matches = [m for m in messages if text == m.message]
		if len(matches):
			msg = matches[0]
			if level is not None and msg.level != level:
				self.fail('There was one matching message but with different'
					'level: %s != %s' % (msg.level, level))
			return
		else:
			messages_str = ", ".join('"%s"' % m for m in messages)
			self.fail('No message contained text "%s", messages were: %s' %
				(text, messages_str))

from django.core.cache import cache
from misc.models import Drawboard
from utilities.admin_tools.dashboard.modules import DashboardModule

class DrawboardModule(DashboardModule):
	def __init__(self, **kwargs):
		super(DrawboardModule, self).__init__(**kwargs)
		self.title = kwargs.get('title', 'Drawboard')
		self.template = 'misc/dashboard/modules/drawboard.html'

	def init_with_context(self, context):
		drawboard = cache.get('misc_drawboard')
		if drawboard is None:
			drawboard, created = Drawboard.objects.get_or_create(pk=1)
			cache.set('misc_drawboard', drawboard)
		self.children.append(drawboard)

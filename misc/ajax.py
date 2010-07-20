from datetime import datetime
from misc.models import Drawboard
from utilities.dajax.core import Dajax
from utilities.dajaxice.core import dajaxice_functions
from utilities.internal.templatetags.utils import user_date

def drawboard_save(request, new_content):
	drawboard, created = Drawboard.objects.get_or_create(pk=1)
	drawboard.last_modified_by = request.user
	new_content = new_content.replace('~~~~', '%s, %s' % \
		(request.user, user_date(datetime.now(), request.user, human_days=False)))
	drawboard.content = new_content
	drawboard.save()
	dajax = Dajax()
	dajax.assign_lesser('#drawboard', 'innerHTML', new_content)
	dajax.assign('#drawboard-div', 'innerHTML', drawboard.content_html)
	dajax.script("finish();")
	return dajax.json()
dajaxice_functions.register(drawboard_save)
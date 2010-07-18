from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from utilities.admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from utilities.annoying.functions import get_config

# to activate your index dashboard add the following to your settings.py:
#
# ADMIN_TOOLS_INDEX_DASHBOARD = 'trinitee.dashboard.CustomIndexDashboard'

class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for trinitee.
    """
    def __init__(self, **kwargs):
        self.columns = 3
        Dashboard.__init__(self, **kwargs)
        
        self.children.append(modules.AppList(
            title=_('Users'),
            include_list=('django.contrib.auth','accounts'),
            css_classes=['collapse', 'open'],
        ))
        
        self.children.append(modules.AppList(
            title='Forums',
            include_list=('forums',),
            css_classes=['collapse', 'open'],
        ))

        self.children.append(modules.AppList(
            title='Downloads',
            include_list=('downloads',),
            css_classes=['collapse', 'open'],
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            column=2,
            title=_('Recent Actions'),
            limit=10
        ))

        # append a feed module
        # self.children.append(modules.Feed(
        #     column=2,
        #     title=_('Latest Django News'),
        #     feed_url='http://www.djangoproject.com/rss/weblog/',
        #     limit=5
        # ))

        self.children.append(modules.LinkList(
            column=3,
            title=_('Quick actions'),
            children=[
                {
                    'title': _('Add forum category'),
                    'url': reverse('admin:forums_forum_add'),
                },
                {
                    'title': _('Add new TW version'),
                    'url': reverse('admin:downloads_version_add'),
                },
                {
                    'title': _('Post new news'),
                    'url': reverse('admin:forums_topic_add') + '?forum=%s' % get_config('NEWS_FORUM', 1),
                },
                {
                    'title': _('Post new developer\'s entry'),
                    'url': reverse('admin:forums_topic_add') + '?forum=%s' % get_config('JOURNAL_FORUM', 2),
                },
            ]
        ))

        self.children.append(modules.LinkList(
            column=3,
            title=_('Quick links'),
            children=[
                {
                    'title': _('Return to site'),
                    'url': '/',
                },
                {
                    'title': _('Change password'),
                    'url': reverse('admin:password_change'),
                },
                {
                    'title': _('Log out'),
                    'url': reverse('admin:logout')
                },
            ]
        ))

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        pass


# to activate your app index dashboard add the following to your settings.py:
#
# ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'trinitee.dashboard.CustomAppIndexDashboard'

class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for trinitee.
    """
    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        # we disable title because its redundant with the model list module
        self.title = ''

        # append a model list module
        self.children.append(modules.ModelList(
            title=self.app_title,
            models=self.models,
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            column=2,
            title=_('Recent Actions'),
            include_list=self.get_app_content_types(),
        ))

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        pass

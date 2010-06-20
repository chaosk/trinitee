from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from admin_tools.utils import AppListElementMixin


class MenuItem(object):
    """
    This is the base class for custom menu items.
    A menu item can have the following properties:

    ``title``
        String that contains the menu item title, make sure you use the
        django gettext functions if your application is multilingual.
        Default value: 'Untitled menu item'.

    ``url``
        String that contains the menu item URL.
        Default value: '#'.

    ``css_classes``
        A list of css classes to be added to the menu item ``li`` class
        attribute. Default value: [].

    ``accesskey``
        The menu item accesskey. Default value: None.

    ``description``
        An optional string that will be used as the ``title`` attribute of
        the menu-item ``a`` tag. Default value: None.

    ``enabled``
        Boolean that determines whether the menu item is enabled or not.
        Disabled items are displayed but are not clickable.
        Default value: True.

    ``template``
        The template to use to render the menu item.
        Default value: 'admin_tools/menu/item.html'.

    ``children``
        A list of children menu items. All children items must be instances of
        the ``MenuItem`` class.
    """

    def __init__(self, **kwargs):
        """
        ``MenuItem`` constructor.
        """
        self.title = kwargs.get('title', 'Untitled menu item')
        self.url = kwargs.get('url', '#')
        self.css_classes = kwargs.get('css_classes', [])
        self.accesskey = kwargs.get('accesskey')
        self.description = kwargs.get('description')
        self.enabled = kwargs.get('enabled', True)
        self.template = kwargs.get('template', 'admin_tools/menu/item.html')
        self.children = kwargs.get('children', [])

    def init_with_context(self, context):
        """
        Like for menus, menu items have a ``init_with_context`` method that is
        called with a ``django.template.RequestContext`` instance as unique
        argument.
        This gives you enough flexibility to build complex items, for example,
        let's build a "history" menu item, that will list the last ten visited
        pages::

            from admin_tools.menu.items import MenuItem

            class HistoryMenuItem(MenuItem):
                def init_with_context(self, context):
                    self.title = 'History'
                    request = context['request']
                    # we use sessions to store the visited pages stack
                    history = request.session.get('history', [])
                    for item in history:
                        self.children.append(MenuItem(
                            title=item['title'],
                            url=item['url']
                        ))
                    # add the current page to the history
                    history.insert(0, {
                        'title': context['title'],
                        'url': request.META['PATH_INFO']
                    })
                    if len(history) > 10:
                        history = history[:10]
                    request.session['history'] = history

        Here's a screenshot of our history item:

        .. image:: images/history_menu_item.png
        """
        pass

    def is_selected(self, request):
        """
        Helper method that returns ``True`` if the menu item is active.
        A menu item is considered as active if it's URL or one of its
        descendants URL is equals to the current URL.
        """
        current_url = request.get_full_path()
        return self.url == current_url or \
            len([c for c in self.children if c.is_selected(request)]) > 0


class AppList(MenuItem, AppListElementMixin):
    """
    A menu item that lists installed apps an their models.
    In addition to the parent :class:`~admin_tools.menu.items.MenuItem`
    properties, the ``AppList`` has two extra properties:

    ``exclude_list``
        A list of apps to exclude, if an app name (e.g. "django.contrib.auth"
        starts with an element of this list (e.g. "django.contrib") it won't
        appear in the menu item.

    ``include_list``
        A list of apps to include, only apps whose name (e.g.
        "django.contrib.auth") starts with one of the strings (e.g.
        "django.contrib") in the list will appear in the menu item.

    If no include/exclude list is provided, **all apps** are shown.

    Here's a small example of building an app list menu item::

        from admin_tools.menu import items, Menu

        class MyMenu(Menu):
            def __init__(self, **kwargs):
                super(MyMenu, self).__init__(**kwargs)
                self.children.append(items.AppList(
                    title='Applications',
                    exclude_list=('django.contrib',)
                )

    The screenshot of what this code produces:

    .. image:: images/applist_menu_item.png

    .. note::

        Note that this module takes into account user permissions, as a
        consequence, if a user has no rights to change or add a ``Group`` for
        example, the ``django.contrib.auth.Group model`` child item won't be
        displayed in the menu item.
    """

    def __init__(self, **kwargs):
        """
        ``AppListMenuItem`` constructor.
        """
        super(AppList, self).__init__(**kwargs)
        self.include_list = kwargs.get('include_list', [])
        self.exclude_list = kwargs.get('exclude_list', [])
        self.models = list(kwargs.get('models', []))
        self.exclude = list(kwargs.get('exclude', []))


    def init_with_context(self, context):
        """
        Please refer to the :meth:`~admin_tools.menu.items.MenuItem.init_with_context`
        documentation from :class:`~admin_tools.menu.items.MenuItem` class.
        """
        items = self._visible_models(context['request'])
        apps = {}
        for model, perms in items:
            if not perms['change']:
                continue
            app_label = model._meta.app_label
            if app_label not in apps:
                apps[app_label] = {
                    'title': capfirst(app_label.title()),
                    'url': reverse('admin:app_list', args=(app_label,)),
                    'models': []
                }
            apps[app_label]['models'].append({
                'title': capfirst(model._meta.verbose_name_plural),
                'url': self._get_admin_change_url(model)
            })

        apps_sorted = apps.keys()
        apps_sorted.sort()
        for app in apps_sorted:
            app_dict = apps[app]
            item = MenuItem(title=app_dict['title'], url=app_dict['url'])
            # sort model list alphabetically
            apps[app]['models'].sort(lambda x, y: cmp(x['title'], y['title']))
            for model_dict in apps[app]['models']:
                item.children.append(MenuItem(**model_dict))
            self.children.append(item)


class Bookmarks(MenuItem, AppListElementMixin):
    """
    A menu item that lists pages bookmarked by the user. This menu item also
    adds an extra button to the menu that allows the user to bookmark or
    un-bookmark the current page.

    Here's a small example of adding a bookmark menu item::

        from admin_tools.menu import items, Menu

        class MyMenu(Menu):
            def __init__(self, **kwargs):
                super(MyMenu, self).__init__(**kwargs)
                self.children.append(items.Bookmarks(title='My bookmarks'))

    """

    def __init__(self, **kwargs):
        super(Bookmarks, self).__init__(**kwargs)
        self.title = kwargs.get('title', _('Bookmarks'))
        if 'bookmark' not in self.css_classes:
            self.css_classes.append('bookmark')

    def init_with_context(self, context):
        """
        Please refer to the :meth:`~admin_tools.menu.items.MenuItem.init_with_context`
        documentation from :class:`~admin_tools.menu.items.MenuItem` class.
        """
        from admin_tools.menu.models import Bookmark
        for b in Bookmark.objects.filter(user=context['request'].user):
            self.children.append(MenuItem(
                url=b.url,
                title=mark_safe(b.title)
            ))
        if not len(self.children):
            self.enabled = False

    def is_selected(self, request):
        """
        A bookmark menu item is never considered as active, the real item is.
        """
        return False



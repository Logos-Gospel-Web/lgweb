"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'project.dashboard.CustomIndexDashboard'
"""

from django.core.files.storage import default_storage
from django.urls import reverse

from grappelli.dashboard import modules, Dashboard

class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        self.children.append(modules.AppList(
            '',
            column=1,
            collapsible=False,
            css_classes=('collapse closed',),
            exclude=('django.contrib.*',),
        ))

        self.children.append(modules.ModelList(
            'Administration',
            column=1,
            collapsible=False,
            models=('django.contrib.*',),
        ))

        request = context['request']
        links = []

        links.append({
            'title': 'Purge Cache',
            'url': reverse('purge'),
            'target': '_blank',
        })

        if request.user.has_perm('app.view_analytics'):
            links.append({
                'title': 'Statistics',
                'url': reverse('statistics'),
                'target': '_blank',
            })

        links.append({
            'title': 'Template Doc',
            'url': default_storage.url('template.doc', parameters={ 'dl': '1' }),
        })

        self.children.append(modules.LinkList(
            'Additional info',
            column=2,
            collapsible=False,
            children=links
        ))

        self.children.append(modules.RecentActions(
            'Recent actions',
            column=2,
            collapsible=False,
        ))

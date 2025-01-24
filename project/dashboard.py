"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'project.dashboard.CustomIndexDashboard'
"""

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

        self.children.append(modules.LinkList(
            'Additional info',
            column=2,
            collapsible=False,
            children=[
                {
                    'title': 'Statistics',
                    'url': reverse('statistics'),
                    'external': True,
                    'target': '_blank',
                },
            ]
        ))

        self.children.append(modules.RecentActions(
            'Recent actions',
            column=2,
            collapsible=False,
        ))

from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect

from django_ratelimit.core import is_ratelimited

def login_wrapper(login_func):
    def admin_login(request, **kwargs):
        if request.method != "GET" and is_ratelimited(request, key='ip', group='login', rate='5/5m', method='POST', increment=True):
            messages.error(request, 'Too many login attempts, please wait 5 minutes')
            return redirect(reverse("admin:index"))
        else:
            return login_func(request, **kwargs)

    return admin_login
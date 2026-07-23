from django.core.cache import cache as default_cache, caches
from django.http import HttpRequest, HttpResponse, HttpResponseNotModified
from hashlib import md5
from base64 import urlsafe_b64encode

def use_cache(disabled: bool | None = None):
    def decorator(view_func):
        def _wrapped_view(request: HttpRequest, *args, **kwargs):
            if disabled or request.method not in ('GET', 'HEAD') or request.GET:
                return view_func(request, *args, **kwargs)

            key = request.path

            current_etag = caches['etag'].get(key)
            client_etag: str | None = request.META.get('HTTP_IF_NONE_MATCH')

            if client_etag:
                if client_etag.startswith('W/'):
                    client_etag = client_etag[2:]
                client_etag = client_etag.strip('"')

            response = None

            if current_etag:
                if client_etag == current_etag:
                    response = HttpResponseNotModified()
                else:
                    cached_data = default_cache.get(key)
                    if cached_data is not None:
                        cached_content, content_type = cached_data
                        response = HttpResponse(cached_content, content_type=content_type)

            if not response:
                response = view_func(request, *args, **kwargs)
                if hasattr(response, 'render') and callable(response.render):
                    response.render()

                if response.status_code != 200:
                    return response

                content_type = response.get('Content-Type', 'text/html; charset=utf-8')
                default_cache.set(key, (response.content, content_type))

                current_etag = urlsafe_b64encode(md5(response.content).digest()).decode('utf-8').strip('=')
                caches['etag'].set(key, current_etag)

                if client_etag == current_etag:
                    response = HttpResponseNotModified()

            response['ETag'] = f'"{current_etag}"'
            response['Cache-Control'] = 'max-age=60'

            return response

        return _wrapped_view
    return decorator

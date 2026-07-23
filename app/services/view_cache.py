from django.core.cache import cache as default_cache, caches
from django.http import HttpResponse, HttpResponseNotModified
from hashlib import sha256

def use_cache(disabled = None):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if disabled or request.method not in ('GET', 'HEAD') or request.GET:
                return view_func(request, *args, **kwargs)

            key = request.path

            current_etag = caches['etag'].get(key)
            client_etag = request.META.get('HTTP_IF_NONE_MATCH')

            if client_etag:
                client_etag = client_etag.replace('W/', '').strip('"')

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

                current_etag = sha256(response.content).hexdigest()[:16]
                caches['etag'].set(key, current_etag)

                if client_etag == current_etag:
                    response = HttpResponseNotModified()

            response['ETag'] = f'"{current_etag}"'
            response['Cache-Control'] = 'max-age=60'

            return response

        return _wrapped_view
    return decorator

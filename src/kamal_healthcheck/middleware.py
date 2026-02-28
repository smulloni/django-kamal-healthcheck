from django.conf import settings
from django.http import HttpResponse


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.healthcheck_path = getattr(
            settings, "KAMAL_HEALTHCHECK_PATH", "/up/"
        )

    def __call__(self, request):
        if request.path == self.healthcheck_path:
            return HttpResponse("OK", content_type="text/plain")
        return self.get_response(request)

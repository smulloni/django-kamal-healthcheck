from django.test import RequestFactory, SimpleTestCase, override_settings
from django.http import HttpResponse

from kamal_healthcheck.middleware import HealthCheckMiddleware
from kamal_healthcheck.checks import check_secure_ssl_redirect, check_middleware_order


def dummy_get_response(request):
    return HttpResponse("passed through", content_type="text/plain")


class HealthCheckMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = HealthCheckMiddleware(dummy_get_response)

    def test_healthcheck_returns_200(self):
        request = self.factory.get("/up/")
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
        self.assertEqual(response["Content-Type"], "text/plain")

    def test_other_requests_pass_through(self):
        request = self.factory.get("/other/")
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"passed through")

    def test_head_request(self):
        request = self.factory.head("/up/")
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_post_request(self):
        request = self.factory.post("/up/")
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")

    def test_path_without_trailing_slash_passes_through(self):
        request = self.factory.get("/up")
        response = self.middleware(request)
        self.assertEqual(response.content, b"passed through")

    @override_settings(KAMAL_HEALTHCHECK_PATH="/healthz/")
    def test_custom_path(self):
        middleware = HealthCheckMiddleware(dummy_get_response)
        request = self.factory.get("/healthz/")
        response = middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")

    @override_settings(KAMAL_HEALTHCHECK_PATH="/healthz/")
    def test_default_path_passes_through_with_custom_path(self):
        middleware = HealthCheckMiddleware(dummy_get_response)
        request = self.factory.get("/up/")
        response = middleware(request)
        self.assertEqual(response.content, b"passed through")


class HealthCheckIntegrationTests(SimpleTestCase):
    """Test using the Django test client, exercising the full middleware stack."""

    def test_healthcheck_through_full_stack(self):
        response = self.client.get("/up/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")

    def test_missing_route_returns_404(self):
        response = self.client.get("/nonexistent/")
        self.assertEqual(response.status_code, 404)


class CheckSecureSSLRedirectTests(SimpleTestCase):
    @override_settings(
        SECURE_SSL_REDIRECT=True,
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "kamal_healthcheck.middleware.HealthCheckMiddleware",
        ],
    )
    def test_warns_when_security_middleware_before_healthcheck(self):
        warnings = check_secure_ssl_redirect(None)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].id, "kamal_healthcheck.W001")

    @override_settings(
        SECURE_SSL_REDIRECT=True,
        MIDDLEWARE=[
            "kamal_healthcheck.middleware.HealthCheckMiddleware",
            "django.middleware.security.SecurityMiddleware",
        ],
    )
    def test_no_warning_when_healthcheck_is_first(self):
        warnings = check_secure_ssl_redirect(None)
        self.assertEqual(len(warnings), 0)

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_no_warning_when_ssl_redirect_disabled(self):
        warnings = check_secure_ssl_redirect(None)
        self.assertEqual(len(warnings), 0)


class CheckMiddlewareOrderTests(SimpleTestCase):
    @override_settings(
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "kamal_healthcheck.middleware.HealthCheckMiddleware",
        ]
    )
    def test_warns_when_security_middleware_is_before_healthcheck(self):
        warnings = check_middleware_order(None)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].id, "kamal_healthcheck.W002")

    @override_settings(
        MIDDLEWARE=[
            "kamal_healthcheck.middleware.HealthCheckMiddleware",
            "django.middleware.security.SecurityMiddleware",
        ]
    )
    def test_no_warning_when_healthcheck_is_before_security(self):
        warnings = check_middleware_order(None)
        self.assertEqual(len(warnings), 0)

    @override_settings(
        MIDDLEWARE=[
            "some.other.Middleware",
            "kamal_healthcheck.middleware.HealthCheckMiddleware",
            "django.middleware.security.SecurityMiddleware",
        ]
    )
    def test_no_warning_when_other_middleware_precedes_healthcheck(self):
        warnings = check_middleware_order(None)
        self.assertEqual(len(warnings), 0)

    @override_settings(MIDDLEWARE=["django.middleware.security.SecurityMiddleware"])
    def test_no_warning_when_healthcheck_not_installed(self):
        warnings = check_middleware_order(None)
        self.assertEqual(len(warnings), 0)

    @override_settings(MIDDLEWARE=["kamal_healthcheck.middleware.HealthCheckMiddleware"])
    def test_no_warning_when_security_not_installed(self):
        warnings = check_middleware_order(None)
        self.assertEqual(len(warnings), 0)

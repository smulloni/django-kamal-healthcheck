from django.conf import settings
from django.core.checks import Warning, register, Tags

MIDDLEWARE_PATH = "kamal_healthcheck.middleware.HealthCheckMiddleware"
SECURITY_MIDDLEWARE_PATH = "django.middleware.security.SecurityMiddleware"


@register(Tags.security)
def check_secure_ssl_redirect(app_configs, **kwargs):
    errors = []
    if not getattr(settings, "SECURE_SSL_REDIRECT", False):
        return errors
    middleware = list(settings.MIDDLEWARE)
    if MIDDLEWARE_PATH not in middleware or SECURITY_MIDDLEWARE_PATH not in middleware:
        return errors
    if middleware.index(SECURITY_MIDDLEWARE_PATH) < middleware.index(MIDDLEWARE_PATH):
        errors.append(
            Warning(
                "SECURE_SSL_REDIRECT is enabled and SecurityMiddleware runs "
                "before HealthCheckMiddleware. This will cause healthcheck "
                "redirect loops since kamal-proxy does not follow redirects.",
                id="kamal_healthcheck.W001",
            )
        )
    return errors


@register(Tags.security)
def check_middleware_order(app_configs, **kwargs):
    errors = []
    middleware = list(settings.MIDDLEWARE)
    if MIDDLEWARE_PATH not in middleware or SECURITY_MIDDLEWARE_PATH not in middleware:
        return errors
    if middleware.index(SECURITY_MIDDLEWARE_PATH) < middleware.index(MIDDLEWARE_PATH):
        errors.append(
            Warning(
                "SecurityMiddleware is before HealthCheckMiddleware in "
                "MIDDLEWARE. HealthCheckMiddleware must run first so "
                "healthcheck requests bypass host validation.",
                id="kamal_healthcheck.W002",
            )
        )
    return errors

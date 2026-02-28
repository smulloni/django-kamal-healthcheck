SECRET_KEY = "test-secret-key"
INSTALLED_APPS = [
    "kamal_healthcheck",
]
MIDDLEWARE = [
    "kamal_healthcheck.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
]
ROOT_URLCONF = "tests.urls"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

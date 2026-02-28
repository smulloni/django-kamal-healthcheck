from django.apps import AppConfig


class KamalHealthCheckConfig(AppConfig):
    name = "kamal_healthcheck"

    def ready(self):
        from . import checks  # noqa: F401

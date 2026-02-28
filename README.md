# django-kamal-healthcheck

Django middleware that handles [Kamal](https://kamal-deploy.org/) healthcheck requests.

## The problem

kamal-proxy sends healthcheck requests to `/up/` with a `Host` header that won't match your Django `ALLOWED_HOSTS`. The request hits Django's `SecurityMiddleware` or host validation and gets rejected before your app can respond, so kamal-proxy thinks the container is unhealthy.

## The solution

`HealthCheckMiddleware` sits first in the middleware stack and intercepts healthcheck requests, returning a `200 OK` response before any host validation or SSL redirect logic runs.

## Installation

If you use `uv`:

```
uv add django-kamal-healthcheck
```

or 

```
pip install django-kamal-healthcheck
```

## Configuration

Add `kamal_healthcheck` to `INSTALLED_APPS` and put the middleware **first** in `MIDDLEWARE`:

```python
# settings.py

INSTALLED_APPS = [
    "kamal_healthcheck",
    # ...
]

MIDDLEWARE = [
    "kamal_healthcheck.middleware.HealthCheckMiddleware",  # must precede SecurityMiddleware
    "django.middleware.security.SecurityMiddleware",
    # ...
]
```

That's it. Requests to `/up/` will return a `200 OK` plain text response.

### Custom healthcheck path

The default path is `/up/`, matching kamal-proxy's default. To change it:

```python
KAMAL_HEALTHCHECK_PATH = "/healthz/"
```

## System checks

The app registers two Django system checks that run automatically:

- **`kamal_healthcheck.W001`**: Warns if `SECURE_SSL_REDIRECT = True` and `SecurityMiddleware` is ordered before `HealthCheckMiddleware`. kamal-proxy handles SSL termination and does not follow redirects, so this combination causes healthcheck redirect loops.

- **`kamal_healthcheck.W002`**: Warns if `HealthCheckMiddleware` is not the first entry in `MIDDLEWARE`. It must run before host validation and other security middleware.

## Requirements

- Python >= 3.10
- Django >= 4.2

## License

MIT

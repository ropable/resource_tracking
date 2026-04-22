# GitHub Copilot Instructions

## Project Overview

`resource_tracking` is a DBCA (Department of Biodiversity, Conservation and Attractions, WA) internal Django application that downloads, stores and serves location data from remote tracking devices installed in vehicles and aircraft. The primary domain models are `Device` and `LoggedPoint`.

- **Version:** 1.4.45 (`pyproject.toml` is the source of truth)
- **Python:** ≥ 3.13
- **Django:** 5.2.x
- **Database:** PostgreSQL with PostGIS (`django.contrib.gis`)
- **Package manager:** `uv` (not pip or pipenv — always update `pyproject.toml` and `uv.lock`)

---

## Repository Structure

```
resource_tracking/   # Django project package (settings, urls, wsgi, asgi, middleware, api)
tracking/            # Main application (models, views, forms, api, signals, utils, harvest, email_utils)
  management/
    commands/        # One management command per harvest source (harvest_tracplus, harvest_dfes_feed, etc.)
  migrations/        # Django migrations — never edit manually
  templates/         # Django HTML templates (djlint profile: django)
  static/            # App-level static files
kustomize/           # Kubernetes deployment manifests (base + overlays: prod, uat)
staticfiles/         # WhiteNoise-compiled static output — do not edit
```

---

## Tech Stack & Key Libraries

| Concern               | Library                                             |
| --------------------- | --------------------------------------------------- |
| Web framework         | Django 5.2                                          |
| GeoDjango / spatial   | `django.contrib.gis`, PostGIS, GDAL                 |
| REST API              | `django-tastypie`                                   |
| Forms / UI            | `django-crispy-forms` + `crispy-bootstrap5`         |
| GeoJSON serialization | `djgeojson` / `django.core.serializers` `"geojson"` |
| GeoPackage output     | `fudgeo`                                            |
| JSON serialization    | `orjson` (imported as `json`)                       |
| CSV serialization     | `unicodecsv` (imported as `csv`)                    |
| Static files          | `whitenoise` with Brotli compression                |
| Environment config    | `dbca_utils.utils.env`                              |
| SSO authentication    | `dbca_utils.middleware.SSOLoginMiddleware`          |
| Database URL          | `dj_database_url`                                   |
| Error tracking        | `sentry-sdk[django]`                                |
| Linter                | `ruff` (line-length 140)                            |
| Template linter       | `djlint` (profile: django)                          |
| ASGI server           | `gunicorn` with `uvloop`                            |
| Test fixtures         | `mixer` (from `mixer.backend.django`)               |
| Azure blob storage    | `azure-storage-blob`                                |

---

## Coding Conventions

### General

- **Line length:** 140 characters (`ruff` enforced — do not wrap earlier).
- **Type hints:** Use them on function signatures, especially in `utils.py` and `harvest.py`.
- **Return type annotations:** Use `-> str`, `-> int`, `-> bool`, `-> None` consistently.
- **Logging:** Obtain loggers by module name at module level — `LOGGER = logging.getLogger("tracking")`. Log to stdout only (no file handlers).
- **f-strings:** Prefer f-strings for string formatting.

### Imports

- `orjson` is always imported as `import orjson as json` — use `json.loads()` / `json.dumps()` accordingly.
- `unicodecsv` is always imported as `import unicodecsv as csv`.
- Group imports: stdlib → third-party → Django → local app.

### Settings & Environment

- All environment variables are read through `dbca_utils.utils.env(name, default)`. **Never** use `os.environ` directly.
- Secrets must never be hardcoded; always rely on environment variables.
- The application version is read from `pyproject.toml` at runtime — keep `APPLICATION_VERSION_NO` sourced from there.
- Timezone is `"Australia/Perth"` — always use `timezone.now()` (not `datetime.now()`) and store aware datetimes.

### Models

- Use `django.contrib.gis.db.models` not `django.db.models` (to support spatial fields).
- Spatial fields use WGS84 / EPSG:4326.
- `Device` is the central model; `LoggedPoint` stores historical positions.
- Choice field constants are defined as module-level string/int constants before `CHOICES` tuples (see `DISTRICT_*` pattern).
- Models override `save()` to populate denormalised display fields (e.g. `district_display`, `callsign_display`, `rin_display`).
- Model `clean()` enforces business-rule validation; raise `django.forms.ValidationError`.
- Use `class Meta: ordering` to set a sensible default ordering.
- `DEFAULT_AUTO_FIELD = "django.db.models.AutoField"` — do not use BigAutoField unless justified.

### Views

- Use **class-based views** (CBVs): `ListView`, `DetailView`, `UpdateView`, `TemplateView`, `View`.
- Always set `http_method_names` explicitly on views to restrict allowed HTTP methods.
- Use `reverse("tracking:<name>")` — URL patterns are namespaced under `app_name = "tracking"`.
- Authorization checks belong in `dispatch()` — return `HttpResponseForbidden` directly.
- For multi-format download views (GeoJSON / CSV / GeoPackage) use a `format` query parameter or class attribute.
- Pass JavaScript configuration to templates via a `javascript_context` dict in `get_context_data()`.
- Prefer `orjson` (`import orjson as json`) for JSON serialization in views.
- Use `StreamingHttpResponse` for large data exports to avoid memory pressure.

### Forms

- Use `django-crispy-forms` with Bootstrap 5 (`crispy_bootstrap5`).
- Define layout using `FormHelper`, `Layout`, `Fieldset`, `Field`, `Submit`, etc.
- Always set `CRISPY_TEMPLATE_PACK = "bootstrap5"`.

### REST API (Tastypie)

- All API resources extend `APIResource` (which extends `ModelResource`).
- Use `generate_meta()` and `generate_filtering()` utility functions for `Meta` class generation.
- The API base path is `/api/v1/`.
- Use `CSVSerializer` (extends `Serializer`) to support CSV output alongside JSON.
- Use `HttpCache` for cache-control headers on resources.
- `TASTYPIE_DEFAULT_FORMATS = ["json"]` and `TASTYPIE_DATETIME_FORMATTING = "iso-8601-strict"`.

### URL Patterns

- All `tracking` app URLs are namespaced: `app_name = "tracking"`.
- Old-style URL patterns are kept as permanent `RedirectView` entries rather than removed.
- Resource-style paths follow `devices/`, `devices/<int:pk>/`, `devices/<int:pk>/update/` etc.

### Management Commands

- One command per harvest source in `tracking/management/commands/`.
- Commands delegate to functions in `tracking/harvest.py` — keep command classes thin.
- Use `add_arguments()` with `required=True/False` and `action="store"` / `action="store_true"`.

### Harvest / Data Ingestion

- Parse functions live in `tracking/utils.py` (e.g. `parse_tracplus_row`, `parse_dfes_feature`).
- Save functions live in `tracking/harvest.py` (e.g. `save_iriditrak`, `save_tracplus`).
- Always call `validate_latitude_longitude(lat, lon)` before creating a `LoggedPoint`.
- Use `get_or_create` for `Device` lookups; use `update_or_create` where appropriate.
- Use `typing.Literal` for `device_type` parameters.

### Testing

- Use `django.test.TestCase` for all tests.
- Use `mixer.blend(Model, ...)` from `mixer.backend.django` to create test fixtures — do **not** use `Model.objects.create()` for fixture generation.
- Use `self.client.force_login(User.objects.create(username="testuser"))` for authenticated test cases.
- Use `reverse("tracking:<name>")` to build URLs in tests — never hardcode URL strings.
- Assert HTTP status codes and response `Content-Type` headers explicitly.
- Test files follow the naming convention `test_<module>.py` inside the app directory.

### Signals

- Connect signals via the `@receiver` decorator, not `Signal.connect()`.
- Signal handlers live in `tracking/signals.py` and are connected in `TrackingConfig.ready()`.

### Middleware

- Custom middleware uses the callable-class pattern with `__init__(self, get_response)` and `__call__(self, request)`.
- Health-check endpoints (`/readyz`, `/livez`) are handled by `HealthCheckMiddleware` before the security middleware stack.

---

## Spatial / GeoJSON Conventions

- All spatial data is stored and served in WGS84 / EPSG:4326.
- GeoJSON serialization uses Django's built-in `django.core.serializers` with the `"geojson"` format (registered via `djgeojson`).
- GeoPackage exports use `fudgeo` — use `WGS84` constant and `SpatialReferenceSystem` from `tracking/utils.py`.
- Content types: `application/vnd.geo+json` for GeoJSON, `text/csv` for CSV, `application/x-sqlite3` for GeoPackage.

---

## Authentication & Authorisation

- SSO login is handled by `dbca_utils.middleware.SSOLoginMiddleware`.
- Group-based authorisation: users must be in the `DEVICE_EDITOR_USER_GROUP` group (default: `"Edit Resource Tracking Device"`) or be a superuser to edit devices.
- New users are automatically added to this group via the `post_save` signal on `User`.
- The Django admin is available at `/admin/` with a custom site header.

---

## Deployment

- **Container:** Multi-stage Docker build using `uv` for dependency installation.
- **Server:** Gunicorn ASGI with 4 workers, uvloop, port 8080.
- **Kubernetes:** Kustomize manifests in `kustomize/` — `base/` plus `overlays/prod/` and `overlays/uat/`.
- **Static files:** Collected to `staticfiles/` at build time via `manage.py collectstatic`.
- **Migrations:** Run separately — never baked into the Docker image startup.

---

## What to Avoid

- Do **not** use `os.environ` directly — always use `dbca_utils.utils.env()`.
- Do **not** use `datetime.datetime.now()` — always use `django.utils.timezone.now()`.
- Do **not** use `django.db.models` for models that need spatial fields — use `django.contrib.gis.db.models`.
- Do **not** add function-based views — use class-based views.
- Do **not** use `pip install` — use `uv add` to manage dependencies.
- Do **not** hardcode URLs — always use `reverse()`.
- Do **not** edit files under `staticfiles/` or `tracking/migrations/` by hand.
- Do **not** disable Sentry in production code.
- Do **not** suppress Django security middleware or bypass CSRF protection.

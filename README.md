# Airport Service API

A Django REST Framework API for managing airports, routes, aircraft, crews,
flights, and ticket bookings. Users sign in with an email address and authenticate
using JWT (SimpleJWT). Local development uses SQLite.

## 1. Local setup

Windows PowerShell commands with Python 3.14 (the tested environment):

```powershell
git clone https://github.com/lukianlukian/airport-api.git
cd airport-api
git switch develop
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` instead
of `python`. On Linux/macOS, run `python3 -m venv .venv` and
`source .venv/bin/activate`, then use the same Python commands.
The `createsuperuser` command asks for an email and password; no username is required.

No `.env` file is required or loaded automatically. The settings are intended
for local development: SQLite, `DEBUG=True`, and a development secret key in
settings.py. Public deployments need separate secret, DEBUG, and host settings.

### Run with Docker

On Windows, start Docker Desktop with Linux containers. From the project root:

```powershell
docker compose up --build -d
docker compose exec web python manage.py createsuperuser
docker compose ps
```

Open http://127.0.0.1:8000/api/docs/. Migrations run automatically before the
server starts. Stop any local runserver process already using port 8000.

```powershell
# Follow logs
docker compose logs -f web
# Run tests inside the container
docker compose exec web python manage.py test
# Stop containers and preserve the database
docker compose down
# Rebuild and start again, including after code changes
docker compose up --build -d
```

`Dockerfile` builds a Python image with the application and runs it as a
non-root user. `compose.yaml` configures the port, API healthcheck, and the
`airport_data` named volume for SQLite under `/data`.
The container database is separate from the local `db.sqlite3`, so create
users and sample data on the first run. `docker compose down` preserves the
volume; adding `-v` deletes it and its data.

`requirements-runtime.txt` contains only API dependencies. The original
`requirements.txt` also includes development tools and unrelated libraries.
Update both files when adding an application dependency.
`.dockerignore` excludes the local database, .env files, virtual environments,
and caches from the build context. Docker setup does not require a `.env` file.

This setup uses Django runserver for local development and demonstrations.
Code is copied into the image, so code changes require rebuilding.
See the [Docker Compose documentation](https://docs.docker.com/compose/gettingstarted/)
for details about Compose and volumes.

## 2. API documentation

- Swagger UI: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/
- OpenAPI: http://127.0.0.1:8000/api/schema/
- Browsable API: http://127.0.0.1:8000/api/airport/
- Browsable API login: http://127.0.0.1:8000/api-auth/login/

Swagger/ReDoc load UI assets from a CDN, so the browser needs internet access.
To reproduce the documentation setup in another project:

```powershell
python -m pip install drf-spectacular==0.30.0 django-filter==26.1
```

Add `drf_spectacular` and `django_filters` to INSTALLED_APPS in
`airport_service/settings.py`, along with these settings:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "airport.pagination.AirportPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_THROTTLE_RATES": {"order_create": "10/hour"},
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Airport Service API",
    "DESCRIPTION": "Flights, routes, aircraft and ticket booking with JWT authentication.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}
```

The following routes are configured in `airport_service/urls.py`:

```python
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView,
)

# Entries in urlpatterns:
path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
```

The schema is generated from serializers and viewsets and documents JWT
authentication and filter parameters. Validate and export it with:

```powershell
python manage.py spectacular --file schema.yaml --validate --fail-on-warn
```

## 3. Features and custom behavior

| Feature | Implementation and purpose |
| --- | --- |
| Pagination | `airport/pagination.py`: PageNumberPagination, 10 items by default, `?page=2&page_size=20`, maximum 100. Response fields: `count`, `next`, `previous`, `results`. |
| Filtering | `airport/filters.py`: DjangoFilterBackend for Route/Flight replaces manual query_params handling. `source` and `destination` match part of an **airport name**, case-insensitively. |
| Flight date | `?date=2026-10-01` filters by departure date in UTC. Invalid dates return 400. Filters can be combined. |
| Permissions | `airport/permissions.py`: anyone can read reference data and flights; POST/PUT/PATCH/DELETE require `is_staff=True`. |
| Booking | Authenticated users create orders with a nonempty ticket list. The server assigns the owner. GET orders returns only the current user's orders, including for staff. |
| Throttling | `airport/throttles.py`: up to 10 order creation requests per hour per user, then 429 with Retry-After. GET is unrestricted; invalid POST requests also count toward the limit. |
| Flight representations | Lists show available seat counts; detail responses include the route, aircraft, crew, and occupied seats. |

All four additions are enabled: pagination limits response size, filters provide
validation and documented parameters, permissions separate schedule management
from booking, and throttling limits request frequency.
To disable order throttling, remove `OrderViewSet.get_throttles`.
DRF throttling uses a cache and does not enforce an exact quota under concurrent
requests. The default local cache is not shared between processes; multiple
processes require a shared cache.

| Resource under `/api/airport/` | Operations |
| --- | --- |
| `airports/`, `routes/`, `airplane-types/`, `airplanes/`, `crews/`, `flights/` | GET list/detail; staff: POST, PUT, PATCH, DELETE |
| `orders/` | GET own orders and POST bookings; authentication required |

There is no standalone Ticket endpoint or Order detail endpoint.

## 4. Registration → JWT → authenticated requests

1. POST an email and password to `/api/user/register/`.
2. POST the same credentials to `/api/user/token/` to obtain `access` and `refresh`.
3. Send the `Authorization: Bearer <access>` header with authenticated requests.
4. POST the refresh token to `/api/user/token/refresh/` to obtain a new access token.
5. Use GET/PATCH `/api/user/me/` to view or update your profile.

Access tokens expire after 30 minutes; refresh tokens expire after one day.
In Swagger, click **Authorize** and paste only the access token into `jwtAuth`;
the Bearer prefix is added automatically.
For the Browsable API, sign in at `/api-auth/login/` with your email and password.
This creates a separate session; HTML forms include a CSRF token.

The examples below use Bash/Git Bash (available on Windows).
Replace the flight ID with an existing ID and choose an available seat.

```bash
BASE=http://127.0.0.1:8000
curl -X POST "$BASE/api/user/register/" \
  -H 'Content-Type: application/json' \
  -d '{"email":"passenger@example.com","password":"DemoPass123!"}'

curl -X POST "$BASE/api/user/token/" \
  -H 'Content-Type: application/json' \
  -d '{"email":"passenger@example.com","password":"DemoPass123!"}'

ACCESS='paste the access token from the response'
REFRESH='paste the refresh token from the response'
curl "$BASE/api/user/me/" -H "Authorization: Bearer $ACCESS"
curl "$BASE/api/airport/flights/?source=Heathrow&destination=Gaulle&date=2026-10-01&page_size=5"
curl "$BASE/api/airport/flights/1/"

curl -X POST "$BASE/api/airport/orders/" \
  -H "Authorization: Bearer $ACCESS" \
  -H 'Content-Type: application/json' \
  -d '{"tickets":[{"flight":1,"row":1,"seat":1}]}'
curl "$BASE/api/airport/orders/" -H "Authorization: Bearer $ACCESS"

curl -X POST "$BASE/api/user/token/refresh/" \
  -H 'Content-Type: application/json' \
  -d "{\"refresh\":\"$REFRESH\"}"

# Obtain a superuser access token using the same token endpoint:
STAFF_ACCESS='paste the staff access token'
curl -X POST "$BASE/api/airport/airports/" \
  -H "Authorization: Bearer $STAFF_ACCESS" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Heathrow","closest_big_city":"London"}'
```

For an empty database, a staff user first creates two Airport records, a Route,
an AirplaneType, an Airplane, optional Crew records, and a Flight.
Use the IDs returned by POST requests. Regular users can then book seats.

## 5. Validation

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py spectacular --file schema.yaml --validate --fail-on-warn
```

Tests cover registration and the email user manager, JWT authentication,
prevention of is_staff escalation, permissions for reference data and flights,
order privacy, booking, pagination, filters, throttling, and documentation endpoints.

## 6. Database diagram and PR preparation

- [Tables and relationships for draw.io](docs/database.md).
- [Screenshot checklist and develop → main workflow](docs/finalization.md).
- [PR description template](docs/pr-description.md).

Configuration references:
[drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/readme.html),
[django-filter + DRF](https://django-filter.readthedocs.io/en/stable/guide/rest_framework.html),
[DRF throttling](https://www.django-rest-framework.org/api-guide/throttling/).

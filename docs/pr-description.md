## Changes

Airport Service API provides airport, route, aircraft, and crew management,
flight schedules, and ticket booking. Only staff can modify reference data
and flights; passengers can read schedules and create orders.
Authenticated users can list only their own orders.

- OpenAPI via drf-spectacular: `/api/schema/`, Swagger `/api/docs/`, ReDoc `/api/redoc/`.
- PageNumberPagination: 10 items by default, configurable page_size up to 100.
- django-filter for routes/flights: source, destination, and date, with date validation.
- Staff write permissions, IsAuthenticated, and ownership filtering for orders.
- POST orders throttling: 10 requests per hour per user; GET is unrestricted.
- Email UserManager for registration and createsuperuser, with a manager migration.
- SessionAuthentication and login for Browsable API forms.
- English README with setup, JWT, and curl examples; database structure and screenshot checklist.
- Dockerfile and Docker Compose for local development: automatic migrations,
  persistent PostgreSQL storage, a healthcheck, and a non-root process.

Beyond basic CRUD/JWT, this adds documentation, pagination, declarative filters,
access control, throttling, Docker support, and regression tests.

## Validation before publishing

- [ ] `python manage.py check`
- [ ] `python manage.py makemigrations --check --dry-run`
- [ ] `python manage.py test`
- [ ] `python manage.py spectacular --file schema.yaml --validate --fail-on-warn`
- [ ] `docker compose config --quiet`
- [ ] Build and run the Docker container successfully.
- [ ] Check Swagger/Browsable API in a browser.
- [ ] Attach the database diagram export and screenshots listed in `docs/finalization.md`.

## Diagram and screenshots

See `docs/database.md` for tables, cardinalities, and the Mermaid diagram.
Before publishing, attach the draw.io export, Swagger overview, flight list/detail,
staff create form, registration/JWT screens with secret values hidden,
a successful booking (201), and a denied write request (403).

## Notes

List responses now return count/next/previous/results instead of a plain array.
Apply migrations with `python manage.py migrate`.
Throttling uses the default local cache; multiple processes need a shared cache,
and the limit is not an exact quota under concurrent requests.
The Docker setup uses Django runserver for local development.

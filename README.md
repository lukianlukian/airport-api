# Airport Service API

A Django REST Framework API for managing airports, routes, aircraft, crews,
flights, and ticket bookings. Built with email-based authentication and JWT.

## Features

- Browse airports, routes, aircraft types, aircraft, crews, and flights.
- View flight details, available seat counts, and occupied seats.
- Book tickets and view your own orders.
- Register, sign in with JWT, and manage your profile.
- Staff-only access to create, update, and delete reference data and flights.

## Highlights

- Route and flight filters by airport name; flight filtering by departure date.
- Pagination: 10 items by default, configurable up to 100.
- Order creation limited to 10 requests per hour per user.
- OpenAPI documentation with Swagger UI and ReDoc.
- Docker Compose with automatic migrations and persistent SQLite storage.
- [Database structure and relationships](docs/database.md).

## URLs

Base URL: `http://127.0.0.1:8000`

| URL | Purpose |
| --- | --- |
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | OpenAPI schema |
| `/api/airport/` | Browsable API root |
| `/api/airport/airports/` | Airports |
| `/api/airport/routes/` | Routes |
| `/api/airport/airplane-types/` | Aircraft types |
| `/api/airport/airplanes/` | Aircraft |
| `/api/airport/crews/` | Crews |
| `/api/airport/flights/` | Flights |
| `/api/airport/orders/` | List your orders or create a booking |
| `/api/user/register/` | Register |
| `/api/user/token/` | Obtain JWT access and refresh tokens |
| `/api/user/token/refresh/` | Refresh an access token |
| `/api/user/token/verify/` | Verify a token |
| `/api/user/me/` | Current user profile |
| `/api-auth/login/` | Browsable API login |
| `/admin/` | Django administration |

Use `Authorization: Bearer <access_token>` for authenticated API requests.
Resource detail URLs use `<id>/`; orders support list and create only.

## Screenshots

Airport list in the Browsable API:

![Airport list](screenshots/Screenshot%202026-09-22%20181800.png)

Route list with filtering:

![Route list with filters](screenshots/Screenshot%202026-09-22%20181820.png)

Flight request in Postman:

![Flight list request in Postman](screenshots/Screenshot%202026-09-22%20183059.png)

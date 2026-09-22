from datetime import (
    datetime,
    timezone,
)
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase

from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    Crew,
    Flight,
    Order,
    Route,
)
from airport.throttles import OrderCreateThrottle


class AirportAPITests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user("reader@example.com", "Secret123!")
        self.staff = get_user_model().objects.create_user("staff@example.com", "Secret123!", is_staff=True)
        self.source = Airport.objects.create(name="Heathrow", closest_big_city="London")
        self.destination = Airport.objects.create(name="Charles de Gaulle", closest_big_city="Paris")
        self.route = Route.objects.create(source=self.source, destination=self.destination, distance=350)
        self.kind = AirplaneType.objects.create(name="Jet")
        self.airplane = Airplane.objects.create(name="A320", rows=20, seats_in_row=6, airplane_type=self.kind)
        self.crew = Crew.objects.create(first_name="Alex", last_name="Smith")
        self.flight = Flight.objects.create(
            route=self.route, airplane=self.airplane,
            departure_time=datetime(2026, 10, 1, 12, tzinfo=timezone.utc),
            arrival_time=datetime(2026, 10, 1, 14, tzinfo=timezone.utc),
        )

    def test_catalog_permissions(self):
        resources = {
            "airports": (self.source.pk, {"name": "Other", "closest_big_city": "Rome"}),
            "routes": (self.route.pk, {"source": self.destination.pk, "destination": self.source.pk, "distance": 350}),
            "airplane-types": (self.kind.pk, {"name": "Propeller"}),
            "airplanes": (self.airplane.pk, {"name": "Other", "rows": 10, "seats_in_row": 4, "airplane_type": self.kind.pk}),
            "crews": (self.crew.pk, {"first_name": "Sam", "last_name": "Jones"}),
            "flights": (self.flight.pk, {"route": self.route.pk, "airplane": self.airplane.pk, "departure_time": "2026-10-02T12:00:00Z", "arrival_time": "2026-10-02T14:00:00Z"}),
        }
        for resource, (pk, payload) in resources.items():
            url = f"/api/airport/{resource}/"
            with self.subTest(resource=resource):
                self.client.force_authenticate(None)
                self.assertEqual(self.client.get(url).status_code, 200)
                self.assertEqual(self.client.post(url, payload).status_code, 401)
                self.client.force_authenticate(self.user)
                self.assertEqual(self.client.post(url, payload).status_code, 403)
                self.assertEqual(self.client.patch(f"{url}{pk}/", payload).status_code, 403)
                self.assertEqual(self.client.delete(f"{url}{pk}/").status_code, 403)
                self.client.force_authenticate(self.staff)
                response = self.client.post(url, payload)
                self.assertEqual(response.status_code, 201, response.data)
                new_url = f"{url}{response.data['id']}/"
                self.assertEqual(self.client.patch(new_url, payload).status_code, 200)
                self.assertEqual(self.client.delete(new_url).status_code, 204)

    def test_pagination(self):
        Airport.objects.bulk_create([Airport(name=f"Airport {i}", closest_big_city="City") for i in range(105)])
        response = self.client.get("/api/airport/airports/")
        self.assertEqual(len(response.data["results"]), 10)
        self.assertEqual(response.data["count"], 107)
        self.assertIsNotNone(response.data["next"])
        response = self.client.get("/api/airport/airports/?page_size=1000")
        self.assertEqual(len(response.data["results"]), 100)
        self.assertEqual(self.client.get("/api/airport/airports/?page=999").status_code, 404)

    def test_filters(self):
        for resource in ("routes", "flights"):
            url = f"/api/airport/{resource}/"
            self.assertEqual(self.client.get(url, {"source": "HEATH", "destination": "Gaulle"}).data["count"], 1)
            self.assertEqual(self.client.get(url, {"source": "missing"}).data["count"], 0)
        url = "/api/airport/flights/"
        self.assertEqual(self.client.get(url, {"date": "2026-10-01"}).data["count"], 1)
        self.assertEqual(self.client.get(url, {"date": "2026-10-02"}).data["count"], 0)
        self.assertEqual(self.client.get(url, {"date": "invalid"}).status_code, 400)

    def test_orders_require_authentication_and_are_private(self):
        url = "/api/airport/orders/"
        payload = {"tickets": [{"flight": self.flight.pk, "row": 1, "seat": 1}]}
        self.assertEqual(self.client.get(url).status_code, 401)
        self.assertEqual(self.client.post(url, payload, format="json").status_code, 401)
        Order.objects.create(user=self.staff)
        self.client.force_authenticate(self.user)
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(Order.objects.get(pk=response.data["id"]).user, self.user)
        self.assertEqual(self.client.get(url).data["count"], 1)

    def test_only_order_creation_is_throttled(self):
        self.client.force_authenticate(self.user)
        url = "/api/airport/orders/"
        with patch.object(OrderCreateThrottle, "rate", "1/hour", create=True):
            response = self.client.post(url, {"tickets": [{"flight": self.flight.pk, "row": 1, "seat": 1}]}, format="json")
            self.assertEqual(response.status_code, 201)
            self.assertEqual(self.client.post(url, {}, format="json").status_code, 429)
            self.assertEqual(self.client.get(url).status_code, 200)
            self.client.force_authenticate(self.staff)
            self.assertEqual(self.client.post(url, {}, format="json").status_code, 400)

    def test_documentation_endpoints(self):
        for url in ("/api/schema/", "/api/docs/", "/api/redoc/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

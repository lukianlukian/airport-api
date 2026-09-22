from django.db.models import Count, F
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from airport.filters import FlightFilter, RouteFilter
from airport.permissions import IsStaffOrReadOnly
from airport.throttles import OrderCreateThrottle
from rest_framework.viewsets import GenericViewSet

from airport.models import (
    Airport, Route, AirplaneType, Airplane, Crew, Flight, Order
)
from airport.serializers import (
    AirportSerializer,
    RouteSerializer, RouteListSerializer, RouteDetailSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer, AirplaneListSerializer,
    CrewSerializer,
    FlightSerializer, FlightListSerializer, FlightDetailSerializer,
    OrderSerializer, OrderListSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsStaffOrReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination").order_by("id")
    serializer_class = RouteSerializer
    permission_classes = (IsStaffOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RouteFilter

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.order_by("id")
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsStaffOrReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type").order_by("id")
    serializer_class = AirplaneSerializer
    permission_classes = (IsStaffOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        return AirplaneSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.order_by("id")
    serializer_class = CrewSerializer
    permission_classes = (IsStaffOrReadOnly,)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.select_related("route__source", "route__destination", "airplane")
        .prefetch_related("crew", "tickets")
        .annotate(
            tickets_available=F("airplane__rows") * F("airplane__seats_in_row")
            - Count("tickets")
        )
        .order_by("-departure_time", "id")
    )
    serializer_class = FlightSerializer
    permission_classes = (IsStaffOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FlightFilter

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer


class OrderViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    queryset = Order.objects.prefetch_related("tickets__flight").order_by("-created_at", "id")
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_throttles(self):
        return [OrderCreateThrottle()] if self.action == "create" else []

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset.none()
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

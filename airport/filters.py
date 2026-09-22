from django_filters import rest_framework as filters

from airport.models import (
    Flight,
    Route,
)


class RouteFilter(filters.FilterSet):
    source = filters.CharFilter(field_name="source__name", lookup_expr="icontains")
    destination = filters.CharFilter(field_name="destination__name", lookup_expr="icontains")

    class Meta:
        model = Route
        fields = ("source", "destination")


class FlightFilter(filters.FilterSet):
    source = filters.CharFilter(field_name="route__source__name", lookup_expr="icontains")
    destination = filters.CharFilter(field_name="route__destination__name", lookup_expr="icontains")
    date = filters.DateFilter(field_name="departure_time", lookup_expr="date")

    class Meta:
        model = Flight
        fields = ("source", "destination", "date")

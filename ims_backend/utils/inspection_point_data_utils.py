from geopy.distance import geodesic
from rest_framework import status
from rest_framework.response import Response


def get_user_location(request):
    """Extracts and validates user's latitude and longitude from query parameters."""
    try:
        user_lat = float(request.query_params.get("latitude"))
        user_lon = float(request.query_params.get("longitude"))
        return user_lat, user_lon
    except (TypeError, ValueError):
        return Response(
            {"error": "Invalid or missing latitude/longitude."},
            status=status.HTTP_400_BAD_REQUEST,
        )


def sort_evinces_by_distance(evinces, user_location):
    """Sorts evinces based on their proximity to the user without using Point and Distance."""
    user_lat, user_lon = user_location

    try:
        evinces_with_distance = [
            {
                **format_inspection_point(
                    evince, geodesic_distance(user_lat, user_lon, evince)
                ),
                "distance": geodesic_distance(user_lat, user_lon, evince),
            }
            for evince in evinces
        ]

        sorted_evinces = sorted(evinces_with_distance, key=lambda x: x["distance"])

        return sorted_evinces
    except Exception as e:
        return []


def geodesic_distance(lat1, lon1, evince):
    """Calculates the geodesic distance between two points using geopy."""
    lat2, lon2 = evince.inspection_point.latitude, evince.inspection_point.longitude
    return geodesic((lat1, lon1), (lat2, lon2)).meters


def format_inspection_point(evince, distance):
    """Formats inspection point data for the response."""
    return {
        "inspections_point_id": evince.inspection_point.id,
        "inspections_point_name": evince.inspection_point.name,
        "longitude": evince.inspection_point.longitude,
        "latitude": evince.inspection_point.latitude,
        "number_of_evinces_with_respect_to_user": evince.inspection_point.evince_set.count(),
        "number_of_evinces_with_status_of_results_entered": evince.inspection_point.evince_set.filter(
            status="ResultsEntered"
        ).count(),
        "distance": distance,
    }

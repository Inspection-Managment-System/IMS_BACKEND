from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.services.admin_dashboard import (
    get_entity_breakdown_counts, get_evince_status_counts,
    get_evince_status_overview, get_top_business_units_by_evince_count,
    get_top_managers, statistic_cards_data)
from users.models import User


class AdminChartsViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="entity_breakdown")
    def entity_breakdown(self, request):
        user_id = request.query_params.get("user")
        if not user_id:
            return Response({"error": "User ID is required."}, status=400)

        try:
            user = User.objects.get(id=int(user_id))
            data = get_entity_breakdown_counts(user)
            if "error" in data:
                return Response(data, status=400)

            return Response(data, status=200)
        except User.DoesNotExist:
            return Response(
                {"error": f"User with ID {user_id} does not exist."}, status=404
            )
        except ValueError:
            return Response({"error": "Invalid user ID."}, status=400)

    @action(detail=False, methods=["get"], url_path="evince_status_counts")
    def evince_status_counts(self, request):
        user_id = request.query_params.get("user")
        time_period = request.query_params.get("time_period", "all")

        if not user_id:
            return Response({"error": "User ID is required."}, status=400)

        try:
            data = get_evince_status_counts(
                user_id=int(user_id), time_period=time_period
            )

            if "error" in data:
                return Response(data, status=400)

            return Response(data, status=200)
        except ValueError:
            return Response({"error": "Invalid user ID."}, status=400)

    @action(detail=False, methods=["get"], url_path="evince_status_overview")
    def evince_status_overview(self, request):
        time_period = request.query_params.get("time_period", "all")
        user_id = request.query_params.get("user")

        if not user_id:
            return Response({"error": "User ID is required."}, status=400)

        try:
            data = get_evince_status_overview(user_id, time_period)
            return Response(data, status=200)
        except ValueError:
            return Response({"error": "Invalid user ID."}, status=400)

    @action(detail=False, methods=["get"], url_path="evince_status_overall_counts")
    def evince_status_counts(self, request):
        time_period = request.query_params.get("time_period", "all")
        user_id = request.query_params.get("user")

        if not user_id:
            return Response({"error": "User ID is required."}, status=400)

        try:
            data = get_evince_status_counts(user_id, time_period)
            return Response(data, status=200)
        except ValueError:
            return Response({"error": "Invalid user ID."}, status=400)

    @action(
        detail=False, methods=["get"], url_path="top_business_units_by_evince_count"
    )
    def top_business_units_by_evince_count(self, request):
        user_id = request.query_params.get("user")
        limit = request.query_params.get("limit", 5)

        if not user_id:
            return Response({"error": "User ID is required."}, status=400)

        try:
            data = get_top_business_units_by_evince_count(user_id, int(limit))
            return Response(data, status=200)
        except ValueError:
            return Response({"error": "Invalid user ID or limit."}, status=400)

    @action(detail=False, methods=["get"], url_path="top_managers")
    def top_managers(self, request):
        time_period = request.query_params.get("time_period", "all")
        limit = request.query_params.get("limit", 5)

        try:
            data = get_top_managers(time_period, int(limit))
            return Response(data, status=200)
        except ValueError:
            return Response({"error": "Invalid time period or limit."}, status=400)

    @action(detail=False, methods=["get"], url_path="overall_counts")
    def overall_counts(self, request):
        user_id = request.query_params.get("user")
        if not user_id:
            return Response({"error": "User ID is required."}, status=400)

        try:
            user = User.objects.get(id=int(user_id))
            data = statistic_cards_data(user_id=user.id)
            return Response(data, status=200)
        except User.DoesNotExist:
            return Response(
                {"error": f"User with ID {user_id} does not exist."}, status=404
            )
        except ValueError:
            return Response({"error": "Invalid user ID."}, status=400)

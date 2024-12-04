from datetime import timedelta

from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.services.manager_dashboard import (
    get_average_processing_time, get_business_unit_data,
    get_evince_status_overview_for_manager, get_inspectors_list,
    get_manager_stats, get_manager_sunburst_data, get_top_business_units,
    get_top_inspectors_by_evinces)
from inspection_management.models import Evince
from users.models import User, UserProfile


class ManagerChartsViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="manager_evinces_overview")
    def manager_evinces_overview(self, request):
        user_id = request.query_params.get("user")
        if not user_id:
            return Response({"error": "User ID is required."}, status=400)

        try:
            user = User.objects.get(id=user_id)

            data_groups = user.userprofile.data_groups.all()

            if not data_groups.exists():
                return Response(
                    {"error": "No data groups assigned to the user."}, status=400
                )

            data_group_ids = data_groups.values_list("id", flat=True)
            data = get_evince_status_overview_for_manager(user_id, data_group_ids)

            return Response(data, status=200)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=False, methods=["get"], url_path="top_inspectors_by_evinces")
    def top_inspectors_by_evinces(self, request):
        manager_id = request.query_params.get("user")
        inspector_id = request.query_params.get("inspector_id")

        if not manager_id:
            return Response({"error": "Manager ID is required."}, status=400)
        if not inspector_id:
            return Response({"error": "Inspector ID is required."}, status=400)

        try:
            user = User.objects.get(id=manager_id)
            data_groups = user.userprofile.data_groups.all()

            if not data_groups.exists():
                return Response(
                    {"error": "Manager has no associated data groups."}, status=404
                )

            data_group_ids = data_groups.values_list("id", flat=True)

            data = get_top_inspectors_by_evinces(
                manager_id, data_group_ids, inspector_id
            )
            if not data:
                return Response(
                    {"error": "No data found for the specified inspector."}, status=404
                )

            return Response(data[0], status=200)

        except User.DoesNotExist:
            return Response({"error": "Manager not found."}, status=404)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=False, methods=["get"], url_path="list_inspectors")
    def list_inspectors(self, request):
        manager_id = request.query_params.get("user")

        if not manager_id:
            return Response({"error": "Manager ID is required."}, status=400)

        try:
            inspectors = get_inspectors_list(manager_id)
            return Response(inspectors, status=200)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=False, methods=["get"], url_path="manager_stats")
    def manager_stats(self, request):
        manager_id = request.query_params.get("user")
        if not manager_id:
            return Response({"error": "Manager ID is required."}, status=400)

        stats_result = get_manager_stats(manager_id)
        if "error" in stats_result:
            return Response(
                {"error": stats_result["error"]}, status=stats_result["status"]
            )
        return Response(stats_result["data"], status=stats_result["status"])

    @action(detail=False, methods=["get"], url_path="average_time")
    def average_time(self, request):
        manager_id = request.query_params.get("user")
        if not manager_id:
            return Response({"error": "Manager ID is required."}, status=400)

        response = get_average_processing_time(manager_id)
        status = response.pop("status", 200)
        return Response(response, status=status)

    @action(detail=False, methods=["get"], url_path="sunburst_data")
    def sankey_data(self, request):
        user_id = request.query_params.get("user")
        if not user_id:
            return Response({"error": "User ID is required."}, status=400)
        data = get_manager_sunburst_data(user_id)
        if "error" in data:
            return Response(data, status=data.get("status", 500))
        return Response(data, status=200)

    @action(detail=False, methods=["get"], url_path="business_unit_status")
    def business_unit_status(self, request):
        manager_id = request.query_params.get("user")
        business_unit_id = request.query_params.get("business_unit")

        if not manager_id:
            return Response({"error": "Manager ID is required."}, status=400)

        data = get_business_unit_data(manager_id, business_unit_id)
        if "error" in data:
            return Response(data, status=data.get("status", 500))

        return Response(data, status=200)

    @action(detail=False, methods=["get"], url_path="top_business_units")
    def top_business_units(self, request):
        user_id = request.query_params.get("user")
        if not user_id:
            return Response({"error": "User ID is required."}, status=400)

        result = get_top_business_units(user_id)
        if "error" in result:
            return Response(result, status=result.get("status", 500))
        return Response(result["data"], status=200)

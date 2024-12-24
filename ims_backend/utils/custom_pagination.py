from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        request = self.request
        pagination = request.query_params.get("pagination", "false").lower()

        if pagination == "true":
            return Response(
                {
                    "currentPage": self.page.number,
                    "pageCount": self.page.paginator.num_pages,
                    "totalResults": self.page.paginator.count,
                    "pageSize": self.page.paginator.per_page,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "results": data,
                }
            )

        return Response(data)

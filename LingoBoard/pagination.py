from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    # sensible defaults
    page_size = 20
    page_size_query_param = "page_size"  # allow client to change page size
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

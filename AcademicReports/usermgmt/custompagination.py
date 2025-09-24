
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
    page_query_param = 'page'

    def get_paginated_response(self, data):
        # Get the total number of items
        total_count = self.page.paginator.count
        # Determine the current page
        current_page = self.request.query_params.get(self.page_query_param, 1)
        try:
            current_page = int(current_page)
        except ValueError:
            current_page = 1

        # Get page_size from request or use the default
        page_size = self.get_page_size(self.request)

        # Calculate bottom ('from') and top ('to') values
        bottom_value = (current_page - 1) * page_size + 1 if total_count > 0 else 0
        top_value = min(current_page * page_size, total_count)

        # Get next and previous page numbers
        next_page_number = self.page.next_page_number() if self.page.has_next() else None
        previous_page_number = self.page.previous_page_number() if self.page.has_previous() else None

        # Status and message
        status = 1 if total_count > 0 else 0
        message = "Data successfully obtained" if total_count > 0 else "Data not found"

        return Response({
            'total_count': total_count,
            'total_pages': self.page.paginator.num_pages,
            'next_page': self.get_next_link(),
            'previous_page': self.get_previous_link(),
            'current_page_number': current_page,
            'next_page_number': next_page_number,
            'previous_page_number': previous_page_number,
            'default_page_size': self.page_size,
            'from': bottom_value,
            'to': top_value,
            'status': status,
            'message': message,
            'results': data
        })
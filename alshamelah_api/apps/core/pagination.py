from collections import OrderedDict

from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 10

    def paginate_queryset(self, queryset, request, view=None):
        if view is not None:
            self.page_size = getattr(view, 'page_size', None)
        return super(CustomPageNumberPagination, self).paginate_queryset(
            queryset, request, view
        )


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """
    A limit/offset based style with custom count and result name. For example:

    http://api.example.org/accounts/?limit=100
    http://api.example.org/accounts/?offset=400&limit=100
    http://api.example.org/accounts/?offset=400&limit=100&count=total
    http://api.example.org/accounts/?offset=400&limit=100&count=total&result=rows
    """
    default_limit = 10
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 200
    template = 'rest_framework/pagination/numbers.html'
    result_name = 'results'
    count_name = 'count'

    def paginate_queryset(self, queryset, request, view=None):
        if 'count' in request.query_params:
            self.count_name = request.query_params['count']

        if 'result' in request.query_params:
            self.result_name = request.query_params['result']

        return super(CustomLimitOffsetPagination, self).paginate_queryset(queryset, request, view=view)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            (self.count_name, self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            (self.result_name, data)
        ]))

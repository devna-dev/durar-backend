import coreapi
import coreschema
import django_filters
from django.utils.encoding import force_str
from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi

from .models import Book


class BookFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter()
    sub_category = django_filters.NumberFilter()
    author = django_filters.NumberFilter()
    title = django_filters.CharFilter(lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')
    from_year = django_filters.NumberFilter(field_name='publish_date__year', lookup_expr='gte')
    to_year = django_filters.NumberFilter(field_name='publish_date__year', lookup_expr='lte')

    class Meta:
        model = Book
        fields = ['category', 'author', 'title', 'content']


class BooksFilterBackend(DjangoFilterBackend):
    category_query_param = 'category'
    category_query_description = _('Filter books by sub category id')
    sub_category_query_param = 'sub_category'
    sub_category_query_description = _('Filter books by sub category id')
    author_query_param = 'author'
    author_query_description = _('Filter books by author id')
    title_query_param = 'title'
    title_query_description = _('Filter books which contains this title')
    content_query_param = 'content'
    content_query_description = _('Filter books which contains this content')
    audio_query_param = 'has_audio'
    audio_query_description = _('Filter books which has audio files')
    from_year_query_param = 'from_year'
    from_year_query_description = _('Filter books published from this year')
    to_year_query_param = 'to_year'
    to_year_query_description = _('Filter books published to this year')
    sort_query_param = 'sort'
    sort_query_description = _('Sort books by (publish_date, .. etc) "-" is for descending order')

    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(
                name=self.category_query_param,
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title='Category',
                    description=force_str(self.category_query_description)
                )
            ),
            coreapi.Field(
                name=self.sub_category_query_param,
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title='Sub Category',
                    description=force_str(self.sub_category_query_description)
                )
            ),
            coreapi.Field(
                name=self.author_query_param,
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title='Author',
                    description=force_str(self.author_query_description)
                )
            ),
            coreapi.Field(
                name=self.title_query_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title='Title',
                    description=force_str(self.title_query_description)
                )
            ),
            coreapi.Field(
                name=self.content_query_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title='Title',
                    description=force_str(self.category_query_description)
                )
            ),
            coreapi.Field(
                name=self.audio_query_param,
                required=False,
                location='query',
                schema=coreschema.Boolean(
                    title='Has Audio',
                    description=force_str(self.audio_query_description)
                )
            ),
            coreapi.Field(
                name=self.from_year_query_param,
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title='From Year',
                    description=force_str(self.from_year_query_description)
                )
            ),
            coreapi.Field(
                name=self.to_year_query_param,

                required=False,
                location='query',
                schema=coreschema.Integer(
                    title='To Year',
                    description=force_str(self.to_year_query_description)
                )
            ),
            coreapi.Field(
                name=self.sort_query_param,
                required=False,
                location='query',
                schema=coreschema.Enum(
                    title='Sort by',
                    description=force_str(self.sort_query_description),
                    enum=['publish_date', 'add_date', 'author', 'has_audio', 'pages', 'downloads', 'reads', 'rate',
                          '-publish_date', '-add_date', '-author', '-has_audio', '-pages', '-downloads', '-reads',
                          '-rate',
                          ]
                )
            ),
        ]
        return fields

    def get_schema_operation_parameters(self, view):
        parameters = [
            {
                'name': self.category_query_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.category_query_description),
                'schema': {
                    'type': 'integer',
                },
            }, {
                'name': self.sub_category_query_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.sub_category_query_description),
                'schema': {
                    'type': 'integer',
                },
            }, {
                'name': self.author_query_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.author_query_description),
                'schema': {
                    'type': 'integer',
                },
            }, {
                'name': self.title_query_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.title_query_description),
                'schema': {
                    'type': 'string',
                },
            }, {
                'name': self.content_query_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.content_query_description),
                'schema': {
                    'type': 'string',
                },
            }, {
                'name': self.audio_query_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.audio_query_description),
                'schema': {
                    'type': 'boolean',
                },
            }, {
                'name': self.from_year_query_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.from_year_query_description),
                'schema': {
                    'type': 'integer',
                },
            }, {
                'name': self.to_year_query_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.to_year_query_description),
                'schema': {
                    'type': 'integer',
                },
            }, {
                'name': self.sort_query_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.sort_query_description),
                'schema': {
                    'type': 'string',
                },
            }
        ]
        return parameters


BookParameters = [openapi.Parameter('tashkeel', openapi.IN_QUERY, description="View with tashkeel", required=False,
                                    type=openapi.TYPE_BOOLEAN), ]

BookPageParameters = [openapi.Parameter('tashkeel', openapi.IN_QUERY, description="View with tashkeel", required=False,
                                        type=openapi.TYPE_BOOLEAN),
                      openapi.Parameter('page', openapi.IN_QUERY, description="Get page", required=False,
                                        type=openapi.TYPE_INTEGER, default=None), ]

BookPageSearchParameters = [
    openapi.Parameter('tashkeel', openapi.IN_QUERY, description="View with tashkeel", required=False,
                      type=openapi.TYPE_BOOLEAN),
    openapi.Parameter('word', openapi.IN_QUERY, description="Search for word in book", required=True,
                      type=openapi.TYPE_STRING, default=None), ]

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import coreapi
import coreschema
import django_filters
from django.db.models import Avg, F, Count, Q
from django.utils.encoding import force_str
from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pyarabic.araby import strip_tashkeel
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from .models import Book, BookMark, BookComment, BookHighlight, BookAudio, BookPDF, BookReview, BookReviewLike, \
    ReadBook, FavoriteBook, BookSuggestion
from .permissions import CanManageBook, CanSubmitBook, CanManageBookMark, CanManageBookRating, CanManageBookAudio, \
    CanManageBookComment, CanManageBookHighlight, CanManageBookPdf, CanManageBookReview, CanManageUserData
from .serializers import BookSerializer, BookMarkSerializer, BookPDFSerializer, BookAudioSerializer, \
    BookCommentSerializer, \
    BookHighlightSerializer, BookRatingSerializer, UploadBookSerializer, BookListSerializer, SubmitBookSerializer, \
    BookReviewSerializer, BookReviewLikeSerializer, ReadBookSerializer, FavoriteBookSerializer, BookSuggestionSerializer
from ..core.pagination import CustomLimitOffsetPagination, CustomPageNumberPagination


class BookFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter()
    author = django_filters.CharFilter(lookup_expr='unaccent__icontains')
    title = django_filters.CharFilter(lookup_expr='unaccent__icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Book
        fields = ['category', 'author', 'title', 'content']


class BooksFilterBackend(DjangoFilterBackend):
    category_query_param = 'category'
    category_query_description = _('Filter books by category id')
    author_query_param = 'author'
    author_query_description = _('Filter books by author')
    title_query_param = 'title'
    title_query_description = _('Filter books which contains this title')
    content_query_param = 'content'
    content_query_description = _('Filter books which contains this content')
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
                name=self.sort_query_param,
                required=False,
                location='query',
                schema=coreschema.Enum(
                    title='Sort by',
                    description=force_str(self.sort_query_description),
                    enum=['publish_date', 'add_date', 'author', 'has_audio', 'pages', 'downloads', 'reads', 'rate',
                          'searches',
                          '-publish_date', '-add_date', '-author', '-has_audio', '-pages', '-downloads', '-reads',
                          '-rate',
                          '-searches'
                          ]
                )
            )
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
                'name': self.author_query_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.author_query_description),
                'schema': {
                    'type': 'string',
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


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.filter(approved=True).prefetch_related('category', 'book_ratings')
    permission_classes = (CanManageBook,)
    filterset_class = BookFilter
    filter_backends = (BooksFilterBackend,)
    parser_classes = [MultiPartParser]

    @property
    def pagination_class(self):
        if 'offset' in self.request.query_params:
            return CustomLimitOffsetPagination
        else:
            return CustomPageNumberPagination

    def get_queryset(self):
        if self.action == 'list':
            return Book.objects.filter(approved=True).prefetch_related('category', 'book_ratings', 'downloads',
                                                                       'listens', 'searches', 'book_media', 'readers')
        return self.queryset

    def filter_queryset(self, queryset):
        ordering = self.request.query_params.get('sort', 'author')
        if self.request.user.is_superuser:
            queryset = Book.objects.all().prefetch_related('category', 'book_ratings')
        queryset = super(BookViewSet, self).filter_queryset(queryset)
        if ordering == 'rate':
            return queryset.annotate(avg_rate=Avg('book_ratings__rating')).order_by(F('avg_rate').asc(nulls_last=False))
        if ordering == '-rate':
            return queryset.annotate(avg_rate=Avg('book_ratings__rating')).order_by(F('avg_rate').desc(nulls_last=True))
        if ordering == 'add_date':
            ordering = 'creation_time'
        if ordering == '-add_date':
            ordering = '-creation_time'
        if ordering in ['pages', '-pages']:
            ordering = ordering + 's_count'
        if ordering == 'downloads':
            return queryset.annotate(download_count=Count('downloads')).order_by(
                F('download_count').asc(nulls_last=False))
        if ordering == '-downloads':
            return queryset.annotate(download_count=Count('downloads')).order_by(
                F('download_count').desc(nulls_last=True))
        if ordering == 'reads':
            return queryset.annotate(read_count=Count('readers')).order_by(F('read_count').asc(nulls_last=False))
        if ordering == '-reads':
            return queryset.annotate(read_count=Count('readers')).order_by(F('read_count').desc(nulls_last=True))
        if ordering == 'searches':
            return queryset.annotate(search_count=Count('searches')).order_by(F('search_count').asc(nulls_last=False))
        if ordering == '-searches':
            return queryset.annotate(search_count=Count('searches')).order_by(F('search_count').desc(nulls_last=True))
        if ordering == 'has_audio':
            return queryset.annotate(has_audio=Count('book_media', filter=Q(book_media__type='audio') & Q(
                book_media__approved=True))).order_by(F('has_audio').asc(nulls_last=True))
        if ordering == '-has_audio':
            return queryset.annotate(has_audio=Count('book_media', filter=Q(book_media__type='audio') & Q(
                book_media__approved=True))).order_by(F('has_audio').desc(nulls_last=True))

        return queryset.order_by(ordering)

    def get_serializer_class(self):
        if self.action == 'create':
            return UploadBookSerializer
        if self.action == 'list':
            return BookListSerializer
        if self.action == 'submit':
            return SubmitBookSerializer
        return BookSerializer

    def list(self, request, *args, **kwargs):
        request.encoding = 'utf-8'
        return super(BookViewSet, self).list(request, args, kwargs)

    @swagger_auto_schema(manual_parameters=BookParameters)
    def retrieve(self, request, *args, **kwargs):
        request.encoding = 'utf-8'
        # Client can control the page using this query parameter.
        book = self.get_object()
        tashkeel = request.query_params.get('tashkeel', None) != 'false'
        if not tashkeel:
            book.content = strip_tashkeel(book.content)

        serializer = self.get_serializer(book)

        return Response(serializer.data)

    @swagger_auto_schema(manual_parameters=BookPageParameters)
    @action(detail=True, methods=['get'], permission_classes=[])
    def view(self, request, pk=None):
        book = self.get_object()
        tashkeel = request.query_params.get('tashkeel', None) != 'false'
        page = request.query_params.get('page', "1")
        if page: page = int(page)
        if not page or not book.pages or page > len(book.pages):
            return Response(_('Page not found'), status=status.HTTP_400_BAD_REQUEST)
        data = book.pages[page]['text']
        if not tashkeel and data:
            data = strip_tashkeel(data)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], permission_classes=[CanSubmitBook])
    def submit(self, request, pk=None):
        self.partial_update(request, {'pk': pk, })
        return Response(status=status.HTTP_202_ACCEPTED)


class NestedBookViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    def dispatch(self, request, *args, **kwargs):
        book_id = kwargs.get('parent_lookup_book', None)
        self.book = get_object_or_404(Book, pk=book_id)
        self.user = self.request.user
        return super(NestedBookViewSet, self).dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(NestedBookViewSet, self).get_serializer_context()
        if hasattr(self, 'book') and hasattr(self, 'user'):
            context.update(
                book=self.book,
                user=self.user
            )
        return context


class BookMarkViewSet(NestedBookViewSet):
    serializer_class = BookMarkSerializer
    book_query = 'book'
    permission_classes = (CanManageBookMark,)

    def get_queryset(self):
        return BookMark.objects.filter(user_id=self.request.user.id)


class BookCommentViewSet(NestedBookViewSet):
    serializer_class = BookCommentSerializer
    permission_classes = (CanManageBookComment,)
    book_query = 'book'

    def get_queryset(self):
        return BookComment.objects.filter(user_id=self.request.user.id)


class BookHighlightViewSet(NestedBookViewSet):
    serializer_class = BookHighlightSerializer
    permission_classes = (CanManageBookHighlight,)
    book_query = 'book'

    def get_queryset(self):
        return BookHighlight.objects.filter(user_id=self.request.user.id)


class BookAudioViewSet(NestedBookViewSet):
    queryset = BookAudio.objects.filter(approved=True)
    serializer_class = BookAudioSerializer
    permission_classes = (CanManageBookAudio,)
    book_query = 'book'


class BookPdfViewSet(NestedBookViewSet):
    queryset = BookPDF.objects.filter(approved=True)
    serializer_class = BookPDFSerializer
    permission_classes = (CanManageBookPdf,)
    book_query = 'book'


class BookRatingViewSet(NestedBookViewSet):
    serializer_class = BookRatingSerializer
    permission_classes = (CanManageBookRating,)
    book_query = 'book'


class BookReviewViewSet(NestedBookViewSet):
    serializer_class = BookReviewSerializer
    permission_classes = (CanManageBookReview,)
    book_query = 'book'


class Authours(views.APIView):
    def get_object(self, queryset=None):
        return self.queryset.none()

    queryset = Book.objects.all().values_list('author', flat=True)

    def get(self, *args, **kwargs):
        data = list(filter(lambda a: a is not None and a != '', self.queryset.all()))
        return Response(data,
                        status=status.HTTP_200_OK)


authors_view = Authours.as_view()


class CategoryBooks(views.APIView):
    def get_object(self, queryset=None):
        return self.queryset.none()

    queryset = Book.objects.filter(approved=True)

    def get(self, *args, **kwargs):
        data = self.queryset.filter(category_id=kwargs.pop('category_id'))
        serializer = BookListSerializer(instance=data, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


category_books_view = CategoryBooks.as_view()


class BookReviewLikesViewSet(viewsets.ModelViewSet):
    def dispatch(self, request, *args, **kwargs):
        review_id = kwargs.get('review_id', None)
        book_id = kwargs.get('book_id', None)
        self.book = get_object_or_404(Book, pk=book_id)
        self.review = get_object_or_404(BookReview, pk=review_id)
        self.user = self.request.user
        return super(BookReviewLikesViewSet, self).dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(BookReviewLikesViewSet, self).get_serializer_context()
        if hasattr(self, 'review') and hasattr(self, 'user') and hasattr(self, 'book'):
            context.update(
                book=self.book,
                review=self.review,
                user=self.user
            )
        return context

    def get_queryset(self):
        return BookReviewLike.objects.filter(review_id=self.review.id, user_id=self.request.user.id)

    def list(self, request, *args, **kwargs):
        return Response(BookReviewLike.objects.count(review_id=self.review.id), status=status.HTTP_200_OK)

    serializer_class = BookReviewLikeSerializer
    permission_classes = (CanManageBookReview,)


class ReadViewSet(viewsets.ModelViewSet):
    permission_classes = (CanManageUserData,)
    serializer_class = ReadBookSerializer

    @property
    def pagination_class(self):
        if 'offset' in self.request.query_params:
            return CustomLimitOffsetPagination
        else:
            return CustomPageNumberPagination

    def get_queryset(self):
        return ReadBook.objects.filter(user_id=self.request.user.id).prefetch_related('book')


class FavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = (CanManageUserData,)
    serializer_class = FavoriteBookSerializer

    @property
    def pagination_class(self):
        if 'offset' in self.request.query_params:
            return CustomLimitOffsetPagination
        else:
            return CustomPageNumberPagination

    def get_queryset(self):
        return FavoriteBook.objects.filter(user_id=self.request.user.id).prefetch_related('book')


class SuggestionsViewSet(viewsets.ModelViewSet):
    permission_classes = (CanManageUserData,)
    serializer_class = BookSuggestionSerializer

    @property
    def pagination_class(self):
        if 'offset' in self.request.query_params:
            return CustomLimitOffsetPagination
        else:
            return CustomPageNumberPagination

    def get_queryset(self):
        return BookSuggestion.objects.filter(user_id=self.request.user.id)


class UserDownloads(views.APIView):
    def get_object(self, queryset=None):
        return self.queryset.none()

    queryset = Book.objects
    permission_classes = [CanManageUserData]

    def get(self, *args, **kwargs):
        data = self.queryset.filter(downloads__user_id=self.request.user.id)
        serializer = BookListSerializer(instance=data, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


user_downloads_view = UserDownloads.as_view()


class UserListens(views.APIView):
    def get_object(self, queryset=None):
        return self.queryset.none()

    queryset = Book.objects
    permission_classes = [CanManageUserData]

    def get(self, *args, **kwargs):
        data = self.queryset.filter(listens__user_id=self.request.user.id)
        serializer = BookListSerializer(instance=data, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


user_listens_view = UserListens.as_view()

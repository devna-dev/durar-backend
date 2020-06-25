#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db.models import Avg, F, Count, Q
from django.utils.translation import ugettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from pyarabic.araby import strip_tashkeel
from rest_framework import viewsets, status, views, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin
from rolepermissions.checkers import has_permission

from .filters import BookFilter, BooksFilterBackend, BookParameters, BookPageParameters
from .models import Book, BookMark, BookComment, BookHighlight, BookAudio, BookPDF, BookReview, BookReviewLike, \
    ReadBook, FavoriteBook, BookSuggestion, DownloadBook, ListenBook, SearchBook
from .permissions import CanManageBook, CanSubmitBook, CanManageBookMark, CanManageBookAudio, \
    CanManageBookComment, CanManageBookHighlight, CanManageBookPdf, CanManageBookReview, CanManageUserData
from .serializers import BookSerializer, BookMarkSerializer, BookPDFSerializer, BookAudioSerializer, \
    BookCommentSerializer, \
    BookHighlightSerializer, UploadBookSerializer, BookListSerializer, SubmitBookSerializer, \
    BookReviewSerializer, BookReviewLikeSerializer, FavoriteBookSerializer, \
    BookSuggestionSerializer, DownloadBookSerializer, BookSearchSerializer, BookSearchListSerializer
from ..core.pagination import CustomLimitOffsetPagination, CustomPageNumberPagination
from ..users.roles import AppPermissions


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.filter(approved=True).prefetch_related('category', 'reviews')
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
            return Book.objects.filter(approved=True).prefetch_related('category', 'reviews', 'downloads',
                                                                       'listens', 'book_media', 'readers')
        return self.queryset

    def filter_queryset(self, queryset):
        ordering = self.request.query_params.get('sort', 'author')
        if self.request.user.is_superuser:
            queryset = Book.objects.all().prefetch_related('category', 'reviews')
        queryset = super(BookViewSet, self).filter_queryset(queryset)
        if self.request.query_params.get('has_audio', None) is not None:
            has_audio = self.request.query_params.get('has_audio') != 'true'
            queryset = queryset.filter(book_media__isnull=False, book_media__type='audio',
                                       book_media__approved=True).prefetch_related(
                'book_media') if not has_audio else queryset.annotate(
                audio_count=Count('book_media', filter=Q(book_media__type='audio') & Q(
                    book_media__approved=True))).filter(audio_count=0)
        if ordering == 'rate':
            return queryset.annotate(avg_rate=Avg('reviews__rating')).order_by(F('avg_rate').asc(nulls_last=False))
        if ordering == '-rate':
            return queryset.annotate(avg_rate=Avg('reviews__rating')).order_by(F('avg_rate').desc(nulls_last=True))
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
        # if ordering == 'searches':
        #     return queryset.annotate(search_count=Count('searches')).order_by(F('search_count').asc(nulls_last=False))
        # if ordering == '-searches':
        #     return queryset.annotate(search_count=Count('searches')).order_by(F('search_count').desc(nulls_last=True))
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
        if self.action == 'download':
            return DownloadBookSerializer
        if self.action == 'listen':
            return BookAudioSerializer
        return BookSerializer

    def list(self, request, *args, **kwargs):
        request.encoding = 'utf-8'
        if request.user.id and request.query_params.keys():
            keys = list(request.query_params.keys())
            non_filter_keys = ['sort', 'page', 'page_size']
            for key in non_filter_keys:
                if key in keys:
                    keys.remove(key)
            if len(keys) > 0:
                serializer_context = {'request': request}
                search = BookSearchSerializer(data=request.query_params, context=serializer_context)
                if search.is_valid():
                    search.save()
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
        if has_permission(request.user, AppPermissions.edit_user_data):
            ReadBook.objects.update_or_create(book_id=pk, user_id=request.user.id)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], permission_classes=[CanSubmitBook])
    def submit(self, request, pk=None):
        self.partial_update(request, {'pk': pk, })
        return Response(status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['get'], permission_classes=[])
    def download(self, request, pk=None):
        serializer = self.get_serializer(self.get_object())
        if has_permission(request.user, AppPermissions.edit_user_data) and serializer.data:
            DownloadBook.objects.update_or_create(book_id=pk, user_id=request.user.id)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[])
    def listen(self, request, pk=None):
        serializer = self.get_serializer(BookAudio.objects.filter(approved=True, book_id=pk), many=True)
        if has_permission(request.user, AppPermissions.edit_user_data) and serializer.data:
            ListenBook.objects.update_or_create(book_id=pk, user_id=request.user.id)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


# class BookRatingViewSet(NestedBookViewSet):
#     serializer_class = BookRatingSerializer
#     permission_classes = (CanManageBookRating,)
#     book_query = 'book'


class BookReviewViewSet(NestedBookViewSet):
    queryset = BookReview.objects.all()
    serializer_class = BookReviewSerializer
    permission_classes = (CanManageBookReview,)
    book_query = 'book'


class CategoryBooksView(views.APIView):
    def get_object(self, queryset=None):
        return self.queryset.none()

    queryset = Book.objects.filter(approved=True)

    def get(self, *args, **kwargs):
        data = self.queryset.filter(category_id=kwargs.pop('category_id'))
        serializer = BookListSerializer(instance=data, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


category_books_view = CategoryBooksView.as_view()


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


class FavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = (CanManageUserData,)
    serializer_class = FavoriteBookSerializer

    def dispatch(self, request, *args, **kwargs):
        book_id = kwargs.get('book_id', None)
        self.book = get_object_or_404(Book, pk=book_id)
        self.user = self.request.user
        return super(FavoriteViewSet, self).dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(FavoriteViewSet, self).get_serializer_context()
        if hasattr(self, 'user') and hasattr(self, 'book'):
            context.update(
                book=self.book,
                user=self.user
            )
        return context

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


class UserBooksView(views.APIView):
    def get_object(self, queryset=None):
        return self.queryset.none()

    queryset = Book.objects
    permission_classes = [CanManageUserData]

    def get(self, *args, **kwargs):
        reads_serializer = BookListSerializer(instance=self.queryset.filter(readers__user_id=self.request.user.id),
                                              many=True)
        listens_serializer = BookListSerializer(instance=self.queryset.filter(listens__user_id=self.request.user.id),
                                                many=True)
        downloads_serializer = BookListSerializer(
            instance=self.queryset.filter(downloads__user_id=self.request.user.id),
            many=True)
        favorites_serializer = BookListSerializer(
            instance=self.queryset.filter(favorite_books__user_id=self.request.user.id),
            many=True)

        return Response({
            'reads': reads_serializer.data,
            'listens': listens_serializer.data,
            'downloads': downloads_serializer.data,
            'favorites': favorites_serializer.data
        },
            status=status.HTTP_200_OK)


user_books_view = UserBooksView.as_view()


class UserReadsView(views.APIView):
    def get_object(self, queryset=None):
        return self.queryset.none()

    queryset = Book.objects
    permission_classes = [CanManageUserData]

    def get(self, *args, **kwargs):
        data = self.queryset.filter(readers__user_id=self.request.user.id)
        serializer = BookListSerializer(instance=data, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


user_reads_view = UserReadsView.as_view()


class UserDownloadsView(views.APIView):
    def get_object(self, queryset=None):
        return self.queryset.none()

    queryset = Book.objects
    permission_classes = [CanManageUserData]

    def get(self, *args, **kwargs):
        data = self.queryset.filter(downloads__user_id=self.request.user.id)
        serializer = BookListSerializer(instance=data, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


user_downloads_view = UserDownloadsView.as_view()


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


class SortsListens(mixins.ListModelMixin, viewsets.GenericViewSet):
    def get_object(self, queryset=None):
        return self.queryset.none()

    queryset = Book.objects
    permission_classes = [CanManageUserData]

    def get(self, *args, **kwargs):
        data = [
            {'id': "publish_date", 'name': "publish_date_asc"}
            , {'id': "add_date", 'name': "add_date_asc"}
            , {'id': "author", 'name': "author_asc"}
            , {'id': "has_audio", 'name': "has_audio_asc"}
            , {'id': "pages", 'name': "pages_asc"}
            , {'id': "downloads", 'name': "downloads_asc"}
            , {'id': "reads", 'name': "reads_asc"}
            , {'id': "rate", 'name': "rate_asc"}
            , {'id': "-publish_date", 'name': "publish_date_desc"}
            , {'id': "-add_date", 'name': "add_date_desc"}
            , {'id': "-author", 'name': "author_desc"}
            , {'id': "-has_audio", 'name': "has_audio_desc"}
            , {'id': "-pages", 'name': "pages_desc"}
            , {'id': "-downloads", 'name': "downloads_desc"}
            , {'id': "-reads", 'name': "reads_desc"}
            , {'id': "-rate", 'name': "rate_desc"}
        ]
        return Response(data,
                        status=status.HTTP_200_OK)


class PopularBooksView(views.APIView):
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Book.objects.filter(approved=True)

    def get(self, request, *args, **kwargs):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        reads_serializer = BookListSerializer(
            instance=self.get_queryset().filter(readers__isnull=False).annotate(
                readers_count=Count('readers',
                                    filter=Q(creation_time__year=year) & Q(creation_time__month=month))).order_by(
                F('readers_count').desc(nulls_last=True))[:10],
            many=True)
        listens_serializer = BookListSerializer(
            instance=self.get_queryset().filter(listens__isnull=False).annotate(
                listens_count=Count('listens',
                                    filter=Q(creation_time__year=year) & Q(creation_time__month=month))).order_by(
                F('listens_count').desc(nulls_last=True))[:10],
            many=True)
        downloads_serializer = BookListSerializer(
            instance=self.get_queryset().filter(downloads__isnull=False).annotate(
                downloads_count=Count('downloads',
                                      filter=Q(creation_time__year=year) & Q(creation_time__month=month))).order_by(
                F('downloads_count').desc(nulls_last=True))[:10],
            many=True)

        recent_serializer = BookListSerializer(instance=self.get_queryset().order_by(F('creation_time').desc())[:10],
                                               many=True)

        return Response({
            'reads': reads_serializer.data,
            'listens': listens_serializer.data,
            'downloads': downloads_serializer.data,
            'recent': recent_serializer.data
        },
            status=status.HTTP_200_OK)


class PopularBooksViewSet(viewsets.GenericViewSet):
    permission_classes = (AllowAny,)

    @property
    def pagination_class(self):
        if 'offset' in self.request.query_params:
            return CustomLimitOffsetPagination
        else:
            return CustomPageNumberPagination

    def get_queryset(self):
        return Book.objects.filter(approved=True)

    @action(['get'], detail=False)
    def reads(self, request, *args, **kwargs):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        query = self.get_queryset().filter(readers__isnull=False).annotate(
            readers_count=Count('readers',
                                filter=Q(creation_time__year=year) & Q(creation_time__month=month))).order_by(
            F('readers_count').desc(nulls_last=True))
        page = self.paginate_queryset(query)
        reads_serializer = BookListSerializer(instance=page if page is not None else query, many=True)

        return Response(reads_serializer.data,
                        status=status.HTTP_200_OK) if page is None else self.get_paginated_response(
            reads_serializer.data)

    @action(['get'], detail=False)
    def listens(self, request, *args, **kwargs):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        query = self.get_queryset().filter(listens__isnull=False).annotate(
            listens_count=Count('listens',
                                filter=Q(creation_time__year=year) & Q(creation_time__month=month))).order_by(
            F('listens_count').desc(nulls_last=True))
        page = self.paginate_queryset(query)
        listens_serializer = BookListSerializer(instance=page if page is not None else query, many=True)

        return Response(listens_serializer.data,
                        status=status.HTTP_200_OK) if page is None else self.get_paginated_response(
            listens_serializer.data)

    @action(['get'], detail=False)
    def downloads(self, request, *args, **kwargs):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        query = self.get_queryset().filter(downloads__isnull=False).annotate(
            downloads_count=Count('downloads',
                                  filter=Q(creation_time__year=year) & Q(creation_time__month=month))).order_by(
            F('downloads_count').desc(nulls_last=True))
        page = self.paginate_queryset(query)
        downloads_serializer = BookListSerializer(instance=page if page is not None else query, many=True)

        return Response(downloads_serializer.data,
                        status=status.HTTP_200_OK) if page is None else self.get_paginated_response(
            downloads_serializer.data)

    @action(['get'], detail=False)
    def recent(self, request, *args, **kwargs):
        query = self.get_queryset().order_by(F('creation_time').desc())
        page = self.paginate_queryset(query)
        recent_serializer = BookListSerializer(instance=page if page is not None else query, many=True)

        return Response(recent_serializer.data,
                        status=status.HTTP_200_OK) if page is None else self.get_paginated_response(
            recent_serializer.data)


class SearchesViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = (CanManageUserData,)

    @property
    def pagination_class(self):
        if 'offset' in self.request.query_params:
            return CustomLimitOffsetPagination
        else:
            return CustomPageNumberPagination

    def get_queryset(self):
        return SearchBook.objects.filter(user_id=self.request.user.id)

    def get_serializer_class(self):
        if self.action == 'list':
            return BookSearchListSerializer
        return BookSearchSerializer

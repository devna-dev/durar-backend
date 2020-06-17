from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from .models import Book, BookMark, BookComment, BookHighlight, BookAudio, BookPDF
from .permissions import CanManageBook, CanSubmitBook, CanManageBookMark, CanManageBookRating, CanManageBookAudio, \
    CanManageBookComment, CanManageBookHighlight, CanManageBookPdf
from .serializers import BookSerializer, BookMarkSerializer, BookPDFSerializer, BookAudioSerializer, \
    BookCommentSerializer, \
    BookHighlightSerializer, BookRatingSerializer, UploadBookSerializer, BookListSerializer, SubmitBookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().prefetch_related('category', 'book_ratings')
    filter_fields = ('user',)
    permission_classes = (CanManageBook,)

    def get_serializer_class(self):
        if self.action == 'create':
            return UploadBookSerializer
        if self.action == 'list':
            return BookListSerializer
        if self.action == 'submit':
            return SubmitBookSerializer
        return BookSerializer

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
    queryset = BookAudio.objects.all()
    serializer_class = BookAudioSerializer
    permission_classes = (CanManageBookAudio,)
    book_query = 'book'


class BookPdfViewSet(NestedBookViewSet):
    queryset = BookPDF.objects.all()
    serializer_class = BookPDFSerializer
    permission_classes = (CanManageBookPdf,)
    book_query = 'book'


class BookRatingViewSet(NestedBookViewSet):
    serializer_class = BookRatingSerializer
    permission_classes = (CanManageBookRating,)
    book_query = 'book'

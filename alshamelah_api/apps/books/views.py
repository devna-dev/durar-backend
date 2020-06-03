from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from .models import Book, BookMark, BookRating, BookComment, BookHighlight, BookAudio, BookPDF
from .serializers import BookSerializer, BookMarkSerializer, BookPDFSerializer, BookAudioSerializer, \
    BookCommentSerializer, \
    BookHighlightSerializer, BookRatingSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookMarkViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = BookMark.objects.all()
    serializer_class = BookMarkSerializer
    book_query = 'book'


class BookCommentViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = BookComment.objects.all()
    serializer_class = BookCommentSerializer
    book_query = 'book'


class BookHighlightViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = BookHighlight.objects.all()
    serializer_class = BookHighlightSerializer
    book_query = 'book'


class BookAudioViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = BookAudio.objects.all()
    serializer_class = BookAudioSerializer
    book_query = 'book'


class BookPdfViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = BookPDF.objects.all()
    serializer_class = BookPDFSerializer
    book_query = 'book'


class BookRatingViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = BookRating.objects.all()
    serializer_class = BookRatingSerializer
    book_query = 'book'

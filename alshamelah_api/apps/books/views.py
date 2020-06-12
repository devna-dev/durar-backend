from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from .models import Book, BookMark, BookRating, BookComment, BookHighlight, BookAudio, BookPDF
from .permissions import CanManageBook
from .serializers import BookSerializer, BookMarkSerializer, BookPDFSerializer, BookAudioSerializer, \
    BookCommentSerializer, \
    BookHighlightSerializer, BookRatingSerializer
from ..users.models import EmailOTP


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_fields = ('user',)
    permission_classes = (
        CanManageBook,
    )

    def list(self, request, **kwargs):
        serializer = BookSerializer(self.queryset, many=True)
        if request.user and request.user.id:
            print(request.user.id)
            print(EmailOTP.objects.generate(request.user.id))
            print(EmailOTP.objects.verify(request.user.id, '288092', 360))
            print(EmailOTP.objects.verify(request.user.id, '288092', 2))
            print(EmailOTP.objects.verify(request.user.id, '288092', 2))
        return Response(serializer.data)


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

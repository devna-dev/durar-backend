from django.conf.urls import url
from django.urls import include, path
from rest_framework_extensions.routers import (
    ExtendedDefaultRouter as DefaultRouter
)

from .views import BookViewSet, BookMarkViewSet, BookAudioViewSet, BookCommentViewSet, BookHighlightViewSet, \
    BookPdfViewSet, \
    BookRatingViewSet, BookReviewViewSet, authors_view, category_books_view

router = DefaultRouter()

books_router = router.register(
    r'books', BookViewSet, 'books'
)
book_marks_routes = books_router.register(
    r'marks', BookMarkViewSet, 'book_marks',
    parents_query_lookups=['book'],
)

book_comments_routes = books_router.register(
    r'comments', BookCommentViewSet, 'book_comments',

    parents_query_lookups=['book']
)

book_highlights_routes = books_router.register(
    r'highlights', BookHighlightViewSet, 'book_highlights',
    parents_query_lookups=['book']
)

book_audio_routes = books_router.register(
    r'audio', BookAudioViewSet, 'book_audio',
    parents_query_lookups=['book']
)

book_pdf_routes = books_router.register(
    r'pdf', BookPdfViewSet, 'book_pdf',
    parents_query_lookups=['book']
)

book_rating_routes = books_router.register(
    r'rating', BookRatingViewSet, 'book_rating',
    parents_query_lookups=['book']
)
book_reviews_routes = books_router.register(
    r'reviews', BookReviewViewSet, 'book_reviews',

    parents_query_lookups=['book']
)
urlpatterns = [
    path(r"authors/", authors_view, name="authors"),
    path(r"categories/<category_id>/books/", category_books_view, name="category_books"),
    url(r'', include(router.urls))
]

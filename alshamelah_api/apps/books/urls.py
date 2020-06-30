from django.conf.urls import url
from django.urls import include, path
from rest_framework_extensions.routers import (
    ExtendedDefaultRouter as DefaultRouter
)

from .views import BookViewSet, BookMarkViewSet, BookAudioViewSet, BookNoteViewSet, \
    BookPdfViewSet, BookReviewViewSet, category_books_view, user_reads_view, FavoriteViewSet, \
    SuggestionsViewSet, user_listens_view, user_downloads_view, user_books_view, PopularBooksView, PopularBooksViewSet, \
    SearchesViewSet, PaperViewSet, ThesisViewSet, ActivitiesBooksView

router = DefaultRouter()

books_router = router.register(
    r'books', BookViewSet, 'books'
)

papers_router = router.register(
    r'activities/papers', PaperViewSet, 'papers'
)

thesis_router = router.register(
    r'activities/thesis', ThesisViewSet, 'thesis'
)

popular_books_router = router.register(
    r'books/popular', PopularBooksViewSet, 'popular_books'
)
book_marks_routes = books_router.register(
    r'marks', BookMarkViewSet, 'book_marks',
    parents_query_lookups=['book'],
)

book_notes_routes = books_router.register(
    r'notes', BookNoteViewSet, 'book_notes',

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
# book_rating_routes = books_router.register(
#     r'rating', BookRatingViewSet, 'book_rating',
#     parents_query_lookups=['book']
# )
book_reviews_routes = books_router.register(
    r'reviews', BookReviewViewSet, 'book_reviews',

    parents_query_lookups=['book']
)

user_favorites_router = router.register(
    r'user/favorites', FavoriteViewSet, 'favorites'
)

user_suggestions_router = router.register(
    r'user/suggestions', SuggestionsViewSet, 'suggestions'
)

user_searches_router = router.register(
    r'user/searches', SearchesViewSet, 'searches'
)

urlpatterns = [
    path(r"categories/<category_id>/books/", category_books_view, name="category_books"),
    path(r"user/books/", user_books_view, name="user_books"),
    path(r"user/reads/", user_reads_view, name="user_reads"),
    path(r"user/downloads/", user_downloads_view, name="user_downloads"),
    path(r"user/listens/", user_listens_view, name="user_listens"),
    path(r"books/popular/", PopularBooksView.as_view(), name="popular_books"),
    path(r"activities/", ActivitiesBooksView.as_view(), name="activities"),
    url(r'', include(router.urls))
]

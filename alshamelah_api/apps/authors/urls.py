from django.conf.urls import url
from django.urls import include
from rest_framework_extensions.routers import (
    ExtendedDefaultRouter as DefaultRouter
)

from .views import AuthorViewSet

router = DefaultRouter()

authors_router = router.register(
    r'authors', AuthorViewSet, 'authors'
)

urlpatterns = [
    url(r'', include(router.urls))
]

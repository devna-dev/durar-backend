from django.conf.urls import url
from django.urls import include
from rest_framework_extensions.routers import (
    ExtendedDefaultRouter as DefaultRouter
)

from .views import ChatRoomsViewSet

router = DefaultRouter()

categories_router = router.register(
    r'chatrooms', ChatRoomsViewSet, 'chatrooms'
)

urlpatterns = [
    url(r'', include(router.urls))
]

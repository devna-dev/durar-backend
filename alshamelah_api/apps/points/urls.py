from django.conf.urls import url
from django.urls import include
from rest_framework_extensions.routers import (
    ExtendedDefaultRouter as DefaultRouter
)

from .views import UserPointsViewSet

router = DefaultRouter()

categories_router = router.register(
    r'user/points', UserPointsViewSet, 'user_points'
)

urlpatterns = [
    url(r'', include(router.urls))
]

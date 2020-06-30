from django.conf.urls import url
from django.urls import include
from rest_framework_extensions.routers import (
    ExtendedDefaultRouter as DefaultRouter
)

from .views import PaymentsViewSet

router = DefaultRouter()

payments_router = router.register(
    r'payments', PaymentsViewSet, 'payments'
)

urlpatterns = [
    url(r'', include(router.urls))
]

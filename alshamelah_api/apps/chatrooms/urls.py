from django.conf.urls import url
from django.urls import include
from rest_framework_extensions.routers import (
    ExtendedDefaultRouter as DefaultRouter
)

from .views import SeminarsViewSet, DiscussionsViewSet, DiscussionsRegistrationViewSet, SeminarRegistrationViewSet

router = DefaultRouter()

seminars_registration_router = router.register(
    r'activities/seminars/registration', SeminarRegistrationViewSet, 'seminars_registration'
)
discussions_registration_router = router.register(
    r'activities/discussions/registration', DiscussionsRegistrationViewSet, 'discussions_registration'
)
seminars_router = router.register(
    r'activities/seminars', SeminarsViewSet, 'seminars'
)
discussions_router = router.register(
    r'activities/discussions', DiscussionsViewSet, 'discussions'
)

urlpatterns = [
    url(r'', include(router.urls))
]

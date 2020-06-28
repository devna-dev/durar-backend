from django.conf.urls import url
from django.urls import include, path
from rest_framework_extensions.routers import (
    ExtendedDefaultRouter as DefaultRouter
)

from .views import TermsView, PolicyView

router = DefaultRouter()

urlpatterns = [
    path(r"site/terms/", TermsView.as_view(), name="site_terms"),
    path(r"site/policy/", PolicyView.as_view(), name="site_policy"),
    url(r'', include(router.urls))
]

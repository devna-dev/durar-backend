from django.conf.urls import url
from django.urls import include, path
from rest_framework_extensions.routers import (
    ExtendedDefaultRouter as DefaultRouter
)

from .views import TermsView, PolicyView, AppUrlsView

router = DefaultRouter()

urlpatterns = [
    path(r"site/terms/", TermsView.as_view(), name="site_terms"),
    path(r"site/policy/", PolicyView.as_view(), name="site_policy"),
    path(r"site/app-urls/", AppUrlsView.as_view(), name="app_urls"),
    url(r'', include(router.urls))
]

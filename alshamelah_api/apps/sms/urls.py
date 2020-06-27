from django.conf.urls import url
from django.urls import include, path
from rest_framework_extensions.routers import (
    ExtendedDefaultRouter as DefaultRouter
)

from . import views

router = DefaultRouter()

urlpatterns = [
    path(r"sms/twilio/", views.TwilioStatusView.as_view(),
         name="sms_update_status"),
    url(r'', include(router.urls))
]

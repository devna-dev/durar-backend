from django.conf.urls import url
from django.urls import path, include
from rest_auth.urls import urlpatterns as rest_patterns
from rest_framework_extensions.routers import (
    ExtendedDefaultRouter as DefaultRouter
)

from . import views

router = DefaultRouter()

# user_router = router.register(
#     r'user', views.UserViewSet, 'user'
# )

user_notes_router = router.register(
    r'user/notes', views.UserNoteViewSet, 'user_notes'
)

user_notifications_router = router.register(
    r'user/notifications', views.UserNotificationsViewSet, 'user_notifications'
)

user_notification_settings_router = router.register(
    r'user/notification/settings', views.UserNotificationSettingViewSet, 'user_notification_settings'
)
accounts_urls = list(url for url in rest_patterns if url.name != 'rest_user_details')
user_urls = list(url for url in rest_patterns if url.name == 'rest_user_details')
urlpatterns = [
    path(r"accounts/verify-email/<key>/", views.confirm_email,
         name="account_confirm_email"),
    url(r'accounts/', include(accounts_urls)),
    url(r'', include(user_urls)),
    path(r"accounts/logout/", views.logout_view,
         name="account_logout"),
    url(r'', include(router.urls))
]

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
    path(r"accounts/verify-email/", views.VerifyEmailView.as_view(),
         name="account_confirm_email"),
    path(r"accounts/verify-email/<key>/", views.ConfirmEmailView.as_view(),
         name="account_confirm_email"),
    path(r"accounts/verify-phone/", views.VerifyPhoneView.as_view(),
         name="account_verify_phone"),
    path(r"accounts/verify-phone/<key>/", views.ConfirmPhoneView.as_view(),
         name="account_confirm_phone"),
    url(r'accounts/', include(accounts_urls)),
    url(r'', include(user_urls)),
    path(r"accounts/logout/", views.LogoutView.as_view(),
         name="account_logout"),
    path(r"user/daily-login/", views.DailyLoginView.as_view(),
         name="daily_login"),
    path(r"user/share/app/", views.ShareAppView.as_view(),
         name="share_app"),
    path(r"user/share/book/", views.ShareBookView.as_view(),
         name="share_book"),
    path(r"user/share/lecture/", views.ShareLectureView.as_view(),
         name="share_lecture"),
    path(r"user/share/highlight/", views.ShareHighlightView.as_view(),
         name="share_highlight"),
    path(r"user/lecture-attendance/", views.AttendLectureView.as_view(),
         name="attend_lecture"),
    url(r'', include(router.urls))
]

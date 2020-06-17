from django.urls import path

from . import views

urlpatterns = [
    path(r"user/verify-email/<key>/", views.confirm_email,
         name="account_confirm_email"),
    path(r"logout/", views.logout_view,
         name="account_logout"),
    # path('', include('django.contrib.auth.urls')),
]

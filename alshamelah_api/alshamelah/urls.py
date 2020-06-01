from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# from alshamelah_api.apps.swagger.views import SwaggerSchemaView



urlpatterns = [
    path("admin/", admin.site.urls),
    # url(r'swagger/$', SwaggerSchemaView.as_view()),
    path('accounts/', include('allauth.urls')),
    path('', include('apps.pages.urls')),
]

api_v1_urls = [
    path('users/', include('django.contrib.auth.urls')),
    url(r'^accounts/', include('rest_auth.urls')),
    url(r'^accounts/registration/', include('rest_auth.registration.urls')),
]

urlpatterns += [
    path(r'api/v1/', include(api_v1_urls))
]
if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns


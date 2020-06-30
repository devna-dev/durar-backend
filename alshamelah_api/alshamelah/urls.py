from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from .swagger_api_generator import SwaggerAPISchemaGenerator

urlpatterns = [
    path("admin/", admin.site.urls),
    path('accounts/', include('allauth.urls')),
]

api_v1_urls = [
    url(r'^users/', include('django.contrib.auth.urls')),
    url(r'^accounts/registration/', include('rest_auth.registration.urls')),
    path('', include('apps.users.urls')),
    path('', include('apps.categories.urls')),
    path('', include('apps.books.urls')),
    path('', include('apps.authors.urls')),
    path('', include('apps.support.urls')),
    path('', include('apps.chatrooms.urls')),
    path('', include('apps.sms.urls')),
    path('', include('apps.site_data.urls')),
    path('', include('apps.payments.urls')),
]

urlpatterns += [
    path(r'api/v1/', include(api_v1_urls))
]

api_info = openapi.Info(
    title="Al-Shamelah API",
    default_version='v1',
    description="api documentation",
    terms_of_service="",
    contact=openapi.Contact(email=""),
    license=openapi.License(name=""),
)

schema_view = get_schema_view(
    info=api_info,
    public=True,
    permission_classes=(AllowAny,),
    patterns=urlpatterns,
    generator_class=SwaggerAPISchemaGenerator
)

urlpatterns += [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^api-docs/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
    # url(r'', name='home')

]
if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns

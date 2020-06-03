from django.conf.urls import url
from django.urls import include
from rest_framework_extensions.routers import (
    ExtendedDefaultRouter as DefaultRouter
)

from .views import CategoryViewSet, SubCategoryViewSet

router = DefaultRouter()

categories_router = router.register(
    r'categories', CategoryViewSet, 'categories'
)
subcategory_routes = categories_router.register(
    r'sub-categories', SubCategoryViewSet, 'sub_categories',
    parents_query_lookups=['category']
)

urlpatterns = [
    url(r'', include(router.urls))
]

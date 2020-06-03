from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from .models import Category, SubCategory
from .serializers import CategorySerializer, SubCategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubCategoryViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    category_query = 'category'

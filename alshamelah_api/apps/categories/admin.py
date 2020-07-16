from django.contrib import admin

from .models import Category, SubCategory
from ..core.admin import BaseModelAdmin


@admin.register(Category)
class CategoryAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'name',
    )


@admin.register(SubCategory)
class SubCategoryAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'name',
        'category'
    )

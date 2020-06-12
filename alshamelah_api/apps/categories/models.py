from django.db import models
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_(u'name'), null=False, blank=False)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name=_(u'name'), null=False, blank=False)
    category = models.ForeignKey(Category, related_name='sub_categories', verbose_name=_(u'Category'), null=True,
                                 on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

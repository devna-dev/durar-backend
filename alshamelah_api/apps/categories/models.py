import os

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):
    def path(self, filename):
        return os.path.join(
            self.path,
            'image',
            filename
        )

    name = models.CharField(max_length=100, verbose_name=_(u'name'), null=False, blank=False)
    image = models.ImageField(
        upload_to=path,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    @property
    def path(self):
        if not self.pk:
            return None
        return os.path.join('categories', str(self.pk))

    def save(self, *args, **kwargs):
        if self.pk is None:
            saved_image = self.image
            self.image = None
            super(Category, self).save(*args, **kwargs)
            self.image = saved_image
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')

        super(Category, self).save(*args, **kwargs)


class SubCategory(models.Model):
    def path(self, filename):
        return os.path.join(
            self.path,
            'image',
            filename
        )

    name = models.CharField(max_length=100, verbose_name=_(u'name'), null=False, blank=False)
    image = models.ImageField(
        upload_to=path,
        blank=True,
        null=True
    )
    category = models.ForeignKey(Category, related_name='sub_categories', verbose_name=_(u'Category'), null=True,
                                 on_delete=models.SET_NULL)

    class Meta:
        verbose_name_plural = "Sub Categories"

    def __str__(self):
        return self.name

    @property
    def path(self):
        if not self.pk:
            return None
        return os.path.join('categories', str(self.category_id), 'sub-categories', str(self.pk))

    def save(self, *args, **kwargs):
        if self.pk is None:
            saved_image = self.image
            self.image = None
            super(SubCategory, self).save(*args, **kwargs)
            self.image = saved_image
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')

        super(SubCategory, self).save(*args, **kwargs)

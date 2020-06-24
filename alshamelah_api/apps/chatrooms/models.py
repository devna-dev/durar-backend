import os

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..core.models import BaseModel


class RoomType(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_(u'Name'), null=False, blank=False)

    class Meta:
        verbose_name_plural = "Chat Room Types"

    def __str__(self):
        return self.name


class ChatRoom(BaseModel):
    def get_path(self, filename):
        return os.path.join(
            self.path,
            'image',
            filename
        )

    title = models.CharField(max_length=100, verbose_name=_(u'Title'), null=False, blank=False)
    type = models.ForeignKey(RoomType, verbose_name=_(u'Type'), on_delete=models.CASCADE)
    description = models.CharField(max_length=8000, verbose_name=_(u'description'), null=True)
    lecturer = models.CharField(max_length=255, verbose_name=_(u'lecturer'), null=False, blank=False)
    date = models.DateField(verbose_name=_('Date'), null=False)
    from_time = models.TimeField(verbose_name=_('From Time'), null=False)
    to_time = models.TimeField(verbose_name=_('To Time'), null=False)
    image = models.ImageField(
        upload_to=get_path,
        blank=True,
        null=True
    )
    url = models.URLField(verbose_name=_(u'Hangout Url'))

    @property
    def path(self):
        if not self.pk:
            return None
        return os.path.join('chatrooms', str(self.pk))

    def save(self, *args, **kwargs):
        if self.pk is None:
            saved_image = self.image
            self.image = None
            super(ChatRoom, self).save(*args, **kwargs)
            self.image = saved_image
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')

        super(ChatRoom, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Chatrooms"
        ordering = ['-date', 'from_time']

    def __str__(self):
        return self.lecturer + ': ' + self.title

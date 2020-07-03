import os

from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from .managers import SeminarManager, DiscussionManager, DiscussionRegistrationManager, SeminarRegistrationManager
from ..core.models import BaseModel


class RoomType(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_(u'Name'), null=False, blank=False)

    class Meta:
        verbose_name_plural = "Chat Room Categories"

    def __str__(self):
        return self.name


class ChatRoom(BaseModel):
    TYPE_CHOICES = Choices(
        ('seminar', _(u'Seminar')),
        ('discussion', _(u'Discussion')),
    )

    def get_path(self, filename):
        return os.path.join(
            self.path,
            'image',
            filename
        )

    title = models.CharField(max_length=100, verbose_name=_(u'Title'), null=False, blank=False)
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
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name=_(u'Type'))

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


class Seminar(ChatRoom):
    objects = SeminarManager()

    class Meta:
        verbose_name_plural = "Seminars"
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Seminar, self).__init__(*args, **kwargs)
        self.type = 'seminar'


class Discussion(ChatRoom):
    objects = DiscussionManager()

    class Meta:
        verbose_name_plural = "Discussions"
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Discussion, self).__init__(*args, **kwargs)
        self.type = 'discussion'

    def __str__(self):
        return self.title


class ChatRoomRegistration(BaseModel):
    user = models.ForeignKey('users.User', related_name='registrations', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    chat_room = models.ForeignKey(ChatRoom, related_name='registrations', verbose_name=_(u'Chat Room'), null=False,
                                  on_delete=models.CASCADE)

    def __str__(self):
        return str(self.chat_room) + ', ' + str(self.user)


class DiscussionRegistration(ChatRoomRegistration):
    objects = DiscussionRegistrationManager()

    class Meta:
        verbose_name_plural = "Discussion Registrations"
        proxy = True


class SeminarRegistration(ChatRoomRegistration):
    objects = SeminarRegistrationManager()

    class Meta:
        verbose_name_plural = "Seminar Registrations"
        proxy = True

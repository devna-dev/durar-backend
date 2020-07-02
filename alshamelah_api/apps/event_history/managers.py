from django.db import models


class SeminarManager(models.Manager):
    def get_queryset(self):
        return super(SeminarManager, self).get_queryset().filter(
            type='seminar')


class DiscussionManager(models.Manager):
    def get_queryset(self):
        return super(DiscussionManager, self).get_queryset().filter(
            type='discussion')


class SeminarRegistrationManager(models.Manager):
    def get_queryset(self):
        return super(SeminarRegistrationManager, self).get_queryset().filter(
            chat_room__type='seminar')


class DiscussionRegistrationManager(models.Manager):
    def get_queryset(self):
        return super(DiscussionRegistrationManager, self).get_queryset().filter(
            chat_room__type='discussion')

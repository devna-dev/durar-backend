from django.db import models


class BookAudioManager(models.Manager):
    def get_queryset(self):
        return super(BookAudioManager, self).get_queryset().filter(
            type='audio')


class BookPDFManager(models.Manager):
    def get_queryset(self):
        return super(BookPDFManager, self).get_queryset().filter(
            type='pdf')

from django.db import models


class BookAudioManager(models.Manager):
    def get_queryset(self):
        return super(BookAudioManager, self).get_queryset().filter(
            type='audio')


class BookPDFManager(models.Manager):
    def get_queryset(self):
        return super(BookPDFManager, self).get_queryset().filter(
            type='pdf')


class BookManager(models.Manager):
    def get_queryset(self):
        return super(BookManager, self).get_queryset().filter(
            type='book')


class PaperManager(models.Manager):
    def get_queryset(self):
        return super(PaperManager, self).get_queryset().filter(
            type='paper')


class ThesisManager(models.Manager):
    def get_queryset(self):
        return super(ThesisManager, self).get_queryset().filter(
            type='thesis')

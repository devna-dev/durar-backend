from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from rest_framework.fields import JSONField

from ..core.models import BaseModel


class Payment(BaseModel):
    PAYMENT_CHOICES = Choices(
        ('credit_card', _(u'Credit Card')),
        ('apple_pay', _(u'Apple Pay')),
        ('google_pay', _(u'Google Pay')),
    )
    STATUS_CHOICES = Choices(
        ('pending', _(u'Pending')),
        ('success', _(u'Success')),
        ('failed', _(u'Failed')),
    )
    CURRENCY_CHOICES = Choices(
        ('usd', _(u'USD')),
    )

    user = models.ForeignKey('users.User', related_name='book_media', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_(u'Date'), null=False, blank=False)
    amount = models.DecimalField(verbose_name=_('Amount'))
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, verbose_name=_('Currency'))
    type = models.CharField(max_length=10, choices=PAYMENT_CHOICES, verbose_name=_('Payment way'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name=_('Payment status'))
    execute_response = JSONField(null=True)
    payment_response = JSONField(null=True)

    class Meta:
        verbose_name_plural = "Payments"
        ordering = ['-date']

    def __str__(self):
        return '{amount} @ {date} {by}'.format(amount=self.amount, date=self.date,
                                               by=(self.user.name if self.user_id is not None else ''))

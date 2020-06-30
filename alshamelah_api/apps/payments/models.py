from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

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

    user = models.ForeignKey('users.User', related_name='payments', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_(u'Date'), null=False, blank=False)
    amount = models.DecimalField(verbose_name=_('Amount'), decimal_places=2, max_digits=10)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, verbose_name=_('Currency'))
    type = models.CharField(max_length=15, choices=PAYMENT_CHOICES, verbose_name=_('Payment way'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name=_('Payment status'))
    execute_response = JSONField(null=True)
    payment_response = JSONField(null=True)
    payment_card = models.CharField(verbose_name=_('Card Number'), null=True, blank=False, max_length=24)
    payment_card_type = models.CharField(verbose_name=_('Card Type'), null=True, blank=False, max_length=50)

    class Meta:
        verbose_name_plural = "Payments"
        ordering = ['-date']

    def __str__(self):
        return '{amount} @ {date} {by}'.format(amount=self.amount, date=self.date,
                                               by=(self.user.name if self.user_id is not None else ''))


class CreditCardInfo(object):
    def __init__(self, card, year, month, cvc):
        self.card = card
        self.exp_year = year
        self.exp_month = month
        self.cvc = cvc

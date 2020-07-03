import json
from datetime import datetime

from rest_framework import serializers

from .models import Payment, CreditCardInfo
from .services.my_fatoorah import initiate_payment
from ..points.services import PointsService
from ..users.services import FCMService


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'date', 'type', 'currency', 'status']


class PaymentCreditCardSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    date = serializers.HiddenField(default=datetime.now().date())
    type = serializers.HiddenField(default='credit_card')
    status = serializers.HiddenField(default='pending')
    card = serializers.RegexField(regex=r'^[\d]+$', required=True)
    expiry_year = serializers.IntegerField()
    expiry_month = serializers.IntegerField()
    cvc = serializers.RegexField(regex=r'^[\d]+$', required=True, max_length=3, min_length=3)
    amount = serializers.DecimalField(min_value=0.1, decimal_places=2, max_digits=10)
    currency = serializers.CharField(default='USD', max_length=3, min_length=3, required=False)

    # def validate_expiry_year(self, expiry_year):
    #     year = datetime.now().year
    #     if year > expiry_year:
    #         pass
    #     return expiry_year
    #
    # def validate_expiry_month(self, expiry_month):
    #     year = datetime.now().year
    #     month = datetime.now().month
    #     if year <= self.expiry_year.get_value() and expiry_month < month:
    #         pass
    #     return expiry_month

    class Meta:
        model = Payment
        fields = ['card', 'expiry_year', 'expiry_month', 'amount', 'cvc', 'user', 'date', 'type', 'status', 'currency']

    def create(self, validated_data):
        card = CreditCardInfo(validated_data['card'], validated_data['expiry_year'], validated_data['expiry_month'],
                              validated_data['cvc'])
        for info in ['card', 'expiry_year', 'expiry_month', 'cvc']:
            del validated_data[info]
            self.data.pop(info)
        created = super(PaymentCreditCardSerializer, self).create(validated_data)
        user = self.context.get('request').user
        try:
            payment = initiate_payment(self.context.get('request'), payment_data=created, card=card)
        except Exception as ex:
            created.payment_response = json.dumps(ex)
            created.status = 'failed'
            created.save()
            FCMService.notify_payment_rejected(user)
            return created
        if payment.status_code > 210:
            created.payment_response = payment.json()
            created.status = 'failed'
            created.save()
            FCMService.notify_payment_rejected(user)
        elif payment.status_code == 200:
            response = payment.json()
            created.status = str(response['Data']['Status']).lower()
            created.payment_card = response['Data']['CardInfo']['Number']
            created.payment_card_type = response['Data']['CardInfo']['Brand']
            created.payment_response = response
            created.save()
            FCMService.notify_payment_success(user)
            PointsService().donation_award(user, created)
        return created

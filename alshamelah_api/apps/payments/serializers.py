from datetime import datetime

from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'date', 'type', 'currency', 'status']


class PaymentCreditCardSerializer(serializers.Serializer):
    card = serializers.CharField()
    expiry_year = serializers.IntegerField()
    expiry_month = serializers.IntegerField()
    amount = serializers.DecimalField(min_value=0.1, decimal_places=2, )

    def validate_expiry_year(self, expiry_year):
        year = datetime.now().year
        if year > expiry_year:
            pass
        return expiry_year

    def validate_expiry_month(self, expiry_month):
        year = datetime.now().year
        month = datetime.now().month
        if year <= self.expiry_year.get_value() and expiry_month < month:
            pass
        return expiry_month

    class Meta:
        fields = ['card', 'expiry_year', 'expiry_month', 'amount']

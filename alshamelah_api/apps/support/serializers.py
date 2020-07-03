from rest_framework import serializers

from .models import Support
from ..users.services import FCM


class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Support
        fields = '__all__'

    def create(self, validated_data):
        support = super(SupportSerializer, self).create(validated_data)
        request = self.context.get('request')
        if support and request and request.user.id:
            FCM.notify_support_request(request.user)
        return support

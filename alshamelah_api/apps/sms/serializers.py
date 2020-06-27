from rest_framework import serializers


class TwilioStatusSerializer(serializers.Serializer):
    sid = serializers.CharField(source='MessageSid')
    status = serializers.CharField(source='MessageStatus')

    class Meta:
        fields = ['sid', 'status', ]

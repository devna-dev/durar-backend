from rest_framework import serializers

from .models import Legal


class TermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Legal
        fields = ['terms']


class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Legal
        fields = ['policy']

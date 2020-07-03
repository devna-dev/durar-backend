from rest_framework import serializers

from .models import UserPoints


class UserPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPoints
        fields = '__all__'

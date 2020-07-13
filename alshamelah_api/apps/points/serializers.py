from rest_framework import serializers

from .models import UserPoints, UserAchievement, Achievement


class UserPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPoints
        fields = '__all__'


class UserAchievementSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()
    class Meta:
        model = UserAchievement
        fields = ['title', 'category', 'points', 'icon', 'type']

    def get_icon(self, achievement):
        request = self.context.get('request')
        return request.build_absolute_uri(achievement.icon) if achievement.icon else None
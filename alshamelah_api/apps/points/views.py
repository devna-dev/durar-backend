from django.db.models import Sum
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import UserPoints, UserAchievement, Achievement
from .serializers import UserPointsSerializer, UserAchievementSerializer, AchievementSerializer


class UserPointsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = UserPoints.objects.all()
    serializer_class = UserPointsSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        points = list(self.queryset.filter(user_id=request.user.id).values('type').annotate(points=Sum('point_num')))
        donation = next((point['points'] for point in points if points if point['type'] == 'donation'), None)
        book_approved = next((point['points'] for point in points if point['type'] == 'book_approved'), None)
        paper_approved = next((point['points'] for point in points if point['type'] == 'paper_approved'), None)
        thesis_approved = next((point['points'] for point in points if point['type'] == 'thesis_approved'), None)
        audio_approved = next((point['points'] for point in points if point['type'] == 'audio_approved'), None)
        total = (donation if donation else 0) + \
                (paper_approved if paper_approved else 0) + \
                (thesis_approved if thesis_approved else 0) + \
                (audio_approved if audio_approved else 0)
        user_achievements = UserAchievement.objects.filter(user_id=request.user.id)
        achievements = UserAchievementSerializer(user_achievements,
                                                 context={'request': request}, many=True)
        all_achievements = Achievement.objects.all() if not user_achievements else Achievement.objects.all().exclude(
            type__in=list(achievement.type for achievement in user_achievements))
        unfulfilled_achievements = AchievementSerializer(all_achievements, many=True)
        data = {
            'donation': donation if donation else 0,
            'book_approval': book_approved if book_approved else 0,
            'paper_approval': paper_approved if paper_approved else 0,
            'thesis_approval': thesis_approved if thesis_approved else 0,
            'audio_approval': audio_approved if audio_approved else 0,
            'total': total,
            'membership': request.user.membership,
            'badges': achievements.data,
            'unfulfilled_achievements': unfulfilled_achievements.data
        }
        return Response(data, status=status.HTTP_200_OK)

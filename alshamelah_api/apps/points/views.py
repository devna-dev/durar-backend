from django.db.models import Sum
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import UserPoints
from .serializers import UserPointsSerializer


class UserPointsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = UserPoints.objects.all()
    serializer_class = UserPointsSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        points = self.queryset.filter(user_id=request.user.id).values('type').annotate(points=Sum('point_num'))
        donation = points.filter(type='donation').first()
        book_approved = points.filter(type='book_approved').first()
        paper_approved = points.filter(type='paper_approved').first()
        thesis_approved = points.filter(type='thesis_approved').first()
        audio_approved = points.filter(type='audio_approved').first()
        data = {
            'donation': donation['points'] if donation else 0,
            'book_approval': book_approved['points'] if book_approved else 0,
            'paper_approval': paper_approved['points'] if paper_approved else 0,
            'thesis_approval': thesis_approved['points'] if thesis_approved else 0,
            'audio_approval': audio_approved['points'] if audio_approved else 0
        }
        return Response(data, status=status.HTTP_200_OK)

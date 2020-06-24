from rest_framework import viewsets, mixins

from .models import Support
from .permissions import CanManageSupport
from .serializers import SupportSerializer


class AuthorViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Support.objects.all()
    serializer_class = SupportSerializer
    permission_classes = (CanManageSupport,)

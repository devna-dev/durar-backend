from rest_framework import views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Legal
from .serializers import TermsSerializer, PolicySerializer


class TermsView(views.APIView):
    serializer_class = TermsSerializer
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        data = Legal.objects.all().first()
        return Response(data.terms if data else None)


class PolicyView(views.APIView):
    serializer_class = PolicySerializer
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        data = Legal.objects.all().first()
        return Response(data.policy if data else None)

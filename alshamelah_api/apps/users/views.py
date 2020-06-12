from django.contrib.auth.models import User
from rest_framework import viewsets

from .serializers import UserSerializer


# Create your views here.

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Default accepted fields: email, name, phone
    Default display fields: pk, name, email, phone, birthdate, gender, country, address, photo
    Read-only fields: pk, email

    Returns UserModel fields.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

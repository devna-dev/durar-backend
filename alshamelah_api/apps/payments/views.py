from rest_framework import viewsets

from .models import Author
from .permissions import CanManageAuthor
from .serializers import AuthorSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = (CanManageAuthor,)

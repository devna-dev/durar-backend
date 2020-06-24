import coreapi
import coreschema
import django_filters
from django.utils.encoding import force_str
from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser

from .models import ChatRoom
from .permissions import CanManageChatRoom
from .serializers import ChatRoomSerializer, ChatRoomListSerializer
from ..core.pagination import CustomPageNumberPagination, CustomLimitOffsetPagination


class ChatRoomFilter(django_filters.FilterSet):
    date = django_filters.DateFilter()

    class Meta:
        model = ChatRoom
        fields = ['date']


class ChatRoomFilterBackend(DjangoFilterBackend):
    date_query_param = 'date'
    date_year_query_description = _('Filter chatrooms by date')

    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(
                name=self.date_query_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title='Date',
                    description=force_str(self.date_year_query_description)
                )
            ),
        ]
        return fields

    def get_schema_operation_parameters(self, view):
        parameters = [
            {
                'name': self.date_query_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.date_year_query_description),
                'schema': {
                    'type': 'string',
                },
            },
        ]
        return parameters


class ChatRoomsViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = (CanManageChatRoom,)
    filterset_class = ChatRoomFilter
    parser_classes = [MultiPartParser]
    filter_backends = [ChatRoomFilterBackend]

    @property
    def pagination_class(self):
        if 'offset' in self.request.query_params:
            return CustomLimitOffsetPagination
        else:
            return CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return ChatRoomListSerializer
        return ChatRoomSerializer

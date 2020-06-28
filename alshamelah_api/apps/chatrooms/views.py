import coreapi
import coreschema
import django_filters
from django.utils.encoding import force_str
from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .models import ChatRoom, Seminar, SeminarRegistration, ChatRoomRegistration, DiscussionRegistration, Discussion
from .permissions import CanManageChatRoom
from .serializers import SeminarSerializer, SeminarListSerializer, \
    DiscussionSerializer, DiscussionListSerializer, DiscussionRegistrationSerializer, \
    SeminarRegistrationSerializer
from ..books.permissions import CanManageUserData
from ..core.pagination import CustomPageNumberPagination, CustomLimitOffsetPagination


class ChatRoomFilter(django_filters.FilterSet):
    date = django_filters.DateFilter()

    class Meta:
        model = ChatRoom
        fields = ['date']


class ChatRoomRegistrationFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(name='chat_room__date', lookup_expr='exact')

    class Meta:
        model = ChatRoomRegistration
        fields = ['date']


class ChatRoomFilterBackend(DjangoFilterBackend):
    date_query_param = 'date'
    date_year_query_description = _('Filter by date')

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


class SeminarsViewSet(viewsets.ModelViewSet):
    queryset = Seminar.objects.all()
    serializer_class = SeminarSerializer
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
            return SeminarListSerializer
        return SeminarSerializer


class SeminarRegistrationViewSet(mixins.DestroyModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = SeminarRegistration.objects.all()
    serializer_class = SeminarSerializer
    permission_classes = (CanManageUserData,)
    filterset_class = ChatRoomRegistrationFilter
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
            return SeminarListSerializer
        return SeminarRegistrationSerializer

    def get_queryset(self):
        if self.action == 'list':
            return Seminar.objects.filter(registrations__user_id=self.request.user.id)
        return self.queryset.filter(user_id=self.request.user.id)

    def destroy(self, request, pk=None, *args, **kwargs):
        registration = get_object_or_404(SeminarRegistration, user_id=request.user.id, chat_room_id=pk)
        return Response(registration.delete(), status=status.HTTP_204_NO_CONTENT)


class DiscussionsViewSet(viewsets.ModelViewSet):
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer
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
            return DiscussionListSerializer
        return DiscussionSerializer


class DiscussionsRegistrationViewSet(mixins.DestroyModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = DiscussionRegistration.objects.all()
    serializer_class = DiscussionSerializer
    permission_classes = (CanManageUserData,)
    filterset_class = ChatRoomRegistrationFilter
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
            return DiscussionListSerializer
        return DiscussionRegistrationSerializer

    def get_queryset(self):
        if self.action == 'list':
            return Discussion.objects.filter(registrations__user_id=self.request.user.id)
        return self.queryset.filter(user_id=self.request.user.id)

    def destroy(self, request, pk=None, *args, **kwargs):
        registration = get_object_or_404(DiscussionRegistration, user_id=request.user.id, chat_room_id=pk)
        return Response(registration.delete(), status=status.HTTP_204_NO_CONTENT)

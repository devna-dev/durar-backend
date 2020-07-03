from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .models import RoomType, Seminar, Discussion, ChatRoomRegistration, DiscussionRegistration, \
    SeminarRegistration, ChatRoom


class ChatRoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ['id', 'name', ]


class ChatRoomListSerializer(serializers.ModelSerializer):
    # category = ChatRoomTypeSerializer()
    registered = serializers.SerializerMethodField('is_registered')
    duration = serializers.SerializerMethodField()
    day = serializers.SerializerMethodField()

    def is_registered(self, chatroom):
        return chatroom.registrations.filter(user_id=self.user_id).exists()

    def get_duration(self, chatroom):
        if chatroom.from_time is None or chatroom.to_time is None:
            return None
        time_format = '%H:%M:%S'
        return str(datetime.strptime(str(chatroom.to_time), time_format) - datetime.strptime(str(chatroom.from_time),
                                                                                             time_format))

    def get_day(self, chatroom):
        return chatroom.date.strftime("%A")

    @property
    def request(self):
        return self.context.get('request')

    @property
    def user_id(self):
        return self.request.user.id if self.request else None

    class Meta:
        model = ChatRoom
        fields = '__all__'


class SeminarListSerializer(ChatRoomListSerializer):

    @property
    def request(self):
        return self.context.get('request')

    @property
    def user_id(self):
        return self.request.user.id if self.request else None

    class Meta(ChatRoomListSerializer.Meta):
        model = Seminar
        fields = None
        exclude = ['type']


class SeminarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seminar
        exclude = ['type']
        list_serializer_class = SeminarListSerializer


class DiscussionListSerializer(ChatRoomListSerializer):

    @property
    def request(self):
        return self.context.get('request')

    @property
    def user_id(self):
        return self.request.user.id if self.request else None

    class Meta(ChatRoomListSerializer.Meta):
        model = Discussion
        fields = None
        exclude = ['type']


class DiscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seminar
        exclude = ['type']
        list_serializer_class = DiscussionListSerializer


class ChatRoomRegistrationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ChatRoomRegistration
        fields = '__all__'

    def validate_chat_room(self, room):
        if room.type != self.type:
            raise serializers.ValidationError(_('Invalid room id'))
        return room

    def create(self, validated_data):
        registration, created = ChatRoomRegistration.objects.update_or_create(
            user=validated_data.get('user', None),
            chat_room=validated_data.get('chat_room', None), )
        return registration


class DiscussionRegistrationSerializer(ChatRoomRegistrationSerializer):
    class Meta(ChatRoomRegistration.Meta):
        model = DiscussionRegistration
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DiscussionRegistrationSerializer, self).__init__(*args, **kwargs)
        self.type = Discussion().type


class SeminarRegistrationSerializer(ChatRoomRegistrationSerializer):
    class Meta(ChatRoomRegistration.Meta):
        model = SeminarRegistration
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SeminarRegistrationSerializer, self).__init__(*args, **kwargs)
        self.type = Seminar().type

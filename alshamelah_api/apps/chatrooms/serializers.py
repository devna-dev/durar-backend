from rest_framework import serializers

from .models import ChatRoom, RoomType


class ChatRoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ['id', 'name', ]


class ChatRoomListSerializer(serializers.ModelSerializer):
    type = ChatRoomTypeSerializer()

    class Meta:
        model = ChatRoom
        fields = '__all__'


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'
        list_serializer_class = ChatRoomListSerializer

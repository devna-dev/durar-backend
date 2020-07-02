import json

from rest_framework import serializers

from .models import Event
from ..books.models import BookReview, BookMark, Book, BookNote
from ..books.serializers import BookDetailSerializer


class BookForEvent(serializers.ModelSerializer):
    book = BookDetailSerializer()

    # def __init__(self, book):
    #     self.book = BookDetailSerializer(instance=book)
    #     super(BookForEvent, self).__init__()

    class Meta:
        model = Book
        fields = '__all__'


class ReviewForEvent(BookForEvent):
    class Meta(BookForEvent.Meta):
        fields = BookForEvent.Meta.fields
        model = BookReview


class MarkForEvent(BookForEvent):
    class Meta(BookForEvent.Meta):
        fields = BookForEvent.Meta.fields
        model = BookMark


class BookNoteForEvent(BookForEvent):
    class Meta(BookForEvent.Meta):
        fields = BookForEvent.Meta.fields
        model = BookNote


class EventSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Event
        fields = '__all__'

    def set_data(self, data):
        for key in data.keys():
            self.data[key] = data[key]


class EmailVerifyEventSerializer(EventSerializer):
    class Meta(EventSerializer.Meta):
        model = Event
        fields = EventSerializer.Meta.fields

    def __init__(self, *args, **kwargs):
        super(EmailVerifyEventSerializer, self).__init__(*args, **kwargs)
        self.set_data({'type': 'email', 'action': 'email_verified', 'data': json.dumps({'verified': True})})


class UserProfileEventSerializer(EventSerializer):
    class Meta(EventSerializer.Meta):
        model = Event
        fields = EventSerializer.Meta.fields

    def __init__(self, *args, **kwargs):
        super(UserProfileEventSerializer, self).__init__(*args, **kwargs)
        self.set_data({'type': 'profile', 'action': 'update'})

    def create(self, validated_data):
        self.set_data({'data': json.dumps(self.data['user'])})
        validated_data['data'] = json.dumps(self.data['user'])
        return super(UserProfileEventSerializer, self).create(validated_data)


class PasswordChangeEventSerializer(EventSerializer):
    class Meta(EventSerializer.Meta):
        model = Event
        fields = EventSerializer.Meta.fields

    def __init__(self, change_type, *args, **kwargs):
        super(PasswordChangeEventSerializer, self).__init__(*args, **kwargs)
        self.set_data({'type': 'password', 'action': change_type})

    def create(self, validated_data):
        self.set_data({'data': json.dumps(self.data['user'])})
        validated_data['data'] = json.dumps(self.data['user'])
        return super(PasswordChangeEventSerializer, self).create(validated_data)


class BookReviewEventSerializer(EventSerializer):
    class Meta(EventSerializer.Meta):
        model = Event
        fields = EventSerializer.Meta.fields

    def __init__(self, change_type, review, *args, **kwargs):
        self.set_data({'type': 'book_review', 'action': change_type, 'data': ReviewForEvent(instance=review).data
                       })
        super(BookReviewEventSerializer, self).__init__(*args, **kwargs)

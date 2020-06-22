import os

from django.db.models import Avg
from django.utils.translation import ugettext_lazy as _
from munch import munchify
from rest_framework import serializers
from rest_framework.utils import json

from .models import Book, BookMark, BookAudio, BookPDF, BookRating, BookComment, BookHighlight, BookReview, \
    BookReviewLike
from ..categories.serializers import CategorySerializer


class CurrentBookDefault(object):
    def set_context(self, serializer_field):
        self.book = serializer_field.context.get('book')

    def __call__(self):
        return self.book

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class CurrentReviewDefault(object):
    def set_context(self, serializer_field):
        self.review = serializer_field.context.get('review')

    def __call__(self):
        return self.review

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class BookListSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField('get_average_rating')
    category = CategorySerializer()

    class Meta:
        model = Book
        fields = ['title', 'author', 'author_id', 'category', 'rating', 'page_count']

    @staticmethod
    def get_average_rating(book):
        return book.book_ratings.all().aggregate(Avg('rating')).get('rating__avg', 0.00)


class UploadBookSerializer(serializers.ModelSerializer):
    file = serializers.FileField(allow_empty_file=False, use_url=False, required=False)
    uploader = serializers.HiddenField(default=serializers.CurrentUserDefault())
    pdf = serializers.FileField(use_url=False, required=False)

    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['content', 'data', 'uploader', 'has_audio', 'approved', 'read_count',
                            'download_count', 'page_count', 'search_count', 'author_id']
        extra_kwargs = {'title': {'required': True},
                        'content': {'required': False, 'allow_null': True},
                        'data': {'required': False, 'allow_null': True},
                        'author': {'required': True},
                        'file': {'required': False, 'allow_null': True, 'read_only': False},
                        'pdf': {'required': False, 'allow_null': True},
                        'category': {'required': True},
                        }

    def __init__(self, **kwargs):
        self.json_data = None
        super().__init__(**kwargs)

    def validate_file(self, file):
        if not file:
            return file
        try:
            self.json_data = json.load(file)
        except:
            raise serializers.ValidationError(_('Bad json file'))
        return file

    def validate_pdf(self, pdf):
        if not pdf:
            return pdf
        filename, file_extension = os.path.splitext(pdf.name)
        if not file_extension or file_extension.lower() != '.pdf':
            raise serializers.ValidationError(_('Bad PDF file'))
        return pdf

    def get_data(self):
        return munchify(self.json_data) if self.json_data else None

    # def create(self, validated_data):
    #     data = self.get_data()
    #     category, category_created = Category.objects.get_or_create(name=data.meta.categories[0])
    #     user = validated_data.get('uploader')
    #     return Book.objects.create(title=data.meta.name, author_id=data.meta.author_id, content=self.json_data['pages'],
    #                                data=self.json_data, category=category, uploader=user,
    #                                page_count=len(self.json_data['pages']))
    def create(self, validated_data):
        data = validated_data
        if self.json_data:
            data['content'] = self.json_data['pages']
            data['data'] = self.json_data
            data['page_count'] = len(self.json_data['pages'])
        if data.__contains__('file'):
            data.pop('file')
        pdf = None
        if data.__contains__('pdf'):
            pdf = data.pop('pdf')
        book = Book.objects.create(**data)
        if pdf:
            BookPDF.objects.update_or_create(book_id=book.id, user=book.uploader, url=pdf)
        return book


class BookSerializer(serializers.ModelSerializer):
    file = serializers.FileField(allow_empty_file=False, use_url=False, write_only=True)
    pdf = serializers.FileField(use_url=False, write_only=True)
    uploader = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Book
        fields = '__all__'
        list_serializer_class = BookListSerializer

    read_only_fields = ['content', 'data', 'uploader', 'has_audio', 'approved', 'read_count',
                        'download_count', 'page_count', 'search_count']
    extra_kwargs = {'title': {'required': True},
                    'content': {'required': False, 'allow_null': True},
                    'data': {'required': False, 'allow_null': True},
                    'author': {'required': True},
                    }

    def __init__(self, **kwargs):
        self.json_data = None
        super().__init__(**kwargs)

    def validate_file(self, file):
        if not file:
            return file
        try:
            self.json_data = json.load(file)
        except:
            raise serializers.ValidationError(_('Bad json file'))
        return file

    def get_data(self):
        return munchify(self.json_data) if self.json_data else None

    def create(self, validated_data):
        data = self.get_data()
        data['content'] = self.json_data['pages']
        data['data'] = self.json_data
        data['page_count'] = len(self.json_data['pages'])
        book = Book.objects.create(**data)
        if data['pdf']:
            BookPDF.objects.update_or_create(book_id=book.id, user=book.uploader, url=data['pdf'])
        return book


class SubmitBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['approved']

    def update(self, instance, validated_data):
        validated_data['approved'] = True
        book = Book.objects.get(pk=instance.id)
        Book.objects.filter(pk=instance.id) \
            .update(**validated_data)
        return book


class NestedBookSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    book = serializers.HiddenField(default=CurrentBookDefault())

    class Meta:
        fields = '__all__'


class BookMarkSerializer(NestedBookSerializer):
    class Meta(NestedBookSerializer.Meta):
        model = BookMark

    def create(self, validated_data):
        mark, created = BookMark.objects.update_or_create(
            user=validated_data.get('user', None),
            book=validated_data.get('book', None),
            defaults={'page': validated_data.get('page', None)})
        return mark


class BookCommentSerializer(NestedBookSerializer):
    class Meta(NestedBookSerializer.Meta):
        model = BookComment


class BookRatingSerializer(NestedBookSerializer):
    class Meta(NestedBookSerializer.Meta):
        model = BookRating
        # fields = NestedBookSerializer.Meta.fields + ['rating']

    def create(self, validated_data):
        rating, created = BookRating.objects.update_or_create(
            user=validated_data.get('user', None),
            book=validated_data.get('book', None),
            defaults={'rating': validated_data.get('rating', None)})
        return rating


class BookReviewSerializer(NestedBookSerializer):
    class Meta(NestedBookSerializer.Meta):
        model = BookReview
        # fields = NestedBookSerializer.Meta.fields + ['rating']

    def create(self, validated_data):
        review, created = BookReview.objects.update_or_create(
            user=validated_data.get('user', None),
            book=validated_data.get('book', None),
            defaults={'comment': validated_data.get('comment', None)})
        return review


class BookHighlightSerializer(NestedBookSerializer):
    class Meta(NestedBookSerializer.Meta):
        model = BookHighlight
        # fields = NestedBookSerializer.Meta.fields + ['page', 'line', 'start', 'end']


class BookAudioSerializer(NestedBookSerializer):
    class Meta(NestedBookSerializer.Meta):
        model = BookAudio


class BookPDFSerializer(NestedBookSerializer):
    class Meta(NestedBookSerializer.Meta):
        model = BookPDF


class BookReviewLikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    review = serializers.HiddenField(default=CurrentReviewDefault())

    class Meta:
        model = BookReviewLike
        fields = '__all__'

    def create(self, validated_data):
        like, created = BookReviewLike.objects.update_or_create(
            user=validated_data.get('user', None),
            review=validated_data.get('review', None), )
        return like

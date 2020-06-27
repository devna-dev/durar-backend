import os

from django.db.models import Avg
from django.utils.translation import ugettext_lazy as _
from munch import munchify
from rest_framework import serializers
from rest_framework.reverse import reverse_lazy
from rest_framework.utils import json

from .models import Book, BookMark, BookAudio, BookPDF, BookComment, BookHighlight, BookReview, \
    BookReviewLike, ReadBook, FavoriteBook, DownloadBook, ListenBook, BookSuggestion, SearchBook, ListenProgress
from ..authors.serializers import AuthorSerializer
from ..categories.serializers import CategorySerializer, SubCategorySerializer


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
    readers = serializers.SerializerMethodField('get_readers')
    downloads = serializers.SerializerMethodField('get_downloads')
    listens = serializers.SerializerMethodField('get_listens')
    pdf = serializers.SerializerMethodField('get_pdf')
    download_url = serializers.SerializerMethodField('get_download_url')
    # searches = serializers.SerializerMethodField('get_searches')
    has_audio = serializers.SerializerMethodField('does_have_audio')
    category = CategorySerializer()
    sub_category = SubCategorySerializer()
    author = AuthorSerializer()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'category', 'sub_category', 'rating', 'page_count', 'downloads', 'listens',
                  'readers', 'has_audio', 'pdf', 'download_url']

    @staticmethod
    def get_average_rating(book):
        return book.reviews.all().aggregate(Avg('rating')).get('rating__avg', 0.00)

    @staticmethod
    def get_readers(book):
        return book.readers.count()

    @staticmethod
    def get_downloads(book):
        return book.downloads.count()

    @staticmethod
    def get_listens(book):
        return book.listens.count()

    # @staticmethod
    # def get_searches(book):
    #     return book.searches.count()

    @staticmethod
    def does_have_audio(book):
        return book.book_media.filter(approved=True, type='audio').exists()

    @staticmethod
    def get_pdf(book):
        pdf = book.book_media.filter(approved=True, type='pdf').first()
        return pdf.url if pdf else None

    def get_download_url(self, book):
        url = reverse_lazy('books-download', request=self.context.get('request'), kwargs={'pk': book.id})
        return url if url else None


class UploadBookSerializer(serializers.ModelSerializer):
    file = serializers.FileField(allow_empty_file=False, use_url=False, required=False)
    uploader = serializers.HiddenField(default=serializers.CurrentUserDefault())
    pdf = serializers.FileField(use_url=False, required=False)

    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['content', 'data', 'uploader', 'has_audio', 'approved', 'read_count',
                            'download_count', 'page_count', 'search_count']
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

    read_only_fields = ['content', 'data', 'uploader', 'approved', 'page_count']
    extra_kwargs = {'title': {'required': True},
                    'content': {'required': False, 'allow_null': True},
                    'data': {'required': False, 'allow_null': True},
                    'author': {'required': True},
                    }


class BookDetailSerializer(BookSerializer):
    category = CategorySerializer()
    sub_category = SubCategorySerializer()
    author = AuthorSerializer()

    class Meta:
        model = Book
        fields = '__all__'

    read_only_fields = ['content', 'data', 'uploader', 'approved', 'page_count']
    extra_kwargs = {'title': {'required': True},
                    'content': {'required': False, 'allow_null': True},
                    'data': {'required': False, 'allow_null': True},
                    'author': {'required': True},
                    }


class DownloadBookSerializer(serializers.ModelSerializer):
    content_no_tashkeel = serializers.SerializerMethodField('get_no_tashkeel_content')
    category = CategorySerializer()
    sub_category = SubCategorySerializer()
    author = AuthorSerializer()

    class Meta:
        model = Book
        fields = ['title', 'category', 'sub_category', 'cover_image', 'content', 'author', 'page_count',
                  'content_no_tashkeel']

    @staticmethod
    def get_no_tashkeel_content(book):
        from pyarabic.araby import strip_tashkeel
        if not book.content:
            return None
        content = list(book.content)
        for page in content:
            page['text'] = strip_tashkeel(page['text'])
        return content


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


# class BookRatingSerializer(NestedBookSerializer):
#     class Meta(NestedBookSerializer.Meta):
#         model = BookReview
#         # fields = NestedBookSerializer.Meta.fields + ['rating']
#
#     def create(self, validated_data):
#         rating, created = BookReview.objects.update_or_create(
#             user=validated_data.get('user', None),
#             book=validated_data.get('book', None),
#             defaults={'rating': validated_data.get('rating', None)})
#         return rating


class BookReviewSerializer(NestedBookSerializer):
    class Meta(NestedBookSerializer.Meta):
        model = BookReview
        # fields = NestedBookSerializer.Meta.fields + ['rating']

    def create(self, validated_data):
        review, created = BookReview.objects.update_or_create(
            user=validated_data.get('user', None),
            book=validated_data.get('book', None),
            defaults=validated_data)
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


class ReadBookSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ReadBook
        fields = '__all__'

    read_only_fields = ['user']


class FavoriteBookSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = FavoriteBook
        fields = '__all__'

    read_only_fields = ['user']

    def create(self, validated_data):
        favorite, created = FavoriteBook.objects.update_or_create(
            user=validated_data.get('user', None),
            book=validated_data.get('book', None), )
        return favorite


class BookDownloadedSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = DownloadBook
        fields = '__all__'

    read_only_fields = ['user']


class ListenBookSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ListenBook
        fields = '__all__'

    read_only_fields = ['user', 'book']


class ListenProgressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    book = serializers.HiddenField(default=CurrentBookDefault())

    class Meta:
        model = ListenProgress
        exclude = ['listen']
        extra_kwargs = {'audio': {'required': True},
                        'progress': {'required': True},
                        }

    def create(self, validated_data):
        user = validated_data.get('user', None)
        book = validated_data.get('book', None)
        audio = validated_data.get('audio', None)
        if user and book and audio:
            listen, created = ListenBook.objects.get_or_create(user=user, book=book)
            file_progress, created = ListenProgress.objects.update_or_create(
                listen=listen,
                audio=audio,
                defaults={'progress': validated_data.get('progress', None)}
            )
            return file_progress
        return self.Meta.model.objects.none()


class BookSuggestionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = BookSuggestion
        fields = '__all__'

    read_only_fields = ['user']


class BookSearchListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    sub_category = SubCategorySerializer()
    author = AuthorSerializer()

    class Meta:
        model = SearchBook
        fields = '__all__'


class BookSearchSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_has_audio(self, has_audio):
        if 'has_audio' not in self.initial_data.keys():
            return None
        return has_audio

    class Meta:
        model = SearchBook
        fields = '__all__'

    read_only_fields = ['user']

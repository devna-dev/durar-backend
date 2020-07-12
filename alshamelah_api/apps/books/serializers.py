import os

from django.db.models import Avg
from django.utils.translation import ugettext_lazy as _
from munch import munchify
from rest_framework import serializers
from rest_framework.reverse import reverse_lazy
from rest_framework.utils import json

from .models import Book, BookMark, BookAudio, BookPDF, BookNote, BookReview, \
    BookReviewLike, ReadBook, FavoriteBook, DownloadBook, ListenBook, BookSuggestion, SearchBook, ListenProgress, Paper, \
    Thesis
from .util import ArabicUtilities
from ..authors.serializers import AuthorSerializer
from ..categories.serializers import CategorySerializer, SubCategorySerializer, CategoryForBookSerializer
from ..users.serializers import UserProfileSerializer


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
    reviews = serializers.SerializerMethodField('get_reviews')
    downloads = serializers.SerializerMethodField('get_downloads')
    listens = serializers.SerializerMethodField('get_listens')
    pdf = serializers.SerializerMethodField('get_pdf')
    download_url = serializers.SerializerMethodField('get_download_url')
    cover_image = serializers.SerializerMethodField('get_cover_image')
    is_favorite = serializers.SerializerMethodField()
    # searches = serializers.SerializerMethodField('get_searches')
    has_audio = serializers.SerializerMethodField('does_have_audio')
    category = CategoryForBookSerializer()
    sub_category = SubCategorySerializer()
    author = AuthorSerializer()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'category', 'sub_category', 'rating', 'page_count', 'downloads', 'listens',
                  'readers', 'reviews', 'has_audio', 'pdf', 'download_url', 'cover_image', 'description', 'is_favorite']

    @property
    def request(self):
        return self.context.get('request')

    @staticmethod
    def get_average_rating(book):
        return book.reviews.all().aggregate(Avg('rating')).get('rating__avg', 0.00)

    @staticmethod
    def get_reviews(book):
        return book.reviews.count()

    @staticmethod
    def get_readers(book):
        return book.readers.count()

    @staticmethod
    def get_downloads(book):
        return book.downloads.count()

    @staticmethod
    def get_listens(book):
        return book.listens.count()

    @staticmethod
    def does_have_audio(book):
        return book.book_media.filter(approved=True, type='audio').exists()

    def get_pdf(self, book):
        pdf = book.book_media.filter(approved=True, type='pdf').first()
        return self.request.build_absolute_uri(pdf.url.url) if pdf and pdf.url else None

    def get_download_url(self, book):
        if self.request is None: return None
        url = reverse_lazy('books-download', request=self.request, kwargs={'pk': book.id})
        return url if url else None

    def get_cover_image(self, book):
        if self.request is None: return None
        url = self.request.build_absolute_uri(book.image) if book.image else None
        return url if url else None

    def get_is_favorite(self, book):
        if not self.request or not self.request.user.id or not hasattr(self.request.user, 'favorite_books'):
            return False
        return self.request.user.favorite_books.filter(book_id=book.id).exists()


class UserBookListSerializer(BookListSerializer):
    read_progress = serializers.SerializerMethodField()
    listen_progress = serializers.SerializerMethodField()

    class Meta(BookListSerializer.Meta):
        model = Book
        fields = BookListSerializer.Meta.fields + ['read_progress', 'listen_progress']

    def get_read_progress(self, book):
        if self.request is None or self.request.user.id is None:
            return None
        read = book.readers.filter(user_id=self.request.user.id).first()
        return round(read.page / book.page_count, 2) if read is not None and read.page is not None else 0

    def get_listen_progress(self, book):
        if self.request is None or self.request.user.id is None:
            return None
        listen = book.listens.filter(user_id=self.request.user.id).first()
        if not listen or not listen.file_progress.exists():
            return 0
        total = []
        audio = list(book.book_media.filter(type='audio', approved=True))
        for file in audio:
            data = next(item for item in listen.file_progress.all() if item.audio_id == file.id)
            if data:
                total.append(data.progress)
            else:
                total.append(0)

        return round((sum(total) / len(total)) / 100, 2) if total else 0


class UploadBookSerializer(serializers.ModelSerializer):
    file = serializers.FileField(allow_empty_file=False, use_url=False, required=False)
    uploader = serializers.HiddenField(default=serializers.CurrentUserDefault())
    pdf = serializers.FileField(use_url=False, required=False)

    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['content', 'data', 'uploader', 'has_audio', 'approved', 'read_count',
                            'download_count', 'page_count', 'search_count', 'type']
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

    def create(self, validated_data):
        data = validated_data
        if self.json_data:
            data['content'] = self.json_data['pages']
            data['data'] = self.json_data
            data['page_count'] = len(self.json_data['pages'])
            if 'description' not in data.keys() and self.json_data['meta']['betaka']:
                data['description'] = self.json_data['meta']['betaka']
        if data.__contains__('file'):
            data.pop('file')
        pdf = None
        if data.__contains__('pdf'):
            pdf = data.pop('pdf')
        book = Book.objects.create(**data)
        if pdf:
            BookPDF.objects.update_or_create(book_id=book.id, user=book.uploader, url=pdf)
        return book


class UploadPaperSerializer(serializers.ModelSerializer):
    uploader = serializers.HiddenField(default=serializers.CurrentUserDefault())
    pdf = serializers.FileField(use_url=False, required=False)

    class Meta:
        model = Paper
        fields = ['title', 'category', 'author', 'uploader', 'pdf', 'publish_date', 'cover_image', 'page_count',
                  'description']
        extra_kwargs = {'title': {'required': True},
                        'author': {'required': True},
                        'pdf': {'required': True},
                        'category': {'required': True},
                        }

    def validate_pdf(self, pdf):
        if not pdf:
            raise serializers.ValidationError(_('file is required'))
        filename, file_extension = os.path.splitext(pdf.name)
        if not file_extension or file_extension.lower() not in ['.pdf', '.doc', '.docx']:
            raise serializers.ValidationError(_('Bad file'))
        return pdf

    def create(self, validated_data):
        data = validated_data
        pdf = None
        if data.__contains__('pdf'):
            pdf = data.pop('pdf')
        book = Paper.objects.create(**data)
        if pdf:
            BookPDF.objects.update_or_create(book_id=book.id, user=book.uploader, url=pdf)
        return book


class UploadThesisSerializer(serializers.ModelSerializer):
    uploader = serializers.HiddenField(default=serializers.CurrentUserDefault())
    pdf = serializers.FileField(use_url=False, required=False)

    class Meta:
        model = Paper
        fields = ['title', 'category', 'author', 'uploader', 'pdf', 'publish_date', 'cover_image', 'page_count',
                  'description']
        extra_kwargs = {'title': {'required': True},
                        'author': {'required': True},
                        'pdf': {'required': True},
                        'category': {'required': True},
                        }

    def validate_pdf(self, pdf):
        if not pdf:
            raise serializers.ValidationError(_('file is required'))
        filename, file_extension = os.path.splitext(pdf.name)
        if not file_extension or file_extension.lower() not in ['.pdf', '.doc', '.docx']:
            raise serializers.ValidationError(_('Bad file'))
        return pdf

    def create(self, validated_data):
        data = validated_data
        pdf = None
        if data.__contains__('pdf'):
            pdf = data.pop('pdf')
        book = Thesis.objects.create(**data)
        if pdf:
            BookPDF.objects.update_or_create(book_id=book.id, user=book.uploader, url=pdf)
        return book


class PaperListSerializer(serializers.ModelSerializer):
    pdf = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()
    category = CategoryForBookSerializer()
    author = AuthorSerializer()

    class Meta:
        model = Paper
        fields = ['id', 'title', 'author', 'category', 'page_count', 'pdf',
                  'cover_image', 'description', 'publish_date']

    @property
    def request(self):
        return self.context.get('request')

    def get_pdf(self, book):
        pdf = book.book_media.filter(type='pdf').first()
        return self.request.build_absolute_uri(pdf.url.url) if pdf and pdf.url else None

    def get_cover_image(self, book):
        if self.request is None: return None
        url = self.request.build_absolute_uri(book.image) if book.image else None
        return url if url else None


class ThesisListSerializer(PaperListSerializer):
    class Meta(PaperListSerializer.Meta):
        model = Thesis
        fields = PaperListSerializer.Meta.fields


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
        return Book.objects.filter(pk=instance.id).update(**validated_data)


class SubmitPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = ['approved']

    def update(self, instance, validated_data):
        validated_data['approved'] = True
        return Paper.objects.filter(pk=instance.id).update(**validated_data)


class SubmitThesisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thesis
        fields = ['approved']

    def update(self, instance, validated_data):
        validated_data['approved'] = True
        return Thesis.objects.filter(pk=instance.id).update(**validated_data)


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


class BookNoteSerializer(NestedBookSerializer):
    tashkeel_on = serializers.BooleanField()

    class Meta(NestedBookSerializer.Meta):
        model = BookNote
        read_only_fields = ['user', 'tashkeel_start', 'tashkeel_end']
        extra_kwargs = {'tashkeel_start': {'required': False, 'read_only': True},
                        'tashkeel_end': {'required': False, 'read_only': True},
                        }

    def validate_page(self, page):
        if len(self.context.get('book').pages) < page:
            raise serializers.ValidationError(_('Invalid page number'))
        self.page_data = self.context.get('book').pages[page]['text']
        return page

    def create(self, validated_data):
        if validated_data['tashkeel_on']:
            mark_position = ArabicUtilities.get_no_tashkeel_position(self.page_data, validated_data['start'],
                                                                     validated_data['end'])
            validated_data['tashkeel_start'] = validated_data['start']
            validated_data['tashkeel_end'] = validated_data['end']
            validated_data['start'] = mark_position.start
            validated_data['end'] = mark_position.end
        else:
            mark_position = ArabicUtilities.get_tashkeel_position(self.page_data, validated_data['start'],
                                                                  validated_data['end'])
            validated_data['tashkeel_start'] = mark_position.start
            validated_data['tashkeel_end'] = mark_position.end

        del validated_data['tashkeel_on']
        self.data.pop('tashkeel_on')
        return super(BookNoteSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        if validated_data['tashkeel_on']:
            mark_position = ArabicUtilities.get_no_tashkeel_position(self.page_data, validated_data['start'],
                                                                     validated_data['end'])
            validated_data['tashkeel_start'] = validated_data['start']
            validated_data['tashkeel_end'] = validated_data['end']
            validated_data['start'] = mark_position.start
            validated_data['end'] = mark_position.end
        else:
            mark_position = ArabicUtilities.get_tashkeel_position(self.page_data, validated_data['start'],
                                                                  validated_data['end'])
            validated_data['tashkeel_start'] = mark_position.start
            validated_data['tashkeel_end'] = mark_position.end

        del validated_data['tashkeel_on']
        self.data.pop('tashkeel_on')
        return super(BookNoteSerializer, self).update(instance, validated_data)


class BookReviewSerializer(NestedBookSerializer):
    class Meta(NestedBookSerializer.Meta):
        model = BookReview
        # fields = NestedBookSerializer.Meta.fields + ['rating']

    def create(self, validated_data):
        # from ..event_history.serializers import BookReviewEventSerializer
        review, created = BookReview.objects.update_or_create(
            user=validated_data.get('user', None),
            book=validated_data.get('book', None),
            defaults=validated_data)
        # event = BookReviewEventSerializer(change_type=('create' if created else 'update'), review=review,
        #                                   context={'request': self.context.get('request')})
        # if event.is_valid():
        #         event.save()
        return review


class UserReviewWriteSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    like_id = serializers.SerializerMethodField()

    class Meta:
        model = BookReview
        exclude = ['user']

    def get_likes(self, review):
        return review.likes.count()

    def get_like_id(self, review):
        if not self.context.get('request') or not self.context.get('request').user.id:
            return None
        like = review.likes.filter(user_id=self.context.get('request').user.id).first()
        return like.id if like else None


class UserReviewSerializer(UserReviewWriteSerializer):
    book = BookListSerializer(read_only=True, required=False)


class UserReviewListSerializer(serializers.ModelSerializer):
    book = BookListSerializer()
    user = UserProfileSerializer()
    likes = serializers.SerializerMethodField()
    like_id = serializers.SerializerMethodField()

    class Meta:
        model = BookReview
        fields = ['book', 'user', 'likes', 'id', 'like_id']

    def get_likes(self, review):
        return review.likes.count()

    def get_like_id(self, review):
        if not self.context.get('request') or not self.context.get('request').user.id:
            return None
        like = review.likes.filter(user_id=self.context.get('request').user.id).first()
        return like.id if like else None


class BookAudioSerializer(NestedBookSerializer):
    class Meta(NestedBookSerializer.Meta):
        model = BookAudio


class BookPDFSerializer(NestedBookSerializer):
    class Meta(NestedBookSerializer.Meta):
        model = BookPDF


class BookReviewLikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

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


class UserBookNoteListSerializer(serializers.ModelSerializer):
    book = BookListSerializer()

    class Meta:
        model = BookNote
        exclude = ['user', 'tashkeel_start', 'tashkeel_end']


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

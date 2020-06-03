from rest_framework import serializers

from .models import Book, BookMark, BookAudio, BookPDF, BookRating, BookComment, BookHighlight


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookMark
        fields = '__all__'


class BookCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookComment
        fields = '__all__'


class BookRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookRating
        fields = '__all__'


class BookHighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookHighlight
        fields = '__all__'


class BookAudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookAudio
        fields = '__all__'


class BookPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookPDF
        fields = '__all__'

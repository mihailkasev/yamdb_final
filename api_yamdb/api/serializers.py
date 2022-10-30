from django.db.models import Avg
from rest_framework import serializers
from rest_framework.serializers import UniqueTogetherValidator

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id', 'category', 'genre', 'name',
                  'rating', 'year', 'description')
        model = Title

    def get_rating(self, obj):
        rating = Review.objects.filter(title=obj.id).aggregate(Avg('score'))
        return rating['score__avg']


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class EmailSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    def validate(self, data):
        if 'username' in data and data['username'] == 'me':
            raise serializers.ValidationError("can not use that name")

        if 'email' in data and User.objects.filter(
                email=data['email']
        ).exists():
            raise serializers.ValidationError("email is already in use")

        if 'username' in data and User.objects.filter(
                username=data['username']
        ).exists():
            raise serializers.ValidationError("username is already in use")

        return super().validate(data)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = Review
        exclude = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        exclude = ('review',)
        model = Comment
        read_only_fields = ('review',)


class UserSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if 'username' in data and data['username'] == 'me':
            raise serializers.ValidationError("can not use that name")

        if 'email' in data and User.objects.filter(
                email=data['email']
        ).exists():
            raise serializers.ValidationError("email is already in use")

        if 'username' in data and User.objects.filter(
                username=data['username']
        ).exists():
            raise serializers.ValidationError("username is already in use")

        return super().validate(data)

    class Meta:
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'role')
        model = User
        validators = (
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email')
            ),
        )

import re

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from reviews.models import Review, Comment, Genre, Title, Category


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей(админ)."""

    class Meta:
        model = User
        fields = ('email', 'role', 'username',
                  'first_name', 'last_name', 'bio')
        lookup_field = 'username'
        extra_kwargs = {
            'url': {'lookup_field': 'username'}
        }


class RegisterSerializer(serializers.Serializer):
    """Сериализатор для регистрации."""

    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, max_length=254)

    class Meta:
        fields = (
            'username', 'email')

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Using "me" as a username is not allowed.'
            )
        pattern = re.compile(r'^[\w.@+-]+\Z')
        if not pattern.match(value):
            raise serializers.ValidationError('Invalid username!')
        return value

    def validate(self, data):
        email = data['email']
        username = data['username']
        user_username = User.objects.filter(username=username)
        user_email = User.objects.filter(email=email)
        if User.objects.filter(username=username, email=email):
            return data
        if user_email.exists() and user_email[0].username != username:
            raise serializers.ValidationError('Email taken')
        if user_username.exists() and user_username[0].email != email:
            raise serializers.ValidationError('Username taken')
        return data


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор получения токена."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        fields = (
            'username',
            'confirmation_code'
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзывов."""

    author = SlugRelatedField(
        slug_field='username',
        read_only=True, required=False
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        author = self.context['request'].user
        title_id = (self.context['request'].
                    parser_context['kwargs'].get('title_id'))
        title = get_object_or_404(
            Title,
            id=title_id
        )
        if (self.context['request'].method == 'POST'
                and title.reviews.filter(author=author).exists()):
            raise serializers.ValidationError(
                f'Отзыв на произведение {title.name} уже существует'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleReadonlySerializer(serializers.ModelSerializer):
    """Сериализатор произведений для List и Retrieve."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        """Мета класс произведения."""

        fields = '__all__'
        model = Title


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, title):
        """Определяет какой сериализатор будет использоваться для чтения."""
        serializer = TitleReadonlySerializer(title)
        return serializer.data
!
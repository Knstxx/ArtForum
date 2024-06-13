import re

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from reviews.models import Reviews, Comment, Genre, Title, Category

from .utils import generate_confirmation_code
from reviews.validators import slug_validator


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей(админ)."""

    class Meta:
        model = User
        fields = ('email', 'role', 'username', 'first_name', 'last_name', 'bio')
        lookup_field = 'username'
        extra_kwargs = {
            'url': {'lookup_field': 'username'}
        }


class UserMeSerialzier(serializers.Serializer):
    """Сериализатор для профиля пользователя."""

    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    bio = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'first_name', 'last_name', 'bio')

    def validate(self, data):
        if 'first_name' in data:
            if len(data['first_name']) > 150:
                raise serializers.ValidationError('Tooo looong first_name...')
        if 'last_name' in data:
            if len(data['last_name']) > 150:
                raise serializers.ValidationError('Tooo looong last_name...')
        if 'username' in data:
            pattern = re.compile(r'^[\w.@+-]+\Z')
            if len(data['username']) > 150 or not pattern.match(data['username']):
                raise serializers.ValidationError('incorect username !')
        if 'email' in data:
            if len(data['email']) > 254:
                raise serializers.ValidationError('Tooo looong email...')
        return data

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.bio = validated_data.get('bio', instance.bio)

        instance.save()
        return instance

class RegisterSerializer(serializers.Serializer):
    """Сериализатор для регистрации."""

    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username', 'email')

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError("Using 'me' as a username is not allowed.")
        if len(data.get('username')) > 150:
            raise serializers.ValidationError("Email already exists...")
        if len(data.get('email')) > 254:
            raise serializers.ValidationError("Email tooo looong...")
        pattern = re.compile(r'^[\w.@+-]+\Z')
        if not pattern.match(data['username']):
            raise serializers.ValidationError('Корявый username !')
        user_username = User.objects.filter(username=data['username'])
        user_email = User.objects.filter(email=data['email'])
        if user_email.exists() and user_email[0].username != data['username']:
            raise serializers.ValidationError("Email already exists...")
        if user_username.exists() and user_username[0].email != data['email']:
            raise serializers.ValidationError("No")

        return data

    def create(self, validated_data):
        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        if created:
            user.confirmation_code = generate_confirmation_code()
            user.save()
        send_mail(
            'Confirmation code',
            f'Your confirmation code is: {user.confirmation_code}',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )
        return user


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор получения токена."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )


class ReviewsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзывов."""

    author = SlugRelatedField(
        slug_field='username',
        read_only=True, required=False
    )

    class Meta:
        model = Reviews
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class CategoriesSerializer(serializers.Serializer):
    """Сериализатор категорий."""

    name = serializers.CharField()
    slug = serializers.SlugField()

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
    
    def validate(self, data):
        if not data:
            raise serializers.ValidationError('Data is empty...')
        slug = data['slug']
        category = Category.objects.all()
        slugs = []
        for categ in category:
            slugs.append(categ.slug)
        # breakpoint()
        if slug in slugs:
            raise serializers.ValidationError('Already exists...')
        name = data['name']
        if len(name) > 256:
            raise serializers.ValidationError('Too long name !')
        if len(slug) > 50:
            raise serializers.ValidationError('Too long slug !')
        pattern = re.compile(r"^[-a-zA-Z0-9_]+$")
        if not pattern.match(slug):
            raise serializers.ValidationError('Символы латинского алфавита, цифры и знак подчёркивания')
        # breakpoint()
        return data

    def create(self, validated_data):
        category = Category.objects.all()
        slug = validated_data['slug']
        slugs = []
        for categ in category:
            slugs.append(categ.slug)
        # breakpoint()
        if slug in slugs:
            raise serializers.ValidationError('Already exists...')
        category = Category.objects.create(**validated_data)
        return category

    def to_internal_value(self, data):
        # breakpoint()
        if isinstance(data, dict):
            return data
        data = Category.objects.get(slug=data)
        return data


class GenresSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')

    def to_internal_value(self, data):
        # breakpoint()
        if isinstance(data, dict):
            return data
        data = Genre.objects.get(slug=data)
        return data

    def validate_name(self, value):
        if len(value) > 256:
            raise serializers.ValidationError('Слишком длииииное имя!')


class TitleSerializer(serializers.ModelSerializer):

    genre = GenresSerializer(many=True)
    category = CategoriesSerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        rating = 0
        for review in reviews:
            rating += review.score
        rating = round(rating / len(reviews))
        # breakpoint()
        return rating

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(
            **validated_data,
            )
        # breakpoint()
        title.genre.set(genres)
        return title

    def update(self, instance, validated_data):
        # breakpoint()
        if 'genre' in validated_data:
            genres = validated_data.pop('genre')
            instance.genre.set(genres)
        instance.name = validated_data.get('name', instance.name)
        instance.year = validated_data.get('year', instance.year)
        instance.description = validated_data.get('description',
                                                  instance.description)
        instance.save()
        # breakpoint()
        return super().update(instance, validated_data)

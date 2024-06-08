from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from reviews.models import Reviews, Comment, Genre, Title, Category, MyUser

from .utils import generate_confirmation_code


User = get_user_model()


class UserMeSerilaizer(serializers.ModelSerializer):

    class Meta:
        model = User
        model = User
        fields = ('email', 'role', 'username', 'first_name', 'last_name', 'bio')


class UserSerializer(serializers.ModelSerializer):

    role = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = ('email', 'role', 'username', 'first_name', 'last_name', 'bio')
        lookup_field = 'username'
        extra_kwargs = {
            'url': {'lookup_field': 'username'}
        }

    def create(self, validated_data):
        user = MyUser.objects.create(**validated_data)
        user.role = self.initial_data['role']
        return user
    
    def update(self, instance, validated_data):
        # breakpoint()
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.role = self.initial_data.get('role', instance.role)
        return super().update(instance, validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, attrs):
        if 'username' not in attrs:
            raise serializers.ValidationError("Username is required")
        if 'email' not in attrs:
            raise serializers.ValidationError("Email is required")
        if attrs['username'] == 'me':
            raise serializers.ValidationError("Using 'me' as a username is not allowed.")
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("User with this username already exists.")
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.confirmation_code = generate_confirmation_code()
        # breakpoint()
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
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        # breakpoint()
        try:
            user = MyUser.objects.get(username=username)
        except MyUser.DoesNotExist:
            raise serializers.ValidationError('User not found')
        # breakpoint()
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError('Invalid confirmation code')

        return data


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


class CategoriesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')

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

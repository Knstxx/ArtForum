from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from django.contrib.auth import get_user_model

from reviews.models import Reviews, Comment, Genre, Title, Category, Role

from .utils import generate_confirmation_code


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'first_name', 'last_name')


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError("Использование 'me' в качестве имени пользователя запрещено.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password']
        )
        user.confirmation_code = ''.join(generate_confirmation_code())
        role = Role.objects.get(name=Role.USER)
        user.role = role
        user.save()
        user.email_user(
            'Confirmation code',
            f'Your confirmation code is: {user.confirmation_code}'
        )
        return user


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        try:
            user = User.objects.get(username=username)
            if user.confirmation_code != confirmation_code:
                raise serializers.ValidationError('Invalid confirmation code')
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found')
        return data


class ReviewsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзывов."""

    author = SlugRelatedField(
        slug_field='username',
        read_only=True, required=False
    )

    class Meta:
        model = Reviews
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели коментариев."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Comment


class TitlesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели произведений."""

    rating = serializers.SerializerMethodField()

    class Meta:
        fields = "__all__"
        model = Title

    def get_rating(self, obj):
        # Здесь будет рейтинг.
        # Получить все отзывы для произведения
        # Пройтись циклом по queryset и высчитать среднее значение
        # из оценок.
        pass


class TitleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Title
        fields = '__all__'


class CategoriesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class GenresSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = '__all__'

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Reviews, Comment


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
    """Сериализатор для модели комментариев."""

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

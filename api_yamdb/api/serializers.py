from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.shortcuts import get_object_or_404

from reviews.models import Reviews, Comment, Genre, Title, Category, TitleGenre


class ReviewsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзывов."""

    author = SlugRelatedField(
        slug_field='username',
        read_only=True, required=False
    )
    title = serializers.PrimaryKeyRelatedField(required=False, read_only=True)

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


class TitleSerializer(serializers.ModelSerializer):

    genre = GenresSerializer(many=True)
    category = CategoriesSerializer()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre', 'category')

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
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        # breakpoint()
        return super().update(instance, validated_data)

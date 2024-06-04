from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly
)

from reviews.models import Reviews, Comment, Genre, Title, Category
from .serializers import (CommentSerializer, TitleSerializer,
                          CategoriesSerializer, GenresSerializer)
from .permissions import IsAuthorModeratorOrReadOnly


class ReviewsViewSet(viewsets.ModelViewSet):
    """ВьюСет модели отзывов."""

    queryset = Reviews.objects.all()
    model = Reviews

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        # Получаем пользователя.
        user = self.request.user
        # Получаем произведение.
        title = self.get_title()
        # Все отзывы пользователя к произведению.
        user_reviews = user.titles.all().filter(title=title)
        if len(user_reviews) != 0:
            return Response(
                'Нельзя оставить больше одного отзыва',
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().perform_create(serializer)

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()


class CommentsViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментов."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorModeratorOrReadOnly,
                          IsAuthenticatedOrReadOnly]

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = self.get_post()
        return title.comments.all()


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer

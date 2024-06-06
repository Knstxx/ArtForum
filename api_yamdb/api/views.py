import random
import string

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly
)
from rest_framework.decorators import action

from reviews.models import (Reviews, Comment,
                            Genre, Title, Category, MyUser, Role)
from .serializers import (CommentSerializer, TitleSerializer,
                          CategoriesSerializer, GenresSerializer,
                          RegisterSerializer, TokenObtainSerializer,
                          UserSerializer)
from .permissions import IsAuthorModeratorOrReadOnly
from .utils import generate_confirmation_code


User = get_user_model()


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.confirmation_code = generate_confirmation_code()
        user.save()
        user.email_user(
            'Confirmation code',
            f'Your confirmation code is: {user.confirmation_code}'
        )
        return Response({'detail': 'Confirmation email sent'},
                        status=status.HTTP_201_CREATED)


class RegisterViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthorModeratorOrReadOnly]


class TokenObtainViewSet(viewsets.ViewSet):
    serializer_class = TokenObtainSerializer
    permission_classes = [AllowAny]


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
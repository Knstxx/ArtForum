from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticatedOrReadOnly
)
from rest_framework.decorators import action

from reviews.models import (Reviews, Comment,
                            Genre, Title, Category, MyUser)
from .serializers import (CommentSerializer, TitleSerializer,
                          CategoriesSerializer, GenresSerializer,
                          RegisterSerializer, TokenObtainSerializer,
                          UserSerializer, ReviewsSerializer)
from .permissions import IsAuthorModeratorOrReadOnly
from .utils import generate_confirmation_code


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'email': user.email, 'username': user.username},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='token')
    def token(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = MyUser.objects.get(username=serializer.validated_data['username'])
        token = 'JWT_TOKEN_HERE'  # Generate JWT token here
        return Response({'token': token}, status=status.HTTP_200_OK)


class RegisterViewSet(viewsets.ViewSet):
    pass


class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer


class TokenObtainViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    serializer_class = TokenObtainSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            confirmation_code = serializer.validated_data['confirmation_code']
            try:
                user = MyUser.objects.get(username=username)
                breakpoint()
                if user.confirmation_code == confirmation_code:
                    # Проверка прошла успешно, возвращаем JWT-токен
                    # Здесь должна быть ваша логика для создания и возвращения JWT-токена
                    return Response({"token": "your_generated_token"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid confirmation code"}, status=status.HTTP_400_BAD_REQUEST)
            except MyUser.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewsViewSet(viewsets.ModelViewSet):
    """ВьюСет модели отзывов."""

    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        # Получаем пользователя.
        user = MyUser.objects.get(username='regul')
        # breakpoint()
        # Получаем произведение.
        title = self.get_title()
        # Все отзывы пользователя к произведению.
        # user_reviews = user.titles.all().filter(title=title)
        '''if len(user_reviews) != 0:
            return Response(
                'Нельзя оставить больше одного отзыва',
                status=status.HTTP_400_BAD_REQUEST
            )'''
        serializer.save(author=user, title=title)

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()


class CommentsViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментов."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    # permission_classes = [IsAuthorModeratorOrReadOnly, IsAuthenticatedOrReadOnly]

    def get_review(self):
        return get_object_or_404(Reviews, id=self.kwargs.get('review_id'))

    def perform_create(self, serializer):
        review = self.get_review()
        user = MyUser.objects.get(username='regul')
        serializer.save(author=user, review=review)

    def get_queryset(self):
        title = self.get_review()
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

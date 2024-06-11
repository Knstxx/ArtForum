from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny, IsAuthenticated
)
from rest_framework.views import APIView
from django.core.mail import send_mail
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import (Reviews, Comment,
                            Genre, Title, Category, MyUser)
from .serializers import (CommentSerializer, TitleSerializer,
                          CategoriesSerializer, GenresSerializer,
                          RegisterSerializer, TokenObtainSerializer,
                          UserSerializer, ReviewsSerializer)
from .permissions import (IsAdminOrRead, IsAdminOrModerOrRead,
                          AdminModeratorAuthorPermission, AdminOnly,
                          IsAdminUserOrReadOnly)
from .utils import generate_confirmation_code


class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, AdminOnly,)
    lookup_field = 'username'
    filter_backends = (SearchFilter, )
    search_fields = ('username', )

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me')
    def get_current_user_info(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = UserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            else:
                serializer = RegisterSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)


class TokenObtainAPIView(APIView):
    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = MyUser.objects.get(username=data['username'])
        except MyUser.DoesNotExist:
            return Response(
                {'username': 'Пользователь не найден!'},
                status=status.HTTP_404_NOT_FOUND)
        if data.get('confirmation_code') == user.confirmation_code:
            token = RefreshToken.for_user(user).access_token
            return Response({'token': str(token)},
                            status=status.HTTP_201_CREATED)
        return Response(
            {'confirmation_code': 'Неверный код подтверждения!'},
            status=status.HTTP_400_BAD_REQUEST)


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'email': user.email, 'username': user.username},
                        status=status.HTTP_200_OK)


class ReviewsViewSet(viewsets.ModelViewSet):
    """ВьюСет модели отзывов."""

    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer
    permission_classes = [IsAdminOrModerOrRead]

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        # Получаем пользователя.
        user = MyUser.objects.get(username='regular-user')
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
    permission_classes = [IsAdminOrModerOrRead]

    def get_review(self):
        return get_object_or_404(Reviews, id=self.kwargs.get('review_id'))

    def perform_create(self, serializer):
        review = self.get_review()
        user = MyUser.objects.get(username='regular-user')
        serializer.save(author=user, review=review)

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrRead]


class CategoriesViewSet(viewsets.ModelViewSet):
    """Вьюсет для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = [IsAdminOrRead]


class GenresViewSet(viewsets.ModelViewSet):
    """Вьюсет для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenresSerializer
    permission_classes = [IsAdminOrRead]

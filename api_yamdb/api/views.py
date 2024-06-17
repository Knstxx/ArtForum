from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from rest_framework.decorators import action, api_view, permission_classes
from django.db.models import Avg
from rest_framework.filters import SearchFilter
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import (Review, Comment,
                            Genre, Title, Category)
from .serializers import (CommentSerializer, TitleSerializer,
                          CategorieSerializer, GenreSerializer,
                          RegisterSerializer, TokenObtainSerializer,
                          UserSerializer, ReviewSerializer
                          )
from .permissions import (IsAdminOrRead,
                          AdminOnly,
                          IsAdminModeratorAuthorOrReadOnly)
from .mixins import ListCreateDestroyViewSet
from .filters import TitleRangeFilter

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет пользователей(админ)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, AdminOnly,)
    lookup_field = 'username'
    filter_backends = (SearchFilter, )
    search_fields = ('username', )
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(methods=['GET', 'PATCH'], detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'GET':
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = UserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                if 'role' not in request.data:
                    serializer = UserSerializer(
                        request.user,
                        data=request.data,
                        partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    """FBV получения токена."""
    serializer = TokenObtainSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    try:
        user = User.objects.get(username=data['username'])
    except User.DoesNotExist:
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


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    username = serializer.validated_data['username']
    user_username = User.objects.filter(username=username)
    user_email = User.objects.filter(email=email)
    if user_email.exists() and user_email[0].username != username:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if user_username.exists() and user_username[0].email != email:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    user, created = User.objects.get_or_create(
        email=email, username=username)
    confirmation_code = default_token_generator.make_token(user)
    user.confirmation_code = confirmation_code
    user.save()
    send_mail(
        'Confirmation code',
        f'Your code {confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewsViewSet(viewsets.ModelViewSet):
    """ВьюСет модели отзывов."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAdminModeratorAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        # Получаем пользователя.
        user = self.request.user
        # Получаем произведение.
        title = self.get_title()
        # Все отзывы пользователя к произведению.
        serializer.save(author=user, title=title)

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()


class CommentsViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментов."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAdminModeratorAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def perform_create(self, serializer):
        review = self.get_review()
        user = self.request.user
        serializer.save(author=user, review=review)

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('rating')
    serializer_class = TitleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleRangeFilter
    permission_classes = [IsAdminOrRead]
    http_method_names = ['get', 'post', 'patch', 'delete']


class CategoriesViewSet(ListCreateDestroyViewSet):
    """Вьюсет для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorieSerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminOrRead]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


class GenresViewSet(ListCreateDestroyViewSet):
    """Вьюсет для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrRead]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'

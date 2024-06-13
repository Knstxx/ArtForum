from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.views import APIView
from django.db.models import Avg
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import (Review, Comment,
                            Genre, Title, Category, MyUser)
from .serializers import (CommentSerializer, TitleSerializer,
                          CategoriesSerializer, GenresSerializer,
                          RegisterSerializer, TokenObtainSerializer,
                          UserSerializer, ReviewsSerializer, UserMeSerialzier)
from .permissions import (IsAdminOrRead,
                          AdminOnly,
                          IsAdminModeratorAuthorOrReadOnly)
from .mixins import ListCreateDestroyViewSet
from .filters import TitleRangeFilter


class UserViewSet(viewsets.ModelViewSet):

    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, AdminOnly,)
    lookup_field = 'username'
    filter_backends = (SearchFilter, )
    search_fields = ('username', )
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(methods=['GET', 'PATCH'], detail=False,
            permission_classes=(IsAuthenticated,), url_path='me')
    def get_current_user_info(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = UserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            else:
                serializer = UserMeSerialzier(
                    request.user,
                    data=request.data,
                    partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


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

    queryset = Review.objects.all()
    serializer_class = ReviewsSerializer
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
    serializer_class = CategoriesSerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminOrRead]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


class GenresViewSet(ListCreateDestroyViewSet):
    """Вьюсет для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenresSerializer
    permission_classes = [IsAdminOrRead]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'

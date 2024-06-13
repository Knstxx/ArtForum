from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (CommentsViewSet, ReviewsViewSet, TitleViewSet,
                       CategoriesViewSet, GenresViewSet,
                       UserViewSet, TokenObtainAPIView, AuthViewSet)


router = DefaultRouter()
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet, basename='comments')

router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewsViewSet, basename='reviews')
router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'categories', CategoriesViewSet, basename='categories')
router.register(r'genres', GenresViewSet, basename='genres')
router.register(r'users', UserViewSet, basename='users')
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/token/', TokenObtainAPIView.as_view(), name='get_token'),
]

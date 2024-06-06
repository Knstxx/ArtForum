from django.urls import path
from rest_framework.routers import DefaultRouter
from django.urls import include

from api.views import (CommentsViewSet, ReviewsViewSet, TitleViewSet,
                       CategoriesViewSet, GenresViewSet)

v1_router = DefaultRouter()

v1_router.register(
    r'titles/(?P<title_id>\d+)/comments',
    CommentsViewSet,
    basename='comments'
)

v1_router.register(r'titles', TitleViewSet)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet,
    basename='reviews'
)

v1_router.register(
    r'posts',
    TitleViewSet,
    basename='titles'
)

v1_router.register(
    r'categories',
    CategoriesViewSet,
    basename='categories'
)

v1_router.register(
    r'genres',
    GenresViewSet,
    basename='genres'
)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]

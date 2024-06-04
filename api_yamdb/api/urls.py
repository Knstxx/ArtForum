from django.urls import path
from rest_framework.routers import DefaultRouter
from django.urls import include

from api.views import (CommentsViewSet, ReviewsViewSet, TitleViewSet,
                       CategoriesViewSet, GenresViewSet)

comments_router = DefaultRouter()
titles_router = DefaultRouter()
categories_router = DefaultRouter()
genres_router = DefaultRouter()
comments_router.register(
    r'titles/(?P<title_id>\d+)/comments',
    CommentsViewSet,
    basename='comments'
)
comments_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet,
    basename='reviews'
)
titles_router.register(
    r'posts',
    TitleViewSet,
    basename='titles'
)
categories_router.register(
    r'categories',
    CategoriesViewSet,
    basename='categories'
)
genres_router.register(
    r'genres',
    GenresViewSet,
    basename='genres'
)
urlpatterns = [
    path('', include(comments_router.urls)),
    path('', include(titles_router.urls)),
    path('', include(categories_router.urls)),
    path('', include(genres_router.urls)),
]

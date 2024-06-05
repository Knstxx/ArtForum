from django.urls import path
from rest_framework.routers import DefaultRouter
from django.urls import include

from api.views import (CommentsViewSet, ReviewsViewSet, TitleViewSet,
                       CategoriesViewSet, GenresViewSet, AuthViewSet,
                       UsersViewSet)

comments_router = DefaultRouter()
titles_router = DefaultRouter()
categories_router = DefaultRouter()
genres_router = DefaultRouter()
auth_router = DefaultRouter()
users_router = DefaultRouter()
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
auth_router.register(r'auth', AuthViewSet, basename='auth')
users_router.register(r'users', UsersViewSet, basename='users')
urlpatterns = [
    path('', include(comments_router.urls)),
    path('', include(titles_router.urls)),
    path('', include(categories_router.urls)),
    path('', include(genres_router.urls)),
    path('', include(auth_router.urls)),
    path('', include(users_router.urls)),
    path('auth/', include('django.contrib.auth.urls')),
]


urlpatterns += [
    path('users/', include(users_router.urls)),
    path('users/me/', include(users_router.urls)),
]
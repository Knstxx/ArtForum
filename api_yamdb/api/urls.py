from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView,
                                            TokenVerifyView)

from api.views import (CommentsViewSet, ReviewsViewSet, TitleViewSet,
                       CategoriesViewSet, GenresViewSet, AuthViewSet,
                       UserViewSet, RegisterViewSet, TokenObtainViewSet)


router = DefaultRouter()
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
                CommentsViewSet, basename='comments')

router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewsViewSet, basename='reviews')

router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'categories', CategoriesViewSet, basename='categories')
router.register(r'genres', GenresViewSet, basename='genres')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='users')
router.register(r'register', RegisterViewSet, basename='register')
router.register(r'token', TokenObtainViewSet, basename='token_obtain')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('auth/', include('django.contrib.auth.urls')),
    # path('v1/users/me/', UserViewSet.as_view({'post': 'create', 'get': 'list'})),
    # path('v1/users/', UserViewSet.as_view({'post': 'create'})),
    path('jwt/', include([
        path('create/', TokenObtainPairView.as_view(),
             name='token_obtain_pair'),
        path('refresh/', TokenRefreshView.as_view(),
             name='token_refresh'),
        path('verify/', TokenVerifyView.as_view(),
             name='token_verify'),
    ])),
]

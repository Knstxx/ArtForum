from django.urls import path
from rest_framework.routers import SimpleRouter
from django.urls import include

from .views import CommentsViewSet, ReviewsViewSet

router_v1 = SimpleRouter()
router_v1.register(
    r'titles/(?P<title_id>\d+)/comments',
    CommentsViewSet,
    basename='comments'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet,
    basename='reviews'
    )
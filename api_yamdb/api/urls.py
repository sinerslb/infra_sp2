from django.urls import include, path
from rest_framework import routers

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet,
                    authenticate_user, create_user)

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register(
    'categories',
    CategoryViewSet,
    basename='сategory'
)
router.register(
    'titles',
    TitleViewSet,
    basename='title'
)
router.register(
    'genres',
    GenreViewSet,
    basename='genre'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
user_urls = [
    path('signup/', create_user),
    path('token/', authenticate_user)
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(user_urls)),
]

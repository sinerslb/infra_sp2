from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Comment, Genre, Review, Title, User

from .filters import TitleFilter
from .mixins import CategoryGenreModelMixin, TitleModelMixin
from .permissions import (AdminOrReadOnly, UserIsAdmin,
                          UserIsAuthorOrAdministration)
from .serializers import (CategorySerializer, CommentSerialiser,
                          GenreSerializer, RegistrationSerializer,
                          ReviewSerialiser, TitleCreateSerializer,
                          TitleSerializer, TokenSerializer, UserEditSerializer,
                          UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (UserIsAdmin,)
    lookup_field = "username"

    @action(
        methods=[
            "get",
            "patch",
        ],
        detail=False,
        url_path="me",
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserEditSerializer,
    )
    def users_owner_profile(self, request):
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def create_user(request):
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user, created = User.objects.get_or_create(
        User,
        username=serializer.validated_data['username'],
        email=serializer.validated_data['email']
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Регстрация на портале YaMDb',
        f'Привет. Это твой код подтверждения - {confirmation_code}',
        'admin@yamdb.ru',  # Это поле "От кого"
        [user.email],
        fail_silently=False,
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def authenticate_user(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User, username=serializer.validated_data['username']
    )
    if default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
    ):
        token = AccessToken.for_user(user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(CategoryGenreModelMixin):
    """Вьюсет для работы с моделью категорий"""

    queryset = Category.objects.all()
    lookup_field = 'slug'
    serializer_class = CategorySerializer
    permission_classes = [AdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


class GenreViewSet(CategoryGenreModelMixin):
    """Вьюсет для работы с моделью жанров"""

    queryset = Genre.objects.all()
    lookup_field = 'slug'
    serializer_class = GenreSerializer
    permission_classes = [AdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


class TitleViewSet(TitleModelMixin):
    """Вьюсет для работы с названиями произведений"""

    queryset = Title.objects.order_by('id')
    permission_classes = [AdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет модели отзывов."""

    serializer_class = ReviewSerialiser
    queryset = Review.objects.all()
    permission_classes = [UserIsAuthorOrAdministration, ]

    def get_title(self):
        return get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )

    def get_permissions(self):
        if self.action in ('retrieve', 'list'):
            return (AllowAny(), )
        if self.action == 'create':
            return (IsAuthenticated(), )
        return super().get_permissions()

    def get_serializer_context(self):
        context = super(ReviewViewSet, self).get_serializer_context()
        context['title'] = self.get_title()
        return context


@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def change_raiting(instance, **kwargs):
    """Пересчитываем рейтинг произведения,
    после добавления/изменения/удаления отзыва.
    """

    title = instance.title
    title.rating = title.reviews.aggregate(Avg('score'))['score__avg']
    title.save()


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет модели комментариев."""

    serializer_class = CommentSerialiser
    queryset = Comment.objects.all()
    permission_classes = [UserIsAuthorOrAdministration, ]

    def review_obj(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )

    def get_queryset(self):
        return self.review_obj().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.review_obj()
        )

    def get_permissions(self):
        if self.action in ('retrieve', 'list'):
            return (AllowAny(), )
        if self.action == 'create':
            return (IsAuthenticated(), )
        return super().get_permissions()

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from reviews.validators import validate_year
from users.models import User

RATING_ERROR_TEXT = 'Оценка должна быть от 1 до 10!'


class Category(models.Model):
    """Модель категорий произведений"""

    name = models.CharField(
        verbose_name='Категория',
        max_length=100
    )
    slug = models.SlugField(
        verbose_name='Ссылка',
        max_length=30,
        unique=True
    )

    class Meta:
        ordering = ['id', ]
        verbose_name_plural = 'Категории'
        verbose_name = 'Категория'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанров"""

    name = models.CharField(
        max_length=50,
        verbose_name='Жанр'
    )
    slug = models.SlugField(
        unique=True,
        max_length=30,
        verbose_name='Ссылка'
    )

    class Meta:
        ordering = ['id', ]
        verbose_name_plural = 'Жанры'
        verbose_name = 'Жанр'


class Title(models.Model):
    """Модель названия произведения"""
    name = models.CharField(
        'Название произведения',
        max_length=200
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория'
    )
    description = models.TextField(
        max_length=200,
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр'
    )
    year = models.IntegerField(
        validators=(validate_year,),
    )
    rating = models.SmallIntegerField(
        'Средний рейтинг',
        blank=True,
        null=True,
        help_text='Средний рейтинг этого произведения',
        validators=[
            MaxValueValidator(10, RATING_ERROR_TEXT),
            MinValueValidator(1, RATING_ERROR_TEXT)
        ],
    )

    class Meta:
        ordering = ['id', ]
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзывов."""

    text = models.TextField(
        'Текст отзыва',
        help_text='Введите текст отзыва',
        blank=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Рецензент',
        blank=False
    )
    score = models.PositiveSmallIntegerField(
        blank=False,
        help_text='Введите оценку произведения',
        verbose_name='Оценка',
        validators=[
            MaxValueValidator(10, RATING_ERROR_TEXT),
            MinValueValidator(1, RATING_ERROR_TEXT)
        ],
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
        blank=False
    )

    class Meta:
        ordering = ['pub_date', ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]


class Comment(models.Model):
    """Модель комментариев."""

    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария',
        blank=False,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментатор',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta:
        ordering = ['pub_date', ]
        verbose_name = 'Комментарий к отзыву'
        verbose_name_plural = 'Комментарии к отзыву'

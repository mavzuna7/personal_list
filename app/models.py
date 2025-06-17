from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import check_password

class User(AbstractUser):
    user_id = models.AutoField(primary_key=True, verbose_name='ID пользователя')
    email = models.EmailField(unique=True, verbose_name='Электронная почта')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

class Genre(models.Model):
    genre_id = models.AutoField(primary_key=True, verbose_name='ID жанра')
    genre_name = models.CharField(max_length=100, verbose_name='Название жанра')

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.genre_name


class Category(models.Model):
    category_id = models.AutoField(primary_key=True, verbose_name='ID категории')
    category_name = models.CharField(max_length=100, verbose_name='Название категории')
    parent_category = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Родительская категория'
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.category_name


class Collection(models.Model):
    collection_id = models.AutoField(primary_key=True, verbose_name='ID коллекции')
    collection_name = models.CharField(max_length=100, verbose_name='Название коллекции')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', null=True)
    STATUS_CHOICES = [
        ('completed', 'Просмотрено'),
        ('watching', 'Смотрю'),
        ('planned', 'Запланировано'),
        ('paused', 'На паузе'),
        ('dropped', 'Брошено'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name='Статус', default='completed')

    class Meta:
        verbose_name = "Коллекция"
        verbose_name_plural = "Коллекции"

    def __str__(self):
        return self.collection_name


class Content(models.Model):
    content_id = models.AutoField(primary_key=True, verbose_name='ID контента')
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name='Название')
    genre = models.CharField(max_length=100, null=True, blank=True, verbose_name='Жанр')
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Коллекция')
    image = models.ImageField(upload_to='content_posters/', null=True, blank=True, verbose_name='Постер')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name='Пользователь')

    STATUS_CHOICES = [
        ('watching', 'Смотрю'),
        ('planned', 'Запланировано'),
        ('completed', 'Просмотрено'),
        ('paused', 'На паузе'),
        ('dropped', 'Брошено'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name='Статус')

    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name='Оценка')
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')
    
    release_year = models.IntegerField(verbose_name='Год выпуска')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    country = models.CharField(max_length=100, null=True, blank=True, verbose_name='Страна')
    director = models.CharField(max_length=100, null=True, blank=True, verbose_name='Режиссёр')
    actor = models.CharField(max_length=100, null=True, blank=True, verbose_name='Актёр')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = "Элемент контента"
        verbose_name_plural = "Элементы контента"

    def __str__(self):
        return f"{self.title or 'Без названия'}: {self.description[:30] if self.description else ''}"
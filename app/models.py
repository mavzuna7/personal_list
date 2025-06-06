from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True, verbose_name='ID пользователя')
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя пользователя',
        default='default_username'  # <-- добавили значение по умолчанию
    )
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    password_hash = models.CharField(max_length=255, verbose_name='Хэш пароля')

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    collection_name = models.CharField(max_length=100, verbose_name='Название коллекции')

    class Meta:
        verbose_name = "Коллекция"
        verbose_name_plural = "Коллекции"

    def __str__(self):
        return f"{self.collection_name} ({self.user.email})"


class Content(models.Model):
    content_id = models.AutoField(primary_key=True, verbose_name='ID контента')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, verbose_name='Жанр')
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Коллекция')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name='Категория')

    STATUS_CHOICES = [
        ('watching', 'Смотрю'),
        ('planned', 'Запланировано'),
        ('completed', 'Просмотрено'),
        ('paused', 'На паузе'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name='Статус')

    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name='Оценка')
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')
    progress = models.CharField(max_length=100, null=True, blank=True, verbose_name='Прогресс')

    TYPE_CHOICES = [
        ('movie', 'Фильм'),
        ('series', 'Сериал'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Тип')  # фильм или сериал

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
        return f"{self.type}: {self.description[:30]}"
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from .models import User, Collection, Content, Genre, Category
from .forms import RegisterForm, LoginForm, CollectionForm, ContentForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib.auth.hashers import make_password
from django.db import models
from django.core.paginator import Paginator
from .services import MovieService
import requests
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import os
from django.views.decorators.http import require_POST

def dashboard_view(request):
    user = request.user
    watched_content = Content.objects.filter(user=user, status='completed')
    top_genres = watched_content.values('genre').annotate(count=Count('genre')).order_by('-count')

    recommended = Content.objects.none()
    if top_genres:
        genre_ids = [g['genre'] for g in top_genres]
        recommended = Content.objects.filter(
            genre_id__in=genre_ids
        ).exclude(user=user).order_by('-rating')[:10]

    return render(request, 'app/dashboard.html', {
        'recommended': recommended,
        'watched_count': watched_content.count(),
        'in_progress_count': Content.objects.filter(user=user, status='watching').count(),
        'planned_count': Content.objects.filter(user=user, status='planned').count(),
    })

def home_view(request):
    if not request.user.is_authenticated:
        return render(request, 'app/welcome.html')
    contents = Content.objects.filter(user=request.user)
    genres = Genre.objects.all()
    years = Content.objects.values_list('release_year', flat=True).distinct().order_by('-release_year')
    statuses = Content.STATUS_CHOICES

    # Фильтры
    genre_id = request.GET.get('genre')
    year = request.GET.get('year')
    status = request.GET.get('status')
    q = request.GET.get('q')

    if genre_id:
        contents = contents.filter(genre_id=genre_id)
    if year:
        contents = contents.filter(release_year=year)
    if status:
        contents = contents.filter(status=status)
    if q:
        contents = contents.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(genre__genre_name__icontains=q))

    # Пагинация: 10 карточек на страницу
    paginator = Paginator(contents, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'app/index.html', {
        'contents': page_obj,
        'genres': genres,
        'years': years,
        'statuses': statuses,
        'selected_genre': genre_id,
        'selected_year': year,
        'selected_status': status,
        'search_query': q,
        'page_obj': page_obj,
    })



def create_user(username, email, password_hash):
    if User.objects.filter(username=username).exists():
        raise ValidationError(f"Пользователь с именем '{username}' уже существует.")
    if User.objects.filter(email=email).exists():
        raise ValidationError(f"Пользователь с email '{email}' уже зарегистрирован.")

    return User.objects.create(
        username=form.cleaned_data['username'],
        email=form.cleaned_data['email'],
        password_hash=make_password(form.cleaned_data['password'])
    )

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                is_active=True,
                is_staff=False,
                is_superuser=False,
            )
            messages.success(request, "Регистрация успешна. Войдите в аккаунт.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'app/register.html', {'form': form})

def login_view(request):
    # Очищаем все сообщения при загрузке страницы входа
    storage = messages.get_messages(request)
    storage.used = True
    
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            from django.contrib.auth import login
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Неверное имя пользователя или пароль")
    else:
        form = LoginForm()
    return render(request, "app/login.html", {"form": form})

def logout_view(request):
    # Очищаем все сообщения перед выходом
    storage = messages.get_messages(request)
    storage.used = True
    logout(request)
    return redirect('home')

@login_required
def collections_view(request):
    status = request.GET.get('status', 'completed')  # По умолчанию 'Просмотрено'
    status_map = {
        'completed': 'Просмотрено',
        'watching': 'Смотрю',
        'planned': 'Запланировано',
        'paused': 'На паузе',
        'dropped': 'Брошено'
    }
    status_order = ['completed', 'watching', 'planned', 'paused', 'dropped']
    # Для "Брошено" используем тот же контент, что и для "На паузе"
    if status == 'dropped':
        status = 'dropped'
    contents = Content.objects.filter(user=request.user, status=status).order_by(
        models.Case(
            *[models.When(status=st, then=pos) for pos, st in enumerate(status_order)],
            output_field=models.IntegerField()
        )
    )
    selected_status_label = status_map.get(request.GET.get('status', 'completed'), 'Просмотрено')
    return render(request, 'app/collections_page.html', {
        'contents': contents,
        'selected_status': request.GET.get('status', 'completed'),
        'status_map': status_map,
        'selected_status_label': selected_status_label,
    })


def collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, collection_id=collection_id)
    contents = Content.objects.filter(collection=collection)  # Показываем все элементы коллекции
    return render(request, 'app/collection_detail.html', {
        'collection': collection,
        'contents': contents
    })

@login_required
def content_detail(request, content_id):
    content = get_object_or_404(Content, content_id=content_id)
    return render(request, 'app/content_detail.html', {
        'content': content
    })

def add_content(request):
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.user = request.user
            content.save()
            messages.success(request, 'Контент успешно добавлен!')
            return redirect('content_detail', content_id=content.content_id)
    else:
        form = ContentForm()
    return render(request, 'app/add_content.html', {'form': form})

@login_required
def edit_content(request, content_id):
    content = get_object_or_404(Content, content_id=content_id)
    genres = Genre.objects.all()
    categories = Category.objects.all()

    if request.method == 'POST':
        # Получаем данные из формы
        title = request.POST.get('title')
        description = request.POST.get('description')
        release_year = request.POST.get('release_year')
        country = request.POST.get('country')
        director = request.POST.get('director')
        actor = request.POST.get('actor')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        genre_id = request.POST.get('genre')
        category_id = request.POST.get('category')
        status = request.POST.get('status')

        # Обновляем объект
        content.title = title
        content.description = description
        content.release_year = release_year
        content.country = country
        content.director = director
        content.actor = actor
        if rating in [None, '']:
            content.rating = None
        else:
            try:
                content.rating = float(rating.replace(',', '.'))
            except ValueError:
                content.rating = None
        content.comment = comment
        content.status = status

        # Обновляем связи
        if genre_id:
            content.genre = Genre.objects.get(genre_id=genre_id)
        if category_id:
            content.category = Category.objects.get(category_id=category_id)

        # Обработка изображения
        if 'image' in request.FILES:
            if content.image:
                content.image.delete()
            content.image = request.FILES['image']

        content.save()
        messages.success(request, 'Изменения успешно сохранены')
        return redirect('content_detail', content_id=content.content_id)

    return render(request, 'app/edit_content.html', {
        'content': content,
        'genres': genres,
        'categories': categories,
    })

@login_required
def delete_content(request, content_id):
    content = get_object_or_404(Content, content_id=content_id)
    
    # Удаляем изображение, если оно есть
    if content.image:
        content.image.delete()
    
    # Удаляем контент
    content.delete()
    messages.success(request, 'Карточка успешно удалена')
    return redirect('home')

@login_required
def delete_collection(request, collection_id):
    collection = get_object_or_404(Collection, collection_id=collection_id)
    if request.user == collection.user:
        collection.delete()
        messages.success(request, 'Коллекция успешно удалена')
        return redirect('collections')
    else:
        messages.error(request, 'У вас нет прав для удаления этой коллекции')
        return redirect('collection_detail', collection_id=collection_id)

@login_required
def search_content(request):
    """API endpoint для поиска информации о фильме или сериале"""
    if request.method == 'GET':
        title = request.GET.get('title', '')
        content_type = request.GET.get('type', 'movie')
        
        if not title:
            return JsonResponse({'error': 'Название не указано'}, status=400)

        movie_service = MovieService()
        content_info = movie_service.search_content(title, content_type)

        if not content_info:
            return JsonResponse({'error': 'Контент не найден'}, status=404)

        # Если есть URL постера, скачиваем его
        if content_info.get('poster_url'):
            try:
                response = requests.get(content_info['poster_url'])
                if response.status_code == 200:
                    # Создаем временный файл
                    temp_file = ContentFile(response.content)
                    file_name = f"content_posters/{os.path.basename(content_info['poster_url'])}"
                    
                    # Сохраняем файл
                    file_path = default_storage.save(file_name, temp_file)
                    content_info['poster_path'] = file_path
            except Exception as e:
                print(f"Ошибка при скачивании постера: {e}")

        # Автозаполнение жанра
        genres = content_info.get('genres', [])
        genre_id = None
        genre_name = None
        if genres:
            # Берём первый жанр из списка TMDB
            genre_name = genres[0]
            genre_obj, created = Genre.objects.get_or_create(genre_name=genre_name)
            genre_id = genre_obj.genre_id
        content_info['genre_id'] = genre_id
        content_info['genre_name'] = genre_name

        return JsonResponse(content_info)

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

def user_collections_view(request, username):
    user = get_object_or_404(User, username=username)
    contents = Content.objects.filter(user=user).order_by('-rating', 'title')
    user_collections = None
    if request.user.is_authenticated:
        user_collections = Collection.objects.filter(user=request.user)
    return render(request, 'app/user_content.html', {
        'contents': contents,
        'profile_user': user,
        'user_collections': user_collections
    })

def recommendations_view(request):
    user = request.user
    # Найти топ-2 жанра, которые пользователь чаще всего смотрит (completed или watching)
    top_genres = (
        Content.objects.filter(user=user, status__in=["completed", "watching"])
        .values('genre')
        .annotate(count=Count('genre'))
        .order_by('-count')[:2]
    )
    genre_ids = [g['genre'] for g in top_genres if g['genre']]
    # Найти контент этих жанров, которого нет у пользователя
    recommendations = (
        Content.objects.filter(genre_id__in=genre_ids)
        .exclude(user=user)
        .order_by('-rating')[:10]
    )
    data = [
        {
            'title': c.title,
            'genre': c.genre.genre_name if c.genre else '',
            'release_year': c.release_year,
            'rating': str(c.rating) if c.rating else '',
            'image': c.image.url if c.image else '',
            'content_id': c.content_id,
        }
        for c in recommendations
    ]
    return JsonResponse({'recommendations': data})

@login_required
@require_POST
def add_to_collection(request):
    collection_id = request.POST.get('collection_id')
    content_id = request.POST.get('content_id')
    collection = get_object_or_404(Collection, collection_id=collection_id, user=request.user)
    original_content = get_object_or_404(Content, content_id=content_id)

    Content.objects.create(
        title=original_content.title,
        genre=original_content.genre,
        collection=collection,
        category=original_content.category,
        image=original_content.image,
        user=request.user,
        status=collection.status,
        rating=original_content.rating,
        comment=original_content.comment,
        release_year=original_content.release_year,
        description=original_content.description,
        country=original_content.country,
        director=original_content.director,
        actor=original_content.actor
    )
    # Редирект с параметром для уведомления
    referer = request.META.get('HTTP_REFERER', '/')
    if '?' in referer:
        return redirect(referer + '&added=1')
    else:
        return redirect(referer + '?added=1')
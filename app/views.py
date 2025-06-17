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
from django.conf import settings
import traceback

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
    # Только уникальные жанры пользователя (без пустых)
    genres = contents.values_list('genre', flat=True).distinct().order_by('genre')
    genres = [g for g in genres if g]  # убираем пустые
    # Только уникальные года пользователя (без пустых и невалидных)
    years = contents.values_list('release_year', flat=True).distinct().order_by('-release_year')
    years = [y for y in years if y and isinstance(y, int) and 1800 < y < 2100]
    statuses = Content.STATUS_CHOICES

    # Фильтры
    genre_id = request.GET.get('genre')
    year = request.GET.get('year')
    status = request.GET.get('status')
    q = request.GET.get('q')

    if genre_id:
        contents = contents.filter(genre=genre_id)
    if year:
        contents = contents.filter(release_year=year)
    if status:
        contents = contents.filter(status=status)
    if q:
        contents = contents.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(genre__icontains=q))

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
            # Если пользователь не выбрал файл, а есть poster_path — подставить его
            poster_path = request.POST.get('poster_path')
            if not request.FILES.get('image') and poster_path:
                from django.core.files import File
                try:
                    # Если путь относительный, делаем абсолютный
                    if not os.path.isabs(poster_path):
                        abs_path = os.path.join(settings.MEDIA_ROOT, poster_path)
                    else:
                        abs_path = poster_path
                    with open(abs_path, 'rb') as f:
                        content.image.save(os.path.basename(abs_path), File(f), save=False)
                except Exception as e:
                    print(f'Ошибка при автозаполнении постера: {e}')
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
        genre_value = request.POST.get('genre')
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
        content.genre = genre_value
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

        # Автозаполнение жанра (теперь строка)
        genres = content_info.get('genres', [])
        genre = genres[0] if genres else ''
        content_info['genre'] = genre

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
    from django.contrib.auth.decorators import login_required
    import requests
    from django.conf import settings
    user = request.user
    errors = []
    # Берём последние 2 фильма/сериала пользователя с tmdb_id
    user_contents = Content.objects.filter(user=user, tmdb_id__isnull=False).order_by('-created_at')[:2]
    recommendations = []
    api_key = settings.TMDB_API_KEY

    for content in user_contents:
        if not content.tmdb_id or not content.tmdb_type:
            continue
        if content.tmdb_type == 'movie':
            url = f'https://api.themoviedb.org/3/movie/{content.tmdb_id}/similar'
        else:
            url = f'https://api.themoviedb.org/3/tv/{content.tmdb_id}/similar'
        params = {'api_key': api_key, 'language': 'ru-RU', 'page': 1}
        try:
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                results = resp.json().get('results', [])
                for r in results:
                    recommendations.append({
                        'title': r.get('title') or r.get('name'),
                        'poster_url': f"https://image.tmdb.org/t/p/w500{r.get('poster_path')}" if r.get('poster_path') else '',
                        'overview': r.get('overview', ''),
                        'release_year': (r.get('release_date') or r.get('first_air_date') or '')[:4],
                        'rating': r.get('vote_average', ''),
                        'tmdb_id': r.get('id'),
                        'tmdb_type': content.tmdb_type,
                    })
            else:
                errors.append(f"TMDB API error: {resp.status_code} {resp.text}")
        except Exception as e:
            errors.append(traceback.format_exc())

    # Убираем дубли и свои фильмы, оставляем только 4 рекомендации
    seen = set()
    filtered = []
    for rec in recommendations:
        key = (rec['tmdb_id'], rec['tmdb_type'])
        if key not in seen and not Content.objects.filter(user=user, tmdb_id=rec['tmdb_id'], tmdb_type=rec['tmdb_type']).exists():
            filtered.append(rec)
            seen.add(key)
        if len(filtered) == 4:
            break

    if errors and not filtered:
        return JsonResponse({'recommendations': [], 'error': '\n'.join(errors)})
    return JsonResponse({'recommendations': filtered})

@login_required
@require_POST
def add_to_collection(request):
    content_id = request.POST.get('content_id')
    status = request.POST.get('status')
    original_content = get_object_or_404(Content, content_id=content_id)

    Content.objects.create(
        title=original_content.title,
        genre=original_content.genre,
        image=original_content.image,
        user=request.user,
        status=status,
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
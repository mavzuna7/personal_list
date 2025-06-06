from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .models import User, Collection, Content
from .forms import RegisterForm
from django.contrib import messages
from .forms import LoginForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

def home_view(request):
    contents = Content.objects.all()
    return render(request, 'app/index.html', {'contents': contents})

@login_required
def profile_view(request):
    user = request.user
    collections_count = Collection.objects.filter(user=user).count()
    content_count = Content.objects.filter(user=user).count()

    context = {
        'user': user,
        'collections_count': collections_count,
        'content_count': content_count,
    }

    return render(request, 'app/profile.html', context)

def create_user(username, email, password_hash):
    if User.objects.filter(username=username).exists():
        raise ValidationError(f"Пользователь с именем '{username}' уже существует.")
    if User.objects.filter(email=email).exists():
        raise ValidationError(f"Пользователь с email '{email}' уже зарегистрирован.")

    return User.objects.create(
        username=username,
        email=email,
        password_hash=password_hash
    )

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Сохраняем пользователя
            User.objects.create(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password_hash=form.cleaned_data['password']  # В реальном проекте используйте hash-функцию!
            )
            return redirect('home')  # заменить на нужный маршрут
    else:
        form = RegisterForm()

    return render(request, 'app/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            from django.contrib.auth import login
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            return redirect("home")  # замени на нужный маршрут
    else:
        form = LoginForm()

    return render(request, "app/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('home')  # замени 'home' на нужный маршрут

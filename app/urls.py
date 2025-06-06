from django.urls import path
from app.views import home_view
from .views import register_view, login_view, logout_view, profile_view

urlpatterns = [
    path('', home_view, name='home'),  # маршрут с именем 'home'
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
     path('logout/', logout_view, name='logout'), 
     path('profile/', profile_view, name='profile'),
]

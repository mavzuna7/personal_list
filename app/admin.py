from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Genre, Category, Collection, Content

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email')
    search_fields = ('username', 'email')

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('genre_id', 'genre_name')
    search_fields = ('genre_name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_name', 'parent_category')
    list_filter = ('parent_category',)
    search_fields = ('category_name',)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('collection_id', 'collection_name')
    search_fields = ('collection_name',)


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('content_id', 'title', 'genre', 'release_year', 'rating')
    list_filter = ('genre', 'release_year')
    search_fields = ('title', 'description', 'country', 'director', 'actor')
    readonly_fields = ('created_at', 'updated_at')


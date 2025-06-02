from django.contrib import admin

from django.contrib import admin
from .models import User, Genre, Category, Collection, Content


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'email')
    search_fields = ('email',)
    ordering = ('user_id',)


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
    list_display = ('collection_id', 'collection_name', 'user')
    search_fields = ('collection_name',)
    list_filter = ('user',)


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('content_id', 'type', 'user', 'genre', 'category', 'release_year', 'rating')
    list_filter = ('type', 'genre', 'category', 'release_year')
    search_fields = ('description', 'country', 'director', 'actor')
    readonly_fields = ('created_at', 'updated_at')

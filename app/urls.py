from django.urls import path
from app.views import (
    home_view,
    register_view,
    login_view,
    logout_view,
    collections_view,
    collection_detail,
    content_detail,
    add_content,
    edit_content,
    delete_content,
    delete_collection,
    search_content,
    user_collections_view,
    recommendations_view,
    add_to_collection
)

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('collections/', collections_view, name='collections'),
    path('collections/<int:collection_id>/', collection_detail, name='collection_detail'),
    path('collections/<int:collection_id>/delete/', delete_collection, name='delete_collection'),
    path('content/<int:content_id>/', content_detail, name='content_detail'),
    path('content/<int:content_id>/edit/', edit_content, name='edit_content'),
    path('content/<int:content_id>/delete/', delete_content, name='delete_content'),
    path('content/add/', add_content, name='add_content'),
    path('api/search-content/', search_content, name='search_content'),
    path('user/<str:username>/collections/', user_collections_view, name='user_collections'),
    path('recommendations/', recommendations_view, name='recommendations'),
    path('add-to-collection/', add_to_collection, name='add_to_collection'),
]

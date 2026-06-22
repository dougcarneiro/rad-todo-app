from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.list_todos, name='home'),
    path('create/', views.create_todo, name='create_todo'),
    path('<uuid:pk>/edit/', views.edit_todo, name='edit_todo'),
    path('<uuid:pk>/delete/', views.delete_todo, name='delete_todo'),
    path('<uuid:pk>/toggle/', views.toggle_todo, name='toggle_todo'),
    path('profile/', views.profile, name='profile'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.custom_login, name='login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # API URLs
    path('api/', include('todos.api_urls')),
]

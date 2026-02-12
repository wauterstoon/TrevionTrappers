from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('profile/', views.my_profile_view, name='my_profile'),
    path('profile/<str:username>/', views.profile_detail_view, name='profile_detail'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
]

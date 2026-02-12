from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('rides/', views.ride_list_view, name='ride_list'),
    path('rides/create/', views.ride_create_view, name='ride_create'),
    path('rides/<int:pk>/', views.ride_detail_view, name='ride_detail'),
    path('rides/<int:pk>/edit/', views.ride_edit_view, name='ride_edit'),
    path('rides/<int:pk>/delete/', views.ride_delete_view, name='ride_delete'),
    path('rides/<int:pk>/signup/', views.ride_signup_view, name='ride_signup'),
    path('rides/<int:pk>/unsubscribe/', views.ride_unsubscribe_view, name='ride_unsubscribe'),
    path('rides/<int:pk>/finish/', views.mark_finished_self_view, name='ride_finish_self'),
    path('rides/<int:pk>/process/', views.ride_process_view, name='ride_process'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
]

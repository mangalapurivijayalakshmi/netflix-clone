from django.urls import path
from . import api_views

urlpatterns = [
    path('auth/token/', api_views.LoginAPIView.as_view(), name='api_token'),

    path('genres/', api_views.genres_api, name='api_genres'),
    path('movies/', api_views.movies_api, name='api_movies'),
    path('movies/<uuid:pk>/', api_views.movie_detail_api, name='api_movie_detail'),
    path('recommendations/', api_views.recommendations_api, name='api_recommendations'),

    path('my-list/', api_views.my_list_api, name='api_my_list'),
    path('my-list/<uuid:pk>/', api_views.my_list_remove_api, name='api_my_list_remove'),

    path('favorites/', api_views.favorites_api, name='api_favorites'),
    path('favorites/<uuid:pk>/', api_views.favorite_remove_api, name='api_favorite_remove'),

    path('watch-later/', api_views.watch_later_api, name='api_watch_later'),
    path('watch-later/<uuid:pk>/', api_views.watch_later_remove_api, name='api_watch_later_remove'),

    path('notifications/', api_views.notifications_api, name='api_notifications'),
    path('notifications/<int:pk>/read/', api_views.notification_mark_read_api, name='api_notification_read'),
    
    path('profiles/', api_views.profiles_api, name='api_profiles'),
    path('profiles/<int:pk>/select/', api_views.select_profile_api, name='api_select_profile'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('', views.user_login, name='home'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    
    path('signup/', views.signup, name='signup'),
    path('index/', views.index, name='index'),

    path('genre/<str:pk>/', views.genre_view, name='genre'),
    path('movie/<str:pk>/', views.movie_detail, name='movie'),

    path('watch-later/<uuid:pk>/',views.add_to_watch_later,name='add_to_watch_later'),
    path('watch-later/',views.watch_later,name='watch_later'),

    path('favorite/<uuid:pk>/', views.add_to_favorite, name='add_to_favorite'),
    
    path('favorites/', views.favorites, name='favorites'),
    path('remove-favorite/<uuid:pk>/', views.remove_favorite, name='remove_favorite'),
    
    path('history/', views.watch_history, name='history'),
    path('notifications/', views.notifications, name='notifications'),
    
    path('add_to_list/', views.add_to_list, name='add_to_list'),
    path('my_list/', views.my_list, name='my_list'),

    path('search/', views.search, name='search'),
    path('search-suggestions/', views.live_search, name='live_search'),
    
    path('profile/', views.profile_view, name='profile'),
    path('create-profile/', views.create_profile, name='create_profile'),
    path("select-profile/<int:pk>/",views.select_profile,name="select_profile"),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),

    path('watchparty/create/<uuid:pk>/', views.create_watch_party, name='create_watch_party'),
    path('watchparty/<str:code>/', views.watch_party_room, name='watch_party_room'),
    path('chatbot/ask/', views.chatbot_api, name='chatbot_api'),
]

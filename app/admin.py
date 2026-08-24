from django.contrib import admin
from .models import Genre, Movie, Movielist, Profile, UserProfile
from .models import WatchHistory, Review, Favorite,WatchLater, Notification

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'genre',
        'rating',
        'director',
        'language',
        'movie_views',
        'is_trending',
        'is_top_rated',
        'is_original'
    )

    list_filter = (
        'genre',
        'language',
        'is_trending',
        'is_top_rated',
        'is_original',
        'featured',
        'recently_added',
        'top10'
    )

    search_fields = (
        'title',
        'director',
        'cast'
    )

    ordering = ('title',)

@admin.register(Movielist)
class MovielistAdmin(admin.ModelAdmin):
    list_display = ('profile', 'movie', 'added_at')
    search_fields = ('profile__profile_name', 'movie__title')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username',)
admin.site.register(UserProfile)
admin.site.register(WatchHistory)
admin.site.register(Review)
admin.site.register(Favorite)
admin.site.register(WatchLater)
admin.site.register(Notification)
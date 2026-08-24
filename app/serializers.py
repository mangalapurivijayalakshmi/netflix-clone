from rest_framework import serializers
from .models import Genre, Movie, Movielist, Review, UserProfile, Favorite, WatchLater, Notification


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']


class MovieListSerializer(serializers.ModelSerializer):
    """Grid pages (home, genre, search, my list) కోసం light serializer"""
    genre = serializers.CharField(source='genre.name', read_only=True)

    class Meta:
        model = Movie
        fields = ['uu_id', 'title', 'genre', 'release_date', 'length',
                  'image_card', 'rating', 'movie_views', 'is_trending', 'top10']


class MovieDetailSerializer(serializers.ModelSerializer):
    """Movie detail page కోసం పూర్తి serializer"""
    genre = serializers.CharField(source='genre.name', read_only=True)

    class Meta:
        model = Movie
        fields = ['uu_id', 'title', 'description', 'genre', 'release_date', 'length',
                  'image_card', 'image_cover', 'video', 'trailer_preview', 'movie_views',
                  'rating', 'director', 'cast', 'language', 'country', 'age_limit']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'username', 'rating', 'review', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'profile_name', 'avatar']


class MovielistSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)

    class Meta:
        model = Movielist
        fields = ['id', 'movie', 'added_at']

class FavoriteSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'movie', 'added_at']


class WatchLaterSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)

    class Meta:
        model = WatchLater
        fields = ['id', 'movie', 'added_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']
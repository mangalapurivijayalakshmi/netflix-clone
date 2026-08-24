from django.db import models
from django.contrib.auth.models import User
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    uu_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=250)
    description = models.TextField()
    release_date = models.DateField()
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    length = models.PositiveIntegerField()
    image_card = models.ImageField(upload_to='movie_images/')
    image_cover = models.ImageField(upload_to='movie_images/')
    video = models.URLField()
    trailer_preview = models.FileField(upload_to='trailers/', blank=True, null=True)
    movie_views = models.PositiveIntegerField(default=0)
    is_trending = models.BooleanField(default=False)
    is_top_rated = models.BooleanField(default=False)
    is_original = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    director = models.CharField(max_length=100, blank=True)
    cast = models.TextField(blank=True)
    language = models.CharField(max_length=50, default="English")
    country = models.CharField(max_length=50, default="USA")
    age_limit = models.CharField(max_length=10, default="13+")
    subtitles=models.TextField(blank=True,help_text="ఫార్మాట్: start-end|text (ఒక్కో లైన్ కి ఒక subtitle). ఉదా: 0-5|Welcome to the movie")
    featured = models.BooleanField(default=False)
    recently_added = models.BooleanField(default=False)
    top10 = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Movielist(models.Model):
    profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, null=True, blank=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'movie')

    def __str__(self):
        return f"{self.profile} - {self.movie.title}"

class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watched_on = models.DateTimeField(auto_now=True)
    progress = models.PositiveIntegerField(default=0)
    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} watched {self.movie.title}"
    

class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie') 
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"

class Favorite(models.Model):
    profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, null=True, blank=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'movie')

    def __str__(self):
        return f"{self.profile} - {self.movie.title}"

class WatchLater(models.Model):
    profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, null=True, blank=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'movie')

    def __str__(self):
        return f"{self.profile} - {self.movie.title}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_name = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_kids = models.BooleanField(default=False, verbose_name="Kids Profile") 
    
    def __str__(self):
        return f"{self.user.username} - {self.profile_name}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.message

class WatchPartyRoom(models.Model):
    code = models.CharField(max_length=10, unique=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.movie.title}"
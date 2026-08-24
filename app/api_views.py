from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from .views import get_active_profile
from .models import (Genre, Movie, Movielist, Review, UserProfile,
                      Favorite, WatchLater, Notification, WatchHistory)
from .serializers import (GenreSerializer, MovieListSerializer, MovieDetailSerializer,
                           ReviewSerializer, UserProfileSerializer, MovielistSerializer,
                           FavoriteSerializer, WatchLaterSerializer, NotificationSerializer)

class LoginAPIView(ObtainAuthToken):
    """POST username/password -> {"token": "..."}  (React/mobile app కోసం)"""
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        response.data['username'] = token.user.username
        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def genres_api(request):
    genres = Genre.objects.all()
    return Response(GenreSerializer(genres, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def movies_api(request):
    """GET /api/movies/?genre=Action&sort=rating&search=matrix"""
    movies = Movie.objects.select_related('genre').all()

    genre_param = request.GET.get('genre')
    if genre_param:
        movies = movies.filter(genre__name=genre_param)

    search_param = request.GET.get('search')
    if search_param:
        movies = movies.filter(title__icontains=search_param)

    sort = request.GET.get('sort')
    if sort == 'rating':
        movies = movies.order_by('-rating')
    elif sort == 'latest':
        movies = movies.order_by('-release_date')
    elif sort == 'views':
        movies = movies.order_by('-movie_views')

    return Response(MovieListSerializer(movies, many=True, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def movie_detail_api(request, pk):
    """GET /api/movies/<uuid>/ -> movie details + reviews + similar movies"""
    movie = get_object_or_404(Movie, uu_id=pk)
    reviews = Review.objects.filter(movie=movie)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    similar = Movie.objects.filter(genre=movie.genre).exclude(id=movie.id)[:6]

    return Response({
        'movie': MovieDetailSerializer(movie, context={'request': request}).data,
        'average_rating': avg_rating,
        'reviews': ReviewSerializer(reviews, many=True).data,
        'similar_movies': MovieListSerializer(similar, many=True, context={'request': request}).data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommendations_api(request):
    """
    GET /api/recommendations/
    మీ index() view లో ఉన్న logic నే ఇక్కడ API గా ఇస్తోంది —
    last watched genre ఆధారంగా, లేకపోతే top-rated fallback.
    """
    last_watch = WatchHistory.objects.filter(user=request.user).order_by('-id').first()

    if last_watch:
        recommended = Movie.objects.filter(
            genre=last_watch.movie.genre
        ).exclude(uu_id=last_watch.movie.uu_id)[:10]

        if not recommended.exists():
            recommended = Movie.objects.exclude(
                uu_id=last_watch.movie.uu_id
            ).order_by('-rating')[:10]
    else:
        recommended = Movie.objects.order_by('-rating')[:10]

    return Response({
        'has_history': last_watch is not None,
        'results': MovieListSerializer(recommended, many=True, context={'request': request}).data,
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def my_list_api(request):
    active_profile = get_active_profile(request)

    if not active_profile:
        return Response({'error': 'Profile select చేయలేదు. ముందు /api/profiles/<id>/select/ call చేయండి.'}, status=400)

    if request.method == 'GET':
        items = Movielist.objects.filter(owner_user=request.user).select_related('movie')
        return Response(MovielistSerializer(items, many=True, context={'request': request}).data)

    movie = get_object_or_404(Movie, uu_id=request.data.get('movie_id'))
    _, created = Movielist.objects.get_or_create(profile=active_profile, movie=movie)
    return Response(
        {'status': 'added' if created else 'already in list'},
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def my_list_remove_api(request, pk):
    movie = get_object_or_404(Movie, uu_id=pk)
    active_profile=get_active_profile(request)
    Movielist.objects.filter(profile=active_profile, movie=movie).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def profiles_api(request):
    """GET: profiles జాబితా | POST {"profile_name": "...", "avatar": file}: కొత్తది create"""
    if request.method == 'GET':
        profiles = UserProfile.objects.filter(user=request.user)
        return Response(UserProfileSerializer(profiles, many=True, context={'request': request}).data)

    # ✅ కొత్తగా add చేసింది — web app లో ఉన్న 5-profile limit ఇక్కడ కూడా
    existing_count = UserProfile.objects.filter(user=request.user).count()
    if existing_count >= 5:
        return Response({'error': 'మీరు గరిష్టంగా 5 profiles మాత్రమే create చేయగలరు.'}, status=400)

    name = request.data.get('profile_name', '').strip()
    if not name:
        return Response({'error': 'profile_name is required.'}, status=400)
    profile = UserProfile.objects.create(user=request.user, profile_name=name)
    return Response(UserProfileSerializer(profile).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def select_profile_api(request, pk):
    profile = get_object_or_404(UserProfile, id=pk, user=request.user)
    request.session['selected_profile'] = profile.id
    request.session['selected_profile_name'] = profile.profile_name
    request.session['selected_profile_avatar'] = profile.avatar.url if profile.avatar else ''
    return Response(UserProfileSerializer(profile).data)


# ---------- Favorites ----------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def favorites_api(request):
    """GET: favorites జాబితా | POST {"movie_id": "<uuid>"}: add చేస్తుంది"""
    active_profile = get_active_profile(request)
    if not active_profile:
        return Response({'error': 'Profile select చేయలేదు.'}, status=400)

    if request.method == 'GET':
        items = Favorite.objects.filter(profile=active_profile).select_related('movie')
        return Response(FavoriteSerializer(items, many=True, context={'request': request}).data)

    movie = get_object_or_404(Movie, uu_id=request.data.get('movie_id'))
    _, created = Favorite.objects.get_or_create(profile=active_profile, movie=movie)
    return Response(
        {'status': 'added' if created else 'already a favorite'},
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def favorite_remove_api(request, pk):
    movie = get_object_or_404(Movie, uu_id=pk)
    active_profile = get_active_profile(request)
    Favorite.objects.filter(profile=active_profile, movie=movie).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ---------- Watch Later ----------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def watch_later_api(request):
    """GET: watch later జాబితా | POST {"movie_id": "<uuid>"}: add చేస్తుంది"""
    active_profile = get_active_profile(request)
    if not active_profile:
        return Response({'error': 'Profile select చేయలేదు.'}, status=400)

    if request.method == 'GET':
        items = WatchLater.objects.filter(profile=active_profile).select_related('movie')
        return Response(WatchLaterSerializer(items, many=True, context={'request': request}).data)

    movie = get_object_or_404(Movie, uu_id=request.data.get('movie_id'))
    _, created = WatchLater.objects.get_or_create(profile=active_profile, movie=movie)
    return Response(
        {'status': 'added' if created else 'already in watch later'},
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def watch_later_remove_api(request, pk):
    movie = get_object_or_404(Movie, uu_id=pk)
    active_profile = get_active_profile(request)
    WatchLater.objects.filter(profile=active_profile, movie=movie).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ---------- Notifications ----------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications_api(request):
    notifications = Notification.objects.filter(user=request.user)
    return Response(NotificationSerializer(notifications, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notification_mark_read_api(request, pk):
    notif = get_object_or_404(Notification, id=pk, user=request.user)
    notif.is_read = True
    notif.save()
    return Response(NotificationSerializer(notif).data)
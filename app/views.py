from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Avg, Count
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import random
import string
from .models import Genre, Movie, Movielist, Profile, WatchHistory,Review, Favorite, WatchLater, UserProfile, Notification,WatchPartyRoom
from .forms import SignUpForm, ProfileForm, ReviewForm, UserProfileForm
from django.core.paginator import Paginator

from .recommender import get_similar_movies, smart_search, get_collaborative_recommendations
import os
import json
from anthropic import Anthropic

from .sentiment_analysis import analyze_sentiment

def get_active_profile(request):
    """Session లో ఎంచుకున్న profile ని తీసుకువస్తుంది. ఏదీ select చేయకపోతే None వస్తుంది."""
    profile_id = request.session.get("selected_profile")
    if not profile_id:
        return None
    return UserProfile.objects.filter(id=profile_id, user=request.user).first()
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
                return redirect('signup')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
                return redirect('signup')

            user = User.objects.create_user(username=username, email=email, password=password)
            Profile.objects.create(user=user)
            messages.success(request, "Account created successfully")
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        messages.error(request, "Invalid credentials")
    return render(request, 'login.html')

@login_required(login_url='login')
def index(request):

    genres = Genre.objects.all()
    movies = Movie.objects.select_related('genre').all()

    active_profile_check = get_active_profile(request)
    KID_SAFE_RATINGS = ['U', '7+', 'PG', 'G', 'U/A 7+']
    if active_profile_check and active_profile_check.is_kids:
        movies = movies.filter(age_limit__in=KID_SAFE_RATINGS)

    selected_genre = request.GET.get("genre")
    sort = request.GET.get("sort")

    # Genre Filter
    if selected_genre:
        movies = movies.filter(genre__name=selected_genre)

    # Sorting
    if sort == "rating":
        movies = movies.order_by("-rating")

    elif sort == "latest":
        movies = movies.order_by("-release_date")

    elif sort == "views":
        movies = movies.order_by("-movie_views")

    elif sort == "az":
        movies = movies.order_by("title")
    featured_movie = Movie.objects.filter(featured=True).first()
    featured_movies = Movie.objects.select_related('genre').filter(featured=True)

    trending_movies = Movie.objects.select_related('genre').filter(is_trending=True)
    top_rated_movies = Movie.objects.select_related('genre').filter(is_top_rated=True)
    original_movies = Movie.objects.select_related('genre').filter(is_original=True)
    recent_movies = Movie.objects.select_related('genre').filter(recently_added=True)
    top10_movies = Movie.objects.select_related('genre').filter(top10=True)

    if active_profile_check and active_profile_check.is_kids:
        featured_movies = featured_movies.filter(age_limit__in=KID_SAFE_RATINGS)
        trending_movies = trending_movies.filter(age_limit__in=KID_SAFE_RATINGS)
        top_rated_movies = top_rated_movies.filter(age_limit__in=KID_SAFE_RATINGS)
        original_movies = original_movies.filter(age_limit__in=KID_SAFE_RATINGS)
        recent_movies = recent_movies.filter(age_limit__in=KID_SAFE_RATINGS)
        top10_movies = top10_movies.filter(age_limit__in=KID_SAFE_RATINGS)
        if featured_movie and featured_movie.age_limit not in KID_SAFE_RATINGS:
            featured_movie = Movie.objects.filter(featured=True, age_limit__in=KID_SAFE_RATINGS).first()
    featured_movies = featured_movies[:5]
    
    active_profile_obj = active_profile_check

    continue_watching = WatchHistory.objects.filter(
        user=request.user
    ).select_related('movie')[:10] 
 
     
    watched_movie_ids = WatchHistory.objects.filter(
        user=request.user
    ).values_list('movie__uu_id', flat=True) if active_profile_obj else []

    # User ఏ genres ఎన్నిసార్లు చూశారో లెక్కపెడుతుంది (అన్ని history నుండి, ఒక్క సినిమా నుండి కాదు)
    genre_counts = WatchHistory.objects.filter(
        user=request.user
    ).values('movie__genre__name').annotate(
        watch_count=Count('movie__genre')
    ).order_by('-watch_count') 

    recommended_movies = Movie.objects.none()

    if genre_counts.exists():
        
        top_genres = [g['movie__genre__name'] for g in genre_counts[:3]]

        recommended_movies = Movie.objects.filter(
            genre__name__in=top_genres
        ).exclude(
            uu_id__in=watched_movie_ids
        ).order_by('-rating')

        # Fallback: ఇష్టమైన genres లో కొత్త movies లేకపోతే, top-rated movies చూపించు
        if not recommended_movies.exists():
            recommended_movies = Movie.objects.exclude(
                uu_id__in=watched_movie_ids
            ).order_by('-rating')

        if active_profile_check and active_profile_check.is_kids:
            recommended_movies = recommended_movies.filter(age_limit__in=KID_SAFE_RATINGS)

        recommended_movies = recommended_movies[:10]
        
    notification_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count() 

    active_profile = active_profile_obj
    profile_id = request.session.get("selected_profile")

    if profile_id:

        active_profile = UserProfile.objects.filter(
            id=profile_id,
            user=request.user
        ).first()

    selected_profile_name = request.session.get("selected_profile_name")
    selected_profile_avatar = request.session.get("selected_profile_avatar")
               
    paginator = Paginator(movies, 12)  # ఒక్కో page కి 12 movies
    page_number = request.GET.get('page')
    movies_page = paginator.get_page(page_number)
    
    return render(request, 'index.html', {
        'genre': genres,
        'movies': movies_page,
        'selected_genre': selected_genre,
        'sort': sort,

        'featured_movie': featured_movie,
        'featured_movies': featured_movies,

        'trending_movies': trending_movies,
        'top_rated_movies': top_rated_movies,
        'original_movies': original_movies,
        'recent_movies': recent_movies,
        'top10_movies': top10_movies,

        'continue_watching': continue_watching,
        'recommended_movies': recommended_movies,

        'notification_count': notification_count,
        'active_profile': active_profile,

        'selected_profile_name': selected_profile_name,
        'selected_profile_avatar': selected_profile_avatar,

    })

@login_required(login_url='login')
def genre_view(request, pk):
    genres = Genre.objects.all()
    selected_genre = get_object_or_404(Genre, name=pk)
    movies = Movie.objects.filter(genre=selected_genre)
    return render(request, 'genre.html', {
        'genre': genres,
        'movies': movies,
        'movie_genre': selected_genre.name
    })

@login_required(login_url='login')
def movie_detail(request, pk):
    genres = Genre.objects.all()
    movie = get_object_or_404(Movie, uu_id=pk)
    reviews = Review.objects.filter(movie=movie)

    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            already_reviewed = Review.objects.filter(
                user=request.user, movie=movie
            ).exists()

            if already_reviewed:
                messages.error(request, "You have already reviewed this movie.")
                return redirect('movie', pk=movie.uu_id)

            review = form.save(commit=False)
            review.user = request.user
            review.movie = movie
            review.sentiment = analyze_sentiment(review.review)
            review.save()
            messages.success(request, "Review submitted successfully!")

            return redirect('movie', pk=movie.uu_id)

    else:
        form = ReviewForm()

    viewed_key = f"viewed_{movie.uu_id}"
    if not request.session.get(viewed_key):
        movie.movie_views += 1
        movie.save()
        request.session[viewed_key] = True
    history, created = WatchHistory.objects.get_or_create(
        user=request.user,
        movie=movie
    )
    if created:
        history.progress = 20
    else:
        history.progress = min(history.progress + 20, 100)

    history.save()

    active_profile = get_active_profile(request)

    already_saved = False

    if active_profile:
        already_saved = Movielist.objects.filter(
            profile=active_profile,
            movie=movie
    ).exists()
    if "watch?v=" in movie.video:
        embed_url = movie.video.replace("watch?v=", "embed/")
    elif "youtu.be/" in movie.video:
        video_id = movie.video.split("youtu.be/")[-1].split("?")[0]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
    else:
        embed_url = movie.video

    separator = "&" if "?" in embed_url else "?"
    embed_url += f"{separator}cc_load_policy=1&cc_lang_pref=en"

    video_id_match = re.search(r"(?:v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})", movie.video)
    video_id = video_id_match.group(1) if video_id_match else ""

    similar_movies = get_similar_movies(movie, top_n=6)
    if not similar_movies:
        similar_movies = Movie.objects.filter(
            genre=movie.genre
    ).exclude(id=movie.id)[:6]
        
    collaborative_movies = get_collaborative_recommendations(movie, top_n=6)     
    reviews = Review.objects.filter(movie=movie)
    average_rating = reviews.aggregate(
        Avg('rating')
    )['rating__avg']
    return render(request, 'movie.html', {
        'genre': genres,
        'movie_details': movie,
        'already_saved': already_saved,
        'embed_url': embed_url,
        'video_id': video_id,
        'similar_movies': similar_movies,
        'collaborative_movies':collaborative_movies,
        'form': form,
        'reviews': reviews,
        'average_rating': average_rating,
    })

@login_required(login_url='login')
def add_to_watch_later(request, pk):

    movie = get_object_or_404(Movie, uu_id=pk)
    active_profile = get_active_profile(request)
    WatchLater.objects.get_or_create(
        profile=active_profile,
        movie=movie
    )

    messages.success(request, "Movie added to Watch Later!")

    return redirect('movie', pk=pk)

@login_required(login_url='login')   
def watch_later(request):
    active_profile = get_active_profile(request)
    saved = WatchLater.objects.filter(profile=active_profile)
    watch_later_movies = [item.movie for item in saved]            
    return render(request, 'watch_later.html', {
        'watch_later_movies': watch_later_movies
    })
@login_required(login_url='login')
def add_to_list(request):
    if request.method == 'POST':
        movie_url_id = request.POST.get('movie_id')
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        match = re.search(uuid_pattern, movie_url_id)
        movie_id = match.group() if match else None
        movie = get_object_or_404(Movie, uu_id=movie_id)
        active_profile = get_active_profile(request)

        obj, created = Movielist.objects.get_or_create(
            profile=active_profile,
            movie=movie
        )
        if created:
            return JsonResponse({'status': 'success', 'message': 'Added to My List'})
        return JsonResponse({'status': 'info', 'message': 'Already in My List'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required(login_url='login')
def my_list(request):
    genres = Genre.objects.all()
    active_profile = get_active_profile(request)

    saved = Movielist.objects.filter(
        profile=active_profile
    )
    movies = [item.movie for item in saved]
    return render(request, 'my_list.html', {'genre': genres, 'movies': movies})

@login_required(login_url='login')
def search(request):
    genres = Genre.objects.all()

    if request.method == "POST":

        search_term = request.POST.get("search_term")

        # Save recent searches in session
        recent = request.session.get("recent_searches", [])

        if search_term:
            if search_term in recent:
                recent.remove(search_term)

            recent.insert(0, search_term)

            recent = recent[:5]

            request.session["recent_searches"] = recent

        movies = Movie.objects.filter(title__icontains=search_term) if search_term else Movie.objects.none()
        if search_term:
            exact_matches = list(Movie.objects.filter(title__icontains=search_term))
            exact_ids = {m.uu_id for m in exact_matches}
            
            semantic_matches = smart_search(search_term, top_n=20)
            semantic_matches = [m for m in semantic_matches if m.uu_id not in exact_ids]

            movies = exact_matches + semantic_matches
        else:
            movies = []
        return render(request, "search.html", {
            "genre": genres,
            "movies": movies,
            "search_term": search_term,
            "recent_searches": recent,
        })

    return redirect("index")

def live_search(request):

    query = request.GET.get('q', '')
    movies = Movie.objects.filter(title__icontains=query)[:5]

    results = []

    for movie in movies:
        results.append({
            "id": str(movie.uu_id),
            "title": movie.title,
        })

    return JsonResponse(results, safe=False)

@login_required(login_url='login')
def profile_view(request):
    genres = Genre.objects.all()
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    profiles = UserProfile.objects.filter(user=request.user)

    return render(request, 'profile.html', {
        'genre': genres, 
        'form': form, 
        'profile': profile,
        'profiles': profiles,
    })

@login_required(login_url='login')
def dashboard(request):

    active_profile = get_active_profile(request)

    watched_count = WatchHistory.objects.filter(
        user=request.user
    ).count()

    favorite_count = Favorite.objects.filter(
        profile=active_profile
    ).count()

    watch_later_count = WatchLater.objects.filter(
        profile=active_profile
    ).count()

    review_count = Review.objects.filter(
        user=request.user
    ).count()

    genre_count = Genre.objects.count()
    movie_count = Movie.objects.count()


    return render(request, 'dashboard.html', {

        'watched_count': watched_count,
        'favorite_count': favorite_count,
        'watch_later_count': watch_later_count,
        'review_count': review_count,
        'genre_count': genre_count,
        'movie_count': movie_count,
    })
 
@login_required(login_url='login')
def create_profile(request):
    if request.method == "POST":

        existing_count = UserProfile.objects.filter(user=request.user).count()
        if existing_count >= 5:
            messages.error(request, "You can have a maximum of 5 profiles.")
            return redirect("profile")

        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():

            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()

            messages.success(request, "New Profile Created Successfully!")

            return redirect("profile")
    
    else:

        form = UserProfileForm()

    return render(request, "create_profile.html", {
        "form": form
    })

@login_required(login_url='login')   
def select_profile(request, pk):

    profile = get_object_or_404(
        UserProfile,
        id=pk,
        user=request.user
    )

    request.session["selected_profile"] = profile.id
    request.session["selected_profile_name"] = profile.profile_name
    request.session["selected_profile_avatar"] = profile.avatar.url if profile.avatar else ""
    
    messages.success(
        request,
        f"{profile.profile_name} profile selected."
    )

    return redirect("index")

@login_required(login_url='login')
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def add_to_favorite(request, pk):

    movie = get_object_or_404(Movie, uu_id=pk)
    active_profile = get_active_profile(request)

    favorite, created = Favorite.objects.get_or_create(
        profile=active_profile,
        movie=movie
    )
    if created:
        Notification.objects.create(
            user=request.user,
            message=f"❤️ {movie.title} added to your Favorites."
        )

        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{request.user.id}_notifications",
                {
                    "type": "send_notification",
                    "message": f"❤️ {movie.title} added to your Favorites."
                }
            )
            new_count = Favorite.objects.filter(user=request.user).count()
            async_to_sync(channel_layer.group_send)(
                f"dashboard_{request.user.id}",
                {
                    "type": "dashboard_update",
                    "data": {"favorite_count": new_count}
                }
            )
        except Exception:
            pass

    return redirect('movie', pk=pk)


@login_required(login_url='login')
def favorites(request):
    active_profile = get_active_profile(request)
    favorite_movies = Favorite.objects.filter(
        profile=active_profile,
    ).select_related('movie')

    return render(request, 'favorites.html', {
        'favorite_movies': favorite_movies
    })


@login_required(login_url='login')
def remove_favorite(request, pk):
    
    movie = get_object_or_404(Movie, uu_id=pk)
    active_profile = get_active_profile(request)
    Favorite.objects.filter(
        profile=active_profile,
        movie=movie
    ).delete()

    try:
        new_count = Favorite.objects.filter(user=request.user).count()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"dashboard_{request.user.id}",
            {
                "type": "dashboard_update",
                "data": {"favorite_count": new_count}
            }
        )
    except Exception:
        pass

    return redirect('favorites')
    
@login_required(login_url='login')
def watch_history(request):

    history = WatchHistory.objects.filter(
        user=request.user
    ).select_related('movie')

    return render(request, 'history.html', {
        'history': history
    })

@login_required(login_url='login')
def notifications(request):

    notifications = Notification.objects.filter(
        user=request.user
    )

    return render(request, 'notifications.html', {
        'notifications': notifications
    })

def forgot_password(request):

    return render(request, 'forgot_password.html')

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


@login_required(login_url='login')
def create_watch_party(request, pk):
    movie = get_object_or_404(Movie, uu_id=pk)
    code = generate_room_code()
    while WatchPartyRoom.objects.filter(code=code).exists():
        code = generate_room_code()

    room = WatchPartyRoom.objects.create(
        code=code,
        movie=movie,
        host=request.user
    )
    return redirect('watch_party_room', code=room.code)


@login_required(login_url='login')
def watch_party_room(request, code):
    room = get_object_or_404(WatchPartyRoom, code=code)

    video_id_match = re.search(r"(?:v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})", room.movie.video) 
    video_id = video_id_match.group(1) if video_id_match else ""

    context = {
        'room_code': room.code,
        'movie_details': room.movie,
        'video_id': video_id,
    }
    return render(request, 'watchparty.html', context)

# Chatbot కోసం mood/keyword → genre mapping
MOOD_TO_GENRE = {
    "sad": "Drama", "emotional": "Drama", "cry": "Drama",
    "happy": "Comedy", "funny": "Comedy", "laugh": "Comedy", "fun": "Comedy",
    "scary": "Horror", "horror": "Horror", "fear": "Horror",
    "romantic": "Romance", "love": "Romance",
    "exciting": "Action", "action": "Action", "fight": "Action",
    "thrilling": "Thriller", "suspense": "Thriller", "thriller": "Thriller",
    "mystery": "Mystery", "detective": "Mystery",
    "adventure": "Adventure", "journey": "Adventure",
    "sci-fi": "Sci-Fi", "scifi": "Sci-Fi", "space": "Sci-Fi", "future": "Sci-Fi",
    "fantasy": "Fantasy", "magic": "Fantasy",
    "crime": "Crime",
}

GREETINGS = ["hi", "hello", "hey", "namaste", "హాయ్", "హలో"]


@login_required(login_url='login')
def chatbot_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST మాత్రమే అనుమతించబడుతుంది"}, status=400)

    try:
        body = json.loads(request.body)
        user_message = body.get("message", "").strip()
    except Exception:
        return JsonResponse({"error": "Invalid request"}, status=400)

    if not user_message:
        return JsonResponse({"error": "Message ఖాళీగా ఉంది"}, status=400)

    text = user_message.lower()

    # 1. Greeting handling
    if any(g in text for g in GREETINGS) and len(text.split()) <= 3:
        return JsonResponse({
            "reply": "Hi! 🎬 నేను CineVerse Assistant ని. మీకు ఏ mood లో సినిమా కావాలో చెప్పండి "
                      "(ఉదా: 'sad movie', 'funny movie', 'action movie'), లేదా genre పేరు చెప్పండి "
                      "(Action, Comedy, Drama, Horror, Romance, Thriller, Sci-Fi, Fantasy, Mystery, Adventure, Crime)."
        })

    # 2. Available genres నుండి, message లో ఏదైనా genre name directly match అవుతుందా చూడటం
    all_genres = list(Genre.objects.values_list('name', flat=True))
    matched_genre = None

    for g in all_genres:
        if g.lower() in text:
            matched_genre = g
            break

    # 3. Genre direct గా దొరకకపోతే, mood keywords చెక్ చేయడం
    if not matched_genre:
        for keyword, genre_name in MOOD_TO_GENRE.items():
            if keyword in text:
                # ఈ genre_name నిజంగా DB లో ఉందో చెక్ చేయడం
                if Genre.objects.filter(name__iexact=genre_name).exists():
                    matched_genre = genre_name
                    break

    # 4. "best" / "top rated" / "top" లాంటి overall query
    if not matched_genre and any(w in text for w in ["best", "top rated", "top", "highest rated"]):
        movies = Movie.objects.order_by('-rating')[:5]
        if movies:
            lines = [f"⭐ {m.title} ({m.genre.name}) — Rating: {m.rating}" for m in movies]
            reply = "ఇవి మా టాప్ రేటెడ్ సినిమాలు:\n" + "\n".join(lines)
        else:
            reply = "క్షమించండి, ప్రస్తుతం సినిమాలు లేవు."
        return JsonResponse({"reply": reply})

    # 5. Genre matched అయితే, ఆ genre లో టాప్ 5 సినిమాలు సూచించడం
    if matched_genre:
        movies = Movie.objects.filter(
            genre__name__iexact=matched_genre
        ).order_by('-rating')[:5]

        if movies:
            lines = [f"🎬 {m.title} — Rating: {m.rating} — {m.description[:80]}..." for m in movies]
            reply = f"'{matched_genre}' genre లో ఇవి సూచిస్తున్నాను:\n" + "\n".join(lines)
        else:
            reply = f"క్షమించండి, '{matched_genre}' genre లో సినిమాలు ప్రస్తుతం లేవు."

        return JsonResponse({"reply": reply})

    # 6. ఏమీ match అవ్వకపోతే, fallback response with available genres
    genre_list = ", ".join(all_genres)
    reply = (
        "క్షమించండి, అర్థం కాలేదు 🙏. మీకు నచ్చిన mood లేదా genre చెప్పండి.\n"
        f"అందుబాటులో ఉన్న genres: {genre_list}"
    )
    return JsonResponse({"reply": reply})
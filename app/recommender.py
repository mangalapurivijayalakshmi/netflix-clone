"""
CineVerse Recommendation Engine
--------------------------------
Content-based filtering: movie title, genre, description, cast, director
లను కలిపి TF-IDF vectors గా మార్చి, cosine similarity తో "ఇలాంటి సినిమాలు" కనుక్కుంటుంది.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Movie
from collections import Counter
from .models import WatchHistory

# ఒక్కసారి build చేసిన similarity matrix ని cache చేసుకుంటాం (ప్రతి request కి మళ్ళీ కట్టకుండా)
_cache = {"df": None, "sim_matrix": None, "vectorizer": None, "tfidf_matrix": None}


def _build_similarity_matrix():
    movies = Movie.objects.select_related('genre').all()

    data = []
    for m in movies:
        combined_text = f"{m.genre.name} {m.description} {m.cast} {m.director} {m.language}"
        data.append({
            "uu_id": str(m.uu_id),
            "combined": combined_text,
        })

    df = pd.DataFrame(data)
    if df.empty:
        return df, None

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['combined'])
    sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    _cache["df"] = df
    _cache["sim_matrix"] = sim_matrix
    _cache["vectorizer"] = tfidf         
    _cache["tfidf_matrix"] = tfidf_matrix
    return df, sim_matrix


def get_similar_movies(movie, top_n=6):
    """ఒక సినిమా కి సంబంధించి, దానితో పోలిన top_n సినిమాలు తిరిగి ఇస్తుంది."""
    df, sim_matrix = _cache["df"], _cache["sim_matrix"]
    if df is None or sim_matrix is None:
        df, sim_matrix = _build_similarity_matrix()

    if df is None or df.empty:
        return []

    movie_uu_id = str(movie.uu_id)
    matches = df.index[df['uu_id'] == movie_uu_id].tolist()
    if not matches:
        return []

    idx = matches[0]
    scores = list(enumerate(sim_matrix[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    scores = [s for s in scores if s[0] != idx][:top_n]

    similar_uu_ids = [df.iloc[i]['uu_id'] for i, _ in scores]

    similar_movies = list(Movie.objects.filter(uu_id__in=similar_uu_ids))
    order = {uid: pos for pos, uid in enumerate(similar_uu_ids)}
    similar_movies.sort(key=lambda m: order.get(str(m.uu_id), 999))

    return similar_movies


def refresh_cache():
    """కొత్త సినిమాలు add చేసిన తర్వాత, cache refresh చేయడానికి (optional)."""
    _build_similarity_matrix()

def smart_search(query, top_n=20):
    """
    Query టెక్స్ట్ ని TF-IDF space లోకి మార్చి, movies తో cosine similarity
    చూసి, అర్థపరంగా దగ్గరగా ఉన్న సినిమాలను ranked order లో తిరిగి ఇస్తుంది.
    """
    if _cache["vectorizer"] is None or _cache["tfidf_matrix"] is None:
        _build_similarity_matrix()

    vectorizer = _cache["vectorizer"]
    tfidf_matrix = _cache["tfidf_matrix"]
    df = _cache["df"]

    if vectorizer is None or df is None or df.empty or not query.strip():
        return []

    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, tfidf_matrix)[0]

    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    # score 0 అంటే సంబంధమే లేదని అర్థం, వాటిని తీసేయాలి
    ranked = [(i, s) for i, s in ranked if s > 0][:top_n]

    matched_uu_ids = [df.iloc[i]['uu_id'] for i, _ in ranked]

    movies = list(Movie.objects.filter(uu_id__in=matched_uu_ids))
    order = {uid: pos for pos, uid in enumerate(matched_uu_ids)}
    movies.sort(key=lambda m: order.get(str(m.uu_id), 999))

    return movies

def get_collaborative_recommendations(movie, top_n=6):
    """
    'ఈ సినిమా చూసినవాళ్ళు ఇంకా ఏం చూశారు' అనే collaborative filtering.
    Item-based co-occurrence: ఈ సినిమా చూసిన users, వాళ్ళు ఇంకా ఏ సినిమాలు
    ఎక్కువసార్లు కలిసి చూశారో లెక్కపెట్టి, ఆ ఆధారంగా సూచిస్తుంది.
    """
    users_who_watched = WatchHistory.objects.filter(
        movie=movie
    ).values_list('user_id', flat=True)

    if not users_who_watched:
        return []

    co_watched = WatchHistory.objects.filter(
        user_id__in=users_who_watched
    ).exclude(movie=movie).values_list('movie_id', flat=True)

    if not co_watched:
        return []

    counts = Counter(co_watched)
    ranked = counts.most_common(top_n)

    movie_ids = [mid for mid, _ in ranked]
    movies = list(Movie.objects.filter(id__in=movie_ids))

    order = {mid: pos for pos, mid in enumerate(movie_ids)}
    movies.sort(key=lambda m: order.get(m.id, 999))

    return movies
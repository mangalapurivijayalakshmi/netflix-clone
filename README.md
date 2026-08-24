# 🎬 Netflix Clone — Django Full-Stack Project

A feature-rich Netflix-inspired streaming platform built with Django, Django Channels (WebSockets), and Django REST Framework. This project replicates core Netflix functionality including multi-profile support, personalized recommendations, real-time features, and a custom subtitle system.

---

## ✨ Features

### Authentication & Profiles
- User Signup / Login / Logout
- Multiple Profiles per account ("Who's watching" style, up to 5 profiles)
- Profile pictures / avatars

### Movie Browsing
- Genre-based filtering and sorting (rating, latest, views, A-Z)
- Live search with autocomplete + recent search history
- Pagination
- Curated rows: Trending, Top Rated, Originals, Recently Added, Top 10, Recommended

### Personalization
- Continue Watching with progress tracking
- Watch History
- Genre-based recommendation engine
- My List, Favorites, and Watch Later (three independent saved lists)
- User Dashboard with activity stats

### Engagement
- Reviews & star ratings (with average rating calculation)
- Real-time notifications (via WebSockets)
- **Watch Party** — synchronized group viewing with shareable room codes
- Live chat + typing indicators on movie pages
- Real-time "watching now" and trending counters
- Online presence indicator

### Custom Subtitle System
- Timestamp-based subtitle overlay synced with YouTube Player API
- Managed via Django Admin (simple `start-end|text` format)

### REST API
- Token-based authentication (Django REST Framework)
- Endpoints for movies, genres, recommendations, favorites, watch later, my list, profiles, and notifications
- Tested via Postman

### Responsive Design
- Mobile, tablet, and desktop layouts
- Tested on real devices

### Internationalization
- Multi-language support (English, Telugu, Hindi)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.0 |
| Real-time | Django Channels + Daphne (ASGI) |
| API | Django REST Framework (Token Auth) |
| Database | SQLite (dev) |
| Caching / Channel Layer | Redis |
| Frontend | Django Templates, vanilla JS, CSS (custom, responsive) |
| Video | YouTube IFrame Player API |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Redis server (running locally or via a hosted provider)

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Netflix_Clone

# 2. Create and activate a virtual environment
python -m venv myenv
myenv\Scripts\activate      # Windows
# source myenv/bin/activate # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create an admin account
python manage.py createsuperuser

# 6. Run the development server (ASGI, required for WebSockets)
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

### Adding Movies
Movies (including subtitles) are managed through the Django Admin panel at `/admin/`.

---

## 📁 Project Structure

```
Netflix_Clone/
├── app/
│   ├── models.py          # Movie, User Profile, Favorites, Reviews, etc.
│   ├── views.py            # Web views
│   ├── api_views.py        # REST API views
│   ├── serializers.py      # DRF serializers
│   ├── consumers.py        # WebSocket consumers
│   ├── routing.py          # WebSocket URL routing
│   ├── urls.py / api_urls.py
│   └── templates/
├── Netflix_Clone/
│   ├── settings.py
│   └── asgi.py
└── manage.py
```

---

## 📌 Notes

- This is a learning/portfolio project inspired by Netflix's UI and features. Not affiliated with Netflix.
- Video playback uses publicly available YouTube trailers/content.

---

## 🙋 Author

Built by Mangalapuri Vijayalakshmi as a full-stack learning project.
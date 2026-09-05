# 🎬 CineVerse — Django Full-Stack Streaming Platform

A feature-rich streaming platform built with Django, Django Channels (WebSockets), and Django REST Framework, inspired by Netflix's UI and core features. This project demonstrates multi-profile support, personalized recommendations, real-time features, and a custom subtitle system.

**🔗 Live Demo:** [https://netflix-clone-nbcj.onrender.com](https://netflix-clone-nbcj.onrender.com)
*(Free-tier hosting — first load may take ~50 seconds while the server spins up)*

---

## 📸 Screenshots

| Login | Home |
|---|---|
| ![Login](screenshots/login.png) | ![Home](screenshots/home.png) |

| Movie Page | Dashboard |
|---|---|
| ![Movie](screenshots/movie.png) | ![Dashboard](screenshots/dashboard.png) |

*(Add your own screenshots to a `screenshots/` folder in the repo and update the paths above.)*

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
| Database | SQLite (dev/demo) |
| Caching / Channel Layer | Redis |
| Frontend | Django Templates, vanilla JS, CSS (custom, responsive) |
| Video | YouTube IFrame Player API |
| Deployment | Render (Gunicorn + WhiteNoise) |

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

## 🔐 Environment Variables

This project reads sensitive configuration from environment variables (with safe local defaults), following 12-factor app principles for production deployments:

| Variable | Purpose | Example |
|---|---|---|
| `SECRET_KEY` | Django cryptographic signing key | random 50-char string |
| `DEBUG` | Enables/disables debug mode | `False` in production |
| `ALLOWED_HOSTS` | Comma-separated list of allowed domains | `.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | Trusted origins for CSRF protection | `https://yourapp.onrender.com` |
| `REDIS_URL` | Redis connection string (caching + Channels) | `redis://host:6379` |

For local development, sensible defaults are already set in `settings.py`, so the app runs out of the box without configuring these.

---

## 📁 Project Structure

Netflix_Clone/
├── app/
│ ├── models.py # Movie, User Profile, Favorites, Reviews, etc.
│ ├── views.py # Web views
│ ├── api_views.py # REST API views
│ ├── serializers.py # DRF serializers
│ ├── consumers.py # WebSocket consumers
│ ├── routing.py # WebSocket URL routing
│ ├── urls.py / api_urls.py
│ └── templates/
├── Netflix_Clone/
│ ├── settings.py
│ └── asgi.py
└── manage.py

---

## ⚠️ Known Limitations

- **Database persistence**: The demo deployment uses SQLite on Render's free tier, whose filesystem is ephemeral — data resets on every redeploy or restart. This is acceptable for a portfolio/demo project; a production version would migrate to PostgreSQL (Render offers a free tier) for persistent storage.
- **Free-tier cold starts**: The hosted demo spins down after inactivity, so the first request after idle time can take up to 50 seconds.

---

## 📌 Notes

- This is a learning/portfolio project inspired by Netflix's UI and features. Not affiliated with or endorsed by Netflix, Inc.
- Video playback uses publicly available YouTube trailers/content.

---

## 🙋 Author

Built by Mangalapuri Vijayalakshmi as a full-stack learning project.
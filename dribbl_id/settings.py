"""
Django settings for dribbl_id project.
Django 5.2.x
"""

from pathlib import Path
import os
import sys
from urllib.parse import quote_plus

from dotenv import load_dotenv
import dj_database_url

# ── Path & .env ─────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# Muat .env.prod kalau ada (untuk PWS/production), kalau tidak pakai .env
if (BASE_DIR / ".env.prod").exists():
    load_dotenv(BASE_DIR / ".env.prod")
else:
    load_dotenv(BASE_DIR / ".env")

# ── Mode & Security ─────────────────────────────────────────────────────────────
PRODUCTION = os.getenv("PRODUCTION", "False").strip().lower() == "true"
DEBUG = os.getenv("DEBUG", "True").strip().lower() == "true" and not PRODUCTION

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "dev-only-secret-key-change-this-in-.env",  # aman untuk lokal saja
)

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    # domain PWS kamu:
    "febrian-abimanyu-dribbl-id.pbp.cs.ui.ac.id",
] + os.getenv("ALLOWED_HOSTS_EXTRA", "").split()

CSRF_TRUSTED_ORIGINS = [
    "https://*.pbp.cs.ui.ac.id",
    "https://febrian-abimanyu-dribbl-id.pbp.cs.ui.ac.id",
] + [o for o in os.getenv("CSRF_EXTRA", "").split() if o]

# Jika di balik proxy/load balancer (umum di PWS)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if PRODUCTION:
    # Best practices security flags
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7   # 1 minggu
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
else:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False

# ── Aplikasi ────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Apps project
    "main",
    "events",
    "news",
    "matches",
    "teams",
    "players",
]

AUTH_USER_MODEL = "main.CustomUser"

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/login/"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # custom
    "main.middleware.CustomAuthMiddleware",
]

ROOT_URLCONF = "dribbl_id.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dribbl_id.wsgi.application"

# ── Database (SATU sumber, env-driven) ─────────────────────────────────────────
# Aturan:
# 1) Jika ada DATABASE_URL → pakai itu (paksa SSL pada production).
# 2) Jika DATABASE_URL berupa 'postgres:///DBNAME' (tanpa host), bangun dari DB_*.
# 3) Jika tidak ada → fallback ke SQLite (dev).
DATABASE_URL = os.getenv("DATABASE_URL")

def build_url_from_parts() -> str | None:
    db_name = os.getenv("DB_NAME")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    if all([db_name, db_host, db_user, db_password]):
        return (
            f"postgres://{quote_plus(db_user)}:{quote_plus(db_password)}@"
            f"{db_host}:{db_port}/{db_name}"
        )
    return None

# Perbaiki URL tanpa host
if DATABASE_URL and DATABASE_URL.startswith("postgres:///"):
    fixed = build_url_from_parts()
    if fixed:
        DATABASE_URL = fixed

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=int(os.getenv("DB_CONN_MAX_AGE", "600")),
            ssl_require=PRODUCTION,  # SSL diwajibkan di production
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Gunakan SQLite in-memory saat unit test agar stabil & cepat
if "test" in sys.argv:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

# ── Password validation ─────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── I18N / TZ ───────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True

# ── Static & Media ──────────────────────────────────────────────────────────────
# Static
STATIC_URL = "static/"
if DEBUG:
    STATICFILES_DIRS = [BASE_DIR / "static"]  # /static di root project (dev)
else:
    STATIC_ROOT = BASE_DIR / "static"         # collectstatic (prod)

# Media (kalau diperlukan)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── Default PK field ────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Misc ────────────────────────────────────────────────────────────────────────
APPEND_SLASH = True

# ── Logging ringan (bantu debug di server) ──────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO" if PRODUCTION else "DEBUG",
    },
}

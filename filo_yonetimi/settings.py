"""
Django settings for filo_yonetimi project.
Gazi YBS - Araç Takip Sistemi
"""
import os
from pathlib import Path

# Proje ana dizini
BASE_DIR = Path(__file__).resolve().parent.parent

# Güvenlik anahtarı
SECRET_KEY = 'django-insecure-zeynep-filo-projesi'

# Hata ayıklama modu
DEBUG = True

ALLOWED_HOSTS = ['*']

# UYGULAMA TANIMLARI
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # SENİN OLUŞTURDUĞUN UYGULAMA:
    'arac_takip', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'filo_yonetimi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'filo_yonetimi.wsgi.application'

# VERİTABANI AYARLARI (MSSQL)
# settings.py içindeki DATABASES kısmı:

# settings.py dosyasında DATABASES kısmı:

# settings.py dosyasındaki DATABASES kısmını tamamen sil ve bunu yapıştır:

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'FiloDB',
        'USER': '',
        'PASSWORD': '',
        'HOST': r'localhost\SQLEXPRESS',  # Senin sunucu adın (Aynen kalsın)
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            # BURASI ÇOK ÖNEMLİ:
            # 1. TrustServerCertificate=yes : Sertifikaya güven.
            # 2. Trusted_Connection=yes     : Şifresiz (Windows) giriş yap.
            # 3. Encrypt=no                 : Şifreleme zorlama (Hatayı çözen kısım).
            'extra_params': 'TrustServerCertificate=yes;Trusted_Connection=yes;Encrypt=no',
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
]

LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

# Fotoğraf yüklemeleri için (Hasar fotoları)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Kullanıcı giriş yapınca buraya gitsin:
LOGIN_REDIRECT_URL = 'arac_listesi'  # Bu isim urls.py'deki name='arac_listesi' ile aynı

# Çıkış yapınca buraya gitsin (Anasayfaya):
LOGOUT_REDIRECT_URL = 'anasayfa'

# Giriş yapmamış biri yasaklı sayfaya girerse buraya gitsin:
LOGIN_URL = 'giris_yap'
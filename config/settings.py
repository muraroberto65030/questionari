from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '324kjf84ch4c402f42ohf4'

# SECURITY WARNING: don't run with debug turned on in production!
# Check if running on PythonAnywhere (or other prod env) to toggle Debug
DEBUG = 'pythonanywhere' not in str(BASE_DIR)

if DEBUG:
    ALLOWED_HOSTS = ['*']
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
else:
    ALLOWED_HOSTS = ['3sc0b4r.pythonanywhere.com']
    CORS_ALLOWED_ORIGINS = [
        "https://questionaricompt.vercel.app",
    ]
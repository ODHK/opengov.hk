web: gunicorn froide.wsgi
worker: celery -A froide worker -Q emailfetch,celery -B -l INFO
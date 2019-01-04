web: gunicorn -k gevent --bind 0.0.0.0:$PORT app:app
worker: celery -A celery_worker.celery worker
beat: celery -A celery_worker.celery beat
redis: redis-server --dir ./data/redis --bind 127.0.0.1
bot: python bot.py
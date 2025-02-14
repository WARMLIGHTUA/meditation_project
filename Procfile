web: gunicorn meditation_app.wsgi:application --bind 0.0.0.0:$PORT --log-level debug --access-logfile - --error-logfile -
release: python manage.py migrate 
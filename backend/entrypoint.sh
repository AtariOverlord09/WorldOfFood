#!/bin/bash

while ! nc -z db 5432; do
    echo "Waiting for db start..."
    sleep 1
done

python manage.py migrate
python manage.py collectstatic --noinput
gunicorn --bind 0.0.0.0:8030 foodgram.wsgi

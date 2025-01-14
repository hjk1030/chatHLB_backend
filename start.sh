#!/bin/sh
mkdir media
mkdir data
cp advertise_image/abcdefgHIJKLMNopqRSTuvwXYZ123456.jpg media/abcdefgHIJKLMNopqRSTuvwXYZ123456.jpg
python3 manage.py makemigrations user task bank advertise
python3 manage.py migrate
nginx -g 'daemon on;'
setsid redis-server & 
setsid python3 manage.py qcluster &

uwsgi --module=chatHLB_backend.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=chatHLB_backend.settings \
    --master \
    --http=0.0.0.0:8000 \
    --processes=5 \
    --harakiri=60 \
    --max-requests=5000 \
    --vacuum
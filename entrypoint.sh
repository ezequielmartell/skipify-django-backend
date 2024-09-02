#!/bin/sh
# echo 'Waiting for postgres...'
# while ! nc -z db 5432; do
#     sleep 0.1
# done
# echo 'PostgreSQL started'

# python manage.py makemigrations
echo 'Running migrations...'
python manage.py migrate
echo 'Initializing an Admin if no users exist'
python manage.py initiadmin
echo 'Collecting static files...'
python manage.py collectstatic --no-input

exec "$@"


# aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 637423655132.dkr.ecr.us-east-2.amazonaws.com
# docker build . -t 637423655132.dkr.ecr.us-east-2.amazonaws.com/django-aws-backend:latest
# docker push 637423655132.dkr.ecr.us-east-2.amazonaws.com/django-aws-backend:latest
FROM python:3.10-slim-buster

EXPOSE 8000

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update  \
    && apt-get --no-install-recommends install -y \
        build-essential \
        libssl-dev \
        libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip
# RUN pip install gunicorn==20.1.0

COPY django-aws-backend/requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

WORKDIR /app
COPY django-aws-backend /app
# COPY . /app
ADD django-aws-frontend/build /django-aws-frontend/build
# /root/aws-infrastructure/django-aws/django-aws-backend/manage.py
RUN python manage.py collectstatic --noinput


RUN chmod +x ./entrypoint.sh

# COPY . .

ENTRYPOINT ["./entrypoint.sh"]
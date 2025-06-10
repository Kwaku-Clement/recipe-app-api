FROM python:3.12-alpine

LABEL maintainer="Clement Adu Asante <aduclem@gmail.com>"
LABEL version="1.0"
LABEL description="Recipe App API with external image storage"

ENV PYTHONUNBUFFERED=1

# Install build dependencies for potential native packages
RUN apk add --no-cache build-base libffi-dev && \
    rm -rf /var/cache/apk/*

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

ARG DEV=false

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-dev \
    build-base postgresql-dev musl-dev zlib zlib-dev libffi-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then \
    /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-dev && \
    adduser --disabled-password --no-create-home django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol  # Fixed typo: chomd -> chmod

COPY ./app /app
WORKDIR /app
EXPOSE 8000

ENV PATH="/py/bin:$PATH"

USER django-user

# Development server (replace with gunicorn for production)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# For production: CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi:application"]
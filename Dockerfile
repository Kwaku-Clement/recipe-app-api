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
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then \
    /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    apk del build-base libffi-dev && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

COPY ./app /app
WORKDIR /app
EXPOSE 8000

ENV PATH="/py/bin:$PATH"

USER django-user

# Development server (replace with gunicorn for production)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# For production: CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi:application"]
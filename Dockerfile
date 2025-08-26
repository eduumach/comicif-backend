FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.in-project true
RUN poetry install --only main --no-interaction

COPY . .

RUN poetry run python manage.py collectstatic --noinput

CMD ["sh", "-c", "poetry run python manage.py migrate && poetry run gunicorn --bind 0.0.0.0:8000 --workers 4 config.wsgi:application"]
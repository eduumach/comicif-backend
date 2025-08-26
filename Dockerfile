FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"

COPY . .

RUN mkdir -p staticfiles logs

EXPOSE 8000

# Start command
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 --workers 4 config.wsgi:application"]
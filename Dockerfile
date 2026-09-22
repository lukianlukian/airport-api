FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SQLITE_PATH=/data/db.sqlite3

WORKDIR /app

COPY requirements-runtime.txt .
RUN python -m pip install --no-cache-dir -r requirements-runtime.txt

RUN groupadd --system app && useradd --system --gid app app \
    && mkdir /data && chown app:app /data

COPY airport ./airport
COPY airport_service ./airport_service
COPY user ./user
COPY manage.py .

USER app
EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && exec python manage.py runserver 0.0.0.0:8000 --noreload"]

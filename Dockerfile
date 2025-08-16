FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for Playwright headless Chromium will be installed by the next command
COPY requirements.txt ./
RUN pip install -r requirements.txt && \
    python -m playwright install --with-deps chromium

COPY . .

# Expose if needed by your platform
EXPOSE 8080

# Use gunicorn in prod; change module if your entrypoint differs
CMD ["gunicorn", "-w", "2", "-k", "gthread", "--threads", "4", "-b", "0.0.0.0:8080", "app.main:app"]

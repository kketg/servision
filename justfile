# Install dependencies
install:
    pip install -r requirements.txt

# Spin up docker compose
up:
    docker compose up -d

run:
    cd server
    gunicorn --bind 0.0.0.0:8080 main:fl --log-level debug

worker:
    celery -A main worker --loglevel=info

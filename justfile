# Install dependencies
install:
    pip install -r requirements.txt

# Spin up docker compose
up:
    docker compose up -d

run:
    cd server
    gunicorn --bind 0.0.0.0:8080 main:fl --log-level debug

cdn:
    cd cdn
    gunicorn --bind 0.0.0.0:9090 main:flask --log-level debug

down:
    docker compose down

worker:
    celery -A main worker --loglevel=info

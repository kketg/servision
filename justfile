# Install dependencies
install:
    pip install -r requirements.txt

# Spin up docker compose as well as main server
up:
    docker compose up -d
    cd server
    python main.py

worker:
    celery -A main worker --loglevel=info

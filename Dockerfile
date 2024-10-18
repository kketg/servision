# syntax=docker/dockerfile:1
FROM python:3.12.6-slim
WORKDIR /web
COPY requirements.txt requirements.txt
COPY config.json config.json
COPY .env .env
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8080
COPY ./server /web/server
WORKDIR /web/server
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
CMD ["flask", "run", "--debug"]
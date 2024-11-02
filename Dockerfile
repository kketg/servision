# syntax=docker/dockerfile:1
FROM python:3.12.7-slim
WORKDIR /web
COPY requirements.txt requirements.txt
COPY config.json config.json
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8080
COPY ./server /web/server
WORKDIR /web/server
ENV PYTHONUNBUFFERED 1
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:fl", "--log-level", "debug"]
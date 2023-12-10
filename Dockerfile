#FROM python:3.11-alpine
FROM python:3.11-slim-bookworm

ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=True
ENV FLASK_APP="app.py"
ENV FLASK_ENV="development"

WORKDIR /app

RUN apt update -qq && apt install -y curl && apt clean
RUN pip install --upgrade --no-cache-dir pip
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.7.1 && cp /root/.local/bin/poetry /usr/local/bin

COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-root

COPY . /app

CMD bash

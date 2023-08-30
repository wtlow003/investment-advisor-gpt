# Pull base image
FROM python:3.11

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code/

# Install dependencies
COPY poetry.lock .
COPY pyproject.toml .
RUN pip install poetry && \
    poetry config installer.max-workers 10 && \
    poetry config virtualenvs.create false && \
    poetry install

COPY ./src/fastapi /code/src/fastapi
COPY ./src/model /code/src/model
COPY ./db /code/db
COPY .env /code/.env

EXPOSE 8000

CMD poetry run uvicon src.fastapi.api:app --host 0.0.0.0
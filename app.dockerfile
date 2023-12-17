FROM python:3.11-slim-buster

# set working directory
WORKDIR /demo

# Copy only requirements file
COPY ./requirements.txt /demo/requirements.txt

# Install requirements
RUN pip install --no-cache-dir --upgrade -r /demo/requirements.txt

# Copy over html template & static files
COPY ./templates /demo/templates
COPY ./static /demo/static

# Install the app
COPY ./app /demo/app

# Alembic stuff
COPY ./alembic.ini /demo/alembic.ini
COPY ./alembic /demo/alembic

# Copy over env vars
COPY ./.env /demo/.env

# Launch the app
CMD \
    alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000

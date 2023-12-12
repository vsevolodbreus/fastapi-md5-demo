FROM python:3.11-slim-buster

# set working directory
WORKDIR /app

# Copy only requirements file
COPY ./requirements.txt /app/requirements.txt

# Install requirements
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy over html template & static files
COPY ./templates /app/templates
COPY ./static /app/static

# Install the app
COPY ./setup.py /app/setup.py
RUN mkdir -p src/app
COPY ./src/app /app/src/app
RUN python -m pip install -e .

# Alembic stuff
COPY ./alembic.ini /app/alembic.ini
COPY ./alembic /app/alembic

# Copy over env vars
COPY ./.env /app/.env

# Launch the app
CMD \
    alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000

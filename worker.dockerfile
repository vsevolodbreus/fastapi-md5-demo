FROM python:3.11-slim-buster

# set working directory
WORKDIR /worker

# Copy only requirements file
COPY ./requirements.txt /worker/requirements.txt

# Install requirements
RUN pip install --no-cache-dir --upgrade -r /worker/requirements.txt

# Install the worker
COPY ./app /worker/app

# Copy over env vars
COPY ./.env /worker/.env

# Launch the app
ARG CELERY_QUEUE
CMD celery -A app.worker worker -l info -Q ${CELERY_QUEUE} -c 1
